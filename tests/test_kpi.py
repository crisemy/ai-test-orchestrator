from unittest.mock import patch


class TestKPIReport:
    def test_creates_report_with_defaults(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r.generation_success is True
        assert r.test_pass_rate == 0.0
        assert r.hallucination_fixes == 0

    def test_color_green_above_threshold(self):
        from kpi import KPIReport
        assert KPIReport._color(0.90, 0.85, 0.70) == "green"

    def test_color_yellow_between_thresholds(self):
        from kpi import KPIReport
        assert KPIReport._color(0.75, 0.85, 0.70) == "yellow"

    def test_color_red_below_threshold(self):
        from kpi import KPIReport
        assert KPIReport._color(0.50, 0.85, 0.70) == "red"

    def test_rate_color_green(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r._rate_color(0.90) == "green"

    def test_rate_color_yellow(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r._rate_color(0.80) == "yellow"

    def test_rate_color_red(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r._rate_color(0.60) == "red"

    def test_duration_color_fast(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r._duration_color(15) == "green"

    def test_duration_color_moderate(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r._duration_color(45) == "yellow"

    def test_duration_color_slow(self):
        from kpi import KPIReport
        r = KPIReport()
        assert r._duration_color(90) == "red"

    def test_display_creates_table(self):
        from kpi import KPIReport
        r = KPIReport(feature="login", model="test-model")
        with patch("kpi.console.print") as mock_print:
            r.display()
            mock_print.assert_called_once()


class TestComputeHistoricalKpis:
    def test_returns_empty_with_no_executions(self):
        from kpi import compute_historical_kpis
        with patch("kpi.load_executions", return_value=[]):
            assert compute_historical_kpis() == {}

    def test_computes_kpis_from_executions(self):
        from kpi import compute_historical_kpis
        executions = [
            {"status": "success", "metrics": {"passed": 3, "failed": 0, "hallucination_fixes_applied": 1}},
            {"status": "success", "metrics": {"passed": 2, "failed": 1, "hallucination_fixes_applied": 2}},
        ]
        with patch("kpi.load_executions", return_value=executions):
            result = compute_historical_kpis()
            assert result["total_runs"] == 2
            assert result["successful_runs"] == 2
            assert result["total_tests_run"] == 6
            assert result["overall_pass_rate"] == 5 / 6
            assert result["total_hallucinations"] == 3

    def test_handles_missing_metrics_gracefully(self):
        from kpi import compute_historical_kpis
        executions = [
            {"status": "success", "metrics": None},
            {"status": "failed"},
        ]
        with patch("kpi.load_executions", return_value=executions):
            result = compute_historical_kpis()
            assert result["total_runs"] == 2
