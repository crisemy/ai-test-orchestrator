import pytest
from unittest.mock import patch, mock_open, MagicMock


class TestSanitizeUrl:

    def test_valid_http(self):
        from orchestrator import sanitize_url
        assert sanitize_url("http://localhost:3000") == "http://localhost:3000"

    def test_valid_https(self):
        from orchestrator import sanitize_url
        assert sanitize_url("https://example.com") == "https://example.com"

    def test_invalid_protocol_raises(self):
        from orchestrator import sanitize_url
        with pytest.raises(ValueError, match="Invalid URL protocol"):
            sanitize_url("ftp://example.com")

    def test_missing_protocol_raises(self):
        from orchestrator import sanitize_url
        with pytest.raises(ValueError, match="Invalid URL protocol"):
            sanitize_url("localhost:3000")

    def test_strips_control_chars(self):
        from orchestrator import sanitize_url
        result = sanitize_url("http://localhost:3000\r\n\t")
        assert "\r" not in result
        assert "\n" not in result
        assert "\t" not in result

    def test_blocked_chars_raises(self):
        from orchestrator import sanitize_url
        for char in "<>\"'{}|^`\\":
            with pytest.raises(ValueError, match="contains blocked characters"):
                sanitize_url(f"http://example.com/{char}")


class TestSanitizeFeature:

    def test_normal_feature(self):
        from orchestrator import sanitize_feature
        assert sanitize_feature("login") == "login"

    def test_strips_shell_metacharacters(self):
        from orchestrator import sanitize_feature
        result = sanitize_feature("login; rm -rf /")
        assert ";" not in result
        assert "login" in result

    def test_strips_multiple_metachars(self):
        from orchestrator import sanitize_feature
        result = sanitize_feature("a&b|c`d$e(f)g{h}i[j]k!l~m<n>o\\p")
        assert result == "abcdefghijklmnop"

    def test_empty_after_sanitization_raises(self):
        from orchestrator import sanitize_feature
        with pytest.raises(ValueError, match="empty after sanitization"):
            sanitize_feature(";|&")

    def test_empty_string_raises(self):
        from orchestrator import sanitize_feature
        with pytest.raises(ValueError, match="empty after sanitization"):
            sanitize_feature("   ")

    def test_truncates_to_80_chars(self):
        from orchestrator import sanitize_feature
        long = "a" * 200
        result = sanitize_feature(long)
        assert len(result) == 80

    def test_strips_whitespace(self):
        from orchestrator import sanitize_feature
        assert sanitize_feature("  login  ") == "login"


class TestBackupTest:

    def test_no_existing_file_returns_none(self, temp_backup_dir):
        from orchestrator import backup_test
        with patch("os.path.exists", return_value=False):
            result = backup_test("login")
            assert result is None

    def test_existing_file_creates_backup(self, temp_backup_dir):
        from orchestrator import backup_test
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data="test content")), \
             patch("os.makedirs") as mock_makedirs:

            result = backup_test("login")
            assert result is not None
            assert "login.spec.ts." in result
            assert result.endswith(".bak")
            mock_makedirs.assert_called_once()

    def test_backup_copies_content(self, temp_backup_dir):
        from orchestrator import backup_test
        original_content = "test code here"

        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=original_content)) as mock_file, \
             patch("os.makedirs"):

            backup_test("login")
            write_calls = [c for c in mock_file.mock_calls if c[0] == '().write']
            assert len(write_calls) >= 1
            assert original_content in str(write_calls[0])


class TestRestoreTest:

    def test_no_backup_dir_returns_false(self, temp_backup_dir):
        from orchestrator import restore_test
        with patch("os.path.exists", return_value=False):
            assert restore_test("login") is False

    def test_no_candidates_returns_false(self, temp_backup_dir):
        from orchestrator import restore_test
        with patch("os.path.exists", return_value=True), \
             patch("os.listdir", return_value=[]):
            assert restore_test("login") is False

    def test_restores_latest_backup(self, temp_backup_dir):
        from orchestrator import restore_test
        backups = [
            "login.spec.ts.20260609120000.bak",
            "login.spec.ts.20260609130000.bak",
        ]
        with patch("os.path.exists", return_value=True), \
             patch("os.listdir", return_value=backups), \
             patch("builtins.open", mock_open(read_data="restored content")):
            assert restore_test("login") is True


