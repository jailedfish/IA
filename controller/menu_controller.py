from model.task import Task, Priority, Status, UrgentTask
from model.task_manager import TaskManager
from view.console_view import ConsoleView

class MenuController:
    """Controller: связывает Model и View, обрабатывает команды."""
    def __init__(self):
        self.manager = TaskManager()
        self.view = ConsoleView()
        self.filename = "tasks.json"

    def run(self):
        # Попытка загрузить существующий файл при старте
        self.manager.load_from_file(self.filename)
        while True:
            choice = self.view.show_menu()
            if choice == "1":
                self.show_all()
            elif choice == "2":
                self.add_task()
            elif choice == "3":
                self.edit_task()
            elif choice == "4":
                self.delete_task()
            elif choice == "5":
                self.filter_by_status()
            elif choice == "6":
                self.filter_by_priority()
            elif choice == "7":
                self.get_priority_task()
            elif choice == "8":
                self.undo()
            elif choice == "9":
                self.save()
            elif choice == "10":
                self.load()
            elif choice == "0":
                # Автосохранение перед выходом
                self.save()
                print("До свидания!")
                break
            else:
                self.view.show_message("Неверная команда. Попробуйте снова.")

    def show_all(self):
        self.view.show_tasks(self.manager.tasks)

    def add_task(self):
        try:
            data = self.view.input_task_data()
            if data["type"] == "UrgentTask":
                task = UrgentTask(data["title"], data["description"])
            else:
                task = Task(data["title"], data["description"], data["priority"])
            self.manager.add_task(task)
            self.view.show_message("Задача добавлена.")
        except ValueError as e:
            self.view.show_message(f"Ошибка: {e}")

    def edit_task(self):
        self.show_all()
        if not self.manager.tasks:
            return
        idx = self.view.get_index_from_user("редактирования")
        if idx < 0 or idx >= len(self.manager.tasks):
            self.view.show_message("Некорректный номер задачи.")
            return
        try:
            data = self.view.input_task_data(self.manager.tasks[idx])
            self.manager.edit_task(idx, **data)
            self.view.show_message("Задача обновлена.")
        except ValueError as e:
            self.view.show_message(f"Ошибка: {e}")

    def delete_task(self):
        self.show_all()
        if not self.manager.tasks:
            return
        idx = self.view.get_index_from_user("удаления")
        if idx < 0 or idx >= len(self.manager.tasks):
            self.view.show_message("Некорректный номер задачи.")
            return
        removed = self.manager.delete_task(idx)
        if removed:
            self.view.show_message(f"Задача '{removed.title}' удалена.")

    def filter_by_status(self):
        print("Статусы: 1 - To Do, 2 - In Progress, 3 - Done")
        c = self.view.input_string("Выбор: ")
        status_map = {"1": Status.TODO, "2": Status.IN_PROGRESS, "3": Status.DONE}
        if c not in status_map:
            self.view.show_message("Неверный выбор статуса.")
            return
        tasks = self.manager.filter_by_status(status_map[c])
        self.view.show_tasks(tasks)

    def filter_by_priority(self):
        print("Приоритеты: 1 - Low, 2 - Medium, 3 - High")
        c = self.view.input_string("Выбор: ")
        priority_map = {"1": Priority.LOW, "2": Priority.MEDIUM, "3": Priority.HIGH}
        if c not in priority_map:
            self.view.show_message("Неверный выбор приоритета.")
            return
        tasks = self.manager.filter_by_priority(priority_map[c])
        self.view.show_tasks(tasks)

    def get_priority_task(self):
        task = self.manager.get_next_priority_task()
        if task:
            print("Задача с наивысшим приоритетом:")
            task.display()
        else:
            self.view.show_message("Нет задач в очереди.")

    def undo(self):
        if self.manager.undo_last_action():
            self.view.show_message("Последнее действие отменено.")
        else:
            self.view.show_message("Нет действий для отмены.")

    def save(self):
        self.manager.save_to_file(self.filename)
        self.view.show_message(f"Данные сохранены в {self.filename}")

    def load(self):
        self.manager.load_from_file(self.filename)
        self.view.show_message(f"Данные загружены из {self.filename}")