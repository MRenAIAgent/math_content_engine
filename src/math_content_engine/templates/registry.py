"""
Template registry for managing and discovering Manim templates.
"""

from typing import Optional
from .base import ManimTemplate, TemplateCategory


class TemplateRegistry:
    """
    Registry for managing Manim animation templates.

    Provides template registration, lookup, and discovery functionality.
    """

    def __init__(self):
        self._templates: dict[str, ManimTemplate] = {}
        self._by_category: dict[TemplateCategory, list[str]] = {
            cat: [] for cat in TemplateCategory
        }
        self._by_tag: dict[str, list[str]] = {}

    def register(self, template: ManimTemplate) -> None:
        """
        Register a template in the registry.

        Args:
            template: Template to register

        Raises:
            ValueError: If template ID already exists
        """
        if template.id in self._templates:
            raise ValueError(f"Template '{template.id}' already registered")

        self._templates[template.id] = template
        self._by_category[template.category].append(template.id)

        for tag in template.tags:
            if tag not in self._by_tag:
                self._by_tag[tag] = []
            self._by_tag[tag].append(template.id)

    def get(self, template_id: str) -> Optional[ManimTemplate]:
        """Get a template by ID."""
        return self._templates.get(template_id)

    def get_by_category(self, category: TemplateCategory) -> list[ManimTemplate]:
        """Get all templates in a category."""
        return [self._templates[tid] for tid in self._by_category.get(category, [])]

    def get_by_tag(self, tag: str) -> list[ManimTemplate]:
        """Get all templates with a specific tag."""
        return [self._templates[tid] for tid in self._by_tag.get(tag, [])]

    def list_all(self) -> list[ManimTemplate]:
        """Get all registered templates."""
        return list(self._templates.values())

    def list_ids(self) -> list[str]:
        """Get all template IDs."""
        return list(self._templates.keys())

    def search(self, query: str) -> list[ManimTemplate]:
        """
        Search templates by name, description, or example questions.

        Args:
            query: Search query string

        Returns:
            List of matching templates, sorted by relevance
        """
        query_lower = query.lower()
        results = []

        for template in self._templates.values():
            score = 0

            # Check name match
            if query_lower in template.name.lower():
                score += 10

            # Check description match
            if query_lower in template.description.lower():
                score += 5

            # Check example questions
            for example in template.example_questions:
                if query_lower in example.lower():
                    score += 3

            # Check tags
            for tag in template.tags:
                if query_lower in tag.lower():
                    score += 2

            if score > 0:
                results.append((score, template))

        # Sort by score descending
        results.sort(key=lambda x: x[0], reverse=True)
        return [t for _, t in results]

    def get_template_descriptions(self) -> str:
        """
        Get formatted descriptions of all templates for LLM prompts.

        Returns:
            Formatted string describing all templates
        """
        lines = []
        for category in TemplateCategory:
            templates = self.get_by_category(category)
            if templates:
                lines.append(f"\n## {category.value.replace('_', ' ').title()}")
                for t in templates:
                    params = ", ".join(t.get_required_params())
                    lines.append(f"- **{t.id}**: {t.description}")
                    lines.append(f"  - Required parameters: {params}")
                    if t.example_questions:
                        lines.append(f"  - Examples: {'; '.join(t.example_questions[:2])}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return len(self._templates)

    def __contains__(self, template_id: str) -> bool:
        return template_id in self._templates


# Global registry instance
_global_registry: Optional[TemplateRegistry] = None


def get_registry() -> TemplateRegistry:
    """Get the global template registry, initializing if needed."""
    global _global_registry
    if _global_registry is None:
        _global_registry = TemplateRegistry()
        # Load built-in templates
        _load_builtin_templates(_global_registry)
    return _global_registry


def _load_builtin_templates(registry: TemplateRegistry) -> None:
    """Load all built-in templates into the registry."""
    from .definitions import linear_equations, graphing, quadratics, inequalities

    # Register all templates from definition modules
    for module in [linear_equations, graphing, quadratics, inequalities]:
        for template in module.get_templates():
            registry.register(template)
