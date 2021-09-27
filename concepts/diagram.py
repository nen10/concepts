# pylint: disable=invalid-name
# pylint: disable=too-few-public-methods
# pylint: disable=arguments-differ
""" Calicuration of diagram """
from abc import ABC #, abstractmethod
from typing import List #, Optional, Tuple #, Dict, Union # Callable, TypeVar, Set
from enum import IntEnum, auto
import networkx as nx

class Shape(IntEnum):
    """ Drowing shape """
    Dot = auto()
    Round = auto()
    Commute = auto()
    Pullback = auto()
    Pushout = auto()
    Arrow = auto()
    Loop = auto()
    Inclusion = auto()
    Mono = auto()
    Epi = auto()
    Cannonical = auto()
    Equalizer = auto()
    Coequaliser = auto()

class ArrowParam(IntEnum):
    """ ArrowParam """
    Obj = -1
    Dom = 0
    Cod = 1
    Mor = 2

    def dual(self: 'ArrowParam') -> 'ArrowParam':
        """ dual """
        if self == ArrowParam.Obj:
            return ArrowParam.Obj
        if self == ArrowParam.Dom:
            return ArrowParam.Cod
        if self == ArrowParam.Cod:
            return ArrowParam.Dom
        if self == ArrowParam.Mor:
            return ArrowParam.Mor
        raise RuntimeError("Should not be reachable")

class ArrowKey:
    """ ArrowKey """
    def __init__(self, key:tuple, a: ArrowParam = ArrowParam.Mor):
        if a == a.Obj:
            self.dom = key[0]
            return
        self.dom = key[0]
        self.cod = key[1]
        self.key = key[2]
        self.mark = a

    def __eq__(self, other: object) -> bool:
        if self.__class__ == other.__class__:
            if self.mark != getattr(other, "mark"):
                return False
            if self.mark == ArrowParam.Mor:
                return (self.dom == getattr(other, "dom")
                    ) and (self.cod == getattr(other, "cod")
                    ) and (self.key == getattr(other, "key")
                    )
            if self.mark == ArrowParam.Obj:
                return self.dom == getattr(other, "dom")
        raise TypeError()

    def get_key(self) -> tuple:
        """ get_key """
        return (self.dom, self.cod, self.key)

    def as_dom(self) -> 'ArrowKey':
        """ as_dom """
        if self.mark == ArrowParam.Obj:
            return self
        return ArrowKey((self.dom,), ArrowParam.Obj)

    def as_cod(self) -> 'ArrowKey':
        """ as_cod """
        if self.mark == ArrowParam.Obj:
            return self
        return ArrowKey((self.cod,), ArrowParam.Obj)



class Diagram(nx.MultiDiGraph):
    """ Diagram """
    def __init__(self, incoming_graph_data=None, multigraph_input=None, **attr):
        super().__init__()

    def copy(self, as_view=False) -> 'Diagram':
        """ copy """
        return Diagram(super().copy(as_view))

    def has_target(self, key: ArrowKey, a: ArrowParam) -> bool:
        """ has_target """
        targets = list(self.edges) if a == a.Mor else list(self.nodes)
        target_id = key.get_key() if a == a.Mor else key.dom
        return target_id in targets


class DrowingConcept(ABC):
    """ DrowingConcept """
    def __init__(
        self,
        name: str,
        mark: ArrowParam
    ):
        self.name = name
        self.mark = mark
        self.drowings = {} # Diagram -> List[ArrowKey]
        self.properties: set[str] = set()

    def is_drown(self, fig: Diagram, as_key: ArrowKey, as_mark: ArrowParam = None) -> bool:
        """ is_drown """
        if as_key in self.drowings.get(fig, default=[]):
            return fig.has_target(as_key, self.mark if as_mark is None else as_mark)
        return False

    def save_key(self, fig: Diagram, key: ArrowKey):
        """ save_key """
        ids = self.drowings.get(fig, default=[])
        ids.append(key)
        self.drowings[fig] = ids

    def add_property(self, prop: str):
        """ add_property """
        self.properties.add(prop)


