# Conda 环境管理入门

> 目标：学会用 Conda 为不同项目创建互不干扰的 Python 环境，并能够安装依赖、导出配置和排查常见问题。

## 1. 为什么使用虚拟环境

一个 Python 项目通常依赖特定版本的 Python 和第三方库。例如：

- 项目 A 需要 Python 3.10 和 `numpy` 1.x。
- 项目 B 需要 Python 3.12 和更新版本的 `numpy`。

如果所有包都安装在同一个全局 Python 中，版本冲突会越来越多。Conda 环境就是一个隔离的工作目录：每个环境拥有自己的 Python 解释器和依赖包。

常用名词：

| 名词 | 含义 |
| --- | --- |
| `base` | 安装 Conda 后自带的基础环境，通常只用于管理环境 |
| 环境（environment） | 为某个项目准备的一套 Python 和依赖 |
| 包（package） | `numpy`、`requests` 等可安装的软件库 |
| channel | Conda 下载包的软件源，例如 `defaults`、`conda-forge` |

## 2. 开始之前

打开终端后，先确认 Conda 是否可用：

```bash
conda --version
```

如果能看到版本号，例如 `conda 25.x.x`，即可继续。

如果终端提示找不到 `conda`，常见处理方式是：

```bash
conda init
```

执行后关闭并重新打开终端。在 Windows 中也可以先使用安装时附带的 **Anaconda Prompt** 或 **Miniforge Prompt**。

## 3. 第一个环境：从创建到退出

以下示例创建一个用于学习的环境 `py-study`，并安装 Python 与 `pip`：

```bash
conda create --name py-study python=3.12 pip
conda activate py-study
python --version
```

命令说明：

| 命令 | 作用 |
| --- | --- |
| `conda create --name py-study python=3.12 pip` | 创建名为 `py-study` 的环境 |
| `conda activate py-study` | 进入该环境 |
| `python --version` 或 `python -V` | 查看当前正在使用的 Python 版本 |

激活后，终端提示符前通常会出现 `(py-study)`。离开当前环境时执行：

```bash
conda deactivate
```

注意：`conda deactivate` 后面不需要写环境名。

## 4. 环境管理常用命令

### 4.1 查看与切换环境

```bash
# 查看所有环境；当前环境前有 * 标记
conda env list

# 激活指定环境
conda activate py-study

# 退出当前环境
conda deactivate
```

### 4.2 创建不同用途的环境

```bash
# 创建环境时指定 Python 版本
conda create -n data-analysis python=3.12

# 复制已有环境，适合在升级依赖前做实验
conda create -n py-study-backup --clone py-study
```

`-n` 是 `--name` 的简写。环境名称建议使用小写字母、数字和短横线，例如 `web-api`。

### 4.3 删除环境

先退出要删除的环境，再执行：

```bash
conda deactivate
conda env remove -n py-study-backup
```

删除环境会删除其中安装的包，项目源码不会被删除。

## 5. 安装和管理第三方包

### 5.1 优先使用 Conda 安装可用的包

```bash
conda activate py-study
conda install numpy pandas
conda list
```

查看某个包是否已安装：

```bash
conda list numpy
```

更新或移除包：

```bash
conda update numpy
conda remove numpy
```

### 5.2 需要时使用 pip

有些 Python 包在当前 Conda 软件源中不存在，可以在已经激活的环境中使用 `pip`：

```bash
python -m pip install requests
python -m pip show requests
```

推荐写成 `python -m pip`，因为它能明确使用当前环境对应的 Python，减少把包装到错误解释器中的风险。

在同一个环境中混合安装时，建议遵循下面的顺序：

1. 先用 Conda 安装能够获取的依赖。
2. 最后用 `python -m pip install ...` 安装 Conda 中没有的包。
3. pip 安装后如果需要大量修改 Conda 包，通常重新创建环境比反复升级更稳妥。

## 6. 为项目保存可复现的环境

### 6.1 使用 `environment.yml`

在项目根目录创建 `environment.yml`：

```yaml
name: py-study
channels:
  - defaults
dependencies:
  - python=3.12
  - pip
  - numpy
  - pandas
  - pip:
      - requests
```

根据文件创建环境：

```bash
conda env create -f environment.yml
conda activate py-study
```

环境已经存在并修改了文件后，可以更新环境：

```bash
conda env update -f environment.yml --prune
```

`--prune` 表示移除配置文件中已经不再列出的包。

### 6.2 从当前环境导出直接依赖

当环境是通过命令逐步搭建的，可导出一份便于跨平台重建的配置：

```bash
conda env export --from-history > environment.yml
```

`--from-history` 只记录主动安装的主要依赖，不会把大量平台相关的间接依赖都锁死，更适合学习项目和跨系统分享。

## 7. 确认正在使用正确的 Python

安装包之前，先确认当前终端确实使用目标环境。

通用检查：

```bash
conda env list
python --version
python -c "import sys; print(sys.executable)"
```

Windows PowerShell 还可使用：

```powershell
Get-Command python
```

Linux 或 macOS 还可使用：

```bash
which python
```

如果 Python 路径没有指向当前 Conda 环境，请重新执行 `conda activate <环境名>` 后再安装包或运行程序。

## 8. 常见问题

### `conda activate` 提示需要初始化 shell

```bash
conda init
```

重新打开终端后再激活环境。如果只在某一种 shell 中失败，例如 PowerShell，可执行：

```powershell
conda init powershell
```

### 安装了包，但运行程序时提示 `ModuleNotFoundError`

通常是“安装包的环境”和“运行程序的环境”不同。执行：

```bash
python -c "import sys; print(sys.executable)"
python -m pip --version
conda list
```

确认路径一致后，在目标环境中重新安装依赖。

### 环境安装混乱，怎样快速重新开始

对于练习项目，最简单的方法通常是删除并按配置文件重建：

```bash
conda deactivate
conda env remove -n py-study
conda env create -f environment.yml
```

## 9. 推荐学习流程

1. 为每个项目创建单独的 Conda 环境。
2. 激活环境后再执行 `python`、`conda install` 或 `python -m pip install`。
3. 将主要依赖写入 `environment.yml`。
4. 在项目 README 中记录启动命令和环境创建方式。
5. 进入 Python 语法学习笔记：[Conda-python.md](./Conda-python.md)。

## 参考资料

- [Conda 官方文档：管理环境](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html)
- [Conda 官方文档：管理包](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-pkgs.html)
- [Conda 官方文档：pip 与 Conda 的协作建议](https://docs.conda.io/projects/conda/en/latest/user-guide/configuration/pip-interoperability.html)
