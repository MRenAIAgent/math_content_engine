"""
Tests for the template system.
"""

import pytest
from math_content_engine.templates.base import (
    ManimTemplate,
    ParamSpec,
    ParamType,
    TemplateCategory,
    ParseResult,
)
from math_content_engine.templates.registry import TemplateRegistry, get_registry
from math_content_engine.templates.renderer import TemplateRenderer
from math_content_engine.templates.question_parser import SimpleQuestionParser
from math_content_engine.templates.definitions import linear_equations, graphing, quadratics


class TestParamSpec:
    """Tests for ParamSpec validation."""

    def test_int_validation(self):
        spec = ParamSpec(
            name="a",
            param_type=ParamType.INT,
            description="Test param",
            constraints={"min": 0, "max": 10},
        )

        # Valid values
        assert spec.validate(5) == (True, None)
        assert spec.validate(0) == (True, None)
        assert spec.validate(10) == (True, None)

        # Invalid values
        is_valid, error = spec.validate(-1)
        assert not is_valid
        assert "min" in error.lower() or ">=" in error

        is_valid, error = spec.validate(11)
        assert not is_valid
        assert "max" in error.lower() or "<=" in error

    def test_required_validation(self):
        spec = ParamSpec(
            name="required_param",
            param_type=ParamType.INT,
            description="Required",
            required=True,
        )

        is_valid, error = spec.validate(None)
        assert not is_valid
        assert "required" in error.lower()

    def test_optional_with_default(self):
        spec = ParamSpec(
            name="optional_param",
            param_type=ParamType.INT,
            description="Optional",
            required=False,
            default=5,
        )

        is_valid, error = spec.validate(None)
        assert is_valid

    def test_choice_validation(self):
        spec = ParamSpec(
            name="operator",
            param_type=ParamType.CHOICE,
            description="Operator",
            constraints={"choices": [">", "<", ">=", "<="]},
        )

        assert spec.validate(">") == (True, None)
        assert spec.validate(">=") == (True, None)

        is_valid, error = spec.validate("==")
        assert not is_valid
        assert "choices" in error.lower() or "one of" in error.lower()


class TestTemplateRegistry:
    """Tests for TemplateRegistry."""

    def test_register_and_get(self):
        registry = TemplateRegistry()

        template = ManimTemplate(
            id="test_template",
            name="Test Template",
            category=TemplateCategory.LINEAR_EQUATIONS,
            description="A test template",
            parameters=[],
            template_code="# test code",
            example_questions=["Test question"],
            tags=["test"],
        )

        registry.register(template)

        assert "test_template" in registry
        assert registry.get("test_template") == template
        assert len(registry) == 1

    def test_duplicate_registration_fails(self):
        registry = TemplateRegistry()

        template = ManimTemplate(
            id="test_template",
            name="Test",
            category=TemplateCategory.LINEAR_EQUATIONS,
            description="Test",
            parameters=[],
            template_code="# code",
        )

        registry.register(template)

        with pytest.raises(ValueError, match="already registered"):
            registry.register(template)

    def test_get_by_category(self):
        registry = TemplateRegistry()

        t1 = ManimTemplate(
            id="linear1",
            name="Linear 1",
            category=TemplateCategory.LINEAR_EQUATIONS,
            description="Linear",
            parameters=[],
            template_code="# code",
        )
        t2 = ManimTemplate(
            id="quad1",
            name="Quadratic 1",
            category=TemplateCategory.QUADRATICS,
            description="Quadratic",
            parameters=[],
            template_code="# code",
        )

        registry.register(t1)
        registry.register(t2)

        linear = registry.get_by_category(TemplateCategory.LINEAR_EQUATIONS)
        assert len(linear) == 1
        assert linear[0].id == "linear1"

    def test_search(self):
        registry = TemplateRegistry()

        t1 = ManimTemplate(
            id="slope_viz",
            name="Slope Visualization",
            category=TemplateCategory.GRAPHING,
            description="Shows rise over run",
            parameters=[],
            template_code="# code",
            example_questions=["Find the slope"],
        )

        registry.register(t1)

        results = registry.search("slope")
        assert len(results) == 1
        assert results[0].id == "slope_viz"

        results = registry.search("rise")
        assert len(results) == 1

    def test_global_registry_has_templates(self):
        """Test that the global registry loads built-in templates."""
        registry = get_registry()

        assert len(registry) > 0
        assert "linear_equation_graph" in registry
        assert "slope_visualization" in registry


