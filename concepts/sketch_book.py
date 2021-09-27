""" sketch book """
from typing import List, Tuple # Dict, Union # Callable, Optional, TypeVar, Set
from .diagram import Diagram #, Morphism, Identity, Compose

class SketchBook:
    """ sketch book """
    def __init__(self):
        self.points: List[int] = []
        self.lines: List[Tuple[int, int, int]] = []
        self.sketch: Diagram = Diagram()
