# 在 Conda 环境中学习 Python

> 目标：建立 Python 的基础语法框架，并通过可直接运行的示例理解函数、容器、模块、类、异常和文件操作。

开始本笔记前，建议先阅读 [Conda 环境管理入门](./Conda.md)，然后准备练习环境：

```bash
conda create -n py-study python=3.12 pip
conda activate py-study
python --version
```

## 1. 运行第一个 Python 程序

创建文件 `hello.py`：

```python
def main():
    name = input("请输入你的名字：")
    print(f"你好，{name}！")


if __name__ == "__main__":
    main()
```

运行脚本：

```bash
python hello.py
```

关键点：

| 代码 | 含义 |
| --- | --- |
| `def main():` | 定义名为 `main` 的函数 |
| 缩进 | Python 使用缩进表示代码块，通常使用 4 个空格 |
| `input()` | 获取用户输入，返回值总是字符串 |
| `f"你好，{name}"` | 格式化字符串，将变量插入文本 |
| `__name__ == "__main__"` | 仅当文件被直接运行时执行 `main()` |

当文件被另一个脚本 `import` 时，`__name__` 是模块名，而不是 `"__main__"`。这种写法可以避免导入模块时自动执行测试代码。

## 2. 变量与基本类型

Python 不需要预先声明变量类型：

```python
user_name = "Tom"       # str：字符串
age = 18                # int：整数
height = 1.75           # float：浮点数
is_student = True       # bool：布尔值

print(user_name, age, height, is_student)
```

查看值的类型：

```python
print(type(age))        # <class 'int'>
print(type(user_name))  # <class 'str'>
```

不要使用 `list`、`str`、`dict`、`set` 等内置类型名作为变量名，否则之后调用这些工具时会产生混淆：

```python
# 推荐
numbers = [1, 2, 3]
message = "Hello"

# 不推荐：覆盖 Python 的内置名称
# list = [1, 2, 3]
# str = "Hello"
```

## 3. 字符串

字符串是不可修改的字符序列，可以读取、切片或生成新的字符串：

```python
message = "Hello, Python"

print(message[0])               # H
print(message[7:13])            # Python
print(message.lower())          # hello, python
print(message.replace("Python", "Conda"))
print("Python" in message)      # True

words = message.split(", ")
print(words)                    # ['Hello', 'Python']
print(" - ".join(words))        # Hello - Python
```

常用方法：

| 方法 | 作用 |
| --- | --- |
| `text.strip()` | 去掉字符串首尾空白 |
| `text.split(",")` | 按分隔符切成列表 |
| `" ".join(items)` | 将字符串列表连接起来 |
| `text.find("Py")` | 返回第一次出现的位置，找不到返回 `-1` |
| `text.startswith("He")` | 判断是否以指定内容开头 |

## 4. 列表、元组、字典与集合

### 4.1 列表 `list`

列表有顺序，并且可以修改：

```python
numbers = [1, 2, 3]
numbers.append(4)       # 末尾添加元素
numbers.insert(1, 10)   # 在索引 1 前插入元素
numbers.remove(2)       # 删除第一个值为 2 的元素
last = numbers.pop()    # 删除并返回最后一个元素

print(numbers)          # [1, 10, 3]
print(last)             # 4
print(numbers[0])       # 1
```

排序不会自动说明“按什么规则”排序，因此对复杂数据常使用 `key`：

```python
students = [("Tom", 82), ("Alice", 95), ("Bob", 76)]
students.sort(key=lambda item: item[1], reverse=True)
print(students)
```

### 4.2 元组 `tuple`

元组有顺序，但创建后不可修改，适合表示不会变化的一组值：

```python
point = (10, 20)
x, y = point
print(x, y)
```

### 4.3 字典 `dict`

字典使用“键 -> 值”保存数据：

```python
student = {"name": "Tom", "age": 18}
student["score"] = 92

print(student["name"])          # Tom
print(student.get("email"))     # None，不会因键不存在而报错

for key, value in student.items():
    print(key, value)
```

