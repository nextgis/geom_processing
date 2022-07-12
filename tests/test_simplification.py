import unittest
from shapely import wkt
from src.simplification import *


class TestSimplification(unittest.TestCase):
    def test_simple_convex_polygon_1(self):
        poly_6 = wkt.loads("Polygon((1 0, 2 0, 3 1, 2 2, 1 2, 0 1, 1 0))")
        poly_5 = simplify([poly_6], 5)
        correct = wkt.loads("MULTIPOLYGON (((1.5 -0.5, 3 1, 2 2, 1 2, 0 1, 1.5 -0.5)))")
        self.assertTrue(poly_5.equals(correct))

    def test_simple_concave_polygon_1(self):
        poly_7 = wkt.loads("Polygon((1 0, 2 0, 3 1, 2 2, 1.5 1, 1 2, 0 1, 1 0))")
        poly_6 = simplify([poly_7], 6)
        correct = wkt.loads("MULTIPOLYGON (((1.5 -0.5, 3 1, 2 2, 1.5 1, 1 2, 0 1, 1.5 -0.5)))")
        self.assertTrue(poly_6.equals(correct))

    def test_simple_concave_polygon_2(self):
        poly_7 = wkt.loads("Polygon((1 0, 2 0, 3 1, 2 2, 1.5 1, 1 2, 0 1, 1 0))")
        poly_6 = simplify([poly_7], 5)
        correct = wkt.loads("MULTIPOLYGON (((1.5 -0.5, 3 1, 2 2, 1 2, 0 1, 1.5 -0.5)))")
        self.assertTrue(poly_6.equals(correct))

    def test_multipolygon(self):
        mp = wkt.loads("MultiPolygon(((1 0, 2 0, 3 1, 2 2, 1.5 1, 1 2, 0 1, 1 0)),"
                       "((5 2, 6 4, 5 3, 4 4, 5 2)))")
        res = simplify(mp.geoms, 7)
        correct = wkt.loads("MultiPolygon(((1.5 -0.5, 3 1, 1.5 2.5, 0 1, 1 0, 1.5 -0.5)),"
                            "((5 2, 6 4, 4 4, 5 2)))")
        self.assertTrue(res.equals(correct))


if __name__ == '__main__':
    unittest.main()