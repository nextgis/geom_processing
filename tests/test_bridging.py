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

    def test_get_neighbours(self):
        edge = (0, 0, 3, 5)
        size1 = 3
        size2 = 6
        neighbours = get_neighbours(edge, size1, size2)
        self.assertEqual(neighbours, [(0, 2, 3, 4), (0, 2, 3, 0), (0, 1, 3, 4), (0, 1, 3, 0)])

    def test_is_secant_touch(self):
        line = wkt.loads("LineString(0 1, 1 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertFalse(is_secant(line, p))

    def test_is_secant_no(self):
        line = wkt.loads("LineString(0 1, 0 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertFalse(is_secant(line, p))

    def test_is_secant_cross(self):
        line = wkt.loads("LineString(0 1, 1 3)")
        p = wkt.loads("Polygon((0 3, 2 3, 2 2, 0 3))")
        self.assertTrue(is_secant(line, p))

    def test_is_secant_line(self):
        line = wkt.loads("LineString(0 3, 3 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertFalse(is_secant(line, p))

    def test_build_bridges(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0),(0 2, 0 3, 1 3, 0 2),(2 0, 3 0, 3 1, 2 0)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((0 0, 1 0, 2 0, 3 0, 1 3, 3 1, 3 0, 2 0, 1 0, 0 0))")
        self.assertTrue(res.equals(correct))


if __name__ == '__main__':
    unittest.main()