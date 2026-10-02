"""todo 命令行界面。"""
import argparse
import sys

from .store import TodoStore, default_path


def fmt_todo(t):
    mark = "✓" if t["done"] else " "
    return f"[{t['id']}] [{mark}] {t['title']}"


def cmd_add(args, store):
    todo = store.add(" ".join(args.title))
    print(f"已添加 [{todo['id']}] {todo['title']}")


def cmd_list(args, store):
    todos = store.all(include_done=args.all)
    if not todos:
        print("没有任务，先去喝杯水吧。" if args.all else "没有待办任务，都搞定了！")
        return
    for t in todos:
        print(fmt_todo(t))


def cmd_done(args, store):
    if store.done(args.id):
        print(f"[{args.id}] 标记完成，继续加油！")
    else:
        print(f"错误：找不到 id={args.id} 的任务", file=sys.stderr)
        sys.exit(1)


def cmd_rm(args, store):
    if store.remove(args.id):
        print(f"[{args.id}] 已删除")
    else:
        print(f"错误：找不到 id={args.id} 的任务", file=sys.stderr)
        sys.exit(1)


def cmd_clear(args, store):
    if args.all:
        n = store.clear_all()
        print(f"已清空全部 {n} 个任务")
    else:
        n = store.clear_done()
        print(f"已清理 {n} 个已完成任务" if n else "没有已完成的任务可清理")


def build_parser():
    p = argparse.ArgumentParser(
        prog="todo",
        description="极简命令行 todo 工具，数据存在本地 JSON 文件里",
    )
    p.add_argument(
        "--data-file",
        default=None,
        help=f"数据文件路径（默认 {default_path()}）",
    )
    sub = p.add_subparsers(dest="cmd", required=True, metavar="子命令")

    a = sub.add_parser("add", help="添加任务")
    a.add_argument("title", nargs="+", help="任务标题")
    a.set_defaults(func=cmd_add)

    l = sub.add_parser("list", help="列出任务（默认只看待办）")
    l.add_argument("--all", action="store_true", help="同时显示已完成的")
    l.set_defaults(func=cmd_list)

    d = sub.add_parser("done", help="把任务标记为完成")
    d.add_argument("id", type=int, help="任务 id")
    d.set_defaults(func=cmd_done)

    r = sub.add_parser("rm", help="删除任务")
    r.add_argument("id", type=int, help="任务 id")
    r.set_defaults(func=cmd_rm)

    c = sub.add_parser("clear", help="清理任务（默认只清已完成的）")
    c.add_argument("--all", action="store_true", help="清空全部任务，慎用")
    c.set_defaults(func=cmd_clear)

    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    store = TodoStore(args.data_file)
    args.func(args, store)


if __name__ == "__main__":
    main()
