import unittest
import restapi

import geopandas as gpd
from pathlib import Path

import geocricket as gc


TEST_DATA_PATH = Path(r"../demos/demo_data")

class TestGeoHandling(unittest.TestCase):
    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.geo_path = TEST_DATA_PATH / 'abq_blob.gpkg'

    def test_ensure_geometry_crs(self):
        init_geo = gpd.read_file(self.geo_path)
        self.assertEqual(init_geo.crs.to_string(), 'EPSG:4326')
        converted_geo = gc.ensure_crs(init_geo, 3857)
        self.assertEqual(converted_geo.crs.to_string(), 'EPSG:3857')

    def test_gdf_to_restapi_geo(self):
        # convert gdf
        init_geo = gpd.read_file(self.geo_path)
        converted_geo = gc.convert_geometry_bound(init_geo)
        self.assertIsInstance(converted_geo, restapi.Geometry)

        # handle filepath
        converted_geo = gc.convert_geometry_bound(self.geo_path)
        self.assertIsInstance(converted_geo, restapi.Geometry)

    def test_census_geo_collect(self):
        self.assertTrue(gc.check_connection())


if __name__ == '__main__':
    unittest.main()
