from unittest.mock import patch, mock_open
from datetime import datetime, timezone


class TestCreateMetadata:
    def test_creates_metadata_with_execution_id(self):
        from persistence import create_metadata
        meta = create_metadata(execution_id="test-123", contract_name="execution_record")
        assert meta.execution_id == "test-123"
        assert meta.contract_name == "execution_record"
        assert meta.environment == "local"

    def test_metadata_has_timestamp(self):
        from persistence import create_metadata
        meta = create_metadata(execution_id="test-123")
        assert meta.generated_at is not None
        assert isinstance(meta.generated_at, datetime)


class TestSaveGeneration:
    def test_writes_to_log_file(self):
        from persistence import save_generation
        from contracts import GenerationRecord, ContractMetadata
        meta = ContractMetadata(
            contract_name="generation_record",
            execution_id="gen-001",
            environment="local",
            generated_at=datetime.now(timezone.utc),
        )
        record = GenerationRecord(metadata=meta, url="http://test.com", feature="login", model="qwen", engine="ollama", status="success", attempts=1)
        with patch("builtins.open", mock_open()) as mock, \
             patch("os.makedirs"):
            save_generation(record)
            handle = mock()
            written = "".join(c[1][0] for c in handle.method_calls if c[0] == "write")
            assert "generation" in written


class TestSaveExecution:
    def test_saves_new_execution(self):
        from persistence import save_execution
        from contracts import ExecutionRecord, ExecutionMetrics, ContractMetadata
        meta = ContractMetadata(
            contract_name="execution_record",
            execution_id="exec-001",
            environment="local",
            generated_at=datetime.now(timezone.utc),
        )
        record = ExecutionRecord(
            metadata=meta,
            url="http://test.com",
            feature="login",
            model="qwen",
            engine="ollama",
            status="success",
            metrics=ExecutionMetrics(passed=3, failed=0),
        )
        with patch("builtins.open", mock_open()) as mock, \
             patch("os.path.exists", return_value=False), \
             patch("os.makedirs"):
            save_execution(record)
            handle = mock()
            written = "".join(c[1][0] for c in handle.method_calls if c[0] == "write")
            assert "exec-001" in written

    def test_appends_to_existing_log(self):
        import json
        from persistence import save_execution
        from contracts import ExecutionRecord, ExecutionMetrics, ContractMetadata
        meta = ContractMetadata(
            contract_name="execution_record",
            execution_id="exec-002",
            environment="local",
            generated_at=datetime.now(timezone.utc),
        )
        record = ExecutionRecord(
            metadata=meta,
            url="http://test.com",
            feature="login",
            model="qwen",
            engine="ollama",
            status="success",
            metrics=ExecutionMetrics(passed=3, failed=0),
        )
        existing = json.dumps([{"execution_id": "old-exec"}])
        with patch("builtins.open", mock_open(read_data=existing)), \
             patch("os.path.exists", return_value=True), \
             patch("os.makedirs"):
            save_execution(record)


class TestLoadExecutions:
    def test_returns_empty_list_if_no_file(self):
        from persistence import load_executions
        with patch("os.path.exists", return_value=False):
            assert load_executions() == []

    def test_loads_executions_from_file(self):
        import json
        from persistence import load_executions
        data = [{"execution_id": "exec-001"}, {"execution_id": "exec-002"}]
        with patch("os.path.exists", return_value=True), \
             patch("builtins.open", mock_open(read_data=json.dumps(data))):
            result = load_executions()
            assert len(result) == 2
            assert result[0]["execution_id"] == "exec-001"


class TestSaveFailure:
    def test_writes_failure_to_log(self):
        from persistence import save_failure
        from contracts import FailureRecord, ContractMetadata
        meta = ContractMetadata(
            contract_name="failure_record",
            execution_id="fail-001",
            environment="local",
            generated_at=datetime.now(timezone.utc),
        )
        record = FailureRecord(
            metadata=meta,
            failure_id="fail-001",
            error_message="test error",
            log_excerpt="excerpt",
            root_cause_class="test_issue",
            confidence_score=0.8,
            suggested_action="fix test",
            evidence_used=["assertion error"],
        )
        with patch("builtins.open", mock_open()) as mock, \
             patch("os.makedirs"):
            save_failure(record)
            handle = mock()
            written = "".join(c[1][0] for c in handle.method_calls if c[0] == "write")
            assert "failure_classification" in written
