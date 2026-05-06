# Python 编程基础

## 变量和数据类型

Python 是一种动态类型语言，你不需要提前声明变量的类型。基本数据类型包括：

- 整数 (int): 如 42, -10, 0
- 浮点数 (float): 如 3.14, -0.5, 2.0
- 字符串 (str): 如 "Hello", 'World'
- 布尔值 (bool): True, False
- 列表 (list): 如 [1, 2, 3], ['a', 'b', 'c']
- 字典 (dict): 如 {'name': 'Tom', 'age': 18}

## 控制流

Python 使用缩进来表示代码块，而不是大括号。

if 语句：
```python
if age >= 18:
    print("成年人")
else:
    print("未成年人")
```

for 循环：
```python
for i in range(5):
    print(i)
```

while 循环：
```python
while count < 10:
    count += 1
```

## 函数

定义函数使用 def 关键字：

```python
def greet(name):
    return f"Hello, {name}!"

result = greet("World")
print(result)  # 输出: Hello, World!
```

## 列表推导式

列表推导式是 Python 中创建列表的简洁方式：

```python
# 创建 1-10 的平方数列表
squares = [x**2 for x in range(1, 11)]
# 结果: [1, 4, 9, 16, 25, 36, 49, 64, 81, 100]

# 筛选偶数
evens = [x for x in range(1, 21) if x % 2 == 0]
# 结果: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
```

## 字典操作

字典是键值对的集合：

```python
# 创建字典
person = {
    "name": "Alice",
    "age": 30,
    "city": "Beijing"
}

# 访问值
print(person["name"])  # Alice

# 添加键值对
person["email"] = "alice@example.com"

# 遍历字典
for key, value in person.items():
    print(f"{key}: {value}")
```

## 异常处理

使用 try-except 捕获异常：

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
except Exception as e:
    print(f"发生错误: {e}")
finally:
    print("无论如何都会执行")
```

## 文件操作

```python
# 读取文件
with open("file.txt", "r", encoding="utf-8") as f:
    content = f.read()

# 写入文件
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Hello, World!")

# 逐行读取
with open("file.txt", "r") as f:
    for line in f:
        print(line.strip())
```

## 类和对象

```python
class Dog:
    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        return f"{self.name} says Woof!"

    def introduce(self):
        return f"I'm {self.name}, {self.age} years old"

# 创建实例
my_dog = Dog("Buddy", 3)
print(my_dog.bark())      # Buddy says Woof!
print(my_dog.introduce()) # I'm Buddy, 3 years old
```

## 装饰器

装饰器用于修改函数的行为：

```python
def my_decorator(func):
    def wrapper():
        print("执行前")
        func()
        print("执行后")
    return wrapper

@my_decorator
def say_hello():
    print("Hello!")

say_hello()
# 输出:
# 执行前
# Hello!
# 执行后
```

## 模块导入

```python
# 导入整个模块
import math
print(math.sqrt(16))

# 导入特定函数
from random import randint
print(randint(1, 10))

# 导入并重命名
import numpy as np
from pandas import DataFrame as df
```

## 虚拟环境

使用虚拟环境隔离项目依赖：

```bash
# 创建虚拟环境
python -m venv myenv

# 激活虚拟环境
# macOS/Linux:
source myenv/bin/activate
# Windows:
myenv\Scripts\activate

# 安装包
pip install package_name

# 退出虚拟环境
deactivate
```

## 常用内置函数

- `print()`: 输出内容
- `len()`: 获取长度
- `type()`: 获取类型
- `range()`: 生成数字序列
- `enumerate()`: 获取索引和值
- `zip()`: 合并多个可迭代对象
- `map()`: 对每个元素应用函数
- `filter()`: 筛选元素
- `sorted()`: 排序
- `sum()`: 求和
- `max()`, `min()`: 最大值、最小值
