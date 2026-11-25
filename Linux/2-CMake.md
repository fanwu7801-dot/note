# 2-CMake

[总目录](总目录.md) · [上一篇：Ubuntu开发环境与SSH文件共享](1-Ubuntu%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83%E4%B8%8ESSH%E6%96%87%E4%BB%B6%E5%85%B1%E4%BA%AB.md) · [下一篇：Linux串口编程与电气接口](3-Linux%E4%B8%B2%E5%8F%A3%E7%BC%96%E7%A8%8B%E4%B8%8E%E7%94%B5%E6%B0%94%E6%8E%A5%E5%8F%A3.md)

[TOC]

<a id="part-4"></a>

## 2.1 cmake

### 2.1.1 介绍

CMake 是个一个开源的跨平台自动化建构系统，用来管理软件建置的程序，并不依赖于某特定编译器，并可支持多层目录、多个应用程序与多个函数库。 

CMake 通过使用简单的配置文件 CMakeLists.txt，自动生成不同平台的构建文件（如 Makefile、Ninja 构建文件、Visual Studio 工程文件等），简化了项目的编译和构建过程。

CMake 本身不是构建工具，而是生成构建系统的工具，它生成的构建系统可以使用不同的编译器和工具链。

**优点**

- **跨平台支持：** CMake 支持多种操作系统和编译器，使得同一份构建配置可以在不同的环境中使用。
- **简化配置：** 通过 CMakeLists.txt 文件，用户可以定义项目结构、依赖项、编译选项等，无需手动编写复杂的构建脚本。
- **自动化构建：** CMake 能够自动检测系统上的库和工具，减少手动配置的工作量。
- **灵活性：** 支持多种构建类型和配置（如 Debug、Release），并允许用户自定义构建选项和模块。

**配置方式**

- **CMakeLists.txt 文件：** CMake 的配置文件，用于定义项目的构建规则、依赖关系、编译选项等。每个 CMake 项目通常包含一个或多个 CMakeLists.txt 文件。
- **构建目录：** 为了保持源代码的整洁，CMake 鼓励使用独立的构建目录（Out-of-source 构建）。这样，构建生成的文件与源代码分开存放。

**使用流程**

1. **编写 CMakeLists.txt 文件：** 定义项目的构建规则和依赖关系。
2. **生成构建文件：** 使用 CMake 生成适合当前平台的构建系统文件（例如 Makefile、Visual Studio 工程文件）。
3. **执行构建：** 使用生成的构建系统文件（如 `make`、`ninja`、`msbuild`）来编译项目。

**安装**

CMake 可以在不同操作系统上进行安装，本文将介绍 Windows、Linux 以及 macOS 系统下的安装与配置。

CMake 安装包下载地址：https://cmake.org/download/。

对于 Ubuntu 或 Debian 系统：

> sudo apt install gcc g++ make cmake -y

### 2.1.2 使用cmake编译程序

CMakeLists.txt 文件使用一系列的 CMake 指令来描述构建过程。常见的指令包括：

1、指定 CMake 的最低版本要求：

```
cmake_minimum_required(VERSION <version>)
```

例如：

```
cmake_minimum_required(VERSION 3.10)
```

2、定义项目的名称和使用的编程语言：

```
project(<project_name> [<language>...])
```

例如：

```
project(MyProject CXX)
```

3、指定要生成的可执行文件和其源文件：

```
add_executable(<target> <source_files>...)
```

例如：

```
add_executable(MyExecutable main.cpp other_file.cpp)
```

**实验**

```c
#include <stdio.h>

int main(int argc, char *argv[]) {
    printf("Hello, woniu!\n");
    return 0;
}
```

```cmake
# 指定cmake的最低版本
cmake_minimum_required(VERSION 3.10)
# 设置项目名称
project(hello)
# 配置项目的源文件
add_executable(hello 
    testc.c
)
```

```shell
cmake .
make
```

### 2.1.3 优化配置

```cmake
# 指定cmake的最低版本
cmake_minimum_required(VERSION 3.10)
# 设置项目名称
project(hello)

# 配置项目的源文件
add_executable(testc 
    src/testc.c
    src/caculator.c
)
# 一次编译多个源文件
add_executable(testcpp 
    src/testcpp.cpp
)

# 配置包含目录
target_include_directories(testc PUBLIC include)

# 配置安装路径的前缀
set(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_SOURCE_DIR})

# 配置安装目录
install(TARGETS testc testcpp
    RUNTIME DESTINATION install)

```

