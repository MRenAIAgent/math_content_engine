#!/usr/bin/env python3
"""
Enrich the algebra knowledge graph with additional metadata.

This script loads the existing knowledge graph JSON and enriches each concept with:
- grade_levels: Parsed from grade_level string to list format
- keywords: Tokenized from name, category, and description
- learning_objectives: Empty placeholder for future LLM enrichment
- common_misconceptions: Empty placeholder for future LLM enrichment
- subcategory: Derived from category or set to None

Usage:
    python scripts/enrich_knowledge_graph.py

Input:  curriculum/algebra1/algebra_knowledge_graph.json
Output: curriculum/algebra1/algebra_knowledge_graph_enriched.json
"""

import json
import re
from pathlib import Path
from typing import Any

# Common English stopwords to filter from keywords
STOPWORDS = frozenset({
    "a", "an", "the", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "been",
    "be", "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "must", "shall", "can", "need",
    "it", "its", "this", "that", "these", "those", "what", "which", "who",
    "how", "when", "where", "why", "if", "then", "than", "so", "such",
    "up", "down", "out", "into", "over", "under", "between", "through",
    "each", "all", "both", "few", "more", "most", "other", "some", "any",
    "no", "not", "only", "same", "just", "also", "very", "even", "still",
    "using", "use", "used", "find", "given", "give", "within", "without"
})

# Category to subcategory mapping
CATEGORY_SUBCATEGORY_MAP = {
    "Number Sense": {
        "counting": "Counting",
        "place value": "Place Value",
        "property": "Properties of Numbers",
        "commutative": "Properties of Numbers",
        "associative": "Properties of Numbers",
        "identity": "Properties of Numbers",
        "inverse": "Properties of Numbers",
        "multiplication": "Operations",
        "division": "Operations",
        "fraction": "Fractions",
        "decimal": "Decimals",
        "gcf": "Factors and Multiples",
        "lcm": "Factors and Multiples",
        "factor": "Factors and Multiples",
        "multiple": "Factors and Multiples",
        "integer": "Integers",
        "absolute": "Integers",
        "order of operations": "Order of Operations",
        "pemdas": "Order of Operations",
    },
    "Pre-Algebra": {
        "expression": "Expressions",
        "translate": "Expressions",
        "evaluate": "Expressions",
        "like terms": "Simplifying",
        "combine": "Simplifying",
        "distributive": "Simplifying",
        "equation": "Equations",
        "one-step": "Equations",
        "two-step": "Equations",
        "multi-step": "Equations",
        "proportion": "Ratios and Proportions",
        "rate": "Ratios and Proportions",
        "slope": "Ratios and Proportions",
        "coordinate": "Graphing",
        "plot": "Graphing",
        "distance": "Graphing",
    },
    "Linear": {
        "slope": "Slope",
        "slope-intercept": "Linear Forms",
        "point-slope": "Linear Forms",
        "standard form": "Linear Forms",
        "convert": "Linear Forms",
        "parallel": "Line Relationships",
        "perpendicular": "Line Relationships",
        "inequality": "Inequalities",
        "graph": "Graphing",
        "system": "Systems of Equations",
        "substitution": "Systems of Equations",
        "elimination": "Systems of Equations",
        "solution": "Systems of Equations",
    },
    "Exponential": {
        "product rule": "Exponent Rules",
        "power": "Exponent Rules",
        "zero exponent": "Exponent Rules",
        "negative exponent": "Exponent Rules",
        "fractional exponent": "Radicals",
        "root": "Radicals",
        "radical": "Radicals",
        "scientific notation": "Scientific Notation",
    },
    "Polynomials": {
        "add": "Polynomial Operations",
        "subtract": "Polynomial Operations",
        "multiply": "Polynomial Operations",
        "monomial": "Polynomial Operations",
        "binomial": "Polynomial Operations",
        "foil": "Polynomial Operations",
        "factor": "Factoring",
        "gcf": "Factoring",
        "trinomial": "Factoring",
        "difference of squares": "Special Products",
        "special product": "Special Products",
        "division": "Polynomial Division",
        "synthetic": "Polynomial Division",
    },
    "Quadratic": {
        "vertex": "Vertex Form",
        "standard form": "Standard Form",
        "completing the square": "Completing the Square",
        "quadratic formula": "Quadratic Formula",
        "discriminant": "Discriminant",
        "roots": "Solving Quadratics",
        "parabola": "Graphing Parabolas",
        "graph": "Graphing Parabolas",
    },
    "Function Tools": {
        "notation": "Function Basics",
        "evaluate": "Function Basics",
        "domain": "Domain and Range",
        "range": "Domain and Range",
        "composition": "Function Composition",
        "transformation": "Transformations",
        "shift": "Transformations",
        "reflection": "Transformations",
        "stretch": "Transformations",
    },
}

