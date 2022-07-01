import unittest
from shapely import wkt
from src.bridging import *


class TestBridging(unittest.TestCase):
    def test_is_free_true(self):
        line = wkt.loads("LineString(0 1, 1 3)")
        mp = wkt.loads("MultiPolygon(((0 0, 1 0, 0 1, 0 0)),((1 3, 2 3, 2 2, 1 3)))")
        self.assertTrue(is_free(line, mp.geoms))

    def test_is_free_intersection(self):
        line = wkt.loads("LineString(0 1, 2 5)")
        mp = wkt.loads("MultiPolygon(((0 0, 1 0, 0 1, 0 0)),((1 3, 2 3, 2 2, 1 3)),((2 5, 3 5, 3 4, 2 5)))")
        self.assertFalse(is_free(line, mp.geoms))

    def test_is_free_touch(self):
        line = wkt.loads("LineString(0 1, 2 5)")
        mp = wkt.loads("MultiPolygon(((0 0, 1 0, 0 1, 0 0)),((0 3, 2 3, 2 2, 0 3)),((2 5, 3 5, 3 4, 2 5)))")
        self.assertFalse(is_free(line, mp.geoms))


if __name__ == '__main__':
    unittest.main()