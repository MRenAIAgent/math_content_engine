"""
Textbook parser for extracting structured content from markdown files.

This module parses personalized textbook markdown files and extracts
examples, equations, and context that can be used to generate
matching animations.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict


@dataclass
class MathExample:
    """A single math example from the textbook."""
    title: str
    context: str  # The story/scenario
    equation: str  # The main equation to solve
    solution_steps: List[str]  # Step-by-step solution
    final_answer: str
    check_step: Optional[str] = None
    conclusion: Optional[str] = None  # Fun/thematic conclusion
    section: str = ""
    example_number: int = 0


@dataclass
class TextbookSection:
    """A section from the textbook (e.g., 2.1, 2.2)."""
    number: str  # e.g., "2.1"
    title: str
    learning_objectives: List[str]
    key_concepts: Dict[str, str]  # concept name -> explanation
    examples: List[MathExample]
    practice_problems: List[str]


@dataclass
class TextbookChapter:
    """A complete chapter from the textbook."""
    number: int
    title: str
    subtitle: Optional[str]  # e.g., "NBA Edition"
    theme: str  # e.g., "basketball"
    sections: List[TextbookSection]
    summary_points: List[str]
    fun_facts: List[str]


class TextbookParser:
    """
    Parses markdown textbook files into structured content.
    """

    def __init__(self, filepath: str):
        """
        Initialize parser with a textbook file.

        Args:
            filepath: Path to the markdown textbook file
        """
        self.filepath = Path(filepath)
        self.content = ""
        self.chapter: Optional[TextbookChapter] = None

    def parse(self) -> TextbookChapter:
        """Parse the textbook file and return structured content."""
        with open(self.filepath, 'r', encoding='utf-8') as f:
            self.content = f.read()

        # Extract chapter info
        chapter_num, chapter_title, subtitle, theme = self._parse_header()

        # Extract sections
        sections = self._parse_sections()

        # Extract summary and fun facts
        summary_points = self._parse_summary()
        fun_facts = self._parse_fun_facts()

        self.chapter = TextbookChapter(
            number=chapter_num,
            title=chapter_title,
            subtitle=subtitle,
            theme=theme,
            sections=sections,
            summary_points=summary_points,
            fun_facts=fun_facts
        )

        return self.chapter

    def _parse_header(self) -> tuple:
        """Extract chapter number, title, subtitle, and theme."""
        # Match: # Chapter 2: Title
        chapter_match = re.search(r'^# Chapter (\d+):\s*(.+)$', self.content, re.MULTILINE)
        chapter_num = int(chapter_match.group(1)) if chapter_match else 0
        chapter_title = chapter_match.group(2).strip() if chapter_match else "Unknown"

        # Match subtitle: ## 🏀 NBA Edition...
        subtitle_match = re.search(r'^## .+Edition.+$', self.content, re.MULTILINE)
        subtitle = subtitle_match.group(0).replace('## ', '').strip() if subtitle_match else None

        # Detect theme from content
        theme = self._detect_theme()

        return chapter_num, chapter_title, subtitle, theme

    def _detect_theme(self) -> str:
        """Detect the personalization theme from content."""
        content_lower = self.content.lower()
        if 'nba' in content_lower or 'basketball' in content_lower or 'curry' in content_lower:
            return 'basketball'
        elif 'gaming' in content_lower or 'xp' in content_lower or 'damage' in content_lower:
            return 'gaming'
        elif 'music' in content_lower or 'streaming' in content_lower or 'spotify' in content_lower:
            return 'music'
        elif 'soccer' in content_lower or 'football' in content_lower and 'nfl' not in content_lower:
            return 'soccer'
        return 'general'

    def _parse_sections(self) -> List[TextbookSection]:
        """Parse all sections from the textbook."""
        sections = []

        # Split by section headers (## 2.1, ## 2.2, etc.)
        section_pattern = r'^## (\d+\.\d+)\s+(.+)$'
        section_matches = list(re.finditer(section_pattern, self.content, re.MULTILINE))

        for i, match in enumerate(section_matches):
            section_num = match.group(1)
            section_title = match.group(2).strip()

            # Get content until next section or end
            start = match.end()
            end = section_matches[i + 1].start() if i + 1 < len(section_matches) else len(self.content)
            section_content = self.content[start:end]

            # Parse section components
            learning_objectives = self._parse_learning_objectives(section_content)
            key_concepts = self._parse_key_concepts(section_content)
            examples = self._parse_examples(section_content, section_num)
            practice_problems = self._parse_practice_problems(section_content)

            sections.append(TextbookSection(
                number=section_num,
                title=section_title,
                learning_objectives=learning_objectives,
                key_concepts=key_concepts,
                examples=examples,
                practice_problems=practice_problems
            ))

        return sections

    def _parse_learning_objectives(self, content: str) -> List[str]:
        """Extract learning objectives from section content."""
        objectives = []
        obj_match = re.search(r'### Learning Objectives\s*\n((?:- .+\n?)+)', content)
        if obj_match:
            obj_text = obj_match.group(1)
            objectives = [line.strip('- ').strip() for line in obj_text.strip().split('\n') if line.strip()]
        return objectives

    def _parse_key_concepts(self, content: str) -> Dict[str, str]:
        """Extract key concepts (definitions, properties)."""
        concepts = {}

        # Match **Concept Name** followed by explanation
        concept_pattern = r'\*\*([^*]+)\*\*\s*\n([^*\n]+(?:\n[^*\n#]+)*)'
        for match in re.finditer(concept_pattern, content):
            name = match.group(1).strip()
            explanation = match.group(2).strip()
            # Clean up the explanation
            explanation = re.sub(r'\n+', ' ', explanation).strip()
            concepts[name] = explanation

        return concepts

    def _parse_examples(self, content: str, section_num: str) -> List[MathExample]:
        """Extract all examples from section content."""
        examples = []

        # Find all example headers: **Example N: Title**
        example_header_pattern = r'\*\*Example (\d+):\s*([^*]+)\*\*'
        headers = list(re.finditer(example_header_pattern, content))

        for i, match in enumerate(headers):
            example_num = int(match.group(1))
            title = match.group(2).strip()

            # Get content until next example or section end
            start = match.end()
            if i + 1 < len(headers):
                end = headers[i + 1].start()
            else:
                # Find next section marker or practice problems
                next_section = re.search(r'\n### Practice Problems|\n---|\n## ', content[start:])
                end = start + next_section.start() if next_section else len(content)

            example_content = content[start:end].strip()

            example = self._parse_single_example(example_content, title, section_num, example_num)
            if example:
                examples.append(example)

        return examples

    def _parse_single_example(self, content: str, title: str, section: str, num: int) -> Optional[MathExample]:
        """Parse a single example's content."""
        # Split into context (before ```) and solution (inside ```)
        parts = content.split('```')

        if len(parts) < 2:
            return None

        context = parts[0].strip()
        solution_block = parts[1].strip() if len(parts) > 1 else ""

        # Extract equation from context (look for patterns like "Solve: equation" or "equation")
        equation = ""
        eq_match = re.search(r'[Ss]olve[:\s]+([^\n]+)', context)
        if eq_match:
            equation = eq_match.group(1).strip()
        else:
            # Look for equation patterns in context
            eq_match = re.search(r'(\d*[a-z]\s*[+\-*/=]\s*[\d\-]+\s*[=<>≤≥]\s*[\d\-]+)', context)
            if eq_match:
                equation = eq_match.group(1).strip()

        # Parse solution steps
        solution_lines = [line.strip() for line in solution_block.split('\n') if line.strip()]
        solution_steps = []
        final_answer = ""
        check_step = None
        conclusion = None

        for line in solution_lines:
            if line.startswith('Check:'):
                check_step = line
            elif '=' in line and not any(op in line for op in ['✓', '✗', 'FALSE', 'TRUE']):
                solution_steps.append(line)
                # Track last "x = " or "y = " as final answer
                if re.match(r'^[a-z]\s*=\s*[\d\-]+', line):
                    final_answer = line
            elif '✓' in line or '✗' in line or 'solution' in line.lower():
                conclusion = line

        # Get conclusion from after the code block if exists
        if len(parts) > 2:
            after_code = parts[2].strip()
            if after_code and not conclusion:
                conclusion = after_code.split('\n')[0]

        return MathExample(
            title=title,
            context=context,
            equation=equation,
            solution_steps=solution_steps,
            final_answer=final_answer,
            check_step=check_step,
            conclusion=conclusion,
            section=section,
            example_number=num
        )

    def _parse_practice_problems(self, content: str) -> List[str]:
        """Extract practice problems from section."""
        problems = []

        # Find practice section
        practice_match = re.search(r'### Practice Problems[^\n]*\n((?:.+\n?)+?)(?=\n---|\n##|$)', content)
        if practice_match:
            practice_text = practice_match.group(1)
            # Extract individual problems
            for line in practice_text.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('a)') or line.startswith('b)')):
                    problems.append(line)

        return problems

    def _parse_summary(self) -> List[str]:
        """Extract summary/key takeaways."""
        summary = []
        # Find the Key Takeaways section
        start_match = re.search(r'### Key Takeaways', self.content)
        if start_match:
            start = start_match.end()
            # Find the next section header
            end_match = re.search(r'\n###|\n##|\n---', self.content[start:])
            end = start + end_match.start() if end_match else len(self.content)
            section_text = self.content[start:end]

            for line in section_text.split('\n'):
                line = line.strip()
                if line and (line.startswith('-') or (line and line[0].isdigit())):
                    summary.append(line.lstrip('- 0123456789.').strip())
        return summary

    def _parse_fun_facts(self) -> List[str]:
        """Extract fun facts."""
        facts = []
        # Find the Famous Facts section
        start_match = re.search(r'### Famous .+ Facts', self.content)
        if start_match:
            start = start_match.end()
            # Find the next section header
            end_match = re.search(r'\n###|\n##|\n---', self.content[start:])
            end = start + end_match.start() if end_match else len(self.content)
            section_text = self.content[start:end]

            for line in section_text.split('\n'):
                line = line.strip()
                if line and line.startswith('-'):
                    facts.append(line.lstrip('- ').strip())
        return facts

    def get_examples_for_animation(self) -> List[Dict]:
        """
        Get examples formatted for animation generation.

        Returns:
            List of dicts with 'topic', 'requirements', 'context' for each example
        """
        if not self.chapter:
            self.parse()

        animation_specs = []

        for section in self.chapter.sections:
            for example in section.examples:
                # Build comprehensive requirements from textbook content
                requirements = f"""
## TEXTBOOK EXAMPLE - Use This Exact Content

**Title:** {example.title}

**Story/Context:**
{example.context}

**Equation to Solve:** {example.equation}

**Solution Steps (show each step):**
{chr(10).join(f"  {i+1}. {step}" for i, step in enumerate(example.solution_steps))}

**Final Answer:** {example.final_answer}

**Verification:** {example.check_step or 'Show check step'}

**Conclusion:** {example.conclusion or 'Confirm the solution'}

### Animation Requirements:
1. Start with the title "{example.title}"
2. Show the basketball/themed context clearly
3. Display the equation prominently
4. Animate each solution step one by one
5. Highlight the final answer
6. Show the verification step
7. End with the themed conclusion

Use {self.chapter.theme.upper()} colors and visual style.
Reference the exact players/scenarios from the textbook.
"""
                animation_specs.append({
                    'section': section.number,
                    'example_num': example.example_number,
                    'topic': f"{example.title} - {section.title}",
                    'requirements': requirements,
                    'theme': self.chapter.theme,
                    'equation': example.equation,
                    'context': example.context,
                })

        return animation_specs


def parse_textbook(filepath: str) -> TextbookChapter:
    """
    Convenience function to parse a textbook file.

    Args:
        filepath: Path to markdown textbook

    Returns:
        Parsed TextbookChapter
    """
    parser = TextbookParser(filepath)
    return parser.parse()


def get_animation_specs_from_textbook(filepath: str) -> List[Dict]:
    """
    Get animation specifications from a textbook file.

    Args:
        filepath: Path to markdown textbook

    Returns:
        List of animation specification dicts
    """
    parser = TextbookParser(filepath)
    parser.parse()
    return parser.get_examples_for_animation()
