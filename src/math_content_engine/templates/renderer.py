"""
Template renderer for filling Manim templates with parameters.
"""

import re
from typing import Optional

from .base import ManimTemplate, ParseResult
from .registry import TemplateRegistry, get_registry


class TemplateRenderer:
    """
    Renders Manim templates by filling in parameter values.
    """

    def __init__(self, registry: Optional[TemplateRegistry] = None):
        """
        Initialize the renderer.

        Args:
            registry: Template registry (uses global registry if None)
        """
        self.registry = registry or get_registry()

    def render(
        self,
        template_id: str,
        parameters: dict,
        validate: bool = True,
    ) -> tuple[str, str]:
        """
        Render a template with given parameters.

        Args:
            template_id: ID of the template to render
            parameters: Parameter values to fill in
            validate: Whether to validate parameters

        Returns:
            Tuple of (rendered_code, scene_name)

        Raises:
            ValueError: If template not found or validation fails
        """
        template = self.registry.get(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        # Compute derived parameters if needed
        if template.compute_derived:
            derived = template.compute_derived(parameters)
            # Merge, keeping explicit values over derived
            full_params = {**derived, **parameters}
            # But also add derived values for params not explicitly set
            for key, value in derived.items():
                if key not in parameters:
                    full_params[key] = value
            parameters = full_params

        # Add default values for optional parameters
        for spec in template.parameters:
            if spec.name not in parameters and spec.default is not None:
                parameters[spec.name] = spec.default

        # Validate if requested
        if validate:
            is_valid, errors = template.validate_params(parameters)
            if not is_valid:
                raise ValueError(f"Parameter validation failed: {errors}")

        # Render the template
        code = self._fill_template(template.template_code, parameters)

        # Extract scene name from rendered code
        scene_name = self._extract_scene_name(code)

        return code, scene_name

    def render_from_parse_result(
        self,
        result: ParseResult,
        validate: bool = True,
    ) -> tuple[str, str]:
        """
        Render a template from a ParseResult.

        Args:
            result: ParseResult from QuestionParserAgent
            validate: Whether to validate parameters

        Returns:
            Tuple of (rendered_code, scene_name)
        """
        if not result.success:
            raise ValueError(f"Cannot render failed parse result: {result.error_message}")

        return self.render(result.template_id, result.parameters, validate)

    def _fill_template(self, template_code: str, parameters: dict) -> str:
        """
        Fill template placeholders with parameter values.

        Handles:
        - Simple placeholders: {param}
        - Nested placeholders in f-strings
        - None values (converts to 'None')
        """
        code = template_code

        # Sort by key length descending to handle longer keys first
        # This prevents partial replacements (e.g., {x1} before {x})
        sorted_params = sorted(parameters.items(), key=lambda x: len(x[0]), reverse=True)

        for key, value in sorted_params:
            placeholder = "{" + key + "}"

            # Format value appropriately
            if value is None:
                formatted = "None"
            elif isinstance(value, bool):
                formatted = str(value)
            elif isinstance(value, float):
                # Keep integers as integers
                if value == int(value):
                    formatted = str(int(value))
                else:
                    formatted = str(value)
            elif isinstance(value, str):
                # Keep strings as-is for template insertion
                formatted = value
            else:
                formatted = str(value)

            code = code.replace(placeholder, formatted)

        return code

    def _extract_scene_name(self, code: str) -> str:
        """Extract the scene class name from rendered code."""
        match = re.search(r'class\s+(\w+)\s*\(\s*(?:Scene|ThreeDScene|MovingCameraScene)\s*\)', code)
        if match:
            return match.group(1)
        return "GeneratedScene"

    def preview(self, template_id: str, parameters: dict) -> str:
        """
        Preview what a rendered template would look like.

        Returns the rendered code without validation.
        """
        code, _ = self.render(template_id, parameters, validate=False)
        return code

    def get_required_params(self, template_id: str) -> list[str]:
        """Get list of required parameters for a template."""
        template = self.registry.get(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")
        return template.get_required_params()

    def get_param_info(self, template_id: str) -> dict:
        """
        Get detailed parameter information for a template.

        Returns dict with param names as keys and spec info as values.
        """
        template = self.registry.get(template_id)
        if not template:
            raise ValueError(f"Template '{template_id}' not found")

        return {
            spec.name: {
                "type": spec.param_type.value,
                "description": spec.description,
                "required": spec.required,
                "default": spec.default,
                "constraints": spec.constraints,
                "derived": spec.derived_from is not None,
            }
            for spec in template.parameters
        }
