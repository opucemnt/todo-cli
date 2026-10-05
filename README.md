# todo-cli

一个极简的命令行 todo 管理工具，数据存在本地 JSON 文件里，不依赖任何第三方库。

## 功能

- `add`：添加任务
- `list`：列出任务（默认只看待办，`--all` 看全部）
- `done`：把任务标记为完成
- `rm`：删除任务
- `clear`：清理已完成任务（`--all` 清空全部）

数据文件默认在 `~/.todo-cli.json`；如果设置了 `XDG_DATA_HOME`，
则放在 `$XDG_DATA_HOME/todo-cli/todos.json`。也可以用 `--data-file` 随时指定。

## 安装

不需要安装第三方依赖，直接用：

```bash
cd todo-cli
python -m todo --help
```

嫌每次敲 `python -m todo` 太长，可以加个别名：

```bash
alias t="python -m todo"
```

## 使用示例

```bash
# 1. 添加任务（标题带空格不用加引号）
$ python -m todo add 买菜
已添加 [1] 买菜

$ python -m todo add 写周报 记得附上数据截图
已添加 [2] 写周报 记得附上数据截图

# 2. 查看待办
$ python -m todo list
[1] [ ] 买菜
[2] [ ] 写周报 记得附上数据截图

# 3. 标记完成
$ python -m todo done 1
[1] 标记完成，继续加油！

# 4. 再看待办，只剩没完成的
$ python -m todo list
[2] [ ] 写周报 记得附上数据截图

# 5. 想看全部（含已完成）
$ python -m todo list --all
[1] [✓] 买菜
[2] [ ] 写周报 记得附上数据截图

# 6. 删除任务
$ python -m todo rm 2
[2] 已删除

# 7. 清理已完成任务
$ python -m todo clear
已清理 1 个已完成任务

# 8. 数据文件换个地方（比如放网盘同步）
$ python -m todo --data-file ~/Dropbox/todos.json add 重要事项
```

## 跑测试

```bash
python -m unittest discover -s tests -v
```

## 数据格式

JSON 文件长这样，人可以直接打开改：

```json
{
  "todos": [
    {"id": 1, "title": "买菜", "done": true, "created": "2026-10-02T16:00:00"}
  ],
  "next_id": 2
}
```

## 常见问题

- **数据文件丢了怎么办？** 任务存在本地 JSON 文件里，默认没有云同步。建议用 `--data-file` 把数据文件放到网盘同步目录。
- **删掉的任务 id 会复用吗？** 不会。id 只增不减，避免和历史引用混淆。
- **Windows 能用吗？** 能，纯标准库，`python -m todo` 直接跑。
