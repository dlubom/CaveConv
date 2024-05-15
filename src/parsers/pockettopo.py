# pylint: disable=W0511
"""
Module for parsing PocketTopo data files (.top).

The module implements classes and methods to read PocketTopo data files, which include details of cave mapping
trips, shots, and references. 

The format is based on the PocketTopo File Formats document dated 17.3.2010 by bh (file: "PocketTopoFileFormat.txt").
"""

import struct
import datetime
from models import CaveData, Trip, Shot, Reference, Mapping, Element, Drawing


class PocketTopo:
    """
    A parser for PocketTopo files, handling the extraction of trips, shots, and drawing data.
    """

    def __init__(self, filename):
        """
        Initialize the PocketTopo parser with a file path.

        Args:
            filename (str): The path to the .top file to be read.
        """
        self.filename = filename

    def read_string(self, f):
        """Read a string from the file.

        String = { // .Net string format
            Byte[] length // unsigned, encoded in 7 bit chunks, little endian, bit7 set in all but the last byte
            Byte[length]  // UTF8 encoded, 1 to 3 bytes per character, not 0 terminated
        }
        """
        length = 0
        shift = 0
        while True:
            byte = f.read(1)
            if not byte:
                raise ValueError("Unexpected end of file while reading string length.")
            byte = ord(byte)
            length |= (byte & 0x7F) << shift
            if (byte & 0x80) == 0:
                break
            shift += 7

        string_bytes = f.read(length)
        if len(string_bytes) != length:
            raise ValueError("Unexpected end of file while reading the string data.")
        return string_bytes.decode("utf-8")

    def read_id(self, f):
        """Read a station ID, which is either a string or a number.

        Id = { // station identification
                Int32 value  // 0x80000000: undefined, <0: plain numbers + 0x80000001, >=0: major<<16|minor
        }
        """
        (raw_value,) = struct.unpack("<I", f.read(4))

        if raw_value == 0x80000000:
            return None
        if raw_value < 0:
            return raw_value + 0x80000001
        major = raw_value >> 16
        minor = raw_value & 0xFFFF
        return f"{major}.{minor}"

    def read_point(self, f):
        """Read a point consisting of x and y coordinates.

        Point = {  // world coordinates relative to first station in file
            Int32 x  // mm
            Int32 y  // mm
        }
        """
        x, y = struct.unpack("<ii", f.read(8))
        return (x, y)

    def read_trip(self, f):
        """Read a trip data entry from the file.

        Trip = {
            Int64 time  // ticks (100ns units starting at 1.1.1)
            String comment
            Int16 declination  // internal angle units (full circle = 2^16)
        }
        """
        (time_ticks,) = struct.unpack("<Q", f.read(8))
        comment = self.read_string(f)
        (declination,) = struct.unpack("<h", f.read(2))
        declination = (declination * 360.0) / 65536.0
        time = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=time_ticks / 10)
        return Trip(time, comment, declination)

    def read_shot(self, f):
        """Read a shot data entry from the file.

        Shot = {
            Id from
            Id to
            Int32 dist  // mm
            Int16 azimuth  // internal angle units (full circle = 2^16, north = 0, east = 0x4000)
            Int16 inclination // internal angle units (full circle = 2^16, up = 0x4000, down = 0xC000)
            Byte flags  // bit0: flipped shot
            Byte roll   // roll angle (full circle = 256, disply up = 0, left = 64, down = 128)
            Int16 tripIndex  // -1: no trip, >=0: trip reference
            if (flags & 2)
                String comment
        }
        """

        from_id = self.read_id(f)
        to_id = self.read_id(f)
        (dist,) = struct.unpack("<i", f.read(4))
        azimuth, inclination = struct.unpack("<hh", f.read(4))
        flags, roll = struct.unpack("<BB", f.read(2))
        # TODO test and use flipped shot flag
        (trip_index,) = struct.unpack("<h", f.read(2))
        comment = self.read_string(f) if flags & 2 else None

        azimuth = (azimuth * 360.0) / 65536.0
        azimuth = azimuth if azimuth >= 0 else azimuth + 360.0
        inclination = (inclination * 360.0) / 65536.0
        dist = dist / 1000.0

        return Shot(
            from_id,
            to_id,
            dist,
            azimuth,
            inclination,
            flags,
            roll,
            to_id is None,
            trip_index,
            comment,
        )

    def read_reference(self, f):
        """Read a reference data entry from the file.

        Reference = {
            Id station
            Int64 east     // mm
            Int64 north    // mm
            Int32 altitude // mm above sea level
            String comment
        }
        """
        station_id = self.read_id(f)
        east, north = struct.unpack("<qq", f.read(16))
        (altitude,) = struct.unpack("<i", f.read(4))
        comment = self.read_string(f)
        return Reference(station_id, east, north, altitude, comment)

    def read_mapping(self, f):
        """
        Read a mapping entry from the file.

        Mapping = {  // least recently used scroll position and scale
            Point origin // middle of screen relative to first reference
            Int32 scale  // 10..50000
        }
        """
        origin = self.read_point(f)
        (scale,) = struct.unpack("<i", f.read(4))
        return Mapping(origin, scale)

    def read_element(self, f):
        """
        Element = {
            Byte id  // element type
            ...
        }

        PolygonElement = {
            Byte 1  // id
            Int32 pointCount
            Point[pointCount] points // open polygon
            Byte color // black = 1, gray = 2, brown = 3, blue = 4; red = 5, green = 6, orange = 7
        }

        XSectionElement = {
            Byte 3  // id
            Point pos  // drawing position
            Id station
            Int32 direction // -1: horizontal, >=0; projection azimuth (internal angle units)
        }
        """
        element_id = ord(f.read(1))
        if element_id == 1:
            point_count = struct.unpack("<i", f.read(4))[0]
            points = [self.read_point(f) for _ in range(point_count)]
            color = ord(f.read(1))
            return Element(element_id, {"points": points, "color": color})
        if element_id == 3:
            pos = self.read_point(f)
            station = self.read_id(f)
            direction = struct.unpack("<i", f.read(4))[0]
            return Element(element_id, {"pos": pos, "station": station, "direction": direction})
        raise ValueError(f"Unknown element type: {element_id}")

    def read_drawing(self, f):
        """
        Read a drawing from the mapping data.

        Drawing = {
            Mapping mapping
            Element[] elements
            Byte 0  // end of element list
        }
        """
        mapping = self.read_mapping(f)
        elements = []
        while True:
            if f.peek(1)[:1] == b"\x00":
                break
            element = self.read_element(f)
            elements.append(element)
        f.read(1)
        return Drawing(mapping, elements)

    def read_pockettopo_file(self):
        """
        Read the PocketTopo file and return the cave data.

        PocketTopo Data File (.top)

        Version 3

        File = {
            Byte 'T'
            Byte 'o'
            Byte 'p'
            Byte 3  // version
            Int32 tripCount
            Trip[tripCount] trips
            Int32 shotCount
            Shot[shotCount] shots
            Int32 refCount
            Reference[refCount] references
            Mapping overview
            Drawing outline
            Drawing sideview
        }
        """
        with open(self.filename, "rb") as f:
            if f.read(4) != b"Top\x03":
                raise ValueError("Not a PocketTopo file or unsupported version")

            trip_count = struct.unpack("<i", f.read(4))[0]
            trips = [self.read_trip(f) for _ in range(trip_count)]

            shot_count = struct.unpack("<i", f.read(4))[0]
            shots = [self.read_shot(f) for _ in range(shot_count)]

            ref_count = struct.unpack("<i", f.read(4))[0]
            references = [self.read_reference(f) for _ in range(ref_count)]

            mapping_overview = self.read_mapping(f)
            drawing_outline = self.read_drawing(f)
            drawing_sideview = self.read_drawing(f)

            cave_data = CaveData()
            for trip in trips:
                cave_data.add_trip(trip)
            for shot in shots:
                cave_data.add_shot(shot)
            for reference in references:
                cave_data.add_reference(reference)
            cave_data.set_mapping_overview(mapping_overview)
            cave_data.set_drawing_outline(drawing_outline)
            cave_data.set_drawing_sideview(drawing_sideview)

            return cave_data
