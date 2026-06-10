from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field


class ContractMetadata(BaseModel):
    contract_name: str
    contract_version: str = "v1.0"
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source_system: str = "ai-test-orchestrator"
    environment: str = "local"
    project_id: str = "ai-test-orchestrator"
    release_id: Optional[str] = None
    execution_id: str
    owner: str = "qa-team"


class GenerationRecord(BaseModel):
    metadata: ContractMetadata
    url: str
    feature: str
    model: str
    engine: str
    status: str
    attempts: int
    used_fallback: bool = False
    error_context_used: Optional[str] = None


class ExecutionMetrics(BaseModel):
    passed: int = 0
    failed: int = 0
    playwright_attempts: int = 1
    estimated_tokens: int = 0
    estimated_cost_usd: float = 0.0
    estimated_manual_cost_usd: float = 50.0
    estimated_roi: float = 0.0
    execution_duration_seconds: Optional[float] = None
    hallucination_fixes_applied: int = 0


class ExecutionRecord(BaseModel):
    metadata: ContractMetadata
    url: str
    feature: str
    model: str
    engine: str
    status: str
    steps: list[str] = Field(default_factory=list)
    metrics: ExecutionMetrics = Field(default_factory=ExecutionMetrics)
    failure_analysis: Optional["FailureRecord"] = None


class FailureRecord(BaseModel):
    failure_id: str
    test_case_id: Optional[str] = None
    error_message: str
    stack_trace: Optional[str] = None
    log_excerpt: str
    root_cause_class: str = "unknown"
    confidence_score: float = 0.0
    suggested_action: str = "Review logs manually"
    evidence_used: list[str] = Field(default_factory=list)
    uncertainty_flag: bool = True
    metadata: ContractMetadata
