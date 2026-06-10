import os
import json
from datetime import datetime, timezone
from typing import Optional

from contracts import (
    ContractMetadata,
    ExecutionRecord,
    ExecutionMetrics,
    GenerationRecord,
    FailureRecord,
)

LOG_FILE = "logs/pipeline.log"
EXECUTION_LOG = "reports/execution_log.json"


def create_metadata(
    execution_id: str,
    contract_name: str = "execution_record",
    environment: str = "local",
) -> ContractMetadata:
    return ContractMetadata(
        contract_name=contract_name,
        execution_id=execution_id,
        environment=environment,
        generated_at=datetime.now(timezone.utc),
    )


def save_generation(record: GenerationRecord) -> None:
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp": record.metadata.generated_at.isoformat(),
        "action": "generation",
        "details": record.model_dump(mode="json"),
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")


def save_execution(record: ExecutionRecord) -> None:
    os.makedirs("reports", exist_ok=True)
    logs: list[dict] = []
    if os.path.exists(EXECUTION_LOG):
        with open(EXECUTION_LOG, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append(record.model_dump(mode="json"))
    with open(EXECUTION_LOG, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=2)


def load_executions() -> list[dict]:
    if not os.path.exists(EXECUTION_LOG):
        return []
    with open(EXECUTION_LOG, "r", encoding="utf-8") as f:
        return json.load(f)


def save_failure(record: FailureRecord) -> None:
    os.makedirs("logs", exist_ok=True)
    entry = {
        "timestamp": record.metadata.generated_at.isoformat(),
        "action": "failure_classification",
        "details": record.model_dump(mode="json"),
    }
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry) + "\n")