### 4.4 集合 `set`

集合中的元素不重复，适合去重和成员判断：

```python
tags = {"python", "conda", "python"}
tags.add("numpy")
tags.discard("conda")

print(tags)
print("python" in tags)         # True
```

## 5. 条件和循环

### 5.1 条件判断

```python
score = 85

if score >= 90:
    level = "优秀"
elif score >= 60:
    level = "及格"
else:
    level = "需要复习"

print(level)
```

### 5.2 `for` 循环与 `range()`

```python
for number in range(1, 5):
    print(number)
```

输出为 `1` 到 `4`，因为 `range(1, 5)` 包含起始值，不包含结束值。

遍历列表时，如果同时需要索引和值，使用 `enumerate()`：

```python
names = ["Alice", "Bob", "Tom"]

for index, name in enumerate(names, start=1):
    print(index, name)
```

### 5.3 `while` 循环

```python
count = 3

while count > 0:
    print(count)
    count -= 1

print("开始")
```

## 6. 函数

函数可以接收参数并返回结果：

```python
def greet(name, prefix="你好"):
    return f"{prefix}，{name}！"


message = greet("Tom")
another_message = greet("Alice", prefix="欢迎")

print(message)
print(another_message)
```

关键点：

| 概念 | 示例 | 说明 |
| --- | --- | --- |
| 参数 | `name` | 调用函数时传入的数据 |
| 默认参数 | `prefix="你好"` | 调用时可以省略 |
| 返回值 | `return message` | 将结果交给调用方 |
| 关键字参数 | `prefix="欢迎"` | 明确指出参数名称 |

变量作用域示例：

```python
def calculate_total(prices):
    total = sum(prices)  # total 只在函数内部使用
    return total


print(calculate_total([10, 20, 5]))
```

## 7. 模块、包与第三方库

### 7.1 导入标准库模块

Python 自带许多模块，无需安装：

```python
from pathlib import Path

current_file = Path("hello.py")
print(current_file.suffix)  # .py
```

### 7.2 自己编写模块

创建 `calculator.py`：

```python
def add(left, right):
    return left + right
```

创建 `main.py`：

```python
from calculator import add

print(add(2, 3))
```

运行：

```bash
python main.py
```

如果一个目录用于组织多个 Python 模块，通常可以在其中创建 `__init__.py`，将其明确作为包使用。文件名是双下划线 `__init__.py`，不是文件夹名。

### 7.3 安装和使用第三方库

确保已激活 `py-study` 环境，再安装 `requests`：

```bash
python -m pip install requests
```

示例：

```python
import requests


def fetch_status(url):
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.status_code


if __name__ == "__main__":
    print(fetch_status("https://www.python.org"))
```

网络请求可能失败，因此正式程序还应结合第 9 节的异常处理。

## 8. 类与对象

类将数据和处理这些数据的方法组织在一起：

```python
class Student:
    def __init__(self, name, score):
        self.name = name
        self.score = score

    def is_passed(self):
        return self.score >= 60

    def __str__(self):
        return f"{self.name}: {self.score}"


student = Student("Tom", 82)
print(student)              # 自动调用 __str__()
print(student.is_passed())  # True
```

### 8.1 继承与方法重写

```python
class Person:
    def __init__(self, name):
        self.name = name

    def introduce(self):
        return f"我是 {self.name}"


class Student(Person):
    def __init__(self, name, score):
        super().__init__(name)
        self.score = score

    def introduce(self):
        return f"{super().introduce()}，成绩是 {self.score}"


student = Student("Alice", 95)
print(student.introduce())
```

`Student` 继承了 `Person`，并重写了 `introduce()` 方法。`super()` 用于调用父类行为。

### 8.2 对对象列表排序

多数情况下，不必为排序实现比较运算符，直接使用 `key` 更清楚：

