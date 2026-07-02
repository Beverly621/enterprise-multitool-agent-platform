
from app.models.task_progress import TaskProgress
from app.services.task_progress_service import serialize_task_progress, update_task_progress


class FakeDB:
    def __init__(self, task):
        self.task = task
        self.items = []

    def scalar(self, statement):
        return self.task

    def add(self, item):
        self.items.append(item)

    def flush(self):
        return None


def test_task_progress_lifecycle_updates_to_success() -> None:
    task = TaskProgress(
        task_id="task_1",
        run_id=None,
        user_id=1,
        task_type="AGENT_RUN",
        status="PENDING",
        progress=0,
        current_stage="CREATED",
    )
    db = FakeDB(task)

    running = update_task_progress(db, "task_1", "RUNNING", 45, "RAG_RETRIEVAL")
    done = update_task_progress(db, "task_1", "SUCCESS", 100, "SUCCESS")
    serialized = serialize_task_progress(done)

    assert running.progress == 100
    assert done.status == "SUCCESS"
    assert serialized["progress"] == 100
    assert done.finished_at is not None


def test_task_progress_failure_sets_error_message() -> None:
    task = TaskProgress(task_id="task_2", user_id=1, task_type="AGENT_RUN")
    db = FakeDB(task)

    update_task_progress(db, "task_2", "FAILED", 100, "FAILED", error_message="boom")

    assert task.status == "FAILED"
    assert task.error_message == "boom"
