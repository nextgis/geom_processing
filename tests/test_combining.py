import unittest
from shapely import wkt
from src.combining import combine, fill_holes

class TestPolyInfo(unittest.TestCase):
    def setUp(self):
        self.simple_triangle_1 = wkt.loads('MultiPolygon(((0 0, 1 0, 1 1, 0 0)))')
        self.simple_triangle_2 = wkt.loads('MultiPolygon(((0 0, 1 1, 0 1, 0 0)))')
        self.mp_1 = wkt.loads("MultiPolygon(((0 0, 1 0, 1 1, 0 1, 0 0)),((2 0, 3 0, 3 1, 2 1, 2 0)))")
        self.mp_2 = wkt.loads("MultiPolygon(((1 0, 2 0, 2 1, 1 1, 1 0)))")
        self.two_sq_1 = wkt.loads("MultiPolygon(((0 0, 1 0, 1 1, 0 1, 0 0)), ((3 0, 4 0, 4 1, 3 1, 3 0)))")
        self.two_sq_2 = wkt.loads("MultiPolygon(((1 0, 2 0, 2 1, 1 1, 1 0)),((4 0, 5 0, 5 1, 4 1, 4 0)))")
        
        self.sq_with_holes = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0),(0.5 0.5, 0.5 1.5, 1.5 0.5, 0.5 0.5),(2 2, 2.5 2, 2 2.5, 2 2)))')

        self.mp_holed = wkt.loads("MultiPolygon(((0 0, 1 4, 3 4, 4 0, 2 2, 0 0),(1.75 2.75, 2.25 2.75, 2.25 3.25, 1.75 3.25, 1.75 2.75)))")
        self.mp_for_union = wkt.loads("MultiPolygon(((0 0, 0 1, 4 1, 4 0, 0 0)))")

    def test_simple_combining(self):
        res = combine(self.simple_triangle_1, self.simple_triangle_2)
        correct = wkt.loads('MULTIPOLYGON (((1 0, 0 0, 0 1, 1 1, 1 0)))')
        self.assertTrue(res.equals(correct))
    
    def test_mp(self):
        res = combine(self.mp_1, self.mp_2)
        correct = wkt.loads('MULTIPOLYGON (((0 0, 0 1, 1 1, 2 1, 3 1, 3 0, 2 0, 1 0, 0 0)))')
        self.assertTrue(res.equals(correct))
        
    def test_two_sq(self):
        res = combine(self.two_sq_1, self.two_sq_2)
        correct = wkt.loads('MULTIPOLYGON (((0 1, 1 1, 2 1, 2 0, 1 0, 0 0, 0 1)), ((3 1, 4 1, 5 1, 5 0, 4 0, 3 0, 3 1)))')
        self.assertTrue(res.equals(correct)) 
        
    def test_holes_1(self):
        hole_area = 0.1
        res = fill_holes(self.sq_with_holes, hole_area)
        correct = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0),(0.5 0.5, 0.5 1.5, 1.5 0.5, 0.5 0.5),(2 2, 2.5 2, 2 2.5, 2 2)))')
        self.assertTrue(res.equals(correct))
        
    def test_holes_2(self):
        hole_area = 0.4
        res = fill_holes(self.sq_with_holes, hole_area)
        correct = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0),(0.5 0.5, 0.5 1.5, 1.5 0.5, 0.5 0.5)))')
        self.assertTrue(res.equals(correct))
        
    def test_holes_3(self):
        hole_area = 0.7
        res = fill_holes(self.sq_with_holes, hole_area)
        correct = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0)))')
        self.assertTrue(res.equals(correct))

    def test_union_holes_1(self):
        hole_area = 0.1
        res = combine(self.mp_holed, self.mp_for_union, hole_area)
        correct_wkt = "MultiPolygon(((0 0, 0 1, 0.25 1, 1 4, 3 4, 3.75 1, 4 1, 4 0, 0 0)," +\
                      "(1 1, 2 2, 3 1, 1 1),(1.75 2.75, 2.25 2.75, 2.25 3.25, 1.75 3.25, 1.75 2.75)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))
        
    def test_union_holes_2(self):
        hole_area = 0.6
        res = combine(self.mp_holed, self.mp_for_union, hole_area)
        correct_wkt = "MultiPolygon(((0 0, 0 1, 0.25 1, 1 4, 3 4, 3.75 1, 4 1, 4 0, 0 0),(1 1, 2 2, 3 1, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_union_holes_3(self):
        hole_area = 1.1
        res = combine(self.mp_holed, self.mp_for_union, hole_area)
        correct_wkt = "MultiPolygon(((0 0, 0 1, 0.25 1, 1 4, 3 4, 3.75 1, 4 1, 4 0, 0 0)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

if __name__ == '__main__':
    unittest.main()