# Legacy concept ID mapping to structured equivalents
# These are the 9 legacy concepts with string IDs
LEGACY_CONCEPT_MAPPING = {
    "basic_arithmetic": {
        "note": "Legacy concept - maps to foundational Number Sense concepts (NS-01 through NS-07)",
        "related_structured_ids": ["NS-01", "NS-06", "NS-07"],
    },
    "integers": {
        "note": "Legacy concept - maps to Integer operations (NS-13, NS-14)",
        "related_structured_ids": ["NS-13", "NS-14"],
    },
    "fractions": {
        "note": "Legacy concept - maps to Fraction concepts (NS-08, NS-09)",
        "related_structured_ids": ["NS-08", "NS-09"],
    },
    "decimals": {
        "note": "Legacy concept - maps to Fraction-Decimal Conversion (NS-10)",
        "related_structured_ids": ["NS-10"],
    },
    "percentages": {
        "note": "Legacy concept - no direct structured equivalent; relates to decimal/fraction conversion",
        "related_structured_ids": ["NS-10"],
    },
    "algebra": {
        "note": "Legacy concept - maps to Pre-Algebra expression concepts (AT-17, AT-18, AT-21)",
        "related_structured_ids": ["AT-17", "AT-18", "AT-21"],
    },
    "linear_equations": {
        "note": "Legacy concept - maps to Linear equation concepts (AT-22 through AT-25, LF-30 through LF-40)",
        "related_structured_ids": ["AT-22", "AT-24", "AT-25", "LF-30", "LF-31"],
    },
    "quadratic_equations": {
        "note": "Legacy concept - maps to Quadratic concepts (Q-57 through Q-61)",
        "related_structured_ids": ["Q-57", "Q-58", "Q-59", "Q-60", "Q-61"],
    },
}


def parse_grade_level(grade_level_str: str) -> list[str]:
    """
    Parse grade_level string to a list of grade levels.

    Examples:
        "" -> []
        "7" -> ["grade_7"]
        "7-8" -> ["grade_7", "grade_8"]
        "K" -> ["grade_K"]
        "K-2" -> ["grade_K", "grade_1", "grade_2"]
    """
    if not grade_level_str or not grade_level_str.strip():
        return []

    grade_str = grade_level_str.strip()

    # Handle range like "7-8" or "K-2"
    if "-" in grade_str:
        parts = grade_str.split("-")
        if len(parts) != 2:
            return []

        start, end = parts[0].strip(), parts[1].strip()

        # Convert K to 0 for range calculation
        def grade_to_num(g: str) -> int:
            if g.upper() == "K":
                return 0
            try:
                return int(g)
            except ValueError:
                return -1

        def num_to_grade(n: int) -> str:
            if n == 0:
                return "grade_K"
            return f"grade_{n}"

        start_num = grade_to_num(start)
        end_num = grade_to_num(end)

        if start_num < 0 or end_num < 0 or start_num > end_num:
            return []

        return [num_to_grade(i) for i in range(start_num, end_num + 1)]

    # Single grade
    if grade_str.upper() == "K":
        return ["grade_K"]

    try:
        grade_num = int(grade_str)
        return [f"grade_{grade_num}"]
    except ValueError:
        return []


def tokenize_text(text: str) -> set[str]:
    """
    Tokenize text into lowercase words, filtering stopwords and short tokens.

    Handles:
    - Removes punctuation and special characters
    - Converts to lowercase
    - Filters stopwords
    - Filters tokens shorter than 2 characters
    - Filters purely numeric tokens
    """
    if not text:
        return set()

    # Replace special characters with spaces, keep alphanumeric
    cleaned = re.sub(r"[^a-zA-Z0-9\s]", " ", text)

    # Split and lowercase
    tokens = cleaned.lower().split()

    # Filter stopwords, short tokens, and purely numeric tokens
    keywords = {
        token for token in tokens
        if token not in STOPWORDS
        and len(token) >= 2
        and not token.isdigit()
    }

    return keywords


def generate_keywords(concept: dict[str, Any]) -> list[str]:
    """
    Generate keywords from concept name, category, and description.

    Returns a sorted, deduplicated list of keywords.
    """
    name = concept.get("name", "")
    category = concept.get("category", "")
    description = concept.get("description", "")

    # Combine all text sources
    all_text = f"{name} {category} {description}"

    # Tokenize and deduplicate
    keywords = tokenize_text(all_text)

    # Return sorted list for consistency
    return sorted(keywords)


