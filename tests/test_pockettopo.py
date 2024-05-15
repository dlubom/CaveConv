"""
This module contains tests for the PocketTopo parser functionality.
It tests various aspects of data extraction and integrity from a .top file.
"""

import os
import datetime
import pytest
import pandas as pd
from parsers.pockettopo import PocketTopo


def test_read_pockettopo_file():
    """
    Test the functionality of reading PocketTopo files and extracting shot and trip data.
    Ensures that the correct number of shots and trips are extracted and that specific
    data points are as expected.
    """
    test_file_path = os.path.join(os.path.dirname(__file__), "data", "01", "example.top")
    caveconv = PocketTopo(test_file_path)
    cave_data = caveconv.read_pockettopo_file()

    # Test Shots
    assert isinstance(cave_data.shots, list)
    assert len(cave_data.shots) == 205

    assert cave_data.shots[0].from_id == "1.0"
    assert cave_data.shots[0].to_id is None
    assert cave_data.shots[0].comment is None
    expected_distance = 0.0
    assert cave_data.shots[0].dist == pytest.approx(expected_distance, rel=1e-3)
    expected_azimuth = 0.0
    assert cave_data.shots[0].azimuth == pytest.approx(expected_azimuth, rel=1e-3)
    expected_inclination = 0.0
    assert cave_data.shots[0].inclination == pytest.approx(expected_inclination, rel=1e-3)

    assert cave_data.shots[1].comment == "powtorzony"
    expected_distance = 7.196
    assert cave_data.shots[1].dist == pytest.approx(expected_distance, rel=1e-3)
    expected_azimuth = 71.54
    assert cave_data.shots[1].azimuth == pytest.approx(expected_azimuth, rel=1e-3)
    expected_inclination = 41.78
    assert cave_data.shots[1].inclination == pytest.approx(expected_inclination, rel=1e-3)

    # Test Trips
    assert isinstance(cave_data.trips, list)
    assert len(cave_data.trips) == 1
    assert cave_data.trips[0].comment == ""
    assert cave_data.trips[0].declination == pytest.approx(0.0, rel=0.01)
    assert cave_data.trips[0].time == datetime.datetime(2005, 7, 1, 0, 0)

    # Check total distance
    assert cave_data.total_distance() == pytest.approx(119.0, rel=0.01)

    # Additional checks for shot data
    df = pd.DataFrame([shot.__dict__ for shot in cave_data.shots])
    assert df["dist"].between(0, 200).all(), "All dist values should be between 0 and 200"
    assert df["azimuth"].between(0, 360).all(), "All azimuth values should be between 0 and 360"
    assert df["inclination"].between(-90, 90).all(), "All inclination values should be between -90 and 90"

    # Check grouped and averaged shots
    grouped_shots = cave_data.get_grouped_shots()
    assert not grouped_shots.empty, "Grouped shots DataFrame should not be empty"
    assert {"from_id", "to_id", "dist", "azimuth", "inclination", "comment"}.issubset(
        grouped_shots.columns
    ), "Grouped shots should have from_to, dist, azimuth, inclination and comment columns"


def test_read_pockettopo_file_dummy():
    """
    Test with a dummy PocketTopo file to ensure the parser can handle different data layouts or errors gracefully.
    """
    test_file_path = os.path.join(os.path.dirname(__file__), "data", "02", "test.top")
    caveconv = PocketTopo(test_file_path)
    cave_data = caveconv.read_pockettopo_file()

    # Test Shots
    assert isinstance(cave_data.shots, list)
    assert len(cave_data.shots) == 2

    assert cave_data.shots[0].from_id == "1.0"
    assert cave_data.shots[0].to_id == "2.0"
    assert cave_data.shots[0].comment is None

    # Test Trips
    assert isinstance(cave_data.trips, list)
    assert len(cave_data.trips) == 1
    assert cave_data.trips[0].comment == "l;';l';"
    assert cave_data.trips[0].declination == pytest.approx(66.0, rel=0.01)
    assert cave_data.trips[0].time == datetime.datetime(2020, 5, 1, 0, 0)

    # Check total distance
    assert cave_data.total_distance() == pytest.approx(0.0, rel=0.01)
