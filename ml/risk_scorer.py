import json
import os

EXECUTION_LOG = "reports/execution_log.json"


FEATURE_RISK_DEFAULTS = {
    "login": {"criticality": 10, "bug_history": 0.3},
    "checkout": {"criticality": 10, "bug_history": 0.5},
    "payment": {"criticality": 10, "bug_history": 0.4},
    "registration": {"criticality": 8, "bug_history": 0.2},
    "search": {"criticality": 7, "bug_history": 0.3},
    "profile": {"criticality": 5, "bug_history": 0.1},
    "logout": {"criticality": 5, "bug_history": 0.05},
    "navigation": {"criticality": 6, "bug_history": 0.15},
}


def _load_executions():
    if not os.path.exists(EXECUTION_LOG):
        return []
    with open(EXECUTION_LOG, "r", encoding="utf-8") as f:
        return json.load(f)


def compute_risk_score(feature_name, custom_config=None):
    config = FEATURE_RISK_DEFAULTS.get(feature_name, {"criticality": 5, "bug_history": 0.1})
    if custom_config and feature_name in custom_config:
        config = custom_config[feature_name]

    criticality = config.get("criticality", 5)
    bug_history_base = config.get("bug_history", 0.1)

    executions = _load_executions()
    feature_execs = [e for e in executions if e.get("feature") == feature_name]

    if feature_execs:
        failures = sum(1 for e in feature_execs if e.get("status") == "failed")
        total = len(feature_execs)
        actual_bug_rate = failures / max(total, 1)
    else:
        actual_bug_rate = bug_history_base

    change_frequency = len(feature_execs) / max(len(executions), 1)
    change_frequency = min(change_frequency, 1.0)

    risk_score = (
        criticality * 0.5 +
        actual_bug_rate * 100 * 0.3 +
        change_frequency * 100 * 0.2
    )

    return {
        "feature": feature_name,
        "risk_score": round(risk_score, 1),
        "criticality": criticality,
        "actual_bug_rate": round(actual_bug_rate, 3),
        "change_frequency": round(change_frequency, 3),
        "should_generate": risk_score > 30,
    }


def prioritize_features(feature_names, custom_config=None):
    scored = [compute_risk_score(f, custom_config) for f in feature_names]
    scored.sort(key=lambda x: x["risk_score"], reverse=True)
    return scored
