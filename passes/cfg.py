"""Micro-C Control-flow/Program Graph Generation"""
import networkx as nx

from lang.ast   import *
from lang.types import *
from lang.ops   import *

from functools import reduce

class classproperty(property):
    def __get__(self, cls, owner):
        return classmethod(self.fget).__get__(None, owner)()

class UCGraphNode:
    """Micro-C Graph Node"""
    def __init__(self, label):
        self.label = label

    def __eq__(self, other):
        if isinstance(other, UCGraphNode):
            return self.label == other.label
        return False

    def __hash__(self):
        return hash(self.label)

    def __str__(self):
        return self.label

class UCGraphEdge:
    """Micro-C Graph Edge"""
    def __init__(self, x, y, label):
        self.x = x
        self.y = y
        self.label = label

    def __eq__(self, other):
        if isinstance(other, UCGraphEdge):
            return self.x == other.x and \
                    self.y == other.y and \
                    self.label == other.label
        return False
    
    def __hash__(self):
        return hash((self.x, self.y, self.label,))

    def __str__(self):
        return f'({self.x}, {self.y}, {self.label})'

class UCProgramGraph(nx.DiGraph):
    class NodeType:
        source = 'source'
        sink   = 'sink'

    def __init__(self, data=None, **attr):
        super().__init__(data, **attr)
        self.sources = {}
        self.sinks = {}

    def __eq__(self, other):
        if isinstance(other, UCProgramGraph):
            return self.sources == other.sources and \
                    self.sinks == other.sinks and \
                    super.__eq__(self, other)
        
        return False

    def __str__(self):
        s = ''
        dfs_edges = nx.edge_dfs(self, source=self.sources_keys[0])

        for e in dfs_edges:
            x = e[0]
            y = e[1]
            action = self.get_edge_data(*e)['action']
            s += f'{x} {y} => {action}\n'

        return s

    @property
    def sources_keys(self):
        return list(self.sources.keys())

    @property
    def sinks_keys(self):
        return list(self.sinks.keys())

    @property
    def sources_values(self):
        return reduce(lambda x, y: x + y, list(self.sources.values()), [])

    @property
    def sinks_values(self):
        return reduce(lambda x, y: x + y, list(self.sinks.values()), [])

    @classproperty
    def empty_graph(cls):
        return UCProgramGraph()

    def add_node(self, node, **attr):
        if node not in self.sources and attr['type'] == UCProgramGraph.NodeType.source:
            self.sources[node] = []
        if node not in self.sinks and attr['type'] == UCProgramGraph.NodeType.sink:
            self.sinks[node] = []

        if 'selector' not in attr:
            attr['selector'] = None

        return super().add_node(node, **attr)

    def add_edge(self, u, v, **attr):
        if u in self.sources:
            self.sources[u].append((u, v, attr,))
        if v in self.sinks:
            self.sinks[v].append((u, v, attr,))

        return super().add_edge(u, v, **attr)

    def remove_edge(self, u, v):
        e = (u, v, self.edges[(u, v)],)

        if u in self.sources and e in self.sources[u]:
            self.sources[u].remove(e)
        if v in self.sinks and e in self.sinks[v]:
            self.sinks[v].remove(e)

        return super().remove_edge(u, v)

    @staticmethod
    def union(g, h):
        g_out = nx.union(g, h)
        g_out.sources = g.sources.copy()
        g_out.sinks = g.sinks.copy()
        g_out.sources.update(h.sources)
        g_out.sinks.update(h.sinks)

        return g_out

    @staticmethod
    def try_union(g, h):
        try:
            return UCProgramGraph.union(g, h)
        except:
            return None

    @staticmethod
    def join(gs, sources_keep=None):
        if len(gs) == 0:
            return UCProgramGraph.empty_graph

        if sources_keep == None:
            sources_keep = []

        g_out = gs[0]

        g_out_sink_del_list = []
        g_source_del_list = []

        for g in gs[1:]:
            g_out_sink_edges = g_out.sinks_values
            g_source_edges = g.sources_values

            g_out_ = UCProgramGraph.try_union(g_out, g)

            if g_out_ != None:
                g_out = g_out_

            for u, v, attr_uv in g_out_sink_edges:
                for x, _, _ in g_source_edges:
                    if g_out.nodes[v]['selector'] == g.nodes[x]['selector']:
                        if g_out.has_edge(u, v):
                            g_out.remove_edge(u, v)
                            g_out_sink_del_list.append(v)

                        g_out.add_edge(u, x, **attr_uv)

                        if x not in g_source_del_list:
                            g_source_del_list.append(x)
            
        for n in g_out_sink_del_list:
            del g_out.sinks[n]
        for n in g_source_del_list:
            if n not in sources_keep:
                del g_out.sources[n]

        return g_out

    def compute(self, ast, copy=True):
        node_id = 0

        def get_node_id(node):
            nonlocal node_id

            node_id += 1
            return f'{id(node)}:{node_id}'

        def compute_aux(node):
            if isinstance(node, UCProgram):
                assert len(node.children) == 1
                return compute_aux(node.children[0])

            if isinstance(node, UCBlock):
                gs = []
           
                for node_ in node.children:
                   gs.append(compute_aux(node_))

                return UCProgramGraph.join(gs)
    
            if isinstance(node, UCDeclarations):
                gs = []

                for node_ in node.children:
                    gs.append(compute_aux(node_))

                return UCProgramGraph.join(gs)

            if isinstance(node, UCStatements):
                gs = []

                for node_ in node.children:
                    gs.append(compute_aux(node_))

                return UCProgramGraph.join(gs)

            if isinstance(node, UCDeclaration):
                qi = get_node_id(node)
                qf = get_node_id(node)

                g = UCProgramGraph.empty_graph
                g.add_node(qi, type=UCProgramGraph.NodeType.source)
                g.add_node(qf, type=UCProgramGraph.NodeType.sink)
                g.add_edge(qi, qf, action=node)

                return g

            if isinstance(node, UCStatement):
                if isinstance(node, UCAssignment):
                    qi = get_node_id(node)
                    qf = get_node_id(node)

                    g = UCProgramGraph.empty_graph
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(qf, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf, action=node)

                    return g

                if isinstance(node, UCIf):
                    if_expr = node.children[0]
                    if_body = node.children[1]
                    not_if_expr = UCNot(if_expr)

                    qi = get_node_id(node)
                    qf_if = get_node_id(if_expr)
                    qf_not_if = get_node_id(not_if_expr)

                    g = UCProgramGraph.empty_graph
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(qf_if, type=UCProgramGraph.NodeType.sink, selector='if')
                    g.add_node(qf_not_if, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf_if, action=if_expr)
                    g.add_edge(qi, qf_not_if, action=not_if_expr)

                    g_if_body = compute_aux(if_body)
                    g_if_body.nodes[g_if_body.sources_keys[0]]['selector'] = 'if'

                    return UCProgramGraph.join([g, g_if_body])

                if isinstance(node, UCIfElse):
                    if_expr = node.children[0]
                    if_body = node.children[1]
                    else_expr = UCNot(if_expr)
                    else_body = node.children[2]

                    qi = get_node_id(node)
                    qf_if = get_node_id(if_expr)
                    qf_else = get_node_id(else_expr)

                    g = UCProgramGraph.empty_graph
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(qf_if, type=UCProgramGraph.NodeType.sink, selector='if')
                    g.add_node(qf_else, type=UCProgramGraph.NodeType.sink, selector='else')
                    g.add_edge(qi, qf_if, action=if_expr)
                    g.add_edge(qi, qf_else, action=else_expr)

                    g_if_body = compute_aux(if_body)
                    g_else_body = compute_aux(else_body)

                    g_if_body.nodes[g_if_body.sources_keys[0]]['selector'] = 'if'
                    g_else_body.nodes[g_else_body.sources_keys[0]]['selector'] = 'else'

                    return UCProgramGraph.join([g, g_if_body, g_else_body])

                if isinstance(node, UCWhile):
                    while_expr = node.children[0]
                    while_body = node.children[1]
                    not_while_expr = UCNot(while_expr)

                    qi = get_node_id(node)
                    qf_while = get_node_id(while_expr)
                    qf_not_while = get_node_id(not_while_expr)

                    g = UCProgramGraph.empty_graph
                    g.add_node(qi, type=UCProgramGraph.NodeType.source, selector='while')
                    g.add_node(qf_while, type=UCProgramGraph.NodeType.sink, selector='while')
                    g.add_node(qf_not_while, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf_while, action=while_expr)
                    g.add_edge(qi, qf_not_while, action=not_while_expr)

                    g_while_body = compute_aux(while_body)
                    if g_while_body == UCProgramGraph.empty_graph:
                        g_while_body.nodes[g_while_body.sources_keys[0]]['selector'] = 'while'
                        g_while_body.nodes[g_while_body.sinks_keys[0]]['selector'] = 'while'
                    g_out = UCProgramGraph.join([g, g_while_body, g], sources_keep=[qi])

                    # Make the source node available again
                    g_out.nodes[qi]['selector'] = None

                    return g_out
                
            # Unreachable
            assert False

        g_out = compute_aux(ast)

        if copy:
            return g_out

        # TODO: Refactor with move semantics
        self.edges = g_out.edges
        self.nodes = g_out.nodes
        self.sources = g_out.sources
        self.sinks = g_out.sinks
