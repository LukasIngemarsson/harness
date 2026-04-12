from harness.enums import Status
from harness.memory.task import TaskStore


class TestTaskStore:
    def _make_store(self, tmp_path):
        return TaskStore(path=tmp_path / "tasks.json")

    def test_create_task(self, tmp_path):
        store = self._make_store(tmp_path)
        task = store.create("Test goal", ["step 1", "step 2"])
        assert task.goal == "Test goal"
        assert len(task.steps) == 2
        assert task.status == Status.PENDING

    def test_get_missing_task(self, tmp_path):
        store = self._make_store(tmp_path)
        assert store.get("nonexistent") is None

    def test_update_step_completed(self, tmp_path):
        store = self._make_store(tmp_path)
        task = store.create("Test", ["step 1", "step 2"])
        store.update_step(task.id, 0, Status.COMPLETED, "done")
        assert task.steps[0].status == Status.COMPLETED
        assert task.steps[0].result == "done"
        assert task.status == Status.PENDING

    def test_all_steps_completed(self, tmp_path):
        store = self._make_store(tmp_path)
        task = store.create("Test", ["step 1", "step 2"])
        store.update_step(task.id, 0, Status.COMPLETED)
        store.update_step(task.id, 1, Status.COMPLETED)
        assert task.status == Status.COMPLETED

    def test_any_step_failed(self, tmp_path):
        store = self._make_store(tmp_path)
        task = store.create("Test", ["step 1", "step 2"])
        store.update_step(task.id, 0, Status.FAILED)
        assert task.status == Status.FAILED

    def test_in_progress_status(self, tmp_path):
        store = self._make_store(tmp_path)
        task = store.create("Test", ["step 1", "step 2"])
        store.update_step(task.id, 0, Status.IN_PROGRESS)
        assert task.status == Status.IN_PROGRESS

    def test_invalid_step_index(self, tmp_path):
        store = self._make_store(tmp_path)
        task = store.create("Test", ["step 1"])
        assert store.update_step(task.id, 99, Status.COMPLETED) is None

    def test_persistence(self, tmp_path):
        path = tmp_path / "tasks.json"
        store = TaskStore(path=path)
        task = store.create("Test", ["step 1"])
        store.update_step(task.id, 0, Status.COMPLETED, "done")

        store2 = TaskStore(path=path)
        loaded = store2.get(task.id)
        assert loaded is not None
        assert loaded.goal == "Test"
        assert loaded.steps[0].status == Status.COMPLETED
        assert loaded.steps[0].result == "done"
