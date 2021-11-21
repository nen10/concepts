# pylint: disable=invalid-name
""" triality cycle puzzle """

from typing import List, Tuple, Dict, Union # Callable, Optional, TypeVar, Set
from enum import IntEnum, auto
import networkx as nx



class Color(IntEnum):
    """ node color """
    White = auto()
    Black = auto()
    Colours = auto()
    Red = auto()
    Green = auto()
    Blue = auto()
class ColorOrder(IntEnum):
    """ color order """
    Lighting = auto()
    Coloring = auto()
    RBG = auto()
    def get_relations(self, meta_order: ColorOrder = None) -> List[Tuple[Color, Color]]:
        """ order relations """
        if self == ColorOrder.Lighting:
            return [
                (Color.Black, Color.Colours),
                (Color.Colours, Color.White),
                (Color.White, Color.Black),
            ]
        if self == ColorOrder.Coloring:
            return [
                (Color.White, Color.Colours),
                (Color.Colours, Color.Black),
                (Color.Black, Color.White),
            ]
        if self == ColorOrder.RBG:
            ret = [
                (Color.Red, Color.Blue),
                (Color.Blue, Color.Green),
                (Color.Green, Color.Red),
            ]
            if meta_order is None:
                return ret
            for c in self.get_colourations():
                if meta_order == ColorOrder.Lighting:
                    ret.append((Color.Black, c))
                    ret.append((c, Color.White))
                if meta_order == ColorOrder.Coloring:
                    ret.append((Color.White, c))
                    ret.append((c, Color.Black))
        raise RuntimeError("Should not be reachable")

    def get_colourations(self) -> List[Color]:
        """ colourations """
        if self == ColorOrder.Lighting:
            return []
        if self == ColorOrder.Coloring:
            return []
        if self == ColorOrder.RBG:
            return [
                Color.Red,
                Color.Blue,
                Color.Green,
            ]
        raise RuntimeError("Should not be reachable")

class Observer(nx.MultiDiGraph):
    """ ruler of color ordering """
    def __init__(self, composer: ColorOrder, colouration: ColorOrder):
        super().__init__()
        self.composer = composer
        self.colourations = colouration.get_colourations()
        for r in colouration.get_relations(composer):
            self.add_edge(*r)
    
    def get_paintable_colors(self, base_color: Color, prev_color: Color = None) -> List[Color]:
        if prev_color is None:
            colourations = self.colourations
        else:
            colourations = [prev_color]
        ret = []
        for c in colourations:
            if self.has_edge(base_color, c):
                ret.append(c)
        return ret

class Stage(nx.MultiDiGraph):

            