from concurrent.futures import ThreadPoolExecutor
import datetime

from synctrex.base import Named

# TODO:
# - support for concurrent disapprouved cases
# - doc on how its works and is conceived


class Task:
    sync = None
    deps = None
    depth = 0
    result = None
    submitted = False

    def __init__(self, sync, **kwargs):
        self.__dict__.update(kwargs)
        self.sync = sync

class Executor(Named):
    workers = 10

    tasks = None
    todo = None
    done = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def add_task(self, sync, depth=0):
        """
        Add task and depenendenci
        """
        if sync.name in self.tasks:
            return self.tasks[sync.name]

        task = Task(sync)
        task.deps = []
        task.depth = depth
        self.tasks[sync.name] = task
        self.todo.append(task)

        # scan deps and add to syncs/tasks if required
        depth += 1
        for dep in sync.require:
            dep = self.add_task(dep, depth)
            if dep.depth < task.depth:
                raise ValueError(
                    "graph dependency cycle detected for sync {} "
                    "(depth {}) with dep {} (depth: {})"
                    .format(sync.name, task.depth, dep.sync.name, dep.depth)
                )
            task.deps.append(dep)

        return task

    def _do_run(self, task):
        # try:
            sync = task.sync
            self.log("sync {} started", sync.name)
            start = datetime.datetime.now()

            task.result = sync.run()

            duration = datetime.datetime.now() - start
            self.log('sync {} is done after {} seconds, result: {}',
                     sync.name, duration.total_seconds(), task.result)

            self.done.append(task)
        # except Exception as e:
        #    self.log("sync {} failed. Exception thrown: {}",
        #             sync.name, e)
        #    task.result = -1
        # finally:
            return task.result

    def _try_submit(self, task, executor):
        """
        :returns: True if task has been submited to executor
        """
        sync = task.sync

        # update deps list: remove done
        task.deps = [
            dep for dep in task.deps
                if dep not in self.done
        ]

        # wait for deps to be done: report for later
        if task.deps:
            return False

        # check deps result: need to retrieve previous deps from syncs
        # (task.deps is now empty)
        failed = (self.tasks[dep.name] for dep in sync.require)
        failed = [ dep for dep in failed if dep.result ]
        if failed:
            self.log(
                'sync {}: cancelled - required syncs have '
                'failed: {}',
                sync.name,
                ', '.join(dep.name for dep in failed)
            )
            task.result = -2
            self.done.append(task)
            return False

        # submit to executor
        self.log('task {}: submit', task.sync.name)
        executor.submit(self._do_run, task)
        return True

    def run(self, *syncs):
        # done is shared across threads: case of concurrent
        # writing will not pose problem since it only grows
        # and only has an impact when all deps are presents.
        # We also guaranty that a sync only will be run once
        # per running executor.
        self.done = []
        self.tasks = {}
        self.todo = []

        # construct task tree & update todo list
        for sync in syncs:
            self.add_task(sync)

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            while self.todo:
                # a sync is only run when all its dependencies have
                # been successfully done
                task = self.todo.pop()
                if not self._try_submit(task, executor):
                    self.todo.insert(0, task)

