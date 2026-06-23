import pytest
import json
import os
from model.task import Task, Priority, Status, UrgentTask
from model.task_manager import TaskManager
from view.console_view import ConsoleView

# ----------------- Тесты класса Task -----------------
class TestTask:
    def test_create_task_valid(self):
        task = Task("Test", "Description", Priority.LOW, Status.TODO)
        assert task.title == "Test"
        assert task.description == "Description"
        assert task.priority == Priority.LOW
        assert task.status == Status.TODO

    def test_default_values(self):
        task = Task("Title", "Desc")
        assert task.priority == Priority.MEDIUM
        assert task.status == Status.TODO

    def test_setter_empty_title_raises(self):
        task = Task("Title", "Desc")
        with pytest.raises(ValueError, match="Название не может быть пустым"):
            task.title = "   "

    def test_setter_empty_description_raises(self):
        task = Task("Title", "Desc")
        with pytest.raises(ValueError, match="Описание не может быть пустым"):
            task.description = ""

    def test_setter_invalid_priority_raises(self):
        task = Task("Title", "Desc")
        with pytest.raises(ValueError, match="Некорректный приоритет"):
            task.priority = "High"  # строка, а не объект Priority

    def test_setter_invalid_status_raises(self):
        task = Task("Title", "Desc")
        with pytest.raises(ValueError, match="Некорректный статус"):
            task.status = "Done"

    def test_to_dict_and_from_dict(self):
        task = Task("Buy milk", "1 liter", Priority.HIGH, Status.IN_PROGRESS)
        d = task.to_dict()
        assert d["type"] == "Task"
        assert d["title"] == "Buy milk"
        restored = Task.from_dict(d)
        assert restored.title == task.title
        assert restored.priority == task.priority
        assert restored.status == task.status

    def test_display_output(self, capsys):
        task = Task("Test", "Desc", Priority.LOW, Status.TODO)
        task.display()
        captured = capsys.readouterr()
        assert "[To Do] Test (Приоритет: Low)" in captured.out

# ----------------- Тесты подкласса UrgentTask -----------------
class TestUrgentTask:
    def test_urgent_task_always_high(self):
        task = UrgentTask("Fix bug", "Critical")
        assert task.priority == Priority.HIGH
        assert task.status == Status.TODO

    def test_cannot_change_priority(self):
        task = UrgentTask("Fix bug", "Critical")
        with pytest.raises(ValueError, match="Срочная задача должна иметь высокий приоритет"):
            task.priority = Priority.LOW

    def test_to_dict_includes_type(self):
        task = UrgentTask("Fix bug", "Critical")
        d = task.to_dict()
        assert d["type"] == "UrgentTask"
        restored = Task.from_dict(d)
        assert isinstance(restored, UrgentTask)
        assert restored.priority == Priority.HIGH

    def test_display_urgent(self, capsys):
        task = UrgentTask("Fix bug", "Critical")
        task.display()
        captured = capsys.readouterr()
        assert "!!! СРОЧНО !!!" in captured.out

