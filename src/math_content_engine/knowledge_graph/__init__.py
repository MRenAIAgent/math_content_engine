"""
Knowledge graph utilities.

This module hosts loaders and validation helpers for the shared concept graph
used to relate:
- templates/content (videos)
- textbooks/chapters
- exercises
"""

from .algebra import (
    get_default_algebra_knowledge_graph_path,
    load_algebra_knowledge_graph,
    build_concept_index,
    validate_concept_ids,
)
from .concept_extractor import (
    ConceptExtractor,
    ConceptExtractionResult,
    ExtractedConcept,
)

__all__ = [
    "get_default_algebra_knowledge_graph_path",
    "load_algebra_knowledge_graph",
    "build_concept_index",
    "validate_concept_ids",
    # Concept extraction
    "ConceptExtractor",
    "ConceptExtractionResult",
    "ExtractedConcept",
]

