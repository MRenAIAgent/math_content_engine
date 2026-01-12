"""Tests for code validators."""

import pytest
from math_content_engine.utils.validators import validate_manim_code, validate_scene_name


class TestValidateManimCode:
    """Tests for validate_manim_code function."""

    def test_valid_code(self):
        """Test validation of valid Manim code."""
        code = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        text = Text("Hello")
        self.play(Write(text))
        self.wait()
'''
        result = validate_manim_code(code)
        assert result.is_valid
        assert len(result.errors) == 0

    def test_missing_import(self):
        """Test detection of missing manim import."""
        code = '''
class TestScene(Scene):
    def construct(self):
        self.play(Write(Text("Hello")))
'''
        result = validate_manim_code(code)
        assert not result.is_valid
        assert any("import" in e.lower() for e in result.errors)

    def test_missing_scene_class(self):
        """Test detection of missing Scene class."""
        code = '''
from manim import *

class TestAnimation:
    def construct(self):
        pass
'''
        result = validate_manim_code(code)
        assert not result.is_valid
        assert any("scene" in e.lower() for e in result.errors)

    def test_missing_construct_method(self):
        """Test detection of missing construct method."""
        code = '''
from manim import *

class TestScene(Scene):
    def run(self):
        self.play(Write(Text("Hello")))
'''
        result = validate_manim_code(code)
        assert not result.is_valid
        assert any("construct" in e.lower() for e in result.errors)

    def test_syntax_error(self):
        """Test detection of syntax errors."""
        code = '''
from manim import *

class TestScene(Scene)
    def construct(self):
        pass
'''
        result = validate_manim_code(code)
        assert not result.is_valid
        assert any("syntax" in e.lower() for e in result.errors)

    def test_warning_no_play(self):
        """Test warning when no self.play() calls."""
        code = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        text = Text("Hello")
'''
        result = validate_manim_code(code)
        # Should be valid but with warnings
        assert result.is_valid
        assert any("play" in w.lower() for w in result.warnings)

    def test_warning_no_wait(self):
        """Test warning when no self.wait() calls."""
        code = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        self.play(Write(Text("Hello")))
'''
        result = validate_manim_code(code)
        assert result.is_valid
        assert any("wait" in w.lower() for w in result.warnings)

    def test_empty_code(self):
        """Test handling of empty code."""
        result = validate_manim_code("")
        assert not result.is_valid
        assert any("empty" in e.lower() for e in result.errors)

    def test_input_detection(self):
        """Test detection of input() which would hang rendering."""
        code = '''
from manim import *

class TestScene(Scene):
    def construct(self):
        name = input("Enter name: ")
        self.play(Write(Text(name)))
'''
        result = validate_manim_code(code)
        assert not result.is_valid
        assert any("input" in e.lower() for e in result.errors)

    def test_threed_scene(self):
        """Test that ThreeDScene is accepted."""
        code = '''
from manim import *

class Test3DScene(ThreeDScene):
    def construct(self):
        axes = ThreeDAxes()
        self.play(Create(axes))
        self.wait()
'''
        result = validate_manim_code(code)
        assert result.is_valid


class TestValidateSceneName:
    """Tests for validate_scene_name function."""

    def test_valid_names(self):
        """Test valid Python identifiers."""
        assert validate_scene_name("TestScene")
        assert validate_scene_name("My_Scene")
        assert validate_scene_name("_PrivateScene")
        assert validate_scene_name("Scene123")

    def test_invalid_names(self):
        """Test invalid Python identifiers."""
        assert not validate_scene_name("123Scene")  # Starts with number
        assert not validate_scene_name("my-scene")  # Contains hyphen
        assert not validate_scene_name("my scene")  # Contains space
        assert not validate_scene_name("")  # Empty
