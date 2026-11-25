# 7-Python环境与基础

[总目录](总目录.md) · [上一篇：人工智能与边缘计算基础](6-%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E4%B8%8E%E8%BE%B9%E7%BC%98%E8%AE%A1%E7%AE%97%E5%9F%BA%E7%A1%80.md) · [下一篇：PyTorch与YOLOv5训练及数据标注](8-PyTorch%E4%B8%8EYOLOv5%E8%AE%AD%E7%BB%83%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%87%E6%B3%A8.md)

[TOC]

<a id="part-11"></a>

## 7.1 搭建Python环境

### 7.1.1 安装conda

Conda 是一个开源的软件包管理系统和环境管理系统，它可以用于安装、管理和升级软件包和依赖项，我们这里使用 conda 的目的只是构建一个虚拟环境，所以选择轻量化的miniconda。miniconda 的官方链接如下所示：

https://docs.conda.io/en/latest/miniconda.html

进入 miniconda 的网址后如下所示：

可以看到下方有各个系统的安装包，我们选择 Miniconda3 Linux 64-bit 和 Miniconda3 Linux-aarch64 64-bit 两个版本的安装包进行下载.

本章节要用到的是 Miniconda3-latest-Linux-x86_64.sh 安装包，而 Miniconda3-latest-Linux-a

arch64.sh 安装包会用在之后 RKNN Toolkit lite2 环境搭建中。

首先将 Miniconda3-latest-Linux-x86_64.sh 安装包拷贝到虚拟机 ubuntu 上。

切换到普通用户

随后使用“./Miniconda3-latest-Linux-x86_64.sh”命令进行安装，根据提示，输入回车和“yes”，等待安装完成。

安装完成之后会自动设置环境变量，打开新的终端，发现用户名前出现（base），就代表安装成功了，如下图所示：

![image-20240726124631742](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240726124631742.png)

   Linux 用户的配置文件通常是 `~/.condarc`；Windows 通常是 `%USERPROFILE%\.condarc`。下面按实际系统编辑，不要把 Windows 路径用于 Linux。

```
channels: 
  - defaults
show_channel_urls: true
channel_alias: https://mirrors.tuna.tsinghua.edu.cn/anaconda
default_channels: 
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/pro
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels: 
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  msys2: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  bioconda: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  menpo: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  simpleitk: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

```yaml
channels:
  - defaults
show_channel_urls: true
default_channels:
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r
  - https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/msys2
custom_channels:
  conda-forge: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
  pytorch: https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud
```

经过上面的步骤之后就会将 conda 镜像地址更改为清华源，可以极大的提高安装软件的速度。

### 7.1.2 windows配置

> conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
> conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
> conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/r/
> conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
> conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
> conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch
>

> #设置搜索时显示通道地址
> conda config --set show_channel_urls yes

### 7.1.3 创建 RKNN 虚拟环境

为了避免环境后续学习中环境的冲突问题，这里使用 conda 创建 RKNN 虚拟环境，使用命令如下所示：

> conda create -n rknn python=3.10

命令执行之后，首先会要求安装一系列软件包，输入 y 确认即可.

然后使用“ conda activate rknn ”激活相应得 rknn 环境，如下图所示：

![image-20240726124825321](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240726124825321.png)

可以看到，标识符由“base”变成了“rknn”,

### 7.1.4 Python基础语法

#### 7.1.4.1 Python与C的主要差异

- **语法简洁**：Python使用缩进代替大括号，省略分号
- **动态类型**：变量无需声明类型
- **内置高级数据结构**：列表、字典、集合等
- **自动内存管理**：无需手动分配/释放内存
- **解释型语言**：无需编译，直接运行

#### 7.1.4.2 基础语法

**Hello World**

```
print("Hello, World!")  # 不需要分号，注释用#
```

**变量与数据类型**

```
# 变量直接赋值，无需声明类型
x = 10          # 整数
y = 3.14        # 浮点数
name = "Alice"  # 字符串
is_true = True  # 布尔值

# 类型查看
print(type(x))  # <class 'int'>
```

**运算符**

```
# 算术运算符与C类似
a = 10 + 3      # 13
b = 10 / 3      # 3.333... (浮点除法)
c = 10 // 3     # 3 (整数除法)
d = 10 ** 3     # 1000 (幂运算)

# 逻辑运算符
and or not      # 代替C的 && || !
```

#### 7.1.4.3 控制结构

**条件语句**

```
# if-elif-else结构
age = 18
if age < 18:
    print("未成年")
elif age == 18:
    print("刚成年")
else:
    print("成年")
```

**循环**

```
# for循环 (类似C的foreach)
for i in range(5):  # 0到4
    print(i)

# while循环
count = 0
while count < 5:
    print(count)
    count += 1  # Python没有++运算符
```

#### 7.1.4.4 函数

```
# 函数定义
def add(a, b):
    return a + b

# 调用函数
result = add(3, 4)
print(result)  # 7

# 默认参数
def greet(name="World"):
    print(f"Hello, {name}!")

