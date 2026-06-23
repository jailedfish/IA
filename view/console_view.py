from typing import List, Optional
from model.task import Task, Priority, Status, UrgentTask
from model.task_manager import TaskManager

class ConsoleView:
    """View: отвечает за ввод/вывод в консоли."""

    @staticmethod
    def show_menu():
        print("\n=== МЕНЕДЖЕР ЗАДАЧ ===")
        print("1. Показать все задачи")
        print("2. Добавить задачу")
        print("3. Редактировать задачу")
        print("4. Удалить задачу")
        print("5. Фильтр по статусу")
        print("6. Фильтр по приоритету")
        print("7. Получить задачу с наивысшим приоритетом")
        print("8. Отменить последнее действие")
        print("9. Сохранить в JSON")
        print("10. Загрузить из JSON")
        print("0. Выход")
        return input("Выберите действие: ").strip()

    @staticmethod
    def show_tasks(tasks: List[Task]):
        if not tasks:
            print("Список задач пуст.")
            return
        print("\nСписок задач:")
        for i, task in enumerate(tasks):
            print(f"{i+1}. ", end="")
            task.display()

    @staticmethod
    def input_task_data(existing: Task = None) -> dict:
        """Запрашивает данные задачи. Возвращает словарь только заполненных полей."""
        data = {}
        if existing is None:
            title = input("Название: ").strip()
            if not title:
                raise ValueError("Название не может быть пустым")
            data["title"] = title
        else:
            title = input(f"Новое название (Enter - оставить '{existing.title}'): ").strip()
            if title:
                data["title"] = title

        if existing is None:
            desc = input("Описание: ").strip()
            if not desc:
                raise ValueError("Описание не может быть пустым")
            data["description"] = desc
        else:
            desc = input(f"Новое описание (Enter - оставить текущее): ").strip()
            if desc:
                data["description"] = desc

        if existing is None:
            print("Приоритет: 1 - Low, 2 - Medium, 3 - High")
            p_choice = input("Выбор: ").strip()
            priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
            if p_choice not in priority_map:
                raise ValueError("Неверный выбор приоритета")
            data["priority"] = priority_map[p_choice]
        else:
            p_choice = input("Новый приоритет (1-Low,2-Medium,3-High, Enter-пропустить): ").strip()
            if p_choice:
                priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
                if p_choice not in priority_map:
                    raise ValueError("Неверный выбор приоритета")
                data["priority"] = priority_map[p_choice]

        if existing is None:
            print("Тип задачи: 1 - Обычная, 2 - Срочная")
            t_choice = input("Выбор: ").strip()
            if t_choice not in ("1", "2"):
                raise ValueError("Неверный выбор типа задачи")
            data["type"] = "UrgentTask" if t_choice == "2" else "Task"
        # Статус только при редактировании или позже
        if existing is not None:
            s_choice = input("Новый статус (1-To Do,2-In Progress,3-Done, Enter-пропустить): ").strip()
            if s_choice:
                status_map = {"1": Status.TODO, "2": Status.IN_PROGRESS, "3": Status.DONE}
                if s_choice not in status_map:
                    raise ValueError("Неверный выбор статуса")
                data["status"] = status_map[s_choice]
        return data

    @staticmethod
    def get_index_from_user(action: str = "выберите") -> int:
        try:
            idx = int(input(f"Введите номер задачи для {action}: ").strip()) - 1
            return idx
        except ValueError:
            return -1

    @staticmethod
    def show_message(msg: str):
        print(msg)

    @staticmethod
    def input_string(prompt: str) -> str:
        return input(prompt).strip()