```python
students = [
    Student("Tom", 82),
    Student("Alice", 95),
    Student("Bob", 76),
]

students.sort(key=lambda student: student.score, reverse=True)

for student in students:
    print(student.introduce())
```

## 9. 异常处理

当输入或外部资源不可靠时，用 `try`/`except` 处理可以预期的错误：

```python
def divide_from_input():
    try:
        left = float(input("被除数："))
        right = float(input("除数："))
        result = left / right
    except ValueError:
        print("请输入数字。")
    except ZeroDivisionError:
        print("除数不能为 0。")
    else:
        print(f"结果：{result}")
    finally:
        print("计算结束。")


if __name__ == "__main__":
    divide_from_input()
```

| 语句 | 执行时机 |
| --- | --- |
| `try` | 尝试执行可能失败的代码 |
| `except` | 捕获指定类型的异常 |
| `else` | 没有异常时执行 |
| `finally` | 无论成功或失败都会执行 |

尽量捕获明确的异常类型，而不是直接写空泛的 `except Exception`。

## 10. 文件读写

推荐使用 `with` 打开文件，代码块结束后文件会自动关闭：

```python
from pathlib import Path

note_path = Path("notes.txt")

note_path.write_text("第一行\n", encoding="utf-8")

with note_path.open("a", encoding="utf-8") as file:
    file.write("第二行\n")

content = note_path.read_text(encoding="utf-8")
print(content)
```

常用打开模式：

| 模式 | 作用 |
| --- | --- |
| `"r"` | 只读；文件必须存在 |
| `"w"` | 写入；覆盖已有内容或创建文件 |
| `"a"` | 追加；在末尾写入内容 |
| `"x"` | 新建；文件已存在时抛出异常 |
| `"b"` | 二进制模式，例如 `"rb"` |

文本文件通常使用 `encoding="utf-8"`。使用 `file.seek()` 时要注意：在文本模式中，不适合随意按字节从当前位置或末尾偏移；需要精确处理二进制位置时，应使用 `"rb"` 或 `"rb+"`。

## 11. 小练习：统计成绩

将下面代码保存为 `grade_report.py` 并运行：

```python
def average(scores):
    return sum(scores) / len(scores)


def main():
    students = {
        "Alice": [92, 88, 95],
        "Bob": [70, 76, 68],
        "Tom": [85, 91, 80],
    }

    ranking = []
    for name, scores in students.items():
        ranking.append((name, average(scores)))

    ranking.sort(key=lambda item: item[1], reverse=True)

    for index, (name, score) in enumerate(ranking, start=1):
        print(f"{index}. {name}: {score:.1f}")


if __name__ == "__main__":
    main()
```

练习目标：

1. 增加一个学生和三次成绩。
2. 只输出平均分不低于 80 的学生。
3. 将排名结果写入 `ranking.txt`。
4. 尝试将 `students` 数据拆分到另一个模块中导入使用。

## 12. 初学者常见错误速查

| 错误或困惑 | 正确理解或处理方式 |
| --- | --- |
| 写成 `mian` | 程序入口函数通常命名为 `main` |
| `if __name__ == "__main__":` 下没有缩进 | 下一行调用代码必须缩进 |
| 使用 `python -v` 查看版本 | 使用 `python --version` 或 `python -V`；`-v` 是详细导入日志 |
| 用 `list`、`str` 作为变量名 | 改为 `numbers`、`message` 等业务名称 |
| 以为 `input()` 返回数字 | 需要显式转换，例如 `int(input(...))` |
| 忘记 `range()` 不含结束值 | `range(1, 5)` 只生成 `1, 2, 3, 4` |
| 安装库后仍无法导入 | 确认激活了正确 Conda 环境，并用 `python -m pip` 安装 |

## 继续学习

- [Python 官方教程（简体中文）](https://docs.python.org/zh-cn/3/tutorial/)
- [Python 标准库文档](https://docs.python.org/zh-cn/3/library/)
- [Conda 环境管理入门](./Conda.md)
