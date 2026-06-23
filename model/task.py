from enum import Enum

class Priority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3

    def __str__(self):
        return self.name.capitalize()

class Status(Enum):
    TODO = "To Do"
    IN_PROGRESS = "In Progress"
    DONE = "Done"

    def __str__(self):
        return self.value

class Task:
    """Базовая модель задачи с инкапсуляцией."""
    def __init__(self, title: str, description: str, priority: Priority = Priority.MEDIUM,
                 status: Status = Status.TODO):
        self._title = title
        self._description = description
        self._priority = priority
        self._status = status

    # Геттеры и сеттеры
    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, value: str):
        if not value.strip():
            raise ValueError("Название не может быть пустым")
        self._title = value.strip()

    @property
    def description(self) -> str:
        return self._description

    @description.setter
    def description(self, value: str):
        if not value.strip():
            raise ValueError("Описание не может быть пустым")
        self._description = value.strip()

    @property
    def priority(self) -> Priority:
        return self._priority

    @priority.setter
    def priority(self, value: Priority):
        if not isinstance(value, Priority):
            raise ValueError("Некорректный приоритет")
        self._priority = value

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, value: Status):
        if not isinstance(value, Status):
            raise ValueError("Некорректный статус")
        self._status = value

    def to_dict(self) -> dict:
        """Сериализация задачи в словарь."""
        return {
            "type": self.__class__.__name__,
            "title": self._title,
            "description": self._description,
            "priority": self._priority.name,
            "status": self._status.name
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Десериализация задачи из словаря."""
        if data.get("type") == "UrgentTask":
            return UrgentTask(
                data["title"],
                data["description"],
                Status[data["status"]]
            )
        return cls(
            data["title"],
            data["description"],
            Priority[data["priority"]],
            Status[data["status"]]
        )

    def __str__(self):
        return f"[{self._status}] {self._title} (Приоритет: {self._priority})"

    def display(self):
        """Полиморфный метод отображения задачи."""
        print(self)


class UrgentTask(Task):
    """Подкласс задачи, всегда с высоким приоритетом (демонстрация наследования)."""
    def __init__(self, title: str, description: str, status: Status = Status.TODO):
        super().__init__(title, description, Priority.HIGH, status)
        
    @Task.priority.setter
    def priority(self, value: Priority):
        if value != Priority.HIGH:
            raise ValueError("Срочная задача должна иметь высокий приоритет")
        Task.priority.fset(self, value)

    def display(self):
        """Переопределённый вывод для срочной задачи."""
        print(f"!!! СРОЧНО !!! {super().__str__()}")