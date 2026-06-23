import heapq
import json
from typing import List, Optional, Dict, Any
from model.task import Task, Priority, Status, UrgentTask

class TaskManager:
    """Model: управляет списком задач, очередью и стеком отмены."""
    def __init__(self):
        self._tasks: List[Task] = []
        self._priority_queue: List[tuple] = []  # (priority_value, counter, task)
        self._undo_stack: List[Dict[str, Any]] = []
        self._task_counter = 0

    @property
    def tasks(self) -> List[Task]:
        return self._tasks.copy()

    def add_task(self, task: Task):
        self._tasks.append(task)
        # Добавляем в очередь приоритетов (чем выше значение, тем раньше извлекается)
        # Используем отрицание для обратного порядка, чтобы HIGH (3) был первым
        heapq.heappush(self._priority_queue, (-task.priority.value, self._task_counter, task))
        self._task_counter += 1
        self._undo_stack.append({"action": "add", "task": task})

    def edit_task(self, index: int, title: str = None, description: str = None,
                  priority: Priority = None, status: Status = None) -> bool:
        if 0 <= index < len(self._tasks):
            task = self._tasks[index]
            old_state = task.to_dict()
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if priority is not None:
                task.priority = priority
            if status is not None:
                task.status = status
            self._undo_stack.append({"action": "edit", "index": index, "old_state": old_state})
            return True
        return False

    def delete_task(self, index: int) -> Optional[Task]:
        if 0 <= index < len(self._tasks):
            removed = self._tasks.pop(index)
            # Перестраиваем очередь (упрощённо, можно удалить конкретный элемент)
            self._rebuild_priority_queue()
            self._undo_stack.append({"action": "delete", "index": index, "task": removed})
            return removed
        return None

    def undo_last_action(self) -> bool:
        if not self._undo_stack:
            return False
        action = self._undo_stack.pop()
        if action["action"] == "add":
            # Удаляем добавленную задачу (последнюю в списке)
            task = action["task"]
            if task in self._tasks:
                self._tasks.remove(task)
                self._rebuild_priority_queue()
        elif action["action"] == "edit":
            idx = action["index"]
            old = action["old_state"]
            task = self._tasks[idx]
            task.title = old["title"]
            task.description = old["description"]
            task.priority = Priority[old["priority"]]
            task.status = Status[old["status"]]
        elif action["action"] == "delete":
            idx = action["index"]
            task = action["task"]
            self._tasks.insert(idx, task)
            self._rebuild_priority_queue()
        return True

    def get_next_priority_task(self) -> Optional[Task]:
        """Извлекает задачу с наивысшим приоритетом из очереди (без удаления из списка)."""
        while self._priority_queue:
            _, _, task = heapq.heappop(self._priority_queue)
            if task in self._tasks:
                return task
        return None

    def filter_by_status(self, status: Status) -> List[Task]:
        return [t for t in self._tasks if t.status == status]

    def filter_by_priority(self, priority: Priority) -> List[Task]:
        return [t for t in self._tasks if t.priority == priority]

    def save_to_file(self, filename: str):
        data = [task.to_dict() for task in self._tasks]
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load_from_file(self, filename: str):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._tasks = [Task.from_dict(item) for item in data]
            self._rebuild_priority_queue()
            self._undo_stack.clear()
        except FileNotFoundError:
            print(f"Файл {filename} не найден. Начинаем с пустого списка.")
        except json.JSONDecodeError:
            print("Ошибка чтения JSON-файла. Используется пустой список.")

    def _rebuild_priority_queue(self):
        self._priority_queue = []
        for task in self._tasks:
            heapq.heappush(self._priority_queue, (-task.priority.value, self._task_counter, task))
            self._task_counter += 1