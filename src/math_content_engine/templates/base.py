"""
Base dataclasses and types for the template system.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Optional


class TemplateCategory(Enum):
    """Categories of math animation templates."""
    LINEAR_EQUATIONS = "linear_equations"
    GRAPHING = "graphing"
    SYSTEMS = "systems"
    QUADRATICS = "quadratics"
    INEQUALITIES = "inequalities"
    NUMBER_LINE = "number_line"
    POLYNOMIALS = "polynomials"
    FACTORING = "factoring"


class ParamType(Enum):
    """Supported parameter types."""
    INT = "int"
    FLOAT = "float"
    STRING = "str"
    BOOL = "bool"
    LIST_INT = "list[int]"
    LIST_FLOAT = "list[float]"
    CHOICE = "choice"


@dataclass
class ParamSpec:
    """
    Specification for a template parameter.

    Attributes:
        name: Parameter name (used in template placeholders)
        param_type: Type of the parameter
        description: Human-readable description
        required: Whether the parameter is required
        default: Default value if not required
        constraints: Type-specific constraints (min, max, choices, etc.)
        derived_from: Formula to compute this param from others (e.g., "(c - b) / a")
    """
    name: str
    param_type: ParamType
    description: str
    required: bool = True
    default: Any = None
    constraints: dict = field(default_factory=dict)
    derived_from: Optional[str] = None

    def validate(self, value: Any) -> tuple[bool, Optional[str]]:
        """
        Validate a value against this parameter spec.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if self.required and self.default is None:
                return False, f"Parameter '{self.name}' is required"
            return True, None

        # Type validation
        if self.param_type == ParamType.INT:
            if not isinstance(value, int):
                return False, f"Parameter '{self.name}' must be an integer"
            if "min" in self.constraints and value < self.constraints["min"]:
                return False, f"Parameter '{self.name}' must be >= {self.constraints['min']}"
            if "max" in self.constraints and value > self.constraints["max"]:
                return False, f"Parameter '{self.name}' must be <= {self.constraints['max']}"

        elif self.param_type == ParamType.FLOAT:
            if not isinstance(value, (int, float)):
                return False, f"Parameter '{self.name}' must be a number"
            if "min" in self.constraints and value < self.constraints["min"]:
                return False, f"Parameter '{self.name}' must be >= {self.constraints['min']}"
            if "max" in self.constraints and value > self.constraints["max"]:
                return False, f"Parameter '{self.name}' must be <= {self.constraints['max']}"

        elif self.param_type == ParamType.CHOICE:
            if "choices" in self.constraints and value not in self.constraints["choices"]:
                return False, f"Parameter '{self.name}' must be one of {self.constraints['choices']}"

        elif self.param_type == ParamType.STRING:
            if not isinstance(value, str):
                return False, f"Parameter '{self.name}' must be a string"

        elif self.param_type == ParamType.BOOL:
            if not isinstance(value, bool):
                return False, f"Parameter '{self.name}' must be a boolean"

        return True, None


@dataclass
class ManimTemplate:
    """
    A parameterized Manim animation template.

    Attributes:
        id: Unique template identifier (e.g., "linear_equation_graph")
        name: Human-readable name
        category: Template category
        description: What this template visualizes
        parameters: List of parameter specifications
        template_code: Manim Python code with {placeholder} syntax
        example_questions: Sample questions this template can handle
        tags: Additional tags for search/matching
        compute_derived: Function to compute derived parameters
    """
    id: str
    name: str
    category: TemplateCategory
    description: str
    parameters: list[ParamSpec]
    template_code: str
    example_questions: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    compute_derived: Optional[Callable[[dict], dict]] = None

    def get_param_spec(self, name: str) -> Optional[ParamSpec]:
        """Get parameter specification by name."""
        for param in self.parameters:
            if param.name == name:
                return param
        return None

    def get_required_params(self) -> list[str]:
        """Get list of required parameter names."""
        return [p.name for p in self.parameters if p.required and p.derived_from is None]

    def get_derived_params(self) -> list[str]:
        """Get list of derived parameter names."""
        return [p.name for p in self.parameters if p.derived_from is not None]

    def validate_params(self, params: dict) -> tuple[bool, list[str]]:
        """
        Validate all parameters.

        Returns:
            Tuple of (all_valid, list_of_errors)
        """
        errors = []
        for spec in self.parameters:
            value = params.get(spec.name, spec.default)
            is_valid, error = spec.validate(value)
            if not is_valid:
                errors.append(error)
        return len(errors) == 0, errors

    def render(self, params: dict) -> str:
        """
        Render the template with given parameters.

        Args:
            params: Dictionary of parameter values

        Returns:
            Rendered Manim Python code
        """
        code = self.template_code
        for key, value in params.items():
            placeholder = "{" + key + "}"
            code = code.replace(placeholder, str(value))
        return code


@dataclass
class ParseResult:
    """
    Result of parsing a math question.

    Attributes:
        success: Whether parsing succeeded
        template_id: Matched template ID
        parameters: Extracted parameters
        confidence: Confidence score (0-1)
        error_message: Error message if parsing failed
        alternative_templates: Other possible template matches
    """
    success: bool
    template_id: Optional[str] = None
    parameters: dict = field(default_factory=dict)
    confidence: float = 0.0
    error_message: Optional[str] = None
    alternative_templates: list[str] = field(default_factory=list)


@dataclass
class TemplateGenerationResult:
    """
    Result of generating a video from a template.

    Attributes:
        success: Whether generation succeeded
        video_path: Path to the generated video
        template_id: Template that was used
        parameters: Parameters that were used
        code: Generated Manim code
        scene_name: Name of the Manim scene class
        render_time: Time taken to render
        error_message: Error message if failed
    """
    success: bool
    video_path: Optional[str] = None
    template_id: Optional[str] = None
    parameters: dict = field(default_factory=dict)
    code: str = ""
    scene_name: str = ""
    render_time: float = 0.0
    error_message: Optional[str] = None