class TestLinearEquationTemplates:
    """Tests for linear equation templates."""

    def test_compute_derived_simple(self):
        # Test 2x + 3 = 7 => x = 2
        params = {"a": 2, "b": 3, "c": 7}
        derived = linear_equations.compute_linear_derived(params)

        assert derived["solution"] == 2
        assert "x_min" in derived
        assert "x_max" in derived

    def test_compute_derived_negative(self):
        # Test 3x - 6 = 9 => x = 5
        params = {"a": 3, "b": -6, "c": 9}
        derived = linear_equations.compute_linear_derived(params)

        assert derived["solution"] == 5

    def test_compute_derived_fractional(self):
        # Test 2x + 1 = 4 => x = 1.5
        params = {"a": 2, "b": 1, "c": 4}
        derived = linear_equations.compute_linear_derived(params)

        assert derived["solution"] == 1.5

    def test_linear_equation_graph_template(self):
        template = linear_equations.linear_equation_graph

        assert template.id == "linear_equation_graph"
        assert template.category == TemplateCategory.LINEAR_EQUATIONS
        assert len(template.get_required_params()) == 3  # a, b, c
        assert "solution" in template.get_derived_params()


class TestTemplateRenderer:
    """Tests for TemplateRenderer."""

    def test_render_linear_equation(self):
        registry = get_registry()
        renderer = TemplateRenderer(registry=registry)

        params = {"a": 2, "b": 3, "c": 7}
        code, scene_name = renderer.render("linear_equation_graph", params)

        # Check code contains expected values
        assert "a, b, c = 2, 3, 7" in code
        assert "solution = 2" in code
        assert "LinearEquationGraphScene" in code
        assert scene_name == "LinearEquationGraphScene"

    def test_render_slope_visualization(self):
        registry = get_registry()
        renderer = TemplateRenderer(registry=registry)

        params = {"x1": 1, "y1": 2, "x2": 4, "y2": 8}
        code, scene_name = renderer.render("slope_visualization", params)

        assert "x1, y1 = 1, 2" in code
        assert "x2, y2 = 4, 8" in code
        assert "rise, run = 6, 3" in code
        assert scene_name == "SlopeVisualizationScene"

    def test_render_with_parse_result(self):
        registry = get_registry()
        renderer = TemplateRenderer(registry=registry)

        result = ParseResult(
            success=True,
            template_id="linear_equation_graph",
            parameters={"a": 3, "b": 5, "c": 14},
        )

        # Compute derived params (normally done by parser)
        derived = linear_equations.compute_linear_derived(result.parameters)
        result.parameters.update(derived)

        code, scene_name = renderer.render_from_parse_result(result)

        assert "a, b, c = 3, 5, 14" in code
        assert "solution = 3" in code

    def test_get_required_params(self):
        registry = get_registry()
        renderer = TemplateRenderer(registry=registry)

        required = renderer.get_required_params("linear_equation_graph")
        assert "a" in required
        assert "b" in required
        assert "c" in required
        assert "solution" not in required  # derived


