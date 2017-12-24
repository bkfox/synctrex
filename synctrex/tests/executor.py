import random
import unittest

from synctrex import Sync
from synctrex.executor import Executor


class GraphGenerator:
    """
    Generate graph of sync to be used in tests
    """

    stack = None
    syncs = None
    max_depth = 5
    count_per_node = 3

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def make(self, with_cycles = False):
        root = Sync(None, name = '0')
        self.stack = [root]
        self.syncs = [root]
        self._make_node(root, with_cycles)
        self.stack.remove(root)

    def _make_node(self, node, with_cycles):
        depth = len(self.stack)
        if depth >= self.max_depth:
            return

        # add cycles on some items
        if self.syncs and self.stack != self.syncs:
            count = random.choices(range(0,5), [(5-x)**2 for x in range(0,5)])[0]
            for x in range(0,count):
                in_stack = with_cycles and (not x or random.random() > 0.66)
                if in_stack:
                    dep = random.choice(self.stack)
                else:
                    dep = self.stack[0]
                    while dep in self.stack:
                        dep = random.choice(self.syncs)
                node.require.append(dep)

        for i in range(0, self.count_per_node):
            child = Sync(None, name = node.name + '.' + str(i))
            node.require.append(child)

            self.stack.append(child)
            self.syncs.append(child)
            self._make_node(child, with_cycles)
            self.stack.remove(child)


class TestGraph(unittest.TestCase):
    def test_no_cycle(self):
        graph = GraphGenerator(max_depth = 4)
        graph.make()
        executor = Executor(name='test')
        executor.run(graph.syncs[0])

    def test_with_cycle(self):
        graph = GraphGenerator(max_depth = 4)
        graph.make(True)
        executor = Executor(name='test')
        self.assertRaises(Exception, executor.run, graph.syncs[0])

    # TODO: test order
    #       parallelize forbidden (when implemented)


