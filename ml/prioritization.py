import json
import os
import re
from datetime import datetime, timezone

EXECUTION_LOG = "reports/execution_log.json"
PRIORITY_CACHE = "reports/priorities.json"


def _load_executions():
    if not os.path.exists(EXECUTION_LOG):
        return []
    with open(EXECUTION_LOG, "r", encoding="utf-8") as f:
        return json.load(f)


def _extract_features(executions):
    features = {}
    for ex in executions:
        feature_name = ex.get("feature", "unknown")
        metrics = ex.get("metrics", {})
        if feature_name not in features:
            features[feature_name] = {
                "total_runs": 0,
                "total_passed": 0,
                "total_failed": 0,
                "total_attempts": 0,
                "total_cost": 0.0,
                "recent_failures": 0,
                "execution_times": [],
            }
        f = features[feature_name]
        f["total_runs"] += 1
        f["total_passed"] += metrics.get("passed", 0)
        f["total_failed"] += metrics.get("failed", 0)
        f["total_attempts"] += metrics.get("playwright_attempts", 1)
        f["total_cost"] += metrics.get("estimated_cost_usd", 0.0)

        is_failure = ex.get("status") == "failed"
        if is_failure:
            f["recent_failures"] += 1

        try:
            ts = ex.get("timestamp", "")
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            f["execution_times"].append(dt.hour)
        except (ValueError, AttributeError):
            pass

    for name, f in features.items():
        fail_rate = f["recent_failures"] / max(f["total_runs"], 1)
        avg_attempts = f["total_attempts"] / max(f["total_runs"], 1)
        cost_per_run = f["total_cost"] / max(f["total_runs"], 1)
        f["fail_rate"] = round(fail_rate, 3)
        f["avg_attempts"] = round(avg_attempts, 2)
        f["cost_per_run"] = round(cost_per_run, 4)
        f["priority_score"] = _compute_priority_score(fail_rate, avg_attempts, cost_per_run)
    return features


def _compute_priority_score(fail_rate, avg_attempts, cost_per_run):
    score = 0.0
    score += fail_rate * 50.0
    score += min(avg_attempts / 3.0, 1.0) * 30.0
    score += min(cost_per_run / 0.01, 1.0) * 20.0
    return round(score, 1)


def compute_priorities():
    executions = _load_executions()
    features = _extract_features(executions)
    ranked = sorted(features.items(), key=lambda x: x[1]["priority_score"], reverse=True)
    result = []
    for name, data in ranked:
        result.append({
            "feature": name,
            "priority_score": data["priority_score"],
            "fail_rate": data["fail_rate"],
            "avg_attempts": data["avg_attempts"],
            "cost_per_run": data["cost_per_run"],
            "total_runs": data["total_runs"],
        })
    os.makedirs("reports", exist_ok=True)
    with open(PRIORITY_CACHE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return result


def suggest_next_feature(priorities=None):
    if priorities is None:
        priorities = compute_priorities()
    if not priorities:
        return None
    return priorities[0]["feature"]


try:
    from sklearn.ensemble import RandomForestRegressor
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


def _train_sklearn_model(features_data):
    if not HAS_SKLEARN or len(features_data) < 3:
        return None
    X = []
    y = []
    for name, f in features_data.items():
        X.append([f["fail_rate"], f["avg_attempts"], f["cost_per_run"], f["total_runs"]])
        y.append(f["priority_score"])
    model = RandomForestRegressor(n_estimators=10, random_state=42)
    model.fit(X, y)
    return model
