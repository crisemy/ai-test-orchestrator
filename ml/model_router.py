AVAILABLE_MODELS = {
    "fast": {
        "name": "qwen3.5:4b",
        "description": "Fast, lightweight — for simple features",
        "max_complexity": 3,
    },
    "balanced": {
        "name": "qwen2.5-coder:7b",
        "description": "Balanced speed/quality — default",
        "max_complexity": 7,
    },
    "quality": {
        "name": "qwen3.5:latest",
        "description": "Best quality — for complex features",
        "max_complexity": 10,
    },
}


def _estimate_complexity(feature_name, selectors=None, assertions=None):
    score = 1

    name_lower = feature_name.lower()
    complex_keywords = ["checkout", "payment", "registration", "multi", "workflow", "e2e", "end-to-end"]
    for kw in complex_keywords:
        if kw in name_lower:
            score += 2

    simple_keywords = ["login", "logout", "link", "button", "basic"]
    for kw in simple_keywords:
        if kw in name_lower:
            score -= 1

    if selectors:
        score += len(selectors) // 2
    if assertions:
        score += len(assertions) // 2

    return max(1, min(score, 10))


def select_model(feature_name, selectors=None, assertions=None, preference="balanced"):
    complexity = _estimate_complexity(feature_name, selectors, assertions)

    if preference == "fast":
        return AVAILABLE_MODELS["fast"]["name"]

    if preference == "quality":
        return AVAILABLE_MODELS["quality"]["name"]

    for tier in ["fast", "balanced", "quality"]:
        if complexity <= AVAILABLE_MODELS[tier]["max_complexity"]:
            return AVAILABLE_MODELS[tier]["name"]

    return AVAILABLE_MODELS["quality"]["name"]


def get_model_info(model_name):
    for tier, info in AVAILABLE_MODELS.items():
        if info["name"] == model_name:
            return {"tier": tier, **info}
    return {"tier": "unknown", "name": model_name, "description": "Unknown model"}
