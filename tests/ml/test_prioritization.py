import json
import pytest
from unittest.mock import patch, mock_open


class TestComputePriorities:

    def test_empty_log_returns_empty(self):
        from ml.prioritization import compute_priorities
        with patch("os.path.exists", return_value=False):
            result = compute_priorities()
            assert result == []

    def test_ranks_by_priority_score(self):
        from ml.prioritization import compute_priorities
        data = [
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3, "playwright_attempts": 3, "estimated_cost_usd": 0.003}},
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0, "playwright_attempts": 1, "estimated_cost_usd": 0.001}},
            {"feature": "logout", "status": "success", "metrics": {"passed": 3, "failed": 0, "playwright_attempts": 1, "estimated_cost_usd": 0.0005}},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(data))), \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"):
            result = compute_priorities()
            assert len(result) == 2
            # login has failures → higher priority than logout
            login_entry = next(r for r in result if r["feature"] == "login")
            logout_entry = next(r for r in result if r["feature"] == "logout")
            assert login_entry["priority_score"] > logout_entry["priority_score"]

    def test_priority_score_increases_with_failures(self):
        from ml.prioritization import _compute_priority_score
        score_low = _compute_priority_score(0.0, 1.0, 0.001)
        score_high = _compute_priority_score(0.5, 1.0, 0.001)
        assert score_high > score_low

    def test_priority_score_increases_with_attempts(self):
        from ml.prioritization import _compute_priority_score
        score_low = _compute_priority_score(0.0, 1.0, 0.001)
        score_high = _compute_priority_score(0.0, 3.0, 0.001)
        assert score_high > score_low


class TestSuggestNextFeature:

    def test_returns_highest_priority_feature(self):
        from ml.prioritization import suggest_next_feature
        priorities = [
            {"feature": "login", "priority_score": 50},
            {"feature": "logout", "priority_score": 10},
        ]
        assert suggest_next_feature(priorities) == "login"

    def test_returns_none_for_empty(self):
        from ml.prioritization import suggest_next_feature
        assert suggest_next_feature([]) is None
