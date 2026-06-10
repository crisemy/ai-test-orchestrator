import json
import pytest
from unittest.mock import patch, mock_open


class TestDetectFlakyTests:

    def test_empty_log_returns_empty(self):
        from ml.flakiness import detect_flaky_tests
        with patch("os.path.exists", return_value=False):
            assert detect_flaky_tests() == []

    def test_detects_flaky_alternating_pattern(self):
        from ml.flakiness import detect_flaky_tests
        data = [
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(data))), \
             patch("os.path.exists", return_value=True):
            result = detect_flaky_tests()
            assert any(f["feature"] == "login" and f["is_flaky"] for f in result)

    def test_stable_test_not_flaky(self):
        from ml.flakiness import detect_flaky_tests
        data = [
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(data))), \
             patch("os.path.exists", return_value=True):
            result = detect_flaky_tests()
            login = next(f for f in result if f["feature"] == "login")
            assert not login["is_flaky"]

    def test_fewer_than_min_runs_skipped(self):
        from ml.flakiness import detect_flaky_tests
        data = [
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(data))), \
             patch("os.path.exists", return_value=True):
            result = detect_flaky_tests(min_runs=3)
            assert len(result) == 0


class TestGetFlakyFeatures:

    def test_returns_only_flaky_feature_names(self):
        from ml.flakiness import get_flaky_features
        data = [
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
            {"feature": "login", "status": "success", "metrics": {"passed": 6, "failed": 0}},
            {"feature": "login", "status": "failed", "metrics": {"passed": 0, "failed": 3}},
            {"feature": "logout", "status": "success", "metrics": {"passed": 3, "failed": 0}},
            {"feature": "logout", "status": "success", "metrics": {"passed": 3, "failed": 0}},
            {"feature": "logout", "status": "success", "metrics": {"passed": 3, "failed": 0}},
        ]
        with patch("builtins.open", mock_open(read_data=json.dumps(data))), \
             patch("os.path.exists", return_value=True):
            flaky = get_flaky_features()
            assert "login" in flaky
            assert "logout" not in flaky
