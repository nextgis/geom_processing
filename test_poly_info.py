import unittest
from poly_info import poly_info

class TestPolyInfo(unittest.TestCase):
    def setUp(self):
        self.simple_polygon = 'Polygon((0 0, 1 0, 1 1, 0 1, 0 0))'
        self.holey_polygon = 'Polygon((0 0, 4 0, 4 4, 0 4, 0 0), (1 1, 3 1, 3 3, 1 3, 1 1))'
        self.multipolygon = 'MultiPolygon(((0 0, 1 0, 1 1, 0 1, 0 0)),((3 0, 7 3, 4 7, 0 4, 3 0)))'
        self.linestring = 'LineString(0 0, 1 2, 3 4)'

    def test_simple_polygon_area(self):
        self.assertEqual(poly_info(self.simple_polygon)["area"], 1)
        
    def test_simple_polygon_perimetr(self):
        self.assertEqual(poly_info(self.simple_polygon)["perimetr"], 4)
        
    def test_simple_polygon_bb(self):
        bb_test = poly_info(self.simple_polygon)["BoundBox"]
        bb_correct = 'POLYGON ((0.0000000000000000 0.0000000000000000, '+ \
                     '0.0000000000000000 1.0000000000000000, '+ \
                     '1.0000000000000000 1.0000000000000000, '+ \
                     '1.0000000000000000 0.0000000000000000, '+ \
                     '0.0000000000000000 0.0000000000000000))'
        self.assertEquals(bb_test, bb_correct)
        
    def test_holey_polygon_area(self):
        self.assertEqual(poly_info(self.holey_polygon)["area"], 12)
        
    def test_holey_polygon_perimetr(self):
        self.assertEqual(poly_info(self.holey_polygon)["perimetr"], 24)
        
    def test_holey_polygon_bb(self):
        bb_test = poly_info(self.holey_polygon)["BoundBox"]
        bb_correct = 'POLYGON ((0.0000000000000000 0.0000000000000000, '+ \
                     '0.0000000000000000 4.0000000000000000, '+ \
                     '4.0000000000000000 4.0000000000000000, '+ \
                     '4.0000000000000000 0.0000000000000000, '+ \
                     '0.0000000000000000 0.0000000000000000))'
        self.assertEquals(bb_test, bb_correct)
        
    def test_multipolygon_area(self):
        self.assertEqual(poly_info(self.multipolygon)["area"], 26)
        
    def test_multipolygon_perimetr(self):
        self.assertEqual(poly_info(self.multipolygon)["perimetr"], 24)

    def test_multipolygon_bb(self):
        bb_test = poly_info(self.multipolygon)["BoundBox"]
        bb_correct = 'POLYGON ((0.0000000000000000 0.0000000000000000, '+ \
                     '0.0000000000000000 7.0000000000000000, '+ \
                     '7.0000000000000000 7.0000000000000000, '+ \
                     '7.0000000000000000 0.0000000000000000, '+ \
                     '0.0000000000000000 0.0000000000000000))'
        self.assertEquals(bb_test, bb_correct)
        
    def test_lisestring(self):
        with self.assertRaises(ValueError) as context:
            poly_info(self.linestring)
            self.assertEquals(context.exception, ValueError)
           

if __name__ == '__main__':
    unittest.main()