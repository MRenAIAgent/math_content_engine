"""Tests for code extraction utilities."""

import pytest
from math_content_engine.utils.code_extractor import (
    extract_python_code,
    extract_class_name,
    extract_imports,
)


class TestExtractPythonCode:
    """Tests for extract_python_code function."""

    def test_extract_from_python_block(self):
        """Test extraction from ```python block."""
        text = '''Here is the code:

```python
from manim import *

class TestScene(Scene):
    def construct(self):
        pass
```

This code does XYZ.'''

        result = extract_python_code(text)
        assert "from manim import *" in result
        assert "class TestScene(Scene)" in result

    def test_extract_from_generic_block(self):
        """Test extraction from ``` block without language."""
        text = '''
```
from manim import *

class TestScene(Scene):
    def construct(self):
        self.play(Write(Text("Hello")))
```
'''
        result = extract_python_code(text)
        assert "from manim import *" in result
        assert "class TestScene" in result

    def test_raw_code_without_blocks(self):
        """Test handling of raw code without markdown blocks."""
        text = '''from manim import *

class TestScene(Scene):
    def construct(self):
        pass'''

        result = extract_python_code(text)
        assert "from manim import *" in result
        assert "class TestScene" in result

    def test_multiple_code_blocks(self):
        """Test that first relevant block is extracted."""
        text = '''
Here is some JavaScript:
```javascript
console.log("hello");
```

And here is the Manim code:
```python
from manim import *

class MainScene(Scene):
    def construct(self):
        pass
```
'''
        result = extract_python_code(text)
        assert "from manim import *" in result
        assert "console.log" not in result

    def test_strips_whitespace(self):
        """Test that result is stripped of excess whitespace."""
        text = '''```python

    from manim import *

```'''
        result = extract_python_code(text)
        assert result.startswith("from manim")


class TestExtractClassName:
    """Tests for extract_class_name function."""

    def test_extract_scene_class(self):
        """Test extraction of Scene class name."""
        code = '''
from manim import *

class PythagoreanTheorem(Scene):
    def construct(self):
        pass
'''
        assert extract_class_name(code) == "PythagoreanTheorem"

    def test_extract_threed_scene(self):
        """Test extraction of ThreeDScene class name."""
        code = '''
from manim import *

class My3DAnimation(ThreeDScene):
    def construct(self):
        pass
'''
        assert extract_class_name(code) == "My3DAnimation"

    def test_extract_moving_camera_scene(self):
        """Test extraction of MovingCameraScene class name."""
        code = '''
from manim import *

class CameraScene(MovingCameraScene):
    def construct(self):
        pass
'''
        assert extract_class_name(code) == "CameraScene"

    def test_no_scene_class(self):
        """Test handling of code without Scene class."""
        code = '''
from manim import *

class Helper:
    pass
'''
        assert extract_class_name(code) is None

    def test_multiple_classes(self):
        """Test that first Scene class is extracted."""
        code = '''
from manim import *

class Helper:
    pass

class FirstScene(Scene):
    def construct(self):
        pass

class SecondScene(Scene):
    def construct(self):
        pass
'''
        assert extract_class_name(code) == "FirstScene"


class TestExtractImports:
    """Tests for extract_imports function."""

    def test_extract_imports(self):
        """Test extraction of import statements."""
        code = '''
from manim import *
import numpy as np
from pathlib import Path

class TestScene(Scene):
    pass
'''
        imports = extract_imports(code)
        assert len(imports) == 3
        assert "from manim import *" in imports
        assert "import numpy as np" in imports

    def test_no_imports(self):
        """Test handling of code without imports."""
        code = '''
class TestScene(Scene):
    pass
'''
        imports = extract_imports(code)
        assert len(imports) == 0
