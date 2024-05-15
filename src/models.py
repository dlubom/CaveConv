# pylint: disable=R0903,R0902,R0913
"""
Models for representing cave survey data.
"""
from collections import defaultdict
import pandas as pd


class Trip:
    """
    Represents a cave survey trip.
    """

    def __init__(self, time, comment, declination):
        """
        Initialize a Trip instance.

        Args:
            time (datetime): The time of the trip.
            comment (str): The comment associated with the trip.
            declination (float): The declination angle for the trip.
        """
        self.time = time
        self.comment = comment
        self.declination = declination


class Shot:
    """
    Represents a shot taken during a cave survey.
    """

    def __init__(
        self,
        from_id,
        to_id,
        dist,
        azimuth,
        inclination,
        flags,
        roll,
        splay,
        trip_index,
        comment,
    ):
        """
        Initialize a Shot instance.

        Args:
            from_id (str): The ID of the starting station.
            to_id (str): The ID of the ending station.
            dist (float): Distance of the shot.
            azimuth (float): Azimuth angle of the shot.
            inclination (float): Inclination angle of the shot.
            flags (int): Flags associated with the shot.
            roll (int): Roll angle of the shot.
            splay (bool): Indicates if this is a splay shot.
            trip_index (int): Index of the trip associated with the shot.
            comment (str): Comment associated with the shot.
        """
        self.from_id = from_id
        self.to_id = to_id
        self.dist = dist
        self.azimuth = azimuth
        self.inclination = inclination
        self.flags = flags
        self.roll = roll
        self.splay = splay
        self.trip_index = trip_index
        self.comment = comment

    def inverted_shot(self):
        """
        Creates an inverted version of the current shot
        """

        inverted_azimuth = (self.azimuth + 180) % 360
        inverted_inclination = -self.inclination
        return Shot(
            self.to_id,
            self.from_id,
            self.dist,
            inverted_azimuth,
            inverted_inclination,
            self.flags,
            self.roll,
            self.splay,
            self.trip_index,
            self.comment,
        )


class Reference:
    """
    Represents a reference point in a cave survey.
    """

    def __init__(self, station, east, north, altitude, comment):
        """
        Initialize a Reference instance.

        Args:
            station (str): The ID of the reference station.
            east (float): East coordinate of the reference.
            north (float): North coordinate of the reference.
            altitude (float): Altitude of the reference.
            comment (str): Comment associated with the reference.
        """
        self.station = station
        self.east = east
        self.north = north
        self.altitude = altitude
        self.comment = comment


class Mapping:
    """
    Represents mapping data for a cave survey.
    """

    def __init__(self, origin, scale):
        """
        Initialize a Mapping instance.

        Args:
            origin (tuple): The origin point of the mapping.
            scale (int): The scale of the mapping.
        """
        self.origin = origin
        self.scale = scale


class Element:
    """
    Represents an element in the cave drawing.
    """

    def __init__(self, element_id, data):
        """
        Initialize an Element instance.

        Args:
            element_id (int): The ID of the element.
            data (dict): Data associated with the element.
        """
        self.element_id = element_id
        self.data = data


class Drawing:
    """
    Represents a drawing in the cave survey.
    """

    def __init__(self, mapping, elements):
        """
        Initialize a Drawing instance.

        Args:
            mapping (Mapping): The mapping data for the drawing.
            elements (list): A list of elements in the drawing.
        """
        self.mapping = mapping
        self.elements = elements


class CaveData:
    """
    Represents the complete data for a cave survey.
    """

    def __init__(self):
        """
        Initialize a CaveData instance.
        """
        self.trips = []
        self.shots = []
        self.references = []
        self.mapping_overview = None
        self.drawing_outline = None
        self.drawing_sideview = None
        self.shots_dict = defaultdict(list)  # To handle duplicated shots

    def add_trip(self, trip):
        """
        Add a trip to the cave data.

        Args:
            trip (Trip): The trip to add.
        """
        self.trips.append(trip)

    def add_shot(self, shot):
        """
        Add a shot to the cave data.

        Args:
            shot (Shot): The shot to add.
        """
        self.shots.append(shot)

        if shot.splay:
            return

        # Add both normal and inverted shots to handle bidirectional shots
        self.shots_dict[(shot.from_id, shot.to_id)].append(shot)
        inverted = shot.inverted_shot()
        self.shots_dict[(inverted.from_id, inverted.to_id)].append(inverted)

    def add_reference(self, reference):
        """
        Add a reference to the cave data.

        Args:
            reference (Reference): The reference to add.
        """
        self.references.append(reference)

    def set_mapping_overview(self, mapping):
        """
        Set the mapping overview for the cave data.

        Args:
            mapping (Mapping): The mapping overview to set.
        """
        self.mapping_overview = mapping

    def set_drawing_outline(self, drawing):
        """
        Set the drawing outline for the cave data.

        Args:
            drawing (Drawing): The drawing outline to set.
        """
        self.drawing_outline = drawing

    def set_drawing_sideview(self, drawing):
        """
        Set the drawing sideview for the cave data.

        Args:
            drawing (Drawing): The drawing sideview to set.
        """
        self.drawing_sideview = drawing

    def total_distance(self):
        """
        Calculate the total distance of all shots in the cave data.

        Returns:
            float: The total distance.
        """
        df = self.get_grouped_shots()
        return df["dist"].sum()

    def get_grouped_shots(self):
        """
        Get the shots grouped by 'from' and 'to' stations, with measurements averaged.

        Returns:
            pd.DataFrame: DataFrame containing the grouped shots.
        """
        data = []
        seen_pairs = set()
        for (from_id, to_id), measurements in self.shots_dict.items():
            if (from_id, to_id) not in seen_pairs:
                seen_pairs.add((from_id, to_id))
                seen_pairs.add((to_id, from_id))  # Mark both directions as seen
                avg_dist = sum(m.dist for m in measurements) / len(measurements)
                avg_azimuth = sum(m.azimuth for m in measurements) / len(measurements)
                avg_inclination = sum(m.inclination for m in measurements) / len(measurements)
                comment = "; ".join(m.comment for m in measurements if m.comment)
                data.append(
                    {
                        "from_id": from_id,
                        "to_id": to_id,
                        "dist": avg_dist,
                        "azimuth": avg_azimuth,
                        "inclination": avg_inclination,
                        "comment": comment,
                    }
                )

        df = pd.DataFrame(data)

        return df