class Object(DrowingConcept):
    """ Object """
    def __init__(
        self,
        name: str,
    ):
        super().__init__(name, ArrowParam.Obj)
        self.shape = Shape.Dot

    def drow_concept(self, fig: Diagram, key: ArrowKey):
        """ drow_concept """
        if not self.is_drown(fig, key):
            fig.add_node(key.dom, name=self.name)
            self.save_key(fig, key)



class Morphism(DrowingConcept):
    """ Morphism """
    def __init__(
        self,
        name: str,
        domain: Object,
        codomain: Object,
    ):
        super().__init__(name, ArrowParam.Mor)
        self.shape = Shape.Arrow
        # memory : [edge_id, ...]
        # self.path = {}
        # # path :
        # #   {
        # #       edge_id: {domain: int, codomain: int, edge: int},
        # #       ...
        # #   }
        self.domain = domain
        self.codomain = codomain
        self.equations: set[Morphism] = set()
        self.equations.add(self)

    def drow_concept(self, fig: Diagram, key: ArrowKey):
        """ drow_concept """
        self.domain.drow_concept(fig, key.as_dom())
        self.codomain.drow_concept(fig, key.as_cod())

        if not self.is_drown(fig, key):
            fig.add_edge(*key.get_key(), name=self.name)
            self.save_key(fig, key)

    def get_name(self) -> str:
        """ get_name """
        return self.name

    def add_equation(self, mor: 'Morphism'):
        """ add_equation """
        u = self.equations.union(mor.equations)
        self.equations = u
        mor.equations = u

    def is_commutative(self, mor: 'Morphism') -> bool:
        """ is_commutative """
        return self in mor.equations
        # or ...


class Identity(Morphism):
    """ Identity """
    def __init__(
        self,
        obj: Object,
    ):
        super().__init__('id', obj, obj)
        self.add_property('id')
        # fig_id = max(list(self.memory)) + 1 if fig_id in self.used else fig_id

    def get_long_name(self) -> str:
        """ get_long_name """
        return f"id_{self.domain.name}"

class Compose(Morphism):
    """ Compose """
    def __init__(
        self,
        name: str,
        morphisms: List[Morphism],
    ):
        super().__init__(name, morphisms[0].domain, morphisms[-1].codomain)
        # fig_id = max(list(self.memory)) + 1 if fig_id in self.used else fig_id
        self.morphisms = morphisms
        self.factorized_drowings = {} # Diagram -> List[List[ArrowKey]]

        for n in range(len(morphisms) - 1):
            assert morphisms[n].codomain == morphisms[n + 1].domain

    def path_is_drown(self, fig: Diagram, compose_keys: List[ArrowKey]):
        """ path_is_drown """
        for d in self.factorized_drowings.get(fig, default=[]):
            if (*d,) == (*compose_keys,):
                return True
        return False

    def save_commutative_key(self, fig: Diagram, compose_keys: List[ArrowKey]):
        """ save_commutative_key """
        if not self.path_is_drown(fig, compose_keys):
            commute_ids = self.factorized_drowings.get(fig, default=[])
            commute_ids.append(compose_keys)

    def drow_path(self, fig: Diagram, compose_keys: List[ArrowKey]):
        """ drow_path """
        for i, mor in enumerate(self.morphisms):
            mor.drow_concept(fig, compose_keys[i])
        self.save_commutative_key(fig, compose_keys)

    def drow_composed(self, fig: Diagram, key: ArrowKey):
        """ drow_composed """
        if not self.is_drown(fig, key):
            fig.add_edge(*key.get_key(), name=self.name)
            self.save_key(fig, key)
            self.save_commutative_key(fig, [key])

    def drow_concept(self, fig: Diagram, key: ArrowKey, compose_keys: List[ArrowKey]):
        """ drow_concept """
        self.drow_path(fig, compose_keys)
        self.drow_composed(fig, key)

    def get_long_name(self) -> str:
        """ get_long_name """
        names = []
        for mor in self.morphisms:
            names.append(mor.name)
        return ';'.join(names)

    def has_key_as_factor(self, fig: Diagram, key: ArrowKey, a: ArrowParam = ArrowParam.Mor) -> bool:
        """ has_key_as_factor """
        if a == ArrowParam.Mor:
            for m in self.morphisms:
                for k in m.drowings.get(fig, default=[]):
                    if k == key:
                        return True
        else:
            for m in self.morphisms:
                for k in m.domain.drowings.get(fig, default=[]):
                    if k == key:
                        return True
            for k in self.codomain.drowings.get(fig, default=[]):
                if k == key:
                    return True
        return False

    def get_mor_by_key(self, fig: Diagram, key: ArrowKey):
        """ get_mor_by_key """
        for m in self.morphisms:
            for k in m.drowings.get(fig, default=[]):
                if k == key:
                    return m
        return None

