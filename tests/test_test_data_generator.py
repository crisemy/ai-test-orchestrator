import pytest
from unittest.mock import patch, mock_open


class TestGetFallbackData:

    def test_returns_list_of_5_entries(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        assert isinstance(data, list)
        assert len(data) == 5

    def test_each_entry_has_required_keys(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        for entry in data:
            assert "username" in entry
            assert "password" in entry
            assert "expected_result" in entry

    def test_expected_result_is_success_or_failure(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        for entry in data:
            assert entry["expected_result"] in ("success", "failure")

    def test_includes_valid_credentials(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        successes = [e for e in data if e["expected_result"] == "success"]
        assert len(successes) >= 2

    def test_includes_invalid_credentials(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        failures = [e for e in data if e["expected_result"] == "failure"]
        assert len(failures) >= 2

    def test_includes_sql_injection_entry(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        injection = [e for e in data if "OR" in str(e["username"]) or "1=1" in str(e["username"])]
        assert len(injection) >= 1

    def test_includes_empty_fields_entry(self):
        from test_data_generator import get_fallback_data
        data = get_fallback_data()
        empty = [e for e in data if e["username"] == "" or e["password"] == ""]
        assert len(empty) >= 1


class TestGenerateTestData:

    def test_returns_test_data(self):
        from test_data_generator import generate_test_data
        mock_response = {
            "message": {
                "content": '[\n  {"username": "test1", "password": "pass1", "expected_result": "success"}\n]'
            }
        }

        with patch("test_data_generator.ollama.chat", return_value=mock_response), \
             patch("builtins.open", mock_open()), \
             patch("os.makedirs"):
            data = generate_test_data()
            assert len(data) == 1
            assert data[0]["username"] == "test1"

    def test_extracts_json_from_markdown_fence(self):
        from test_data_generator import generate_test_data
        mock_response = {
            "message": {
                "content": "```json\n[\n  {\"username\": \"test1\", \"password\": \"pass1\", \"expected_result\": \"success\"}\n]\n```"
            }
        }

        with patch("test_data_generator.ollama.chat", return_value=mock_response), \
             patch("builtins.open", mock_open()), \
             patch("os.makedirs"):
            data = generate_test_data()
            assert len(data) == 1

    def test_falls_back_on_json_decode_error(self):
        from test_data_generator import generate_test_data
        mock_response = {
            "message": {
                "content": "invalid json here"
            }
        }

        with patch("test_data_generator.ollama.chat", return_value=mock_response), \
             patch("builtins.open", mock_open()), \
             patch("os.makedirs"):
            data = generate_test_data()
            assert len(data) >= 5  # fallback data

    def test_writes_to_file(self):
        from test_data_generator import generate_test_data
        mock_response = {
            "message": {
                "content": '[\n  {"username": "test1", "password": "pass1", "expected_result": "success"}\n]'
            }
        }

        with patch("test_data_generator.ollama.chat", return_value=mock_response), \
             patch("os.makedirs") as mock_mkdir, \
             patch("builtins.open", mock_open()) as mock_file:
            generate_test_data()
            mock_mkdir.assert_called_once_with("generated-tests", exist_ok=True)
            mock_file.assert_called_once()
