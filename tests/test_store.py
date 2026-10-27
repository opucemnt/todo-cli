"""TodoStore 的单元测试。"""
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from todo.store import TodoStore, default_path


class TestTodoStore(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "todos.json"
        self.store = TodoStore(self.path)

    def tearDown(self):
        self.tmp.cleanup()

    def test_add_returns_todo_with_id(self):
        todo = self.store.add("买菜")
        self.assertEqual(todo["id"], 1)
        self.assertEqual(todo["title"], "买菜")
        self.assertFalse(todo["done"])

    def test_add_empty_title_raises(self):
        with self.assertRaises(ValueError):
            self.store.add("   ")

    def test_ids_keep_increasing(self):
        self.store.add("a")
        self.store.add("b")
        self.store.remove(1)
        todo = self.store.add("c")
        # id 不复用，避免和历史引用混淆
        self.assertEqual(todo["id"], 3)

    def test_done(self):
        self.store.add("写周报")
        self.assertTrue(self.store.done(1))
        self.assertTrue(self.store.get(1)["done"])

    def test_done_missing_id_returns_false(self):
        self.assertFalse(self.store.done(999))

    def test_list_filters_done(self):
        self.store.add("待办")
        self.store.add("已办")
        self.store.done(2)
        pending = self.store.all(include_done=False)
        self.assertEqual([t["id"] for t in pending], [1])
        self.assertEqual(len(self.store.all()), 2)

    def test_remove(self):
        self.store.add("删我")
        self.assertTrue(self.store.remove(1))
        self.assertIsNone(self.store.get(1))

    def test_remove_missing_id_returns_false(self):
        self.assertFalse(self.store.remove(999))

    def test_clear_done(self):
        self.store.add("a")
        self.store.add("b")
        self.store.done(1)
        n = self.store.clear_done()
        self.assertEqual(n, 1)
        self.assertEqual([t["id"] for t in self.store.all()], [2])

    def test_clear_all(self):
        self.store.add("a")
        self.store.add("b")
        n = self.store.clear_all()
        self.assertEqual(n, 2)
        self.assertEqual(self.store.all(), [])

    def test_persistence(self):
        """save 后用新实例能完整读回。"""
        self.store.add("持久化测试")
        self.store.done(1)
        again = TodoStore(self.path)
        self.assertEqual(len(again.all()), 1)
        self.assertTrue(again.get(1)["done"])
        # next_id 也要持久化，否则重启后 id 会重复
        self.assertEqual(again.add("第二个")["id"], 2)

    def test_corrupt_file_starts_empty(self):
        self.path.write_text("这不是 json{{{", encoding="utf-8")
        store = TodoStore(self.path)
        self.assertEqual(store.all(), [])

    def test_default_path_prefers_xdg(self):
        with mock.patch.dict(os.environ, {"XDG_DATA_HOME": "/tmp/xdg-data"}):
            self.assertEqual(
                default_path(), Path("/tmp/xdg-data/todo-cli/todos.json")
            )

    def test_default_path_falls_back_to_home(self):
        env = {k: v for k, v in os.environ.items() if k != "XDG_DATA_HOME"}
        with mock.patch.dict(os.environ, env, clear=True):
            self.assertEqual(default_path(), Path.home() / ".todo-cli.json")


    def test_done_twice_is_idempotent(self):
        self.store.add("a")
        self.assertTrue(self.store.done(1))
        self.assertTrue(self.store.done(1))
        self.assertTrue(self.store.get(1)["done"])


    def test_add_strips_whitespace(self):
        todo = self.store.add("  买菜  ")
        self.assertEqual(todo["title"], "买菜")


if __name__ == "__main__":
    unittest.main()
