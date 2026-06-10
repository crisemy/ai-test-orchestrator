from rich.console import Console
from rich.table import Table

from persistence import load_executions

console = Console()


class KPIReport:
    def __init__(
        self,
        generation_success: bool = True,
        test_pass_rate: float = 0.0,
        hallucination_fixes: int = 0,
        execution_duration_seconds: float = 0.0,
        total_tests: int = 0,
        passed_tests: int = 0,
        failed_tests: int = 0,
        feature: str = "",
        model: str = "",
    ):
        self.generation_success = generation_success
        self.test_pass_rate = test_pass_rate
        self.hallucination_fixes = hallucination_fixes
        self.execution_duration_seconds = execution_duration_seconds
        self.total_tests = total_tests
        self.passed_tests = passed_tests
        self.failed_tests = failed_tests
        self.feature = feature
        self.model = model

    @staticmethod
    def _color(value: float, green: float, yellow: float) -> str:
        if value >= green:
            return "green"
        elif value >= yellow:
            return "yellow"
        return "red"

    def _rate_color(self, rate: float) -> str:
        return self._color(rate, 0.85, 0.70)

    def _duration_color(self, secs: float) -> str:
        if secs <= 30:
            return "green"
        elif secs <= 60:
            return "yellow"
        return "red"

    def display(self) -> None:
        table = Table(title=f"KPI Report — {self.feature} ({self.model})", border_style="cyan")
        table.add_column("KPI", style="white")
        table.add_column("Value", style="bold")
        table.add_column("Status", style="bold")

        gen_color = "green" if self.generation_success else "red"
        table.add_row(
            "Generation Success",
            "Yes" if self.generation_success else "No",
            f"[{gen_color}]{'PASS' if self.generation_success else 'FAIL'}[/{gen_color}]",
        )

        pr_color = self._rate_color(self.test_pass_rate)
        table.add_row(
            "Test Pass Rate",
            f"{self.test_pass_rate:.1%}",
            f"[{pr_color}]{'GREEN' if pr_color == 'green' else 'YELLOW' if pr_color == 'yellow' else 'RED'}[/{pr_color}]",
        )

        hf_color = "green" if self.hallucination_fixes <= 3 else "yellow" if self.hallucination_fixes <= 6 else "red"
        table.add_row(
            "Hallucination Fixes",
            str(self.hallucination_fixes),
            f"[{hf_color}]{'LOW' if hf_color == 'green' else 'MEDIUM' if hf_color == 'yellow' else 'HIGH'}[/{hf_color}]",
        )

        dur_color = self._duration_color(self.execution_duration_seconds)
        table.add_row(
            "Execution Duration",
            f"{self.execution_duration_seconds:.1f}s",
            f"[{dur_color}]{'FAST' if dur_color == 'green' else 'MODERATE' if dur_color == 'yellow' else 'SLOW'}[/{dur_color}]",
        )

        table.add_row("Tests Run", str(self.total_tests), "")
        table.add_row("Passed", f"[green]{self.passed_tests}[/green]", "")
        table.add_row("Failed", f"[red]{self.failed_tests}[/red]", "")

        console.print(table)


def compute_historical_kpis() -> dict:
    executions = load_executions()
    if not executions:
        return {}

    total_runs = len(executions)
    successful_runs = sum(1 for e in executions if e.get("status") == "success")
    total_tests_run = sum(
        e.get("metrics", {}).get("passed", 0) + e.get("metrics", {}).get("failed", 0)
        for e in executions
        if e.get("metrics")
    )
    total_passed = sum(
        e.get("metrics", {}).get("passed", 0) for e in executions if e.get("metrics")
    )
    total_failed = sum(
        e.get("metrics", {}).get("failed", 0) for e in executions if e.get("metrics")
    )
    total_hallucinations = sum(
        e.get("metrics", {}).get("hallucination_fixes_applied", 0)
        for e in executions
        if e.get("metrics")
    )

    return {
        "total_runs": total_runs,
        "successful_runs": successful_runs,
        "generation_success_rate": successful_runs / total_runs if total_runs else 0.0,
        "total_tests_run": total_tests_run,
        "overall_pass_rate": total_passed / total_tests_run if total_tests_run else 0.0,
        "overall_fail_rate": total_failed / total_tests_run if total_tests_run else 0.0,
        "total_hallucinations": total_hallucinations,
        "avg_hallucinations_per_run": round(total_hallucinations / total_runs, 1) if total_runs else 0.0,
    }