class TestCheckRateLimit:

    def test_within_limit_appends_timestamp(self):
        from orchestrator import check_rate_limit, _rate_limit_state
        _rate_limit_state["call_timestamps"] = []
        check_rate_limit()
        assert len(_rate_limit_state["call_timestamps"]) == 1

    def test_exact_limit_reached(self):
        from orchestrator import check_rate_limit, _rate_limit_state
        import time
        now = time.time()
        _rate_limit_state["call_timestamps"] = [now - 10, now - 20, now - 30, now - 40, now - 50]
        time_values = iter([now, now, now + 61])

        with patch("time.sleep") as mock_sleep, \
             patch("time.time", side_effect=lambda: next(time_values)), \
             patch("orchestrator.console.print"):
            check_rate_limit()
            assert mock_sleep.call_count >= 1

    def test_old_timestamps_are_cleaned(self):
        from orchestrator import check_rate_limit, _rate_limit_state
        import time
        now = time.time()
        # 5 old timestamps (older than 60s)
        _rate_limit_state["call_timestamps"] = [now - 120, now - 90, now - 80, now - 70, now - 65]

        with patch("time.time", return_value=now), \
             patch("time.sleep"):
            check_rate_limit()
            # All old timestamps should be cleaned
            assert len(_rate_limit_state["call_timestamps"]) <= 5
            for t in _rate_limit_state["call_timestamps"]:
                assert t > now - 60


class TestCheckCostThreshold:

    def test_under_threshold_no_warning(self, capsys):
        from orchestrator import check_cost_threshold
        check_cost_threshold(0.10)
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out

    def test_over_threshold_shows_warning(self, capsys):
        from orchestrator import check_cost_threshold
        check_cost_threshold(1.00)
        captured = capsys.readouterr()
        assert "WARNING" in captured.out
        assert "1.0000" in captured.out

    def test_at_threshold_no_warning(self, capsys):
        from orchestrator import check_cost_threshold
        check_cost_threshold(0.50)
        captured = capsys.readouterr()
        assert "WARNING" not in captured.out

    def test_over_threshold_logs_pipeline(self):
        from orchestrator import check_cost_threshold
        with patch("orchestrator.log_pipeline") as mock_log:
            check_cost_threshold(1.00)
            mock_log.assert_called_once_with(
                "cost_threshold_exceeded",
                {"estimated_cost": 1.00, "threshold": 0.50}
            )

    def test_under_threshold_does_not_log(self):
        from orchestrator import check_cost_threshold
        with patch("orchestrator.log_pipeline") as mock_log:
            check_cost_threshold(0.10)
            mock_log.assert_not_called()


class TestValidateAndFix:

    def test_file_not_found_exits(self):
        from orchestrator import validate_and_fix
        with patch("os.path.exists", return_value=False), \
             pytest.raises(SystemExit):
            validate_and_fix("nonexistent")

    def test_normalizes_and_writes_file(self):
        from orchestrator import validate_and_fix
        original = "page.fill('#username', 'test')"
        fixed = "page.fill('#login-username', 'test')"

        mock_file = mock_open(read_data=original)
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_file):
            validate_and_fix("login")
            # Verify write was called with normalized content
            write_handle = mock_file()
            # After read, the file is opened for writing
            # The normalize_code replaces #username with #login-username
            calls = [c for c in mock_file.mock_calls if c[0] == '().write']
            assert any('#login-username' in str(c) for c in calls)


class TestLogPipeline:

    def test_writes_json_entry(self):
        from orchestrator import log_pipeline
        with patch("builtins.open", mock_open()) as mock, \
             patch("os.makedirs"):
            log_pipeline("test_action", {"key": "value"})
            handle = mock()
            written = "".join(c[1][0] for c in handle.method_calls if c[0] == "write")
            assert "test_action" in written
            assert "key" in written

    def test_defaults_details_to_empty_dict(self):
        from orchestrator import log_pipeline
        with patch("builtins.open", mock_open()) as mock, \
             patch("os.makedirs"):
            log_pipeline("test_action")
            handle = mock()
            written = "".join(c[1][0] for c in handle.method_calls if c[0] == "write")
            assert '"details": {}' in written


class TestRecordExecution:

    def test_saves_valid_record(self):
        from orchestrator import record_execution
        with patch("builtins.open", mock_open()), \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs"):
            record_execution(
                url="http://test.com",
                feature="login",
                model="test-model",
                engine="ollama",
                status="success",
                metrics={"passed": 3}
            )

    def test_appends_to_existing_log(self):
        import json
        from orchestrator import record_execution
        existing = json.dumps([{"execution_id": "old"}])
        with patch("builtins.open", mock_open(read_data=existing)), \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"):
            record_execution(
                url="http://test.com",
                feature="login",
                model="test-model",
                engine="ollama",
                status="success"
            )

    def test_includes_environment_and_metrics(self):
        from orchestrator import record_execution
        with patch("builtins.open", mock_open()), \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs"):
            record_execution(
                url="http://test.com",
                feature="login",
                model="test-model",
                engine="ollama",
                status="success",
                metrics={"passed": 5, "failed": 0}
            )
