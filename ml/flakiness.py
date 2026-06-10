import json
import os
from collections import defaultdict

EXECUTION_LOG = "reports/execution_log.json"


def _load_executions():
    if not os.path.exists(EXECUTION_LOG):
        return []
    with open(EXECUTION_LOG, "r", encoding="utf-8") as f:
        return json.load(f)


def detect_flaky_tests(min_runs=3):
    executions = _load_executions()
    feature_results = defaultdict(list)

    for ex in executions:
        feature = ex.get("feature", "unknown")
        status = ex.get("status", "unknown")
        metrics = ex.get("metrics", {})
        passed = metrics.get("passed", 0)
        failed = metrics.get("failed", 0)
        feature_results[feature].append({
            "status": status,
            "passed": passed,
            "failed": failed,
            "timestamp": ex.get("timestamp", ""),
        })

    flaky = []
    for feature, runs in feature_results.items():
        if len(runs) < min_runs:
            continue
        outcomes = []
        for r in runs:
            outcomes.append(0 if r["status"] == "success" else 1)
        pass_count = outcomes.count(0)
        total = len(outcomes)
        pass_rate = pass_count / total

        alternations = sum(1 for i in range(1, len(outcomes)) if outcomes[i] != outcomes[i - 1])
        max_alternations = len(outcomes) - 1
        alternation_ratio = alternations / max_alternations if max_alternations > 0 else 0

        is_flaky = 0.2 <= pass_rate <= 0.8 and alternation_ratio >= 0.3
        flaky.append({
            "feature": feature,
            "is_flaky": is_flaky,
            "pass_rate": round(pass_rate, 2),
            "total_runs": total,
            "alternation_ratio": round(alternation_ratio, 2),
            "outcomes": outcomes,
        })

    flaky.sort(key=lambda x: x["alternation_ratio"], reverse=True)
    return flaky


def get_flaky_features(min_runs=3):
    return [
        f["feature"] for f in detect_flaky_tests(min_runs)
        if f["is_flaky"]
    ]
