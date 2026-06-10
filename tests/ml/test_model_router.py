import pytest


class TestEstimateComplexity:

    def test_basic_feature_low_complexity(self):
        from ml.model_router import _estimate_complexity
        assert _estimate_complexity("login") >= 1
        assert _estimate_complexity("login") <= 3

    def test_complex_feature_higher_score(self):
        from ml.model_router import _estimate_complexity
        simple = _estimate_complexity("login")
        complex = _estimate_complexity("checkout-payment-flow")
        assert complex >= simple

    def test_selectors_increase_complexity(self):
        from ml.model_router import _estimate_complexity
        no_sel = _estimate_complexity("login")
        with_sel = _estimate_complexity("login", selectors=["#a", "#b", "#c", "#d"])
        assert with_sel >= no_sel

    def test_complexity_capped_at_10(self):
        from ml.model_router import _estimate_complexity
        score = _estimate_complexity(
            "checkout-payment-multi-workflow-e2e",
            selectors=["#a"] * 20,
            assertions=["assert"] * 20,
        )
        assert score <= 10

    def test_complexity_min_1(self):
        from ml.model_router import _estimate_complexity
        assert _estimate_complexity("") >= 1


class TestSelectModel:

    def test_simple_feature_uses_fast_model(self):
        from ml.model_router import select_model
        model = select_model("login")
        assert model == "qwen3.5:4b"

    def test_complex_feature_uses_best_model(self):
        from ml.model_router import select_model
        model = select_model("checkout-payment-e2e-flow",
                             selectors=["#a", "#b", "#c", "#d", "#e", "#f", "#g", "#h"])
        assert model == "qwen3.5:latest"

    def test_preference_fast_bypasses_complexity(self):
        from ml.model_router import select_model
        model = select_model("checkout-payment-e2e-flow",
                             selectors=["#a"] * 10,
                             preference="fast")
        assert model == "qwen3.5:4b"

    def test_preference_quality_bypasses_complexity(self):
        from ml.model_router import select_model
        model = select_model("login", preference="quality")
        assert model == "qwen3.5:latest"


class TestGetModelInfo:

    def test_known_model_returns_info(self):
        from ml.model_router import get_model_info
        info = get_model_info("qwen2.5-coder:7b")
        assert info["tier"] == "balanced"
        assert "description" in info

    def test_unknown_model_returns_unknown(self):
        from ml.model_router import get_model_info
        info = get_model_info("nonexistent-model")
        assert info["tier"] == "unknown"
