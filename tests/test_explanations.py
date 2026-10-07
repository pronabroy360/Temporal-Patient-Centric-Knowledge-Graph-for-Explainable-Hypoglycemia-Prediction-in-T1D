import unittest
from datetime import datetime, timezone

from t1d_tkg.explanations import evidence_record, remove_evidence_nodes
from t1d_tkg.graph import build_asof_graph
from t1d_tkg.synthetic import synthetic_events


class ExplanationTests(unittest.TestCase):
    def test_evidence_record_and_mask_are_as_of_and_edge_closed(self):
        events = synthetic_events()
        graph = build_asof_graph(events, patient_id="p1", index_time=datetime(2026, 1, 1, 3, 45, tzinfo=timezone.utc))
        meal = next(node["id"] for node in graph.nodes if node["type"] == "MealEvent")
        record = evidence_record(graph, [meal], model_name="smoke", model_version="v1", prediction=0.4)
        self.assertEqual(record["evidence_nodes"][0]["id"], meal)
        masked = remove_evidence_nodes(graph, [meal])
        self.assertNotIn(meal, masked.node_ids())
        self.assertTrue(all(edge["source"] in masked.node_ids() and edge["target"] in masked.node_ids() for edge in masked.edges))
        with self.assertRaises(ValueError):
            evidence_record(graph, ["p1-future-meal"], model_name="smoke", model_version="v1", prediction=0.4)


if __name__ == "__main__":
    unittest.main()
