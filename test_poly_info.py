import unittest
from poly_info import poly_info

class TestPolyInfo(unittest.TestCase):
    def setUp(self):
        self.polygon1 = 'Polygon((0 0, 1 0, 1 1, 0 1, 0 0))'

    def test_polygon1_area(self):
        self.assertEquals(poly_info(self.polygon1)["area"], 1)
        
    def test_polygon1_perimetr(self):
        self.assertEquals(poly_info(self.polygon1)["perimetr"], 4)

if __name__ == '__main__':
    unittest.main()