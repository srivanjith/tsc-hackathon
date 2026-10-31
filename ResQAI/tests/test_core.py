import unittest
from data.demo_data import INITIAL_DATA, NODES
from engines.evidence_engine import analyze_reports
from engines.risk_engine import rank_incidents
from engines.routing_engine import route_between, route_roads
from engines.replanning_engine import generate_revised_plan
from engines.allocation_engine import allocate_resources
from engines.shelter_engine import recommend_shelters


class ResQAIEngineTests(unittest.TestCase):
    def test_demo_dataset_minimums_and_consistency(self):
        self.assertGreaterEqual(len(INITIAL_DATA['incidents']), 5)
        self.assertGreaterEqual(len(INITIAL_DATA['reports']), 8)
        self.assertGreaterEqual(len(INITIAL_DATA['resources']), 8)
        self.assertGreaterEqual(len(INITIAL_DATA['shelters']), 3)
        self.assertGreaterEqual(len(INITIAL_DATA['roads']), 8)
        for road in INITIAL_DATA['roads']:
            self.assertIn(road['u'], NODES); self.assertIn(road['v'], NODES)
        for mission in INITIAL_DATA['missions']:
            self.assertTrue(route_roads(mission['route'], INITIAL_DATA['roads']))

    def test_evidence_engine_detects_duplicate_and_conflict(self):
        reports = analyze_reports(INITIAL_DATA['reports'])
        statuses = [r['status'] for r in reports]
        self.assertIn('Duplicate', statuses)
        self.assertIn('Conflicting', statuses)
        self.assertIn('Outdated', statuses)

    def test_low_confidence_does_not_lower_harm_priority(self):
        ranked = rank_incidents(INITIAL_DATA['incidents'], analyze_reports(INITIAL_DATA['reports']))
        low_conf = next(i for i in ranked if i['id'] == 'INC-004')
        self.assertTrue(low_conf['verification_escalation'])
        self.assertGreaterEqual(low_conf['score'], 0)

    def test_road_closure_replans_all_affected_missions(self):
        plan = generate_revised_plan('RD-03', INITIAL_DATA['roads'], NODES, INITIAL_DATA['missions'], INITIAL_DATA['resources'])
        self.assertEqual(set(plan['affected_mission_ids']), {'MIS-001', 'MIS-003'})
        self.assertEqual(plan['summary']['rerouted'], 2)
        for mission in plan['missions']:
            if mission['id'] in plan['affected_mission_ids']:
                self.assertNotIn('RD-03', route_roads(mission['route'], [r for r in INITIAL_DATA['roads'] if r['id'] != 'RD-03']))
        self.assertEqual(next(r['status'] for r in INITIAL_DATA['roads'] if r['id'] == 'RD-03'), 'Open')

    def test_route_and_shelter_recommendations(self):
        result = route_between(INITIAL_DATA['roads'], NODES, 'E', 'A')
        self.assertTrue(result['reachable'])
        incident = INITIAL_DATA['incidents'][0]
        options = recommend_shelters(incident, INITIAL_DATA['shelters'], INITIAL_DATA['roads'], NODES)
        self.assertTrue(options)

    def test_allocation_does_not_reuse_resources(self):
        ranked = rank_incidents(INITIAL_DATA['incidents'], analyze_reports(INITIAL_DATA['reports']))
        suggestions = allocate_resources(ranked, INITIAL_DATA['resources'], INITIAL_DATA['roads'], NODES, INITIAL_DATA['missions'])
        assigned = [x['resource_id'] for x in suggestions if x['status'] == 'Suggested']
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertTrue(any(x['status'].startswith('Unmet') for x in suggestions))

    def test_pluvial_flood_susceptibility_engine(self):
        from engines.pluvial_engine import predict_pluvial_susceptibility, get_pluvial_metadata, get_spatial_sample
        # Test extreme pluvial inundation parameters
        result = predict_pluvial_susceptibility(drainage=232.0, rainfall=95.0, twi=8.0)
        self.assertIn(result["susceptibility"], ["High", "Very_High"])
        self.assertGreaterEqual(result["risk_score"], 70)
        self.assertIn("CRITICAL" in result["advisory"] or "HIGH" in result["advisory"], [True])

        # Test minimal flood parameters
        low_res = predict_pluvial_susceptibility(drainage=205.0, rainfall=60.0, twi=-2.0)
        self.assertIn(low_res["susceptibility"], ["No_Flood", "Low"])
        self.assertLessEqual(low_res["risk_score"], 30)

        meta = get_pluvial_metadata()
        self.assertIn("accuracy", meta)
        
        sample = get_spatial_sample(10)
        self.assertFalse(sample.empty)


if __name__ == '__main__':
    unittest.main(verbosity=2)

