import os
import unittest
from unittest.mock import patch

from orchestration.langgraph.nodes import rca_node


class RCANodeTests(unittest.TestCase):
    def setUp(self):
        self.evidence = {
            "combined_candidates": ["risk-engine", "payment-service"],
            "suspect_scores": {"risk-engine": 0.8, "payment-service": 0.7},
            "evidence_details": [{"service": "risk-engine", "evidence_items": []}],
            "error_cascade_order": ["risk-engine", "payment-service"],
        }
        self.logs_analysis = {"total_logs_analyzed": 10}
        self.metrics_analysis = {"service_metrics": {}}

    def test_perform_rca_uses_gemini_api_key_alias(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch.object(rca_node, "_call_gemini", return_value='{"root_cause": "risk-engine", "confidence": 0.9, "reasoning": "ok", "supporting_evidence": [], "affected_services": []}') as mock_call:
                with patch.object(rca_node, "GOOGLE_API_KEY", None):
                    result = rca_node.perform_rca(self.evidence, self.logs_analysis, self.metrics_analysis)

        self.assertEqual(result["root_cause"], "risk-engine")
        self.assertTrue(mock_call.called)


if __name__ == "__main__":
    unittest.main()
