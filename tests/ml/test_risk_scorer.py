import json
import pytest
from unittest.mock import patch, mock_open


class TestComputeRiskScore:

    def test_login_has_high_risk(self):
        from ml.risk_scorer import compute_risk_score
        with patch("os.path.exists", return_value=False):
            result = compute_risk_score("login")
            assert result["feature"] == "login"
            assert result["criticality"] == 10
            assert "risk_score" in result
            assert "should_generate" in result

    def test_logout_has_lower_risk_than_login(self):
        from ml.risk_scorer import compute_risk_score
        with patch("os.path.exists", return_value=False):
            login = compute_risk_score("login")
            logout = compute_risk_score("logout")
            assert login["risk_score"] > logout["risk_score"]

    def test_unknown_feature_gets_default_score(self):
        from ml.risk_scorer import compute_risk_score
        with patch("os.path.exists", return_value=False):
            result = compute_risk_score("unknown_feature")
            assert result["criticality"] == 5
            assert result["risk_score"] > 0

    def test_failures_increase_risk(self):
        from ml.risk_scorer import compute_risk_score
        data = [
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(data))), \
             patch("os.path.exists", return_value=True):
            result = compute_risk_score("login")
            assert result["actual_bug_rate"] > 0


class TestPrioritizeFeatures:

    def test_returns_sorted_by_risk(self):
        from ml.risk_scorer import prioritize_features
        with patch("os.path.exists", return_value=False):
            result = prioritize_features(["logout", "login"])
            assert result[0]["risk_score"] >= result[1]["risk_score"]
            assert result[0]["feature"] == "login"
            assert result[1]["feature"] == "logout"

    def test_accepts_custom_config(self):
        from ml.risk_scorer import prioritize_features
        with patch("os.path.exists", return_value=False):
            config = {"login": {"criticality": 10, "bug_history": 0.9}}
            result = prioritize_features(["login", "logout"], config)
            assert len(result) == 2