class Commute(Morphism):
    """ Commute """
    def __init__(
        self,
        name: str,
        arrows: List[Compose],
        is_commute: bool = False
    ):
        super().__init__(name, arrows[0].domain, arrows[0].codomain)
        assert is_commute # commuteすることが保障されているものについてコンストラクトしなさい
        # for n in range(len(arrows) - 1):
        #     assert arrows[n].is_commutative(arrows[n+1])
        self.shape = Shape.Commute
        self.equations = set(arrows)
        self.paths = [compose_arrow.morphisms for compose_arrow in arrows]
        if len(arrows) == 1:
            self.paths.append([arrows[0]])
        self.add_property('commute')

class SubDiagram(Diagram):
    """ SubDiagram """
    def __init__(self, incoming_graph_data=None, multigraph_input=None, **attr):
        super().__init__()
        self.objects = {} # int -> Object
        self.morphisms = {} # ArrowKey -> Morphism
        self.commutations = {} # ArrowKey -> List[List[Morphism]]

    def copy(self, as_view=False) -> 'SubDiagram':
        """ copy """
        return SubDiagram(super().copy(as_view))

    def add_object(self, obj: Object, shared: bool = False) -> int:
        """ add_object """
        if shared:
            for k, v in self.objects:
                if v == obj:
                    return k
        k = max(list(self.nodes)) + 1
        obj.drow_concept(self, ArrowKey((k,), ArrowParam.Obj))
        self.objects[k] = obj
        return k

    def add_morphism(self, mor: Morphism, mor_shared: bool = False, dom_shared: bool = True, cod_shared: bool = True) -> ArrowKey:
        """ add_morphism """
        if mor_shared:
            for k, v in self.morphisms:
                if v == mor:
                    return k
        objs = [(dom_shared, mor.domain), (cod_shared, mor.codomain)]
        ids: List[int] = []
        for shared, obj in objs:
            ids.append(self.add_object(obj, shared))
        key = ArrowKey((ids[0], ids[1], self.new_edge_key(ids[0], ids[1])), ArrowParam.Mor)
        mor.drow_concept(self, key)
        self.morphisms[key] = mor
        return key

    def make_commutative_diagram(self, com: Commute) -> ArrowKey:
        """ add_commutation """
        mor_keys = []
        for mors in com.paths:
            l = len(mors) - 1
            i = 0
            for m in mors:
                mor_key = self.add_morphism(m, mor_shared=False, dom_shared=(i==0), cod_shared=(i==l))
                i += 1
                mor_keys.append(mor_key)
        key = self.add_morphism(com, mor_shared=False)
        self.commutations[key] = com
        return key

# class Mono(Morphism):
#     """ mono """
#     def __init__(
#         self,
#         name: str,
#         domain: Object,
#         codomain: Object,
#     ):
#         super().__init__(name, domain, codomain)
#         self.shape = Shape.Mono

#     def universality(self, com: Commute, name: str) -> Morphism:
#         represented = False
#         i = 0
#         unique = Compose(name, [self])
#         for p in com.paths:
#             if self.is_commutative(p[-1]):
#                 i += 1
#                 if not represented:
#                     unique = Compose(name, p[:-1])
#                     represented = True
#                 else:
#                     unique.equations.add(Compose(f"{name}_{i}", p[:-1]))
#         return None