```shell
mkdir build
cd build
cmake ..
make 
make install
```

### 2.1.4 使用shell脚本优化编译

```shell
if [ ! -d "build" ]; then
    mkdir build
fi
cd build
cmake -DCMAKE_INSTALL_PREFIX=../ ..
make
make install
cd -
```

### 2.1.5 如何分享自己的程序

> 1. 直接分享编译好的程序
> 2. 直接分享代码，开源
> 3. 分享动态库，不开源

### 2.1.6 编译动态库

```cmake
# 指定cmake的最低版本
cmake_minimum_required(VERSION 3.10)
# 设置项目名称
project(hello)

# 指定编译为库的源文件 SHARED 动态库  STATIC静态库
add_library(caculator SHARED
    src/caculator.c
)

# 配置安装路径的前缀
set(CMAKE_INSTALL_PREFIX /usr/local)

# 配置安装目录
install(TARGETS caculator
    LIBRARY DESTINATION lib)
    
# 头文件的安装
install(DIRECTORY include/
    DESTINATION include
    FILES_MATCHING PATTERN "*.h"
)
```

### 2.1.7 使用动态库

1. gcc中使用

编译

```shell
 gcc main.c -L/usr/local/lib -lcaculator
```

运行

Linux 动态链接器会按规则搜索共享库；`LD_LIBRARY_PATH` 只是其中一种来源，还可能使用程序中的 RPATH/RUNPATH、`ld.so.cache` 和系统默认库目录，并不是所有库路径都保存在这个环境变量中。

```shell
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib
./a.out
```

2. 把库直接放到linux系统的标准库目录中，（一般不这样用。）

   ```cmake
   # 指定cmake的最低版本
   cmake_minimum_required(VERSION 3.10)
   # 设置项目名称
   project(hello)
   
   # 指定编译为库的源文件 SHARED 动态库  STATIC静态库
   add_library(caculator SHARED
       src/caculator.c
   )
   
   # 配置安装路径的前缀
   set(CMAKE_INSTALL_PREFIX /usr)
   
   # 配置安装目录   /usr/lib/libcaculator.so
   install(TARGETS caculator
       LIBRARY DESTINATION lib)
       
   # 头文件的安装  /usr/include/caculator.h
   install(DIRECTORY include/
       DESTINATION include
       FILES_MATCHING PATTERN "*.h"
   )
   ```

   使用

   ```shell
   gcc main.c  -lcaculator
   ./a.out
   ```

3. cmake中使用

   ```cmake
   # 指定cmake的最低版本
   cmake_minimum_required(VERSION 3.10)
   # 设置项目名称
   project(testadd)
   
   # 配置项目的源文件
   add_executable(testadd 
       src/main.c
   )
   
   set(CalLIB ${CMAKE_CURRENT_SOURCE_DIR}/../3rdparty/caculator/lib/libcaculator.so)                              
   
   message("CalLIB: ${CalLIB}")
   
   # 配置包含目录
   target_include_directories(testadd PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/../3rdparty/caculator/include)
   
   # 配置链接库
   target_link_libraries(testadd PUBLIC ${CalLIB})
   
   # 配置安装路径的前缀
   set(CMAKE_INSTALL_PREFIX ${CMAKE_CURRENT_SOURCE_DIR})
   
   # 配置安装目录
   install(TARGETS testadd
       RUNTIME DESTINATION install)
   ```

   ```shell
   export LD_LIBRARY_PATH=/home/richard/proj/0623-2-cmake_lib/lib
   ```

![image-20240630151028353](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630151028353.png)

---

[总目录](总目录.md) · [上一篇：Ubuntu开发环境与SSH文件共享](1-Ubuntu%E5%BC%80%E5%8F%91%E7%8E%AF%E5%A2%83%E4%B8%8ESSH%E6%96%87%E4%BB%B6%E5%85%B1%E4%BA%AB.md) · [下一篇：Linux串口编程与电气接口](3-Linux%E4%B8%B2%E5%8F%A3%E7%BC%96%E7%A8%8B%E4%B8%8E%E7%94%B5%E6%B0%94%E6%8E%A5%E5%8F%A3.md)