# ----------------- Тесты TaskManager -----------------
class TestTaskManager:
    @pytest.fixture
    def manager(self):
        return TaskManager()

    def test_urgent_task_preserves_status_after_save_load(self, manager, tmp_path):
        """UrgentTask с изменённым статусом должен сохранять его после загрузки из JSON."""
        file = tmp_path / "tasks.json"
        urgent = UrgentTask("Срочный баг", "Исправить немедленно")
        urgent.status = Status.DONE
        manager.add_task(urgent)
        manager.save_to_file(str(file))
        
        new_manager = TaskManager()
        new_manager.load_from_file(str(file))
        loaded_task = new_manager.tasks[0]
        
        assert loaded_task.status == Status.DONE, (
            f"Ожидался статус {Status.DONE}, получен {loaded_task.status}")

    def test_add_task(self, manager):
        task = Task("A", "Desc", Priority.LOW)
        manager.add_task(task)
        assert len(manager.tasks) == 1

    def test_priority_queue(self, manager):
        t1 = Task("Low", "d", Priority.LOW)
        t2 = Task("High", "d", Priority.HIGH)
        t3 = Task("Medium", "d", Priority.MEDIUM)
        manager.add_task(t1)
        manager.add_task(t2)
        manager.add_task(t3)
        next_task = manager.get_next_priority_task()
        assert next_task.priority == Priority.HIGH

    def test_edit_task_valid(self, manager):
        t = Task("Old", "Old desc", Priority.LOW, Status.TODO)
        manager.add_task(t)
        assert manager.edit_task(0, title="New")
        assert manager.tasks[0].title == "New"

    def test_edit_task_invalid_index(self, manager):
        assert not manager.edit_task(10, title="No")

    def test_delete_task_valid(self, manager):
        t = Task("Del", "Desc")
        manager.add_task(t)
        removed = manager.delete_task(0)
        assert removed.title == "Del"
        assert len(manager.tasks) == 0

    def test_delete_task_invalid_index(self, manager):
        assert manager.delete_task(0) is None

    def test_undo_add(self, manager):
        t = Task("To undo", "desc")
        manager.add_task(t)
        assert manager.undo_last_action() == True
        assert len(manager.tasks) == 0

    def test_undo_edit(self, manager):
        t = Task("Original", "desc")
        manager.add_task(t)
        manager.edit_task(0, title="Changed")
        manager.undo_last_action()
        assert manager.tasks[0].title == "Original"

    def test_undo_delete(self, manager):
        t = Task("Restore", "desc")
        manager.add_task(t)
        manager.delete_task(0)
        manager.undo_last_action()
        assert len(manager.tasks) == 1
        assert manager.tasks[0].title == "Restore"

    def test_filter_by_status(self, manager):
        t1 = Task("A", "d", status=Status.TODO)
        t2 = Task("B", "d", status=Status.DONE)
        manager.add_task(t1)
        manager.add_task(t2)
        filtered = manager.filter_by_status(Status.DONE)
        assert len(filtered) == 1
        assert filtered[0].status == Status.DONE

    def test_filter_by_priority(self, manager):
        t1 = Task("Low", "d", Priority.LOW)
        t2 = Task("High", "d", Priority.HIGH)
        manager.add_task(t1)
        manager.add_task(t2)
        filtered = manager.filter_by_priority(Priority.HIGH)
        assert len(filtered) == 1
        assert filtered[0].priority == Priority.HIGH

    def test_save_and_load(self, manager, tmp_path):
        file = tmp_path / "tasks.json"
        t1 = Task("Save", "desc")
        t2 = UrgentTask("Urgent", "now")
        manager.add_task(t1)
        manager.add_task(t2)
        manager.save_to_file(str(file))
        new_manager = TaskManager()
        new_manager.load_from_file(str(file))
        assert len(new_manager.tasks) == 2
        assert isinstance(new_manager.tasks[1], UrgentTask)
        assert new_manager.tasks[1].priority == Priority.HIGH

    def test_load_non_existing_file(self, manager, capsys):
        manager.load_from_file("non_existing.json")
        captured = capsys.readouterr()
        assert "не найден" in captured.out or "FileNotFoundError" in captured.out  # на русском
        assert len(manager.tasks) == 0

# ----------------- Тесты валидации в ConsoleView -----------------
class TestConsoleView:
    def test_input_task_data_valid(self, monkeypatch):
        inputs = iter(["My Task", "Description", "2", "1"])  # priority Medium, type обычный
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        data = ConsoleView.input_task_data()
        assert data["title"] == "My Task"
        assert data["description"] == "Description"
        assert data["priority"] == Priority.MEDIUM
        assert data["type"] == "Task"

    def test_input_task_data_empty_title_raises(self, monkeypatch):
        inputs = iter(["   ", "Desc", "1", "1"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        with pytest.raises(ValueError, match="Название не может быть пустым"):
            ConsoleView.input_task_data()

    def test_input_task_data_empty_description_raises(self, monkeypatch):
        inputs = iter(["Title", "", "1", "1"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        with pytest.raises(ValueError, match="Описание не может быть пустым"):
            ConsoleView.input_task_data()

    def test_input_task_data_invalid_priority(self, monkeypatch):
        inputs = iter(["Title", "Desc", "5", "1"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        with pytest.raises(ValueError, match="Неверный выбор приоритета"):
            ConsoleView.input_task_data()

    def test_input_task_data_invalid_type(self, monkeypatch):
        inputs = iter(["Title", "Desc", "1", "3"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        with pytest.raises(ValueError, match="Неверный выбор типа задачи"):
            ConsoleView.input_task_data()

    def test_input_task_data_edit_existing(self, monkeypatch):
        existing = Task("Old", "Old desc", Priority.HIGH, Status.DONE)
        # Ввод: пропускаем title и desc (Enter), меняем priority на 1, статус на 2
        inputs = iter(["", "", "1", "2"])
        monkeypatch.setattr('builtins.input', lambda _: next(inputs))
        data = ConsoleView.input_task_data(existing)
        assert "title" not in data  # не должно быть в словаре
        assert "description" not in data
        assert data["priority"] == Priority.LOW
        assert data["status"] == Status.IN_PROGRESS

    def test_get_index_from_user_valid(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "3")
        idx = ConsoleView.get_index_from_user()
        assert idx == 2  # 3 -> индекс 2

    def test_get_index_from_user_invalid(self, monkeypatch):
        monkeypatch.setattr('builtins.input', lambda _: "abc")
        idx = ConsoleView.get_index_from_user()
        assert idx == -1
    