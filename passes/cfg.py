"""Micro-C Control-flow/Program Graph Generation"""
import networkx as nx

from lang.ast import *
from lang.types import *
from lang.ops import *

from utils.decorators import classproperty


class UCProgramGraph(nx.DiGraph):
    class NodeType:
        source = 'source'
        sink = 'sink'

    def __init__(self, data=None, **attr):
        super().__init__(data, **attr)

        self.sources = []
        self.sinks = []
        self.vars = {}

    @classproperty
    def empty(cls):
        return UCProgramGraph()

    @property
    def source(self):
        return self.sources[0] if len(self.sources) > 0 else None

    @property
    def sink(self):
        return self.sinks[0] if len(self.sinks) > 0 else None

    def reverse(self, copy=True):
        reversed = super().reverse(copy=copy)

        sources_tmp = self.sources
        reversed.sources = self.sinks.copy() if copy else self.sinks
        reversed.sinks = sources_tmp.copy() if copy else sources_tmp
        reversed.vars = self.vars.copy() if copy else self.vars

        return reversed

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
        g_out.vars = g.vars.copy()
        g_out.sources.extend(h.sources.copy())
        g_out.sinks.extend(h.sinks.copy())
        g_out.vars.update(h.vars)

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
            return UCProgramGraph.empty

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

    def stitch_sinks(self):
        sink_remove_list = []
        edge_add_list = []

        for sink in self.sinks[1:]:
            for u in self.predecessors(sink):
                attrs = self.edges[(u, sink)]
                sink_remove_list.append(sink)
                edge_add_list.append((u, self.sink, attrs,))

        for sink in sink_remove_list:
            self.remove_node(sink)
        for u, v, attrs in edge_add_list:
            self.add_edge(u, v, **attrs)

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
                stmts_g = compute_aux(node.stmts)

                # Stitch sinks
                if not isinstance(node, UCNestedBlock):
                    stmts_g.stitch_sinks()

                return UCProgramGraph.union(compute_aux(node.decls), stmts_g)

            if isinstance(node, UCDeclarations):
                return UCProgramGraph.join(list(map(compute_aux, node.decls)))

            if isinstance(node, UCStatements):
                assert len(node.stmts) > 0
                return UCProgramGraph.join(list(map(compute_aux, node.stmts)))

            if isinstance(node, UCDeclaration):
                g = UCProgramGraph.empty
                g.vars[node.id] = node

                return g

            if isinstance(node, UCStatement):
                if isinstance(node, UCAssignment):
                    qi = get_node_id(node)
                    qf = get_node_id(node)

                    g = UCProgramGraph.empty
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(qf, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf, action=node)

                    return g

                if isinstance(node, UCCall):
                    qi = get_node_id(node)
                    qf = get_node_id(node)

                    g = UCProgramGraph.empty
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

                    g = UCProgramGraph.empty
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(
                        qf_if, type=UCProgramGraph.NodeType.sink, selector='if')
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

                    g = UCProgramGraph.empty
                    g.add_node(qi, type=UCProgramGraph.NodeType.source)
                    g.add_node(
                        qf_if, type=UCProgramGraph.NodeType.sink, selector='if')
                    g.add_node(
                        qf_else, type=UCProgramGraph.NodeType.sink, selector='else')
                    g.add_edge(qi, qf_if, action=if_expr)
                    g.add_edge(qi, qf_else, action=else_expr)

                    g_if_body = compute_aux(if_body)
                    g_else_body = compute_aux(else_body)

                    g_if_body.nodes[g_if_body.sources[0]]['selector'] = 'if'
                    g_else_body.nodes[g_else_body.sources[0]
                                      ]['selector'] = 'else'
                    g_out = UCProgramGraph.join([g, g_if_body, g_else_body])

                    return g_out

                if isinstance(node, UCWhile):
                    while_expr = node.b_expr
                    while_body = node.block
                    not_while_expr = UCNot(while_expr)

                    qi = get_node_id(node)
                    qf_while = get_node_id(while_expr)
                    qf_not_while = get_node_id(not_while_expr)

                    g = UCProgramGraph.empty
                    g.add_node(
                        qi, type=UCProgramGraph.NodeType.source, selector='while')
                    g.add_node(
                        qf_while, type=UCProgramGraph.NodeType.sink, selector='while')
                    g.add_node(qf_not_while, type=UCProgramGraph.NodeType.sink)
                    g.add_edge(qi, qf_while, action=while_expr)
                    g.add_edge(qi, qf_not_while, action=not_while_expr)

                    g_while_body = compute_aux(while_body)

                    if g_while_body != UCProgramGraph.empty:
                        g_while_body.nodes[g_while_body.sources[0]
                                           ]['selector'] = 'while'
                        for s in g_while_body.sinks:
                            g_while_body.nodes[s]['selector'] = 'while'

                    g_out = UCProgramGraph.join(
                        [g, g_while_body, g], sources_keep=[qi])

                    # Make the source node available again
                    g_out.nodes[qi]['selector'] = None

                    return g_out

            return UCProgramGraph.empty

        g_out = compute_aux(ast)

        # Relabel
        nodes = list(map(str, sorted(list(map(int, g_out.nodes)))))
        nodes = list(
            filter(lambda n: n not in g_out.sources + g_out.sinks, nodes))

        relabel_map = {g_out.sources[0]: '▷', g_out.sinks[0]: '◀'}
        relabel_map.update({n_: n for n_, n in zip(
            nodes, list(range(1, len(nodes) + 1)))})

        nx.relabel_nodes(g_out, relabel_map, copy=False)

        # Return g_out if copy=True
        if copy:
            return g_out

        # Else, update result in place
        # TODO: Refactor with move semantics
        self.edges = g_out.edges
        self.nodes = g_out.nodes
        self.sources = g_out.sources
        self.sinks = g_out.sinks
        self.vars = g_out.vars

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

    def draw(self, src_file):
        import os
        import graphviz as gv

        from pathlib import Path
        from importlib import reload
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
        cfg_dot.write(f'{src_file}.dot', prog='dot', encoding='utf-8')

        # Render CFG
        gv.render('dot', 'svg', f'{src_file}.dot')
