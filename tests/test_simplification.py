import unittest
from shapely import wkt
from src.simplification import *


class TestSimplification(unittest.TestCase):
    def test_simple_convex_polygon(self):
        poly_6 = wkt.loads("Polygon((1 0, 2 0, 3 1, 2 2, 1 2, 0 1, 1 0))")
        poly_5 = simplify([poly_6], 5)
        correct = wkt.loads("MULTIPOLYGON (((1.5 -0.5, 3 1, 2 2, 1 2, 0 1, 1.5 -0.5)))")
        self.assertTrue(poly_5.equals(correct))

    def test_simple_concave_polygon(self):
        poly_7 = wkt.loads("Polygon((1 0, 2 0, 3 1, 2 2, 1.5 1, 1 2, 0 1, 1 0))")
        poly_6 = simplify([poly_7], 6)
        correct = wkt.loads("MULTIPOLYGON (((1.5 -0.5, 3 1, 2 2, 1.5 1, 1 2, 0 1, 1.5 -0.5)))")
        self.assertTrue(poly_6.equals(correct))


if __name__ == '__main__':
    unittest.main()