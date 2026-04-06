import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

from config import TASKS_PATH
from utils.enums import Status


@dataclass
class Step:
    description: str
    status: str = Status.PENDING
    result: str | None = None


@dataclass
class Task:
    goal: str
    steps: list[Step] = field(default_factory=list)
    status: str = Status.PENDING
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    created_at: str = field(
        default_factory=lambda: datetime.now().isoformat()
    )


class TaskStore:
    def __init__(self, path: Path = TASKS_PATH) -> None:
        self._path = path
        self._tasks: dict[str, Task] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        data = json.loads(self._path.read_text())
        for task_data in data:
            task_data["steps"] = [
                Step(**s) for s in task_data.get("steps", [])
            ]
            task = Task(**task_data)
            self._tasks[task.id] = task

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        data = [asdict(t) for t in self._tasks.values()]
        self._path.write_text(json.dumps(data, indent=2))

    def create(self, goal: str, steps: list[str]) -> Task:
        task = Task(
            goal=goal,
            steps=[Step(description=s) for s in steps],
        )
        self._tasks[task.id] = task
        self._save()
        return task

    def get(self, task_id: str) -> Task | None:
        return self._tasks.get(task_id)

    def clear(self) -> None:
        self._tasks.clear()
        if self._path.exists():
            self._path.unlink()

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())

    def update_step(
        self,
        task_id: str,
        step_index: int,
        status: str,
        result: str | None = None,
    ) -> Task | None:
        task = self._tasks.get(task_id)
        if not task or step_index >= len(task.steps):
            return None
        task.steps[step_index].status = status
        task.steps[step_index].result = result

        if all(s.status == Status.COMPLETED for s in task.steps):
            task.status = Status.COMPLETED
        elif any(s.status == Status.IN_PROGRESS for s in task.steps):
            task.status = Status.IN_PROGRESS
        elif any(s.status == Status.FAILED for s in task.steps):
            task.status = Status.FAILED

        self._save()
        return task


_store_instance: TaskStore | None = None


def get_task_store() -> TaskStore:
    global _store_instance
    if _store_instance is None:
        _store_instance = TaskStore()
    return _store_instance
