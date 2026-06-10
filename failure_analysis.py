import re
from datetime import datetime, timezone
from typing import Optional

from contracts import FailureRecord, ContractMetadata


def classify_failure(
    exit_code: int,
    stdout: str,
    stderr: str,
    feature: str = "unknown",
    execution_id: Optional[str] = None,
) -> FailureRecord:
    combined = (stdout + " " + (stderr or "")).lower()

    evidence: list[str] = []
    root_cause = "unknown"
    confidence = 0.0
    action = "Review logs manually"
    uncertainty = True

    # Test issue patterns: assertion errors, selector issues, timeout on specific tests
    if re.search(r"assertion failed|tohaveurl|tobevisible|tocontaintext|tohavetext", combined):
        evidence.append("Assertion failure in test logic")
        root_cause = "test_issue"
        confidence = 0.85
        action = "Review generated test assertions and selectors"
        uncertainty = False

    elif re.search(r"strict mode violation|strict mode|multiple.*elements", combined) and re.search(r"locator", combined):
        evidence.append("Strict mode locator ambiguity")
        root_cause = "test_issue"
        confidence = 0.8
        action = "Fix ambiguous selectors in generated test"
        uncertainty = False

    elif re.search(r"page\.click|page\.fill|page\.locator", combined) and re.search(r"timeout", combined):
        evidence.append("Selector timeout — element not found")
        root_cause = "test_issue"
        confidence = 0.7
        action = "Check selector correctness and page load timing"
        uncertainty = False

    elif re.search(r"error: (socket hang up|connect econnrefused|request aborted)", combined):
        evidence.append("Server connection failure")
        root_cause = "environment_issue"
        confidence = 0.95
        action = "Ensure ui-testing-lab server is running on port 3000"
        uncertainty = False

    elif re.search(r"browser.*closed|target closed|page crashed|session.*not.*created", combined):
        evidence.append("Browser/Playwright runtime error")
        root_cause = "environment_issue"
        confidence = 0.9
        action = "Check browser availability and Playwright installation"
        uncertainty = False

    elif re.search(r"error: net::", combined) and re.search(r"404|500|503|502|403", combined):
        evidence.append(f"HTTP error response from server")
        root_cause = "environment_issue"
        confidence = 0.85
        action = "Verify server is healthy and serving correct content"
        uncertainty = False

    elif re.search(r"expected.*to.*be.*visible|expect.*locator.*visible", combined):
        evidence.append("Element visibility expectation failed")
        root_cause = "product_bug"
        confidence = 0.6
        action = "Verify the UI element exists and is visible in the app"
        uncertainty = True

    else:
        evidence.append("No specific pattern matched — defaulting to unknown")
        root_cause = "unknown"
        confidence = 0.3
        action = "Inspect Playwright output and logs manually"
        uncertainty = True

    failure_id = f"fail-{execution_id or datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')}"

    error_msg = stderr[:1000] if stderr else stdout[:1000]

    metadata = ContractMetadata(
        contract_name="failure_record",
        execution_id=execution_id or failure_id,
        environment="local",
    )

    return FailureRecord(
        failure_id=failure_id,
        error_message=error_msg,
        log_excerpt=combined[-500:],
        root_cause_class=root_cause,
        confidence_score=confidence,
        suggested_action=action,
        evidence_used=evidence,
        uncertainty_flag=uncertainty,
        metadata=metadata,
    )
