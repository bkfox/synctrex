import unittest

from synctrex import Sync
from synctrex.executor import Executor


def make_tree(**kwargs):
    print(kwargs)
    syncs = { name: Sync(name = name) for name, deps in kwargs.items() }
    for name, deps in kwargs.items():
        print(name, '---', deps)
        sync = syncs[name]
        sync.require = [syncs[dep] for dep in deps]

    return syncs



class TestExecutor(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.syncs = make_tree(
            a0 = ['b0','b1'],
            b0 = ['c0','c1'],
            b1 = ['c1','c2','c3'],
            c0 = [], c1 = [],
            c2 = [], c3 = [],
        )

    def test_run(self):
        executor = Executor(name='test')
        executor.run(self.syncs['a0'])



