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
        self.sources = []
        self.sinks = []

    def __eq__(self, other):
        if isinstance(other, UCProgramGraph):
            return self.sources == other.sources and \
                    self.sinks == other.sinks and \
                    super.__eq__(self, other)
        
        return False

    def __str__(self):
        s = ''
        dfs_edges = nx.edge_dfs(self, source=self.sources[0])

        for e in dfs_edges:
            x = e[0]
            y = e[1]
            action = self.get_edge_data(*e)['action']
            s += f'{x} {y} => {action}\n'

        return s

    @classproperty
    def empty_graph(cls):
        return UCProgramGraph()

    def add_node(self, node, **attr):
        if node not in self.sources and attr['type'] == UCProgramGraph.NodeType.source:
            self.sources.append(node)
        if node not in self.sinks and attr['type'] == UCProgramGraph.NodeType.sink:
            self.sinks.append(node)

        if 'selector' not in attr:
            attr['selector'] = None

        return super().add_node(node, **attr)

    def remove_node(self, n):
        super().remove_node(n)

        if n in self.sources:
            self.sources.remove(n)
        if n in self.sinks:
            self.sinks.remove(n)

    @staticmethod
    def union(g, h):
        g_out = nx.union(g, h)
        g_out.sources = g.sources.copy()
        g_out.sinks = g.sinks.copy()
        g_out.sources.extend(h.sources.copy())
        g_out.sinks.extend(h.sinks.copy())

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
            g_out_sink_edges = list(g_out.in_edges(g_out.sinks, data=True))
            g_source_edges = list(g.out_edges(g.sources, data=True))

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
            g_out.remove_node(n)

        for n in g_source_del_list:
            if n not in sources_keep:
                g_out.sources.remove(n)
                g_out.nodes[n]['type'] = None

        return g_out

    def compute(self, ast, copy=True):
        node_id = 0

        def get_node_id(node):
            nonlocal node_id

            node_id += 1
            return f'{node_id}'

        def compute_aux(node):
            if isinstance(node, UCProgram):
                assert len(node.blocks) == 1
                return compute_aux(node.blocks[0])

            if isinstance(node, UCBlock):
                return compute_aux(node.stmts)

            if isinstance(node, UCStatements):
                assert len(node.stmts) > 0
                return UCProgramGraph.join(list(map(compute_aux, node.children)))

            if isinstance(node, UCStatement):
                if isinstance(node, UCAssignment):
                    qi = get_node_id(node)
                    qf = get_node_id(node)

                    g = UCProgramGraph.empty_graph
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(qf, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf, action=node)

                    return g

                if isinstance(node, UCCall):
                    qi = get_node_id(node)
                    qf = get_node_id(node)

                    g = UCProgramGraph.empty_graph
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(qf, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf, action=node)

                    return g

                if isinstance(node, UCIf):
                    if_expr = node.b_expr
                    if_body = node.block
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
                    g_if_body.nodes[g_if_body.sources[0]]['selector'] = 'if'

                    return UCProgramGraph.join([g, g_if_body])

                if isinstance(node, UCIfElse):
                    if_expr = node.b_expr
                    if_body = node.if_block
                    else_expr = UCNot(if_expr)
                    else_body = node.else_block

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

                    g_if_body.nodes[g_if_body.sources[0]]['selector'] = 'if'
                    g_else_body.nodes[g_else_body.sources[0]]['selector'] = 'else'
                    g_out = UCProgramGraph.join([g, g_if_body, g_else_body])

                    return g_out

                if isinstance(node, UCWhile):
                    while_expr = node.b_expr
                    while_body = node.block
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

                    if g_while_body != UCProgramGraph.empty_graph:
                        g_while_body.nodes[g_while_body.sources[0]]['selector'] = 'while'
                        for s in g_while_body.sinks:
                            g_while_body.nodes[s]['selector'] = 'while'

                    g_out = UCProgramGraph.join([g, g_while_body, g], sources_keep=[qi])

                    # Make the source node available again
                    g_out.nodes[qi]['selector'] = None

                    return g_out
                
            # Unreachable
            assert False

        g_out = compute_aux(ast)

        # Relabel
        nodes = list(map(str, sorted(list(map(int, g_out.nodes)))))

        nx.edge_dfs(g_out, source=g_out.sources[0])
        nx.relabel_nodes(g_out, {n_: str(n) for n_, n in zip(nodes, list(range(len(nodes))))}, copy=False)

        if copy:
            return g_out

        # TODO: Refactor with move semantics
        self.edges = g_out.edges
        self.nodes = g_out.nodes
        self.sources = g_out.sources
        self.sinks = g_out.sinks

    def draw(self, src_file):
        import os

        import graphviz as gv

        from pathlib import Path
        from networkx.drawing.nx_pydot import to_pydot

        for _, _, attr in self.edges(data=True):
            attr['label'] = attr['action']

        src_file = Path(src_file).name.split('.')[0]

        # Remove CFG files if existing
        try:
            os.remove(f'{src_file}.dot')
            os.remove(f'{src_file}.dot.png')
        except:
            pass
    
        # Generate .dot
        cfg_dot = to_pydot(self)
        cfg_dot.set('nodesep', 3)
        cfg_dot.write(f'{src_file}.dot', prog='dot')

        # Render CFG
        gv.render('dot', 'png', f'{src_file}.dot')