def derive_subcategory(concept: dict[str, Any]) -> str | None:
    """
    Derive subcategory from category and concept details.

    Uses keyword matching against the CATEGORY_SUBCATEGORY_MAP.
    Returns None if no subcategory can be determined.
    """
    category = concept.get("category", "")

    if not category or category not in CATEGORY_SUBCATEGORY_MAP:
        return None

    subcategory_map = CATEGORY_SUBCATEGORY_MAP[category]

    # Combine name and description for matching
    name = concept.get("name", "").lower()
    description = concept.get("description", "").lower()
    combined = f"{name} {description}"

    # Check each keyword in the subcategory map
    for keyword, subcategory in subcategory_map.items():
        if keyword in combined:
            return subcategory

    return None


def is_legacy_concept(concept_id: str) -> bool:
    """Check if a concept ID is a legacy (non-structured) ID."""
    return concept_id in LEGACY_CONCEPT_MAPPING


def enrich_concept(concept: dict[str, Any]) -> dict[str, Any]:
    """
    Enrich a single concept with additional metadata.

    Adds:
    - grade_levels: Parsed from grade_level string
    - keywords: Generated from name, category, description
    - learning_objectives: Empty list placeholder
    - common_misconceptions: Empty list placeholder
    - subcategory: Derived from category or None
    - legacy_mapping: For legacy concepts, includes mapping info
    """
    enriched = concept.copy()

    # Parse grade_level to grade_levels list
    grade_level_str = concept.get("grade_level", "")
    enriched["grade_levels"] = parse_grade_level(grade_level_str)

    # Generate keywords
    enriched["keywords"] = generate_keywords(concept)

    # Add empty placeholders for future LLM enrichment
    enriched["learning_objectives"] = []
    enriched["common_misconceptions"] = []

    # Derive subcategory
    enriched["subcategory"] = derive_subcategory(concept)

    # Add legacy mapping info for legacy concepts
    concept_id = concept.get("id", "")
    if is_legacy_concept(concept_id):
        enriched["legacy_mapping"] = LEGACY_CONCEPT_MAPPING[concept_id]

    return enriched


def enrich_knowledge_graph(data: dict[str, Any]) -> dict[str, Any]:
    """
    Enrich the entire knowledge graph.

    Processes all concepts and preserves relationships.
    """
    enriched = {
        "name": data.get("name", ""),
        "concepts": [],
        "relationships": data.get("relationships", []),
        "metadata": {
            "enrichment_version": "1.0",
            "legacy_concept_ids": list(LEGACY_CONCEPT_MAPPING.keys()),
            "legacy_concept_mapping": LEGACY_CONCEPT_MAPPING,
        },
    }

    # Enrich each concept
    for concept in data.get("concepts", []):
        enriched_concept = enrich_concept(concept)
        enriched["concepts"].append(enriched_concept)

    return enriched


def main() -> None:
    """Main entry point for the enrichment script."""
    # Determine paths relative to this script's location
    script_dir = Path(__file__).parent
    repo_root = script_dir.parent

    input_path = repo_root / "curriculum" / "algebra1" / "algebra_knowledge_graph.json"
    output_path = repo_root / "curriculum" / "algebra1" / "algebra_knowledge_graph_enriched.json"

    # Load input JSON
    print(f"Loading knowledge graph from: {input_path}")
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Count concepts
    concept_count = len(data.get("concepts", []))
    legacy_count = sum(
        1 for c in data.get("concepts", [])
        if is_legacy_concept(c.get("id", ""))
    )
    structured_count = concept_count - legacy_count

    print(f"Found {concept_count} concepts ({structured_count} structured, {legacy_count} legacy)")

    # Enrich the knowledge graph
    print("Enriching concepts...")
    enriched_data = enrich_knowledge_graph(data)

    # Save output JSON
    print(f"Saving enriched knowledge graph to: {output_path}")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, indent=2, ensure_ascii=False)

    # Print summary
    print("\nEnrichment complete!")
    print(f"  - Added grade_levels to all concepts")
    print(f"  - Generated keywords for all concepts")
    print(f"  - Added empty learning_objectives placeholders")
    print(f"  - Added empty common_misconceptions placeholders")
    print(f"  - Derived subcategories where possible")
    print(f"  - Added legacy_mapping for {legacy_count} legacy concepts")
    print(f"  - Added metadata with legacy concept mapping")


if __name__ == "__main__":
    main()
