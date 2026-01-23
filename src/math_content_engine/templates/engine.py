"""
Template engine - main orchestrator for template-based video generation.
"""

import time
from pathlib import Path
from typing import Optional

from ..config import Config, VideoQuality
from ..llm.base import BaseLLMClient
from ..llm.factory import create_llm_client
from ..renderer.manim_renderer import ManimRenderer
from ..utils.validators import validate_manim_code

# Default paths for template engine
DEFAULT_OUTPUT_DIR = Path("./output")
DEFAULT_CACHE_DIR = Path("./.manim_cache")

from .base import ManimTemplate, ParseResult, TemplateGenerationResult
from .registry import TemplateRegistry, get_registry
from .question_parser import QuestionParserAgent, SimpleQuestionParser
from .renderer import TemplateRenderer


class TemplateEngine:
    """
    Main orchestrator for template-based math animation generation.

    Pipeline:
    1. Parse question → extract template_id and parameters
    2. Render template → generate Manim code
    3. Validate code → ensure it's valid Python/Manim
    4. Render video → execute Manim to create MP4/GIF

    Example:
        engine = TemplateEngine()
        result = engine.generate_from_question(
            question="Solve 3x + 5 = 14",
            output_filename="my_equation"
        )
        print(result.video_path)
    """

    def __init__(
        self,
        config: Optional[Config] = None,
        llm_client: Optional[BaseLLMClient] = None,
        registry: Optional[TemplateRegistry] = None,
        use_simple_parser: bool = False,
        output_dir: Optional[Path] = None,
        cache_dir: Optional[Path] = None,
        video_quality: VideoQuality = VideoQuality.MEDIUM,
    ):
        """
        Initialize the template engine.

        Args:
            config: Configuration (uses values from config if provided)
            llm_client: LLM client for question parsing (creates default if None)
            registry: Template registry (uses global if None)
            use_simple_parser: If True, use regex parser instead of LLM
            output_dir: Directory for output videos (defaults to ./output)
            cache_dir: Directory for Manim cache (defaults to ./.manim_cache)
            video_quality: Video quality preset
        """
        self.config = config
        self.registry = registry or get_registry()

        # Use config values if provided, otherwise use explicit args or defaults
        if config:
            self.output_dir = output_dir or config.output_dir
            self.cache_dir = cache_dir or config.manim_cache_dir
            self.video_quality = video_quality or config.video_quality
        else:
            self.output_dir = output_dir or DEFAULT_OUTPUT_DIR
            self.cache_dir = cache_dir or DEFAULT_CACHE_DIR
            self.video_quality = video_quality

        # LLM client (only needed if not using simple parser)
        self._llm_client = llm_client
        self.use_simple_parser = use_simple_parser

        # Initialize components
        self.simple_parser = SimpleQuestionParser()
        self.template_renderer = TemplateRenderer(registry=self.registry)
        self.manim_renderer = ManimRenderer(
            output_dir=self.output_dir,
            cache_dir=self.cache_dir,
            quality=self.video_quality,
        )

    @property
    def llm_client(self) -> BaseLLMClient:
        """Lazy-load LLM client only when needed."""
        if self._llm_client is None:
            self._llm_client = create_llm_client()
        return self._llm_client

    @property
    def question_parser(self) -> QuestionParserAgent:
        """Lazy-load question parser only when needed."""
        if not hasattr(self, '_question_parser'):
            self._question_parser = QuestionParserAgent(
                llm_client=self.llm_client,
                registry=self.registry,
            )
        return self._question_parser

    def generate_from_question(
        self,
        question: str,
        output_filename: Optional[str] = None,
        template_hint: Optional[str] = None,
        use_simple_parser: Optional[bool] = None,
    ) -> TemplateGenerationResult:
        """
        Generate a video from a math question.

        This is the main entry point. It:
        1. Parses the question to identify template and parameters
        2. Renders the template with extracted parameters
        3. Validates the generated code
        4. Renders the video

        Args:
            question: The math question (e.g., "Solve 3x + 5 = 14")
            output_filename: Output filename (without extension)
            template_hint: Optional hint for which template to use
            use_simple_parser: Override instance setting for parser type

        Returns:
            TemplateGenerationResult with video path and metadata
        """
        start_time = time.time()

        # Step 1: Parse the question
        use_simple = use_simple_parser if use_simple_parser is not None else self.use_simple_parser

        if use_simple:
            parse_result = self.simple_parser.parse(question, self.registry)
            # If simple parser fails, fall back to LLM
            if not parse_result.success:
                parse_result = self.question_parser.parse(question)
        else:
            parse_result = self.question_parser.parse(question)

        if not parse_result.success:
            return TemplateGenerationResult(
                success=False,
                error_message=f"Failed to parse question: {parse_result.error_message}",
            )

        # Apply template hint if provided
        if template_hint and template_hint in self.registry:
            parse_result.template_id = template_hint

        # Step 2: Render the template
        try:
            code, scene_name = self.template_renderer.render_from_parse_result(parse_result)
        except ValueError as e:
            return TemplateGenerationResult(
                success=False,
                template_id=parse_result.template_id,
                parameters=parse_result.parameters,
                error_message=f"Template rendering failed: {str(e)}",
            )

        # Step 3: Validate the generated code
        validation = validate_manim_code(code)
        if not validation.is_valid:
            return TemplateGenerationResult(
                success=False,
                template_id=parse_result.template_id,
                parameters=parse_result.parameters,
                code=code,
                scene_name=scene_name,
                error_message=f"Code validation failed: {validation.errors}",
            )

        # Step 4: Render the video
        render_result = self.manim_renderer.render(
            code=code,
            scene_name=scene_name,
            output_filename=output_filename,
        )

        render_time = time.time() - start_time

        if render_result.success:
            return TemplateGenerationResult(
                success=True,
                video_path=str(render_result.output_path) if render_result.output_path else None,
                template_id=parse_result.template_id,
                parameters=parse_result.parameters,
                code=code,
                scene_name=scene_name,
                render_time=render_time,
            )
        else:
            return TemplateGenerationResult(
                success=False,
                template_id=parse_result.template_id,
                parameters=parse_result.parameters,
                code=code,
                scene_name=scene_name,
                render_time=render_time,
                error_message=f"Manim rendering failed: {render_result.error_message}",
            )

    def generate_from_template(
        self,
        template_id: str,
        parameters: dict,
        output_filename: Optional[str] = None,
    ) -> TemplateGenerationResult:
        """
        Generate a video directly from template ID and parameters.

        Use this when you already know the template and parameters.

        Args:
            template_id: The template to use
            parameters: Parameter values
            output_filename: Output filename

        Returns:
            TemplateGenerationResult
        """
        start_time = time.time()

        # Render template
        try:
            code, scene_name = self.template_renderer.render(template_id, parameters)
        except ValueError as e:
            return TemplateGenerationResult(
                success=False,
                template_id=template_id,
                parameters=parameters,
                error_message=f"Template rendering failed: {str(e)}",
            )

        # Validate
        validation = validate_manim_code(code)
        if not validation.is_valid:
            return TemplateGenerationResult(
                success=False,
                template_id=template_id,
                parameters=parameters,
                code=code,
                scene_name=scene_name,
                error_message=f"Code validation failed: {validation.errors}",
            )

        # Render video
        render_result = self.manim_renderer.render(
            code=code,
            scene_name=scene_name,
            output_filename=output_filename,
        )

        render_time = time.time() - start_time

        if render_result.success:
            return TemplateGenerationResult(
                success=True,
                video_path=str(render_result.output_path) if render_result.output_path else None,
                template_id=template_id,
                parameters=parameters,
                code=code,
                scene_name=scene_name,
                render_time=render_time,
            )
        else:
            return TemplateGenerationResult(
                success=False,
                template_id=template_id,
                parameters=parameters,
                code=code,
                scene_name=scene_name,
                render_time=render_time,
                error_message=f"Manim rendering failed: {render_result.error_message}",
            )

    def preview_code(
        self,
        question: str,
        use_simple_parser: Optional[bool] = None,
    ) -> tuple[str, ParseResult]:
        """
        Parse a question and generate code without rendering.

        Useful for debugging or previewing what code will be generated.

        Args:
            question: The math question
            use_simple_parser: Override parser type

        Returns:
            Tuple of (generated_code, parse_result)
        """
        use_simple = use_simple_parser if use_simple_parser is not None else self.use_simple_parser

        if use_simple:
            parse_result = self.simple_parser.parse(question, self.registry)
            if not parse_result.success:
                parse_result = self.question_parser.parse(question)
        else:
            parse_result = self.question_parser.parse(question)

        if not parse_result.success:
            return "", parse_result

        code, _ = self.template_renderer.render_from_parse_result(parse_result)
        return code, parse_result

    def list_templates(self) -> list[ManimTemplate]:
        """Get all available templates."""
        return self.registry.list_all()

    def get_template(self, template_id: str) -> Optional[ManimTemplate]:
        """Get a specific template by ID."""
        return self.registry.get(template_id)

    def search_templates(self, query: str) -> list[ManimTemplate]:
        """Search templates by query."""
        return self.registry.search(query)

    def parse_question(self, question: str) -> ParseResult:
        """
        Just parse a question without generating code.

        Args:
            question: The math question

        Returns:
            ParseResult with template_id and parameters
        """
        if self.use_simple_parser:
            result = self.simple_parser.parse(question, self.registry)
            if not result.success:
                result = self.question_parser.parse(question)
            return result
        return self.question_parser.parse(question)
