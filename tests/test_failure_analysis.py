class TestClassifyFailure:
    def test_assertion_failure_classified_as_test_issue(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="Assertion Failed: toBeVisible",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "test_issue"
        assert result.confidence_score >= 0.8

    def test_strict_mode_violation_classified_as_test_issue(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="strict mode violation: locator resolved to 2 elements",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "test_issue"
        assert "Strict mode" in " ".join(result.evidence_used)

    def test_connection_refused_classified_as_environment(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="",
            stderr="Error: connect ECONNREFUSED localhost:3000",
            feature="login",
        )
        assert result.root_cause_class == "environment_issue"
        assert result.confidence_score >= 0.9

    def test_browser_closed_classified_as_environment(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="browser closed unexpectedly",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "environment_issue"

    def test_http_404_classified_as_environment(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="Error: net::ERR_ABORTED 404",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "environment_issue"

    def test_visibility_expectation_classified_as_product_bug(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="expected element to be visible",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "product_bug"
        assert result.uncertainty_flag is True

    def test_unknown_pattern_returns_unknown(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="completely unrelated error message",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "unknown"
        assert result.confidence_score == 0.3

    def test_returns_failure_record_with_metadata(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="test error",
            stderr="",
            feature="login",
            execution_id="exec-001",
        )
        assert result.metadata.execution_id == "exec-001"
        assert result.failure_id is not None
        assert result.suggested_action is not None

    def test_timeout_on_selector_classified_as_test_issue(self):
        from failure_analysis import classify_failure
        result = classify_failure(
            exit_code=1,
            stdout="Timeout 5000ms exceeded: page.click('#login-btn')",
            stderr="",
            feature="login",
        )
        assert result.root_cause_class == "test_issue"
        assert "timeout" in result.log_excerpt.lower()