greet()        # Hello, World!
greet("Alice") # Hello, Alice!
```

#### 7.1.4.5 数据结构

**列表**（类似数组但更强大）

```
numbers = [1, 2, 3, 4, 5]
numbers.append(6)     # 添加元素
print(numbers[0])     # 1 (索引从0开始)
print(numbers[-1])    # 6 (负索引表示从后往前)

# 切片操作
print(numbers[1:3])   # [2, 3]
print(numbers[:3])    # [1, 2, 3]
print(numbers[3:])    # [4, 5, 6]
```

#### 7.1.4.6 字典（键值对）

```
person = {
    "name": "Alice",
    "age": 25,
    "city": "New York"
}

print(person["name"])  # Alice
person["age"] = 26     # 修改值
person["job"] = "Engineer"  # 添加新键值对
```

#### 7.1.4.7 元组（不可变列表）

```
point = (10, 20)
x, y = point  # 解包
```

#### 7.1.4.8 集合（无序不重复元素）

```
unique_numbers = {1, 2, 3, 3, 4}
print(unique_numbers)  # {1, 2, 3, 4}
```

#### 7.1.4.9 文件操作

```
# 读取文件
with open("file.txt", "r") as file:
    content = file.read()

# 写入文件
with open("output.txt", "w") as file:
    file.write("Hello, Python!")
```

#### 7.1.4.10 面向对象编程

```
class Person:
    # 构造函数
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def greet(self):
        print(f"Hello, my name is {self.name}")

# 创建对象
alice = Person("Alice", 25)
alice.greet()  # Hello, my name is Alice
```

#### 7.1.4.11 异常处理

```
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零!")
finally:
    print("这段代码总会执行")
```

#### 7.1.4.12 常用内置函数

```
# 输入输出
name = input("请输入你的名字: ")
print(f"你好, {name}!")

# 类型转换
num_str = "123"
num = int(num_str)

# 长度
length = len([1, 2, 3])  # 3

# 范围
for i in range(5):       # 0,1,2,3,4
    print(i)
```

#### 7.1.4.13 模块和导入

```
# 导入整个模块
import math
print(math.sqrt(16))  # 4.0

# 导入特定函数
from random import randint
print(randint(1, 10))  # 随机1-10的数字
```

### 7.1.5 pip工具

pip 是 Python 的包管理工具，用于安装和管理 Python 第三方库。它是 Python 生态系统中最重要的工具之一，相当于其他语言的包管理器（如 npm for JavaScript, gem for Ruby）。

**主要功能**：

- 从 PyPI (Python Package Index) 安装包
- 管理已安装的包（查看、升级、卸载）
- 处理包依赖关系

#### 7.1.5.1 基本使用示例

**检查 pip 版本**

```
pip --version
```

**安装包**

```
pip install package_name
# 示例：安装 requests 库
pip install requests
```

**安装特定版本**

```
pip install package_name==version
# 示例：安装 Django 2.2.5
pip install django==2.2.5
```

**升级包**

```
pip install --upgrade package_name
# 示例：升级 numpy
pip install --upgrade numpy
```

**卸载包**

```
pip uninstall package_name
# 示例：卸载 flask
pip uninstall flask
```

**查看已安装的包**

```
pip list
```

**查看过时的包**

```
pip list --outdated
```

**查看包详情**

```
pip show package_name
# 示例：查看 requests 包信息
pip show requests
```

**导出和导入依赖**

```
# 导出当前环境的所有包到 requirements.txt
pip freeze > requirements.txt

# 从 requirements.txt 安装所有依赖
pip install -r requirements.txt
```

#### 7.1.5.2 修改 pip 源（镜像源）

由于国内访问 PyPI 官方源速度较慢，可以切换为国内镜像源提高下载速度。

**临时使用镜像源**

```
pip install package_name -i https://pypi.tuna.tsinghua.edu.cn/simple
# 示例：使用清华源安装 requests
pip install requests -i https://pypi.tuna.tsinghua.edu.cn/simple
```

**常用国内镜像源**

- 清华：https://pypi.tuna.tsinghua.edu.cn/simple
- 阿里云：https://mirrors.aliyun.com/pypi/simple
- 腾讯云：https://mirrors.cloud.tencent.com/pypi/simple
- 华为云：https://repo.huaweicloud.com/repository/pypi/simple
- 豆瓣：https://pypi.douban.com/simple

**永久修改 pip 源** 

**Linux/macOS 系统**

在用户目录下创建 `.pip` 文件夹

```
mkdir ~/.pip
```

创建 `pip.conf` 文件

```
vim ~/.pip/pip.conf
```

添加以下内容：

```
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn

或

[global]
index-url = https://mirrors.aliyun.com/pypi/simple
trusted-host = mirrors.aliyun.com

```

---

[总目录](总目录.md) · [上一篇：人工智能与边缘计算基础](6-%E4%BA%BA%E5%B7%A5%E6%99%BA%E8%83%BD%E4%B8%8E%E8%BE%B9%E7%BC%98%E8%AE%A1%E7%AE%97%E5%9F%BA%E7%A1%80.md) · [下一篇：PyTorch与YOLOv5训练及数据标注](8-PyTorch%E4%B8%8EYOLOv5%E8%AE%AD%E7%BB%83%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%87%E6%B3%A8.md)
