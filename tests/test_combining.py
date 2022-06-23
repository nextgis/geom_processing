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

        self.sq_with_holes = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0),'
                                       '(0.5 0.5, 0.5 1.5, 1.5 0.5, 0.5 0.5),(2 2, 2.5 2, 2 2.5, 2 2)))')

        self.mp_holed = wkt.loads("MultiPolygon(((0 0, 1 4, 3 4, 4 0, 2 2, 0 0),"
                                  "(1.75 2.75, 2.25 2.75, 2.25 3.25, 1.75 3.25, 1.75 2.75)))")
        self.mp_for_union = wkt.loads("MultiPolygon(((0 0, 0 1, 4 1, 4 0, 0 0)))")

        self.with_hole = wkt.loads("MultiPolygon(((0 0, 0 5, 5 5, 5 0, 0 0),(1 1, 1 4, 4 4, 4 1, 1 1)))")
        self.for_cross_2 = wkt.loads("MultiPolygon(((0 2, 0 3, 5 3, 5 2, 0 2)))")
        self.for_cross_3 = wkt.loads("MultiPolygon(((0 2, 0 3, 3 3, 3 2, 0 2)))")
        self.for_touch_1 = wkt.loads("MultiPolygon(((4 2, 4 3, 6 3, 6 2, 4 2)))")
        self.for_touch_2 = wkt.loads("MultiPolygon(((4 2, 6 3, 6 2, 4 2)))")

        self.mp_3_b1 = wkt.loads("MultiPolygon(((0 0, 3 0, 3 1, 0 1, 0 0)))")
        self.mp_3_b2 = wkt.loads("MultiPolygon(((0 1, 1 1, 1 3, 0 3, 0 1)))")
        self.mp_3_n3 = wkt.loads("MultiPolygon(((2 1, 2 3, 3 3, 3 1, 2 1)))")
        self.mp_3_z3 = wkt.loads("MultiPolygon(((2 1, 2 2, 1 2, 1 3, 3 3, 3 1, 2 1)))")

        self.sq = wkt.loads("Multipolygon(((1 1, 1 3, 3 3, 3 1, 1 1)))")
        self.up = wkt.loads("MultiPolygon(((2 2, 2 4, 4 4, 4 2, 3 3, 2 2)))")
        self.down = wkt.loads("MultiPolygon(((2 2, 3 1, 4 2, 4 0, 2 0, 2 2)))")

    def test_simple_combining(self):
        res = combine(geoms=[self.simple_triangle_1, self.simple_triangle_2])
        correct = wkt.loads('MULTIPOLYGON (((1 0, 0 0, 0 1, 1 1, 1 0)))')
        self.assertTrue(res.equals(correct))

    def test_mp(self):
        res = combine(geoms=[self.mp_1, self.mp_2])
        correct = wkt.loads('MULTIPOLYGON (((0 0, 0 1, 1 1, 2 1, 3 1, 3 0, 2 0, 1 0, 0 0)))')
        self.assertTrue(res.equals(correct))

    def test_two_sq(self):
        res = combine(geoms=[self.two_sq_1, self.two_sq_2])
        correct = wkt.loads('MULTIPOLYGON (((0 1, 1 1, 2 1, 2 0, 1 0, 0 0, 0 1)),'
                            '((3 1, 4 1, 5 1, 5 0, 4 0, 3 0, 3 1)))')
        self.assertTrue(res.equals(correct)) 

    def test_holes_1(self):
        res = fill_holes(self.sq_with_holes, hole_area=0.1, init_holes=[])
        correct = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0),'
                            '(0.5 0.5, 0.5 1.5, 1.5 0.5, 0.5 0.5),(2 2, 2.5 2, 2 2.5, 2 2)))')
        self.assertTrue(res.equals(correct))

    def test_holes_2(self):
        res = fill_holes(self.sq_with_holes, hole_area=0.4, init_holes=[])
        correct = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0),(0.5 0.5, 0.5 1.5, 1.5 0.5, 0.5 0.5)))')
        self.assertTrue(res.equals(correct))

    def test_holes_3(self):
        res = fill_holes(self.sq_with_holes, hole_area=0.7, init_holes=[])
        correct = wkt.loads('MultiPolygon(((0 0, 3 0, 3 3, 0 3, 0 0)))')
        self.assertTrue(res.equals(correct))

    def test_union_holes_1(self):
        res = combine(geoms=[self.mp_holed, self.mp_for_union], hole_area=0.1)
        correct_wkt = "MultiPolygon(((0 0, 0 1, 0.25 1, 1 4, 3 4, 3.75 1, 4 1, 4 0, 0 0)," \
                      + "(1 1, 2 2, 3 1, 1 1),(1.75 2.75, 2.25 2.75, 2.25 3.25, 1.75 3.25, 1.75 2.75)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_union_holes_2(self):
        res = combine(geoms=[self.mp_holed, self.mp_for_union], hole_area=0.6)
        correct_wkt = "MultiPolygon(((0 0, 0 1, 0.25 1, 1 4, 3 4, 3.75 1, 4 1, 4 0, 0 0)," \
                      + "(1 1, 2 2, 3 1, 1 1),(1.75 2.75, 2.25 2.75, 2.25 3.25, 1.75 3.25, 1.75 2.75)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_union_holes_3(self):
        res = combine(geoms=[self.mp_holed, self.mp_for_union], hole_area=1.1)
        correct_wkt = "MultiPolygon(((0 0, 0 1, 0.25 1, 1 4, 3 4, 3.75 1, 4 1, 4 0, 0 0)," \
                      + "(1.75 2.75, 2.25 2.75, 2.25 3.25, 1.75 3.25, 1.75 2.75)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_cross_hole_1(self):
        res = combine(geoms=[self.with_hole, self.for_cross_2], hole_area=2)
        correct_wkt = "MultiPolygon(((0 0, 0 2, 0 3, 0 5, 5 5, 5 3, 5 2, 5 0, 0 0)," \
                      + "(1 1, 4 1, 4 2, 1 2, 1 1),(1 3, 4 3, 4 4, 1 4, 1 3)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_cross_hole_2(self):
        res = combine(geoms=[self.with_hole, self.for_cross_2], hole_area=4)
        correct_wkt = "MultiPolygon(((0 0, 0 2, 0 3, 0 5, 5 5, 5 3, 5 2, 5 0, 0 0)," \
                      + "(1 1, 4 1, 4 2, 1 2, 1 1),(1 3, 4 3, 4 4, 1 4, 1 3)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_cross_hole_3(self):
        res = combine(geoms=[self.with_hole, self.for_cross_3], hole_area=6)
        correct_wkt = "MultiPolygon(((0 0, 0 2, 0 3, 0 5, 5 5, 5 0, 0 0)," \
                      + "(1 1, 1 2, 3 2, 3 3, 1 3, 1 4, 4 4, 4 1, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_cross_hole_4(self):
        res = combine(geoms=[self.with_hole, self.for_cross_3], hole_area=8)
        correct_wkt = "MultiPolygon(((0 0, 0 2, 0 3, 0 5, 5 5, 5 0, 0 0)," \
                      "(1 1, 1 2, 3 2, 3 3, 1 3, 1 4, 4 4, 4 1, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))
        
    def test_touch_hole_1(self):
        res = combine(geoms=[self.with_hole, self.for_touch_1], hole_area=8)
        correct_wkt = "MultiPolygon(((0 0, 0 5, 5 5, 5 3, 6 3, 6 2, 5 2, 5 0, 0 0)," \
                      "(1 1, 4 1, 4 2, 4 3, 4 4, 1 4, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_touch_hole_2(self):
        res = combine(geoms=[self.with_hole, self.for_touch_1], hole_area=10)
        correct_wkt = "MultiPolygon(((0 0, 0 5, 5 5, 5 3, 6 3, 6 2, 5 2, 5 0, 0 0)," \
                      "(1 1, 4 1, 4 2, 4 3, 4 4, 1 4, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_touch_hole_3(self):
        res = combine(geoms=[self.with_hole, self.for_touch_2], hole_area=8)
        correct_wkt = "MultiPolygon(((0 0, 0 5, 5 5, 5 2.5, 6 3, 6 2, 5 2, 5 0, 0 0),(1 1, 4 1, 4 2, 4 4, 1 4, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_touch_hole_4(self):
        res = combine(geoms=[self.with_hole, self.for_touch_2], hole_area=10)
        correct_wkt = "MultiPolygon(((0 0, 0 5, 5 5, 5 2.5, 6 3, 6 2, 5 2, 5 0, 0 0),(1 1, 4 1, 4 2, 4 4, 1 4, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_three_n(self):
        res = combine([self.mp_3_b1, self.mp_3_b2, self.mp_3_n3])
        correct_wkt = "MultiPolygon(((0 0, 0 3, 1 3, 1 1, 2 1, 2 3, 3 3, 3 0, 0 0)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_three_z0(self):
        res = combine([self.mp_3_b1, self.mp_3_b2, self.mp_3_z3], hole_area=0)
        correct_wkt = "MultiPolygon(((0 0, 0 3, 3 3, 3 0, 0 0), (1 1, 2 1, 2 2, 1 2, 1 1)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_three_z2(self):
        res = combine([self.mp_3_b1, self.mp_3_b2, self.mp_3_z3], hole_area=2)
        correct_wkt = "MultiPolygon(((0 0, 0 3, 3 3, 3 0, 0 0)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_three_ud0(self):
        res = combine([self.sq, self.up, self.down], hole_area=0)
        correct_wkt = "MultiPolygon(((4 0, 2 0, 2 1, 1 1, 1 3, 2 3, 2 4, 4 4, 4 2, 4 0)," \
                      "(4 2, 3 3, 3 1, 4 2)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_three_ud2(self):
        res = combine([self.sq, self.up, self.down], hole_area=2)
        correct_wkt = "MultiPolygon(((4 0, 2 0, 2 1, 1 1, 1 3, 2 3, 2 4, 4 4, 4 2, 4 0)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))

    def test_three_udh(self):
        res = combine([self.with_hole, self.sq, self.up, self.down], hole_area=0)
        correct_wkt = "MultiPolygon(((0 0, 0 5, 5 5, 5 0, 4 0, 2 0, 0 0), (1 3, 2 3, 2 4, 1 4, 1 3)," \
                      "(3 3, 4 2, 3 1, 3 3)))"
        correct = wkt.loads(correct_wkt)
        self.assertTrue(res.equals(correct))


if __name__ == '__main__':
    unittest.main()

