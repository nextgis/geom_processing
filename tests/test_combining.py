import unittest
from shapely import wkt
from src.combining import combine

class TestPolyInfo(unittest.TestCase):
    def setUp(self):
        self.simple_triangle_1 = wkt.loads('MultiPolygon(((0 0, 1 0, 1 1, 0 0)))')
        self.simple_triangle_2 = wkt.loads('MultiPolygon(((0 0, 1 1, 0 1, 0 0)))')
        self.mp_1 = wkt.loads("MultiPolygon(((0 0, 1 0, 1 1, 0 1, 0 0)),((2 0, 3 0, 3 1, 2 1, 2 0)))")
        self.mp_2 = wkt.loads("MultiPolygon(((1 0, 2 0, 2 1, 1 1, 1 0)))")
        self.two_sq_1 = wkt.loads("MultiPolygon(((0 0, 1 0, 1 1, 0 1, 0 0)), ((3 0, 4 0, 4 1, 3 1, 3 0)))")
        self.two_sq_2 = wkt.loads("MultiPolygon(((1 0, 2 0, 2 1, 1 1, 1 0)),((4 0, 5 0, 5 1, 4 1, 4 0)))")

    def test_simple_combining(self):
        res = combine(self.simple_triangle_1, self.simple_triangle_2)
        correct = 'MULTIPOLYGON (((1 0, 0 0, 0 1, 1 1, 1 0)))'
        self.assertEqual(res, correct)
    
    def test_mp(self):
        res = combine(self.mp_1, self.mp_2)
        correct = 'MULTIPOLYGON (((0 0, 0 1, 1 1, 2 1, 3 1, 3 0, 2 0, 1 0, 0 0)))'
        self.assertEqual(res, correct)
        
    def test_two_sq(self):
        res = combine(self.two_sq_1, self.two_sq_2)
        correct = 'MULTIPOLYGON (((0 1, 1 1, 2 1, 2 0, 1 0, 0 0, 0 1)), ((3 1, 4 1, 5 1, 5 0, 4 0, 3 0, 3 1)))'
        self.assertEqual(res, correct) 
        

if __name__ == '__main__':
    unittest.main()
