# Copyright 2018 archproj-bmwteam
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import unittest
from graph_analyzer import *
from contextlib import redirect_stdout

GRAPH_TEST_FILE_02 = "test02.dot"
TMP_OUT_FILE = "/tmp/graph_analyzer_test_out.txt"


def setUpModule():
    global graph
    graph = load_graph(GRAPH_TEST_FILE_02)


def tearDownModule():
    # clean up the mess
    global graph
    os.remove(TMP_OUT_FILE)


class AnalyzerTest(unittest.TestCase):
    def test_print_vertex(self):
        # redirect stdout to a temporary file
        with open(TMP_OUT_FILE, 'w') as file_w, redirect_stdout(file_w):
            print_graph_vertex(graph, 0)

        # read temporary file to check output
        with open(TMP_OUT_FILE, 'r') as file_r:
            line = file_r.readline()
            self.assertEqual(line, "vtx[0] in: 0 out: 2 val: v00\n")

    def test_print_vertex_children(self):
        # redirect stdout to a temporary file
        with open(TMP_OUT_FILE, 'w') as file_w, redirect_stdout(file_w):
            print_vertex_children(graph, 1, 3)

        exp_results = ["vtx[1] in: 1 out: 3 val: v01\n",
                       "├─ vtx[2] in: 2 out: 1 val: v02\n",
                       "│  └─ vtx[5] in: 1 out: 2 val: v05\n",
                       "│     ├─ vtx[10] in: 1 out: 1 val: v10\n",
                       "│     └─ vtx[11] in: 1 out: 1 val: v11\n",
                       "├─ vtx[3] in: 1 out: 2 val: v03\n",
                       "│  ├─ vtx[6] in: 4 out: 1 val: v06\n",
                       "│  │  └● vtx[6] in: 4 out: 1 val: v06\n",
                       "│  └─ vtx[7] in: 2 out: 0 val: v07\n",
                       "└─ vtx[4] in: 1 out: 3 val: v04\n",
                       "   ├─ vtx[7] in: 2 out: 0 val: v07\n",
                       "   ├─ vtx[8] in: 1 out: 1 val: v08\n",
                       "   │  └─ vtx[6] in: 4 out: 1 val: v06\n",
                       "   └─ vtx[9] in: 2 out: 0 val: v09\n"]

        # read temporary file to check output
        with open(TMP_OUT_FILE, 'r') as file_r:
            act_results = file_r.readlines()
        self.assertListEqual(act_results, exp_results)

    def test_search(self):
        act_results = search_vertices(graph, "v04")
        exp_results = [graph.vertex(4)]
        self.assertEqual(act_results, exp_results)
        act_results = search_vertices(graph, "v05")
        exp_results = [graph.vertex(5)]
        self.assertEqual(act_results, exp_results)
        act_results = search_vertices(graph, "v1")
        exp_results = [graph.vertex(10), graph.vertex(11)]
        self.assertListEqual(act_results, exp_results)
        act_results = search_vertices(graph, "hutzlpfrt")
        exp_results = []
        self.assertEqual(act_results, exp_results)

    def test_find_hotspots_out(self):
        exp_results = [1, 4, 0, 3]
        act_results = find_hotspots_out(graph)
        self.assertListEqual(act_results, exp_results)

    def test_find_hotspots_in(self):
        exp_results = [6, 2, 7, 9]
        act_results = find_hotspots_in(graph)
        self.assertListEqual(act_results, exp_results)

    def test_shared(self):
        exp_results = [graph.vertex(6),  graph.vertex(7)]
        act_results = list_shared_sub_vertices(graph, graph.vertex(3), graph.vertex(4))
        self.assertListEqual(act_results, exp_results)

    def test_collect_subgraph_vertices(self):
        exp_results = {graph.vertex(4), graph.vertex(6), graph.vertex(7), graph.vertex(8), graph.vertex(9)}
        act_results = collect_subgraph_vertices(graph, graph.vertex(4))
        self.assertSetEqual(act_results, exp_results)
        exp_results = {graph.vertex(2),
                       graph.vertex(5),
                       graph.vertex(9),
                       graph.vertex(10),
                       graph.vertex(11),
                       graph.vertex(6)}
        act_results = collect_subgraph_vertices(graph, graph.vertex(2))
        self.assertSetEqual(act_results, exp_results)

    def test_nodes_connected(self):
        self.assertTrue(nodes_connected(graph, ["v04", "v06"]))
        self.assertTrue(nodes_connected(graph, ["v00", "v06"]))
        self.assertTrue(nodes_connected(graph, ["v05", "v06"]))
        self.assertFalse(nodes_connected(graph, ["v10", "v03"]))
        self.assertTrue(nodes_connected(graph, ["v10", "v03", "v00"]))
        self.assertFalse(nodes_connected(graph, ["v02", "v03", "v04"]))

    def test_parse_node_values(self):
        exp_results = ["0", "1", "5", "11"]
        act_results = parse_node_values(graph, ["v00", "1", "v05", "v11"])
        self.assertListEqual(act_results, exp_results)
        exp_results = ["6", "7", "7", "9", "8", "2"]
        act_results = parse_node_values(graph, ["6", "7", "v07", "v09", "8", ".v02"])
        self.assertListEqual(act_results, exp_results)


if __name__ == '__main__':
    unittest.main()
