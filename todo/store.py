"""任务数据的 JSON 文件存储。

数据文件格式示例::

    {
      "todos": [
        {"id": 1, "title": "买菜", "done": false, "created": "2026-10-02T16:00:00"},
        {"id": 2, "title": "写周报", "done": true, "created": "2026-10-02T16:05:00"}
      ],
      "next_id": 3
    }
"""
import json
import os
from datetime import datetime
from pathlib import Path


def default_path():
    """默认数据文件位置。

    优先遵循 XDG 规范（``$XDG_DATA_HOME/todo-cli/todos.json``），
    否则放在用户家目录 ``~/.todo-cli.json``。
    """
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / "todo-cli" / "todos.json"
    return Path.home() / ".todo-cli.json"


class TodoStore:
    """基于 JSON 文件的简单存储。单线程个人使用，不考虑并发。"""

    def __init__(self, path=None):
        self.path = Path(path) if path is not None else default_path()
        self._todos = []
        self._next_id = 1
        self.load()

    def load(self):
        """从文件载入，文件不存在或损坏时当作空库。"""
        if not self.path.exists():
            return
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return
        self._todos = data.get("todos", [])
        ids = [t["id"] for t in self._todos if isinstance(t.get("id"), int)]
        self._next_id = data.get("next_id", (max(ids) + 1) if ids else 1)

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"todos": self._todos, "next_id": self._next_id}
        self.path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def add(self, title):
        title = title.strip()
        if not title:
            raise ValueError("任务标题不能为空")
        todo = {
            "id": self._next_id,
            "title": title,
            "done": False,
            "created": datetime.now().isoformat(timespec="seconds"),
        }
        self._todos.append(todo)
        self._next_id += 1
        self.save()
        return todo

    def all(self, include_done=True):
        """返回任务列表（按 id 排序）。"""
        todos = [t for t in self._todos if include_done or not t["done"]]
        return sorted(todos, key=lambda t: t["id"])

    def get(self, tid):
        for t in self._todos:
            if t["id"] == tid:
                return t
        return None

    def done(self, tid):
        """标记完成，成功返回 True，id 不存在返回 False。"""
        todo = self.get(tid)
        if todo is None:
            return False
        todo["done"] = True
        self.save()
        return True

    def remove(self, tid):
        """删除任务，成功返回 True，id 不存在返回 False。"""
        todo = self.get(tid)
        if todo is None:
            return False
        self._todos.remove(todo)
        self.save()
        return True

    def clear_done(self):
        """删除所有已完成任务，返回删除数量。"""
        before = len(self._todos)
        self._todos = [t for t in self._todos if not t["done"]]
        n = before - len(self._todos)
        if n:
            self.save()
        return n

    def clear_all(self):
        """清空全部任务，返回删除数量。"""
        n = len(self._todos)
        self._todos = []
        self.save()
        return n
