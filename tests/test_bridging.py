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
        edge = Edge(b_poly=0, b_vertex=0, b_poly_size=3,
                    e_poly=3, e_vertex=5, e_poly_size=6, status="unknown")
        neighbours = edge.get_neighbours()
        self.assertEqual([neighbour.make_tuple() for neighbour in neighbours],
                         [(0, 2, 3, 4), (0, 2, 3, 0), (0, 1, 3, 4), (0, 1, 3, 0)])

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

    def test_is_secant_out_line(self):
        line = wkt.loads("LineString(0 3, 3 3)")
        p = wkt.loads("Polygon((1 3, 2 3, 2 2, 1 3))")
        self.assertTrue(is_secant(line, p))

    def test_is_secant_in_line(self):
        line = wkt.loads("LineString(1 2, 2 3)")
        p = wkt.loads("Polygon((0 3, 2 3, 2 1, 0 3))")
        self.assertFalse(is_secant(line, p))

    def test_get_lines(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        res = get_lines(mp.geoms)
        correct = [Edge(0, 0, 3, 0, 1, 3, "bound"), Edge(0, 1, 3, 0, 2, 3, "bound"),
                   Edge(0, 2, 3, 0, 0, 3, "bound"),
                   Edge(1, 0, 3, 1, 1, 3, "bound"), Edge(1, 1, 3, 1, 2, 3, "bound"),
                   Edge(1, 2, 3, 1, 0, 3, "bound"),
                   Edge(2, 0, 3, 2, 1, 3, "bound"), Edge(2, 1, 3, 2, 2, 3, "bound"),
                   Edge(2, 2, 3, 2, 0, 3, "bound"),
                   Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 1, 3, 1, 2, 3, "edge"),
                   Edge(0, 1, 3, 2, 0, 3, "edge"), Edge(0, 1, 3, 2, 2, 3, "edge"),
                   Edge(0, 2, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge"),
                   Edge(0, 2, 3, 2, 0, 3, "edge"), Edge(0, 2, 3, 2, 2, 3, "edge"),
                   Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 0, 3, 2, 2, 3, "edge"),
                   Edge(1, 2, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge")]
        self.assertTrue(res == correct)

    def test_get_quads(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = [Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 1, 3, 1, 2, 3, "edge"),
                 Edge(0, 1, 3, 2, 0, 3, "edge"), Edge(0, 1, 3, 2, 2, 3, "edge"),
                 Edge(0, 2, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge"),
                 Edge(0, 2, 3, 2, 0, 3, "edge"), Edge(0, 2, 3, 2, 2, 3, "edge"),
                 Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 0, 3, 2, 2, 3, "edge"),
                 Edge(1, 2, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge")]
        res = get_quads(edges, vertexes)
        correct = [Quad(Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge")),
                   Quad(Edge(0, 1, 3, 2, 2, 3, "edge"), Edge(0, 2, 3, 2, 0, 3, "edge")),
                   Quad(Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge"))]
        self.assertEqual(res, correct)

    def test_handle_edges_edges(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = [Edge(0, 0, 3, 0, 1, 3, "bound"), Edge(0, 1, 3, 0, 2, 3, "bound"),
                 Edge(0, 2, 3, 0, 0, 3, "bound"),
                 Edge(1, 0, 3, 1, 1, 3, "bound"), Edge(1, 1, 3, 1, 2, 3, "bound"),
                 Edge(1, 2, 3, 1, 0, 3, "bound"),
                 Edge(2, 0, 3, 2, 1, 3, "bound"), Edge(2, 1, 3, 2, 2, 3, "bound"),
                 Edge(2, 2, 3, 2, 0, 3, "bound"),
                 Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 1, 3, 1, 2, 3, "edge"),
                 Edge(0, 1, 3, 2, 0, 3, "edge"), Edge(0, 1, 3, 2, 2, 3, "edge"),
                 Edge(0, 2, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge"),
                 Edge(0, 2, 3, 2, 0, 3, "edge"), Edge(0, 2, 3, 2, 2, 3, "edge"),
                 Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 0, 3, 2, 2, 3, "edge"),
                 Edge(1, 2, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge")]
        qd = Quad(Edge(0, 1, 3, 2, 2, 3, "edge"), Edge(0, 2, 3, 2, 0, 3, "edge"))
        handle_edges(qd, edges, vertexes)
        new_edges = [Edge(0, 0, 3, 0, 1, 3, 'bound'), Edge(0, 1, 3, 0, 2, 3, 'inner'),
                     Edge(0, 2, 3, 0, 0, 3, 'bound'),
                     Edge(1, 0, 3, 1, 1, 3, 'bound'), Edge(1, 1, 3, 1, 2, 3, 'bound'),
                     Edge(1, 2, 3, 1, 0, 3, 'bound'),
                     Edge(2, 0, 3, 2, 1, 3, 'bound'), Edge(2, 1, 3, 2, 2, 3, 'bound'),
                     Edge(2, 2, 3, 2, 0, 3, 'inner'),
                     Edge(0, 1, 3, 1, 0, 3, 'edge'), Edge(0, 1, 3, 1, 2, 3, 'edge'),
                     Edge(0, 1, 3, 2, 0, 3, 'inner'), Edge(0, 1, 3, 2, 2, 3, 'bound'),
                     Edge(0, 2, 3, 1, 0, 3, 'secant'), Edge(0, 2, 3, 1, 2, 3, 'secant'),
                     Edge(0, 2, 3, 2, 0, 3, 'bound'), Edge(0, 2, 3, 2, 2, 3, 'inner'),
                     Edge(1, 0, 3, 2, 0, 3, 'secant'), Edge(1, 0, 3, 2, 2, 3, 'edge'),
                     Edge(1, 2, 3, 2, 0, 3, 'secant'), Edge(1, 2, 3, 2, 2, 3, 'edge')]
        self.assertTrue(edges == new_edges)

    def test_handle_edges_qd(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = [Edge(0, 0, 3, 0, 1, 3, "bound"), Edge(0, 1, 3, 0, 2, 3, "bound"),
                 Edge(0, 2, 3, 0, 0, 3, "bound"),
                 Edge(1, 0, 3, 1, 1, 3, "bound"), Edge(1, 1, 3, 1, 2, 3, "bound"),
                 Edge(1, 2, 3, 1, 0, 3, "bound"),
                 Edge(2, 0, 3, 2, 1, 3, "bound"), Edge(2, 1, 3, 2, 2, 3, "bound"),
                 Edge(2, 2, 3, 2, 0, 3, "bound"),
                 Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 1, 3, 1, 2, 3, "edge"),
                 Edge(0, 1, 3, 2, 0, 3, "edge"), Edge(0, 1, 3, 2, 2, 3, "edge"),
                 Edge(0, 2, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge"),
                 Edge(0, 2, 3, 2, 0, 3, "edge"), Edge(0, 2, 3, 2, 2, 3, "edge"),
                 Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 0, 3, 2, 2, 3, "edge"),
                 Edge(1, 2, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge")]
        qd = Quad(Edge(0, 1, 3, 2, 2, 3, "edge"), Edge(0, 2, 3, 2, 0, 3, "edge"))
        handle_edges(qd, edges, vertexes)
        new_qd = Quad(Edge(0, 1, 3, 2, 2, 3, "bound"), Edge(0, 2, 3, 2, 0, 3, "bound"))
        self.assertTrue(qd == new_qd)

    def test_handle_topology(self):
        item = Quad(Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge"))
        united = []
        handle_topology(item, united)
        correct_united = [{1, 2}]
        self.assertEqual(united, correct_united)

    def test_handle_quads(self):
        item = Quad(Edge(0, 1, 3, 2, 2, 3, "bound"), Edge(0, 2, 3, 2, 0, 3, "bound"))
        quads = [Quad(Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "secant")),
                 Quad(Edge(1, 0, 3, 2, 0, 3, "secant"), Edge(1, 2, 3, 2, 2, 3, "edge"))]
        united = [{0, 2}]
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = [Edge(0, 0, 3, 0, 1, 3, 'bound'), Edge(0, 1, 3, 0, 2, 3, 'inner'),
                 Edge(0, 2, 3, 0, 0, 3, 'bound'),
                 Edge(1, 0, 3, 1, 1, 3, 'bound'), Edge(1, 1, 3, 1, 2, 3, 'bound'),
                 Edge(1, 2, 3, 1, 0, 3, 'bound'),
                 Edge(2, 0, 3, 2, 1, 3, 'bound'), Edge(2, 1, 3, 2, 2, 3, 'bound'),
                 Edge(2, 2, 3, 2, 0, 3, 'inner'),
                 Edge(0, 1, 3, 1, 0, 3, 'edge'), Edge(0, 1, 3, 1, 2, 3, 'edge'),
                 Edge(0, 1, 3, 2, 0, 3, 'inner'), Edge(0, 1, 3, 2, 2, 3, 'bound'),
                 Edge(0, 2, 3, 1, 0, 3, 'secant'), Edge(0, 2, 3, 1, 2, 3, 'secant'),
                 Edge(0, 2, 3, 2, 0, 3, 'bound'), Edge(0, 2, 3, 2, 2, 3, 'inner'),
                 Edge(1, 0, 3, 2, 0, 3, 'secant'), Edge(1, 0, 3, 2, 2, 3, 'edge'),
                 Edge(1, 2, 3, 2, 0, 3, 'secant'), Edge(1, 2, 3, 2, 2, 3, 'edge')]
        handle_quads(item, quads, edges, vertexes, united)
        correct = [Quad(Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge"))]
        self.assertEqual(quads, correct)

    def test_get_bridges(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)),((0 2, 0 3, 1 3, 0 2)),((2 0, 3 0, 3 1, 2 0)))")
        vertexes = [geom.exterior.coords for geom in mp.geoms]
        edges = [Edge(0, 0, 3, 0, 1, 3, "bound"), Edge(0, 1, 3, 0, 2, 3, "bound"),
                 Edge(0, 2, 3, 0, 0, 3, "bound"),
                 Edge(1, 0, 3, 1, 1, 3, "bound"), Edge(1, 1, 3, 1, 2, 3, "bound"),
                 Edge(1, 2, 3, 1, 0, 3, "bound"),
                 Edge(2, 0, 3, 2, 1, 3, "bound"), Edge(2, 1, 3, 2, 2, 3, "bound"),
                 Edge(2, 2, 3, 2, 0, 3, "bound"),
                 Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 1, 3, 1, 2, 3, "edge"),
                 Edge(0, 1, 3, 2, 0, 3, "edge"), Edge(0, 1, 3, 2, 2, 3, "edge"),
                 Edge(0, 2, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge"),
                 Edge(0, 2, 3, 2, 0, 3, "edge"), Edge(0, 2, 3, 2, 2, 3, "edge"),
                 Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 0, 3, 2, 2, 3, "edge"),
                 Edge(1, 2, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge")]
        quads = [Quad(Edge(0, 1, 3, 1, 0, 3, "edge"), Edge(0, 2, 3, 1, 2, 3, "edge")),
                 Quad(Edge(0, 1, 3, 2, 2, 3, "edge"), Edge(0, 2, 3, 2, 0, 3, "edge")),
                 Quad(Edge(1, 0, 3, 2, 0, 3, "edge"), Edge(1, 2, 3, 2, 2, 3, "edge"))]
        res_bridge_wkt = [g.wkt for g in get_bridges(vertexes, edges, quads, 2)]
        correct_wkt = ['POLYGON ((0 1, 3 1, 2 0, 1 0, 0 1))', 'POLYGON ((0 1, 0 2, 1 3, 3 1, 0 1))']
        self.assertEqual(res_bridge_wkt, correct_wkt)

    def test_build_bridges_3_1(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)), ((2 0, 3 0, 3 1, 2 0)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((1 0, 0 0, 0 1, 0 2, 0 3, 1 3, 3 1, 3 0, 2 0, 1 0))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_3_2(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)), ((2 0, 3 0, 3 1, 2 0)))")
        res = build_bridges(mp.geoms, 2)
        correct = wkt.loads("MultiPolygon(((3 1, 3 0, 2 0, 1 0, 0 0, 0 1, 3 1)), ((1 3, 0 2, 0 3, 1 3)))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_2_1(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 0, 0 0)), ((0 2, 0 3, 1 3, 0 2)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((0 1, 0 2, 0 3, 1 3, 1 0, 0 0, 0 1))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_3sq_2(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 1, 1 0, 0 0)), "
                       "((0 2, 0 3, 1 3, 1 2, 0 2)), "
                       "((0 5, 0 6, 1 6, 1 5, 0 5)))")
        res = build_bridges(mp.geoms, 2)
        correct = wkt.loads("MultiPolygon(((0 2, 0 3, 1 3, 1 2, 1 1, 1 0, 0 0, 0 1, 0 2)), "
                            "((1 6, 1 5, 0 5, 0 6, 1 6)))")
        self.assertTrue(res.equals(correct))

    def test_build_bridges_3sq_1(self):
        mp = wkt.loads("MultiPolygon(((0 0, 0 1, 1 1, 1 0, 0 0)), "
                       "((0 2, 0 3, 1 3, 1 2, 0 2)), "
                       "((0 5, 0 6, 1 6, 1 5, 0 5)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((0 2, 0 3, 0 5, 0 6, 1 6, 1 5, 1 3, 1 2, 1 1, 1 0, 0 0, 0 1, 0 2))")
        self.assertTrue(res.equals(correct))

    def test_without_ring(self):
        mp = wkt.loads("MultiPolygon(((0 0, 5 0, 5 1, 4 1, 3 1, 2 1, 1 1, 0 1, 0 0)),"
                       "((0 2, 1 2, 2 2, 3 2, 4 2, 5 2, 5 3, 0 3, 0 2)),"
                       "((7 0, 8 0, 8 2, 7 2, 7 0)))")
        res = build_bridges(mp.geoms, 1)
        correct = wkt.loads("Polygon((2 1, 3 1, 4 1, 5 1, 5 0, 0 0, 0 1, 4 2, 3 2, "
                            "2 2, 1 2, 0 2, 0 3, 5 3, 8 2, 8 0, 7 0, 7 2, 5 2, 1 1, 2 1))")
        self.assertTrue(res.equals(correct))


if __name__ == '__main__':
    unittest.main()
