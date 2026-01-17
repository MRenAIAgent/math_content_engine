"""Common prompt modification patterns."""

# Maps user intent keywords to prompt modifications
CHANGE_PATTERNS: dict[str, dict] = {
    # Timing/Pacing
    "slower": {
        "keywords": ["slower", "slow down", "more time", "longer", "pause", "wait"],
        "description": "Make animations slower with longer pauses",
        "suggestions": [
            "Use slow animation speed with longer durations",
            "Add 1-2 second pauses between each step",
            "Let each element fully appear before showing the next",
        ],
        "pacing": "slow",
    },
    "faster": {
        "keywords": ["faster", "speed up", "quicker", "shorter", "less time"],
        "description": "Speed up the animation",
        "suggestions": [
            "Use fast animation speed",
            "Minimize pauses between animations",
            "Show multiple elements simultaneously where possible",
        ],
        "pacing": "fast",
    },

    # Sequencing
    "sequential": {
        "keywords": ["one at a time", "sequential", "one by one", "step by step", "gradually"],
        "description": "Show elements one at a time",
        "suggestions": [
            "Animate elements one at a time, not simultaneously",
            "Show each element separately with a pause between",
            "Introduce concepts step by step",
        ],
    },
    "simultaneous": {
        "keywords": ["together", "at once", "simultaneous", "all at once"],
        "description": "Show multiple elements together",
        "suggestions": [
            "Animate multiple elements simultaneously",
            "Show related elements appearing together",
        ],
    },

    # Visual Style
    "more_color": {
        "keywords": ["color", "colorful", "colors", "vibrant", "bright"],
        "description": "Add more colors and visual variety",
        "suggestions": [
            "Use distinct colors for each element",
            "Add color transitions during transformations",
            "Use a vibrant color palette",
        ],
    },
    "highlight": {
        "keywords": ["highlight", "emphasize", "focus", "attention", "stand out"],
        "description": "Highlight important elements",
        "suggestions": [
            "Highlight key elements when they appear",
            "Use color or glow effects for emphasis",
            "Make important elements larger or brighter",
        ],
    },

    # Text and Labels
    "more_labels": {
        "keywords": ["label", "text", "annotate", "explain", "name", "title"],
        "description": "Add more text labels and annotations",
        "suggestions": [
            "Label all key elements clearly",
            "Add step-by-step annotations",
            "Include descriptive titles for each section",
        ],
    },
    "bigger_text": {
        "keywords": ["bigger text", "larger text", "larger font", "bigger font", "readable"],
        "description": "Make text larger and more readable",
        "suggestions": [
            "Use large font sizes for all text and labels",
            "Make equations and formulas bigger",
            "Ensure text is readable from a distance",
        ],
    },
    "show_formula": {
        "keywords": ["formula", "equation", "math", "expression", "show equation"],
        "description": "Display mathematical formulas",
        "suggestions": [
            "Display the main formula or equation",
            "Show the mathematical expression step by step",
            "Include the final equation at the end",
        ],
    },

    # Complexity
    "simpler": {
        "keywords": ["simpler", "simple", "basic", "minimal", "less", "clean"],
        "description": "Simplify the animation",
        "suggestions": [
            "Focus on the core concept only",
            "Remove decorative elements",
            "Use simple shapes and minimal text",
            "Keep the animation clean and uncluttered",
        ],
    },
    "more_detail": {
        "keywords": ["detail", "detailed", "more", "elaborate", "thorough", "complete"],
        "description": "Add more detail and explanation",
        "suggestions": [
            "Include intermediate steps in the explanation",
            "Add more visual details and annotations",
            "Show the complete derivation or proof",
        ],
    },

    # Animation Effects
    "draw_gradually": {
        "keywords": ["draw", "trace", "gradually", "construct", "build"],
        "description": "Draw shapes gradually instead of appearing instantly",
        "suggestions": [
            "Draw shapes gradually using Create animation",
            "Trace the outline before filling",
            "Build up the figure piece by piece",
        ],
    },
    "transform": {
        "keywords": ["transform", "morph", "change", "transition", "become"],
        "description": "Use transformation animations",
        "suggestions": [
            "Use Transform to morph between shapes",
            "Animate the transition between states",
            "Show how one form changes into another",
        ],
    },
    "fade": {
        "keywords": ["fade", "fade in", "fade out", "appear", "disappear"],
        "description": "Use fade animations",
        "suggestions": [
            "Use FadeIn for elements appearing",
            "Use FadeOut for elements disappearing",
            "Fade between different views",
        ],
    },

    # Camera/View
    "zoom": {
        "keywords": ["zoom", "zoom in", "zoom out", "close up", "focus on"],
        "description": "Zoom in or out on elements",
        "suggestions": [
            "Zoom in on important details",
            "Use camera movement to focus attention",
            "Start zoomed out, then zoom to details",
        ],
    },
    "move_camera": {
        "keywords": ["pan", "move view", "camera", "scroll", "shift view"],
        "description": "Move the camera view",
        "suggestions": [
            "Pan the camera to follow the action",
            "Move the view to show different parts",
            "Use smooth camera transitions",
        ],
    },

    # Specific Elements
    "show_axes": {
        "keywords": ["axes", "axis", "grid", "coordinate", "graph"],
        "description": "Show coordinate axes or grid",
        "suggestions": [
            "Include coordinate axes",
            "Show a grid background",
            "Label the x and y axes",
        ],
    },
    "show_numbers": {
        "keywords": ["numbers", "values", "calculate", "compute", "numeric"],
        "description": "Show numerical values",
        "suggestions": [
            "Display numerical values for measurements",
            "Show the calculation with actual numbers",
            "Include numeric labels on elements",
        ],
    },
}


def find_matching_patterns(user_request: str) -> list[dict]:
    """Find patterns that match the user's request.

    Args:
        user_request: What the user wants to change

    Returns:
        List of matching patterns with suggestions
    """
    user_request_lower = user_request.lower()
    matches = []

    for pattern_name, pattern_data in CHANGE_PATTERNS.items():
        for keyword in pattern_data["keywords"]:
            if keyword in user_request_lower:
                matches.append({
                    "name": pattern_name,
                    "description": pattern_data["description"],
                    "suggestions": pattern_data["suggestions"],
                    "pacing": pattern_data.get("pacing"),
                    "matched_keyword": keyword,
                })
                break  # Only match each pattern once

    return matches