class TestSimpleQuestionParser:
    """Tests for regex-based question parser."""

    def test_parse_linear_equation(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Solve 2x + 3 = 7")
        assert result.success
        assert result.template_id == "linear_equation_graph"
        assert result.parameters["a"] == 2
        assert result.parameters["b"] == 3
        assert result.parameters["c"] == 7
        assert result.parameters["solution"] == 2

    def test_parse_linear_equation_negative(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Solve 3x - 5 = 10")
        assert result.success
        assert result.parameters["a"] == 3
        assert result.parameters["b"] == -5
        assert result.parameters["c"] == 10
        assert result.parameters["solution"] == 5

    def test_parse_slope_points(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Find the slope between (1, 2) and (4, 8)")
        assert result.success
        assert result.template_id == "slope_visualization"
        assert result.parameters["x1"] == 1
        assert result.parameters["y1"] == 2
        assert result.parameters["x2"] == 4
        assert result.parameters["y2"] == 8
        assert result.parameters["rise"] == 6
        assert result.parameters["run"] == 3

    def test_parse_slope_intercept(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Graph y = 2x + 3")
        assert result.success
        assert result.template_id == "slope_intercept_form"
        assert result.parameters["m"] == 2
        assert result.parameters["b"] == 3

    def test_parse_slope_intercept_negative(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Graph y = 3x - 5")
        assert result.success
        assert result.parameters["m"] == 3
        assert result.parameters["b"] == -5

    def test_parse_inequality(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Graph x > 5")
        assert result.success
        assert result.template_id == "inequality_numberline"
        assert result.parameters["boundary"] == 5
        assert result.parameters["operator"] == ">"
        assert result.parameters["is_inclusive"] is False
        assert result.parameters["direction"] == "right"

    def test_parse_inequality_inclusive(self):
        parser = SimpleQuestionParser()

        result = parser.parse("Graph x <= 3")
        assert result.success
        assert result.parameters["boundary"] == 3
        assert result.parameters["operator"] == "<="
        assert result.parameters["is_inclusive"] is True
        assert result.parameters["direction"] == "left"

    def test_parse_unrecognized_fails(self):
        parser = SimpleQuestionParser()

        result = parser.parse("What is the meaning of life?")
        assert not result.success


class TestQuadraticTemplates:
    """Tests for quadratic templates."""

    def test_compute_quadratic_two_roots(self):
        # x² - 5x + 6 = 0 => x = 2, x = 3
        params = {"a": 1, "b": -5, "c": 6}
        derived = quadratics.compute_quadratic_derived(params)

        assert derived["discriminant"] == 1  # 25 - 24 = 1
        assert derived["num_roots"] == 2
        assert derived["root1"] == 3
        assert derived["root2"] == 2

    def test_compute_quadratic_one_root(self):
        # x² - 4x + 4 = 0 => x = 2 (double root)
        params = {"a": 1, "b": -4, "c": 4}
        derived = quadratics.compute_quadratic_derived(params)

        assert derived["discriminant"] == 0
        assert derived["num_roots"] == 1
        assert derived["root1"] == 2
        assert derived["root2"] == 2

    def test_compute_quadratic_no_real_roots(self):
        # x² + x + 1 = 0 => no real roots
        params = {"a": 1, "b": 1, "c": 1}
        derived = quadratics.compute_quadratic_derived(params)

        assert derived["discriminant"] < 0
        assert derived["num_roots"] == 0
        assert derived["root1"] is None
        assert derived["root2"] is None


class TestIntegration:
    """Integration tests for the full pipeline."""

    def test_full_pipeline_code_generation(self):
        """Test generating code from a question (no rendering)."""
        from math_content_engine.templates import TemplateEngine

        # Use simple parser to avoid needing API key
        engine = TemplateEngine(use_simple_parser=True)

        code, parse_result = engine.preview_code("Solve 4x + 8 = 20")

        assert parse_result.success
        assert parse_result.template_id == "linear_equation_graph"
        assert parse_result.parameters["a"] == 4
        assert parse_result.parameters["b"] == 8
        assert parse_result.parameters["c"] == 20
        assert parse_result.parameters["solution"] == 3

        # Check code is valid
        assert "from manim import *" in code
        assert "class LinearEquationGraphScene" in code
        assert "a, b, c = 4, 8, 20" in code
        assert "solution = 3" in code

    def test_list_templates(self):
        """Test listing all templates."""
        from math_content_engine.templates import TemplateEngine

        engine = TemplateEngine(use_simple_parser=True)
        templates = engine.list_templates()

        assert len(templates) >= 8  # We created at least 8 templates
        template_ids = [t.id for t in templates]
        assert "linear_equation_graph" in template_ids
        assert "slope_visualization" in template_ids
        assert "quadratic_graph" in template_ids

    def test_search_templates(self):
        """Test searching templates."""
        from math_content_engine.templates import TemplateEngine

        engine = TemplateEngine(use_simple_parser=True)

        results = engine.search_templates("slope")
        assert len(results) >= 2  # slope_visualization and slope_intercept_form

        results = engine.search_templates("quadratic")
        assert len(results) >= 2


class TestCodeValidation:
    """Test that generated code passes validation."""

    def test_linear_equation_code_validates(self):
        from math_content_engine.utils.validators import validate_manim_code
        from math_content_engine.templates import TemplateEngine

        engine = TemplateEngine(use_simple_parser=True)
        code, _ = engine.preview_code("Solve 2x + 5 = 11")

        result = validate_manim_code(code)
        assert result.is_valid, f"Validation errors: {result.errors}"

    def test_slope_code_validates(self):
        from math_content_engine.utils.validators import validate_manim_code
        from math_content_engine.templates import TemplateEngine

        engine = TemplateEngine(use_simple_parser=True)
        code, _ = engine.preview_code("Find slope between (0, 0) and (3, 6)")

        result = validate_manim_code(code)
        assert result.is_valid, f"Validation errors: {result.errors}"

    def test_inequality_code_validates(self):
        from math_content_engine.utils.validators import validate_manim_code
        from math_content_engine.templates import TemplateEngine

        engine = TemplateEngine(use_simple_parser=True)
        code, _ = engine.preview_code("Graph x > 3")

        result = validate_manim_code(code)
        assert result.is_valid, f"Validation errors: {result.errors}"
