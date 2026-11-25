# 28-Buildroot

[总目录](总目录.md) · [上一篇：Qt交叉编译与部署](27-Qt交叉编译与部署.md) · [下一篇：镜像打包分区与upgrade_tool烧录](29-镜像打包分区与upgrade_tool烧录.md)

[TOC]

<a id="part-47"></a>

## 28.1 Buildroot 系统构建

在上一个章节我们学习了使用 busybox 来构建文件系统，但是 busybox 构建的文件系统很多东西需要自己交叉编译添加，某些软件需要自己去移植，所以移植过程是非常繁琐的。本章节我们来学习另外一种非常实用的根文件系统构建方法——使用 buildroot 来构建根文件系统。buildroot 不仅集成了 busybox，而且还集成了各种常见的第三方库和软件，需要什么软件，选择哪个软件就好，buildroot 上手门槛低，极大的方便了嵌入式 Linux 开发人员构建根文件系统。

### 28.1.1 buildroot 基本介绍

Buildroot 是一个可以使用交叉编译简单且自动化地为嵌入式系统构建完整 Linux 系统的工具。Buildroot 可以为你的系统生成交叉编译工具链，根文件系统，Linux 内核镜像和引导加载程序。Buildroot 可以独立地用于这些选项的任意组合（比如，你可以使用现有的交叉编译工具链，并且仅仅只编译文件系统）。

Buildroot 主要用于使用嵌入式系统的开发者，嵌入式系统通常使用的处理器并不是 PC 电脑上的X86处理器，他们可以是PowerPc处理器，MIPS处理器或者ARM处理器等等。Buildroot支持很多处理器，它还具有一些可用目标板的默认配置。除此之外，许多第三方项目的 SDK都是基于 buildroot 开发。

构建开源软件包工作流程大致如下所示：

> 1 获取：获取软件包的源码
>
> 2 解压：解压软件包源码
>
> 3 补丁：针对缺陷修复和增加的功能应用补丁
>
> 4 配置：根据环境准备构建过程
>
> 5 安装：复制二进制和辅助文件到目标目录
>
> 6 打包：为在其他系统上安装而打包二进制和辅助文件

如上所示，我们可以看到构建每个软件包的工作流程几乎是相同的，buildroot 主要的功能就是把这些重复操作自动化，用户只需要勾选上所需软件包，便自动完成以上所有操作。Buildroot 生成 uboot Linux Kernel 的编译工作流程是差不多的，只要配置好自定义的参数，在buildroot 配置好编译生成即可。

### 28.1.2 获取 buildroot 官方源码

Buildroot 每隔三个月发布一次版本，2 月 5 月 8 月 11 月各发布一次。版本号格式是YYYY.MM，比如 2019.02、2019.08 等等。

使用浏览器打开以下网址下载 buildroot 最新的源码。

https://buildroot.org/download.html

本教程中使用的 buildroot 版本是 Buildroot-2022.05.tar.bz2，建议大家和本教程保持一致。

点击 buildroot-2022.05.tar.bz2 进行下载。下载之后使用 SSH 拷贝到 ubuntu 虚拟机中。

输入以下命令解压压缩包：

我们进入 buildroot-2022.05 目录，

![image-20240713164058507](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164058507.png)

### 28.1.3 buildroot 目录简介

Buildroot 基本上是一组 Makefile 文件，可以使用正确的选项对所需的软件进行下载，配置和编译。它还包含各种软件包的补丁，主要是那些涉及交叉编译工具链（gcc,bin utils 和uClibc）的软件包。每个软件包基本只有一个 Makefile 文件，它们以.mk扩展名命名。

Buildroot 编译之前的目录如下所示：

![image-20240713164142964](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164142964.png)

Buildroot 编译之后会多出来俩个文件夹，一个是 dl 文件夹，一个是 output 目录文件夹，最终生成的板子镜像在 output/images 目录下

目录介绍

> buildroot/arch:目录存放 CPU 架构相关的配置脚本，如 arm/mips/x86 ，这些 CPU 相关的配置，在制作工具链，编译 boot 和内核时很关键。
> buildroot/board:存放某个具体单板紧密相关的文件，比如内核配置文件、sd 卡制作脚本、rootfs覆盖文件等。
> buildroot/boot:存放各种 Bootloaders 相关的的补丁*.patch、校验文件*.hash、构建脚本*.mk、配置选项 Config.in
> buildroot/configs: 存放各个单板的 buildroot 配置文件
> buildroot/dl:目录存放从官网上下载的开源软件包，第一次下载后，下次就不会再去从官网下载了，而是从 dl/目录下拿开源包，以节约时间。本身下载通常都是很慢的,你可以手动找到相关包下载后放到这里就 OK 了,make 时会自动检测这个目录. buildroot/docs: 存放 pdf,html 格式的 buildroot 详细说明。
> buildroot/fs:放各种文件系统的源代码
> buildroot/fs/skeleton:放生成文件系统镜像的地方，及板子里面的系统*
> *buildroot/linux:存放 Linux 的构建脚本*.mk 和配置选项 Config.in
> buildroot/package/: 此目录下放着应用软件的配置文件，每个应用软件的配置文件有 Config.in 和软件包名字.mk。软件包名字.mk 文件可以下载应用软件包，是 Makefile 脚本的自动构建脚本。
> buildroot/output/: 是编译的输出文件夹，里面的 build/目录存放着解压后的各种软件包编译完后的现场。
> build:所有源码包解压出来的文件存放地和编译的发生地
> staging:包含了根文件系统的层次结构，编译生成的所有头文件和库，以及其他开发文件，体积较大；
> target:目录是用来制作 rootfs 的，里面放着 Linux 系统基本的目录结构，以及各种编译好的应用库和 bin 可执行文件。
> Images:目录下就是最终生成的可烧写到板子上的各种 image。
> host:是由各类源码编译后在你主机上运行的工具的安装目录,如 arm-linux-gcc 就是安装在这里;编译出来的主机工具在 host/usr 下;根目录所需要的库及一些基本目录就在
> host/<tuple>/sysroot/或 host/usr/<tuple>/sysroot/里
> buildroot/support:存放一些为 bulidroot 提供功能支持的脚本、配置文件
> buildroot/system:这里就是根目录的主要骨架了和相关的启动初始化配置,当制作根目录时就是将此处的文件 cp 到 output 里去.然后再安装 toolchain 的动态库和你勾选的 package 的可执行文件之类的. buildroot/toolchain:存放制作各种交叉编译工具链的构建脚本*.mk 和配置选项 Config.in
> buildroot/utils:存放一些 buildroot 的实用脚本和工具。
> buildroot/CHANGES:buildroot 的修改日志。
> buildroot/.config:make menuconfig 后生成的最终配置文件。
> buildroot/Config.in ：所有 Config.in 的入口，也是 Build options 的提供者
> buildroot/Config.in.legacy ：Legacy config options 的提供者
> buildroot/DEVELOPERS ：开发人员列表，N 后面是开发人员名字，F 后面是开发的软件
> buildroot/Makefile ：顶层 Makefile
> buildroot/Makefile.legacy ：旧的 Makefile，为了支持向后兼容
> buildroot/README ：buildroot 简单说明。

### 28.1.4 buildroot 帮助命令

在 buildroot 根目录执行 make help，即可获得 buildroot 常用命令的提示信息

> root@ubuntu:/home/topeet/Linux/buildroot-2022.05# make help
> Cleaning: #清理
> clean - 删除编译产生的文件
> distclean - 删除所有非源码文件（包括.config）
> Build: #编译
> all - 编译所有
> toolchain - 编译工具链
> sdk - 编译 sdk
> Configuration: #配置
> menuconfig - 基于 curses 的 buildroot 配置界面(常用)
> nconfig - 基于 ncursesbuildroot 配置界面
> xconfig - 基于 Qt 的 buildroot 配置界面
> gconfig - 基于 GTK 的 buildroot 配置界面
> oldconfig - 解决所有.config 中未解决的符号问题(symbols)
> syncconfig - 和 oldconfig 类似，但会额外更新依赖
> olddefconfig - 和 syncconfig 类似，但会将新的 symbols 设为默认值
> randconfig - 所有选项随机配置
> defconfig - 所有选项都询问，如果设置有 BR2_DEFCONFIG，则使用它的配置
> savedefconfig - 把当前配置保存到 BR2_DEFCONFIG
> update-defconfig - 类似 savedefconfig
> allyesconfig - 所有配置选项都选择 yes
> allnoconfig - 所有配置选项都选择 no
> alldefconfig - 所有配置选项都选择 default
> randpackageconfig - 软件包选项都选择随机
> allyespackageconfig - 软件包选项都选择 yes
> allnopackageconfig - 软件包选项都选择 no
> Package-specific: #具体的包操作
> <pkg> -编译、安装该 pkg 以及其依赖
> <pkg>-source -下载该 pkg 所有文件
> <pkg>-extract -解压该 pkg(解压后放在 output/build/pkg 名字目录下)
> <pkg>-patch - 给该 pkg 打补丁
> <pkg>-depends - 编译 pkg 的依赖
> <pkg>-configure - 编译 pkg 到配置这一步
> <pkg>-build - 编译 pkg 到构造这一步
> <pkg>-show-info - 显示该 pkg 信息
> <pkg>-show-depends - 显示该 pkg 的所有依赖
> <pkg>-show-rdepends - 显示依赖该 pkg 的所有包
> <pkg>-show-recursive-depends - 递归显示该 pkg 的所有依赖
> <pkg>-show-recursive-rdepends - 递归显示依赖该 pkg 的所有包
> <pkg>-graph-depends - 图形化显示该 pkg 的所有依赖
> <pkg>-graph-rdepends - 图形化显示依赖该 pkg 的所有包
> <pkg>-dirclean - 清除该 pkg 目录(清除解压目录 output/build/pkg 名字)
> <pkg>-reconfigure - 从配置这一步开始重新编译 pkg
> <pkg>-rebuild - 从构造这一步开始重新编译 pkg
> <pkg>-reinstall - 从安装这一步开始重新编译 pkg
> Documentation: -文档
> manual -生成各种格式的帮助手册
> manual-html - 生成 HTML 格式的帮助手册
> manual-split-html - 生成 split HTML 格式的帮助手册
> manual-pdf - 生成 PDF 格式的帮助手册
> manual-text - 生成 text 格式的帮助手册
> manual-epub - 生成 ePub 格式的帮助手册
> graph-build -生成图形化查看编译时间文件
> graph-depends - 生成图形化查看所有依赖文件
> graph-size -生成图形化查看文件系统大小文件
> list-defconfigs - 显示拥有的默认配置的单板列表
> Miscellaneous: - 杂项
> source - 下载所有要离线编译的源码到 dl 路径
> external-deps - 列出使用的所有外部包(make show-targets 的详细版)
> legal-info - 显示所有包的 license 合规性
> show-info - generate info about packages, as a JSON blurb
> pkg-stats - generate info about packages as JSON and HTML
> missing-cpe - generate XML snippets for missing CPE identifiers
> printvars - 打印所有内部指定的变量值
> show-vars - dump all internal variables as a JSON blurb; use VARS=... to limit the list to variables names matching that pattern
> make V=0|1 - 设置编译打印信息(0:安装编译 1:打印编译信息)
> make O=dir - 指定所有文件(包括.config)输出目录
> For further details, see README, generate the Buildroot manual, or consult
> it on-line at http://buildroot.org/docs.html

### 28.1.5 安装编译环境

通过查看官方手册可知构建系统需要的工具有如下图所示， 这些工具需要我们在 ubuntu虚拟机上安装。官方手册地址可以点击以下网址：https://buildroot.org/downloads/manual/manual.html#requirement

![image-20240713164536362](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164536362.png)

我们需要安装这些编译必须工具，不然编译过程会出错。我们可以使用以下命令来安装这些工具，

> sudo apt install -y sed make binutils build-essential gcc g++ patch gzip bzip2 perl tar cpio unzip rsync file bc wget

### 28.1.6 Buildroot 配置

Buildroot 可以和配置内核一样，使用 menuconfig 进行图形化配置。输入“make menuconfig” 命令可以打开图形化配置界面，

![image-20240713164626147](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164626147.png)



### 28.1.7 Buildroot 构建

#### 28.1.7.1 配置 Target option

接下来我们来一步步配置 buildroot，使用“make menuconfig”命令打开配置界面。首先我们来配置 Target option 选项，

![image-20240713164724827](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164724827.png)

Target options 参数与芯片架构相关。如下图所示，Rk3568 Rk3399 imx6ull 芯片信息如下所示：

![image-20240713164744797](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164744797.png)

在 menuconfig 中需要配置的项目和对应的内容如下所示，如果配置的是 RK3568 开发板，配置项目如下所示，此项配置需要根据芯片架构进行修改。

> Target Architecture (AArch64（little endian)) ---> #设置架构和大小端
>
> Target Binary Format(ELF)--> #设置二进制格式
>
> Target Architecture Variant(cortex-A55)--> #设置芯片架构
>
> Floating point strategy(FP-ARMv8)--> #设置浮点数的策略

![image-20240713164807385](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713164807385.png)

#### 28.1.7.2 Build options 选项

Build options 选项主要是一些编译时用到的选项,比如 dl 的路径,下载代码包使用的路径, 同时运行多个编译的上限,是否使能编译器缓冲区等等,这里按照默认就行了，此配置极少需要改动。Build options 选项具体含义如下所示：

> Commands --->
>
> │ │ ($(CONFIG_DIR)/defconfig) Location to save buildroot config \#保存 buildroot config
>
> │ │ ($(TOPDIR)/dl) Download dir #下载目录-buildroot/dl(通常使用默认配置)
>
> │ │ ($(BASE_DIR)/host) Host dir \#主机目录-buildroot/output/host(通常使用默认配置)
>
> │ │ Mirrors and Download locations ---> #镜像和下载位置
>
> │ │ (0) Number of jobs to run simultaneously (0 for auto) #同时要运行的作业数,0 代表自动
>
> │ │ [ ] Enable compiler cache #启用编译器缓存-可以加快编译速度
>
> │ │ [ ] build packages with debugging symbols #使用调试符号生成包
>
> │ │ [ ] build packages with runtime debugging info
>
> │ │ [*] strip target binaries #剥离目标二进制文件，会使文件变小
>
> │ │ () executables that should not be stripped #应该剥离的可执行文件
>
> │ │ () directories that should be skipped when stripping #剥离时应跳过的目录
>
> │ │ gcc optimization level (optimize for size) ---> #gcc 优化级别
>
> │ │ libraries (shared only) --->
>
> │ │ ($(CONFIG_DIR)/local.mk) location of a package override file #包覆盖文件的位置
>
> │ │ () global patch directories #全局修补程序目录
>
> │ │ Advanced --->
>
> │ │ ** Security Hardening Options *** #安全强化选项
>
> │ │ -*- Build code with PIC/PIE #使用 PIC/PIE 构建代码
>
> │ │ Stack Smashing Protection needs a toolchain w/ SSP *** #堆叠粉碎保护需要一个带有 SSP 的工具链
>
> │ │ RELRO Protection (Full) --->
>
> │ │ *** Fortify Source needs a glibc toolchain and optimization *

#### 28.1.7.3 配置 Toolchain

Toolchain 主要介绍如何使用 buildroot 配置内部交叉编译工具链以及外部交叉编译工具链还有如何添加自己的交叉编译工具链

> Toolchain type (Buildroot toolchain) --->
>
> ( ) Buildroot toolchain //内部交叉编译工具链
>
> ( ) External toolchain //外部交叉编译工具链

如上所示，Toolchain type 有俩个选项，选择 Buildroot toolchain 则是使用 buildroot 默认的自动化脚本从零开始制作交叉编译工具链，如果是选择 External toolchain 则是使用外部制作好的工具链。

接下来我们以设置外部交叉编译器进行演示，将交叉编译器压缩包拷贝到 Ubuntu 的 usr/local 目录下，解压缩后如下图所示：

![image-20240713165158511](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713165158511.png)

当前课程目标改为 RK SDK Linux 6.1。Buildroot 的外部工具链 headers series 必须填写工具链实际构建时使用的 Linux UAPI 头文件系列，而不是为了等于板端 uname -r 去修改 sysroot/include/linux/version.h。较旧的 UAPI 头文件通常可以服务较新的运行内核；需要新 UAPI 时应换用或重新构建匹配工具链，不能伪造版本宏。下图属于旧版课堂截图，只用于理解路径。

![image-20240713165220837](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713165220837.png)

`LINUX_VERSION_CODE` 只是版本编码，修改它不会改变实际头文件或工具链功能。例如 6.1.118 的编码为 `(6 << 16) + (1 << 8) + 118 = 393590`；这个计算仅用于理解宏，不是修改 SDK 的操作步骤。













需要配置的项目和对应的内容如下所示：

> Toolchain type (External toolchain) ---> #设置交叉编译器的类型为外部交叉编译器
> *** Toolchain External Options ***
> Toolchain (Custom toolchain) ---> #设置为 Custom toolchain，使用用户自己的交叉编译器
> Toolchain origin (Pre-installed toolchain) ---> # 设置为 Pre-installed toolchain，使用预装的交叉编译器
> (/usr/local/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu) Toolchain path (NEW)#设置外部交叉编译的路径，注意这里要写绝对路径，根据实际编译器的路径进行修改
> (aarch64-none-linux-gnu) Toolchain prefix (NEW) #设置 toolchain 的前缀，在编译器
> /usr/local/gcc-arm-9.2-2019.12-x86_64-aarch64-none-linux-gnu/bin 目录下查看
> External toolchain gcc version (9.x) ---> # 设置外部编译器 GCC 版本选择为 gcc9.x
> External toolchain kernel headers series：选择外部工具链实际使用的头文件系列；若实际是 6.1.x 才选 6.1.x。若选内部工具链，可按需求使用 6.1 头文件。
> External toolchain C library (glibc/eglibc) ---> # C 库选择 选择 glibc
> [ ] Toolchain has WCHAR support? (NEW)
> [ ] Toolchain has locale support? (NEW)
> [*] Toolchain has threads support? (NEW)
> [*] Toolchain has threads debugging support? (NEW)
> [*] Toolchain has NPTL threads support? (NEW)
> [ *] Toolchain has SSP support? (NEW)
> [ *] Toolchain has RPC support? (NEW)
> [ *] Toolchain has C++ support? (NEW)
> [ ] Toolchain has D support? (NEW)
> [ ] Toolchain has Fortran support? (NEW)
> [ ] Toolchain has OpenMP support? (NEW)
> [ ] Copy gdb server to the Target (NEW)
> *** Host GDB Options ***
> [ ] Build cross gdb for the host
> *** Toolchain Generic Options ***
> () Extra toolchain libraries to be copied to target
> () Target Optimizations 不选
> () Target linker options 不选
> [ ] Register toolchain within Eclipse Buildroot plug-in #eclipse 插件支持，不选

#### 28.1.7.4 配置 System configuration

System configuration 页面主要是配置系统主机名，登录欢迎信息 root 密码，以及构建系统镜像版本，根文件系统覆盖。需要配置的项目和对应的内容如下所示：

> Root FS skeleton (default target skeleton) --->
>
> (iTOP-RK3568) System hostname \# 系统主机名，写 iTOP-RK3568
>
> (Welcome to Buildroot) System banner #系统欢迎语
>
> Passwords encoding (sha-256) ---> # 密码编码方式 sha-256
>
> Init system (BusyBox) ---> #系统初始化，选择 BusyBox
>
> \#设备文件管理，选择 Dynamic using devtmpfs + mdev，即使用 mdev 动态加载设备节点的方式/dev management (Dynamic using devtmpfs + mdev) --->\#设备节点的配置表设置，一定要选择 system/device_table.txt，否则后面在 dev 目录下就不会生成各种设备节点。当然我们也可以手动配置该文件，添加必要的节点或删除不需要的节点。
>
> (system/device_table.txt) Path to the permission tables
>
> [ ] support extended attributes in device tables
>
> [ ] Use symlinks to /usr for /bin, /sbin and /lib
>
> [*] Enable root login with password
>
> () Root password # 进入 linux 控制台终端后的密码，为空则登录时不需要密码，默认登录用户名为 root,密码为空。
>
> /bin/sh (busybox' default shell) --->
>
> [*] Run a getty (login prompt) after boot ---> #保持默认，默认为选中
>
> [*] remount root filesystem read-write during boot
>
> () Network interface to configure through DHCP
>
> (/bin:/sbin:/usr/bin:/usr/sbin) Set the system's default PATH
>
> [*] Purge unwanted locales
>
> (C en_US) Locales to keep
>
> () Generate locale data (NEW)
>
> [ ] Enable Native Language Support (NLS) (NEW)
>
> [ ] Install timezone info
>
> () Path to the users tables
>
> () Root filesystem overlay directories
>
> () Custom scripts to run before commencing the build
>
> () Custom scripts to run before creating filesystem images
>
> () Custom scripts to run inside the fakeroot environment
>
> () Custom scripts to run after creating filesystem images

#### 28.1.7.5 Kernel 选项

Kernel 选项主要介绍了在线下载内核源码并自动编译到根文件系统的方法，**这里不选**

> [*] Linux Kernel
>
> Kernel version (Latest version (5.17)) ---> #内核版本，选择用户自定义
>
> () Custom kernel patches (NEW) \# 自定义的内核补丁
>
> Kernel configuration (Using an in-tree defconfig file) #内核配置
>
> () Defconfig name (NEW) #defconfig 文件名字
>
> () Additional configuration fragment files (NEW)
>
> () Custom boot logo file path (NEW)
>
> Kernel binary format (Image) ---> # 内核二进制文件格式
>
> Kernel compression format (gzip compression) ---> # 内核压缩格式
>
> [ ] Build a Device Tree Blob (DTB) (NEW)
>
> [ ] Install kernel image to /boot in target (NEW)
>
> [ ] Needs host OpenSSL (NEW)
>
> [ ] Needs host libelf (NEW)
>
> [ ] Needs host pahole (NEW)
>
> Linux Kernel Extensions ---> #内核扩展，默认不选择
>
> Linux Kernel Tools ---> #内核工具，默认不选择

#### 28.1.7.6 buildroot** **编译

在上面的小节中，我们配置了 build root 的基础功能，然后我们输入 make 命令进行编译，注意编译过程中需要保证虚拟机 ubuntu 是联网状态。如下图所示：

![image-20240713165612753](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713165612753.png)

编译完之后

![image-20240713165624772](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713165624772.png)

我们使用命令“ls output/images/”即可看到编译出来的文件系统。此时编译出来的文件系统是最精简的文件系统。接下来将教大家如何添加软件包。

### 28.1.8 配置 Target packages

Target packages 选项主要介绍在目标开发板上使用根文件系统所需要的软件包的添加方法，以及配置方法，大家可以根据需求来自行添加。

![image-20240713165804406](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713165804406.png)

![image-20240713165823549](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713165823549.png)

详细的选项介绍如下所示：

> Audio and video applications ---> # 主要介绍 buildtroot 支持的音频和视频应用功能介绍以及如何配置使用
> Compressors and decompressors ---> # 主要介绍 buildtroot 支持的压缩和解压应用简介以及如何配置使用
> Debugging, profiling and benchmark ---> # 主要介绍 buildroot 调试、分析和基准测试应用的简介以及如何配置使用。
> Development tools ---> # 主要介绍 buildroot 支持在目标系统上的开发工具应用的简介以及如何配置使用。
> Filesystem and flash utilities ---> #主要介绍 buildroot 支持在目标系统上的文件系统和闪存实用程序的简介以及如何配置使用。
> Fonts, cursors, icons, sounds and themes ---> #主要介绍 buildroot 支持在目标系统上的字体，游标，图标，声音和主题的简介以及如何配置使用。
> Games ---> # 主要介绍 buildroot 支持在目标系统上的游戏以及如何配置使用。
> Graphic libraries and applications (graphic/text) ---> #主要介绍 buildroot 支持在目标系统上的图形库和应用程序(图形/文本)的简介以及如何配置使用。
> Hardware handling ---> # 主要介绍buildroot支持在目标系统上的硬件处理应用/工具的简介以及如何配置使用。
> Interpreter languages and scripting ---># 主要介绍 buildroot 支持在目标系统上的编程语言和脚本的简介以及如何配置使用。
> Libraries ---> #主要介绍 buildroot 支持在目标系统上的库的简介以及如何配置使用。
> Mail ---> #主要介绍 buildroot 支持在目标系统上的邮箱应用的简介以及如何配置使用。
> Miscellaneous --->#主要介绍 buildroot 支持在目标系统上的一些杂项应用的简介以及如何配置使用。
> Networking applications ---> #主要介绍 buildroot 支持在目标系统上的网络应用程序的简介以及如何配置使用。
> Package managers ---> #主要介绍 buildroot 支持在目标系统上的包管理应用的简介以及如何配置使用。
> Real-Time ---> #主要介绍 buildroot 支持在目标系统上的实时时钟的简介以及如何配置使用。
> Security ---> #
> Shell and utilities ---> #主要介绍 buildroot 支持在目标系统上的 Shell 和程序的简介以及如何配置使用。
> System tools ---> # 主要介绍 buildroot 支持在目标系统上的系统工具的简介以及如何配置使用。
> Text editors and viewers --->#主要介绍 buildroot 支持在目标系统上的 文版编辑和浏览工具的简介以及如何配置使用。

以上了解了target packages的基本功能，接下来我们就为文件系统添加一些基本的软件包，进一步增强文件系统的功能。

#### 28.1.8.1 支持** **linux** **磁盘工具

如果读者，想要的文件系统支持 FAT32 格式的分区，则需要参考下述操作进行配置dosfstools 工具包。

依次选择如下配置项：

> -> Target packages
>
> -> Filesystem and flash utilities
>
> ->dosfstools

![image-20240713170126132](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170126132.png)

如果读者，想要的文件系统支持 ext2 ext3 ext4 文件系统分区，请参考下图配置增加e2fsprogs 工具包。

依次选择如下配置项：

> -> Target packages
>
> -> Filesystem and flash utilities
>
> -> e2fsprogs

![image-20240713170140369](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170140369.png)

如果读者，想要格式化 spi nandflash norflash 等块设备，就参考下述配置增加 mtd tools。依次选择如下配置项：

> -> Target packages
>
> -> Filesystem and flash utilities

![image-20240713170151538](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170151538.png)

#### 28.1.8.2 支持 **nfs** **挂载工具

如果读者想要使用 nfs 挂载工具，依次选择如下配置项：

> -> Target packages
>
> -> Filesystem and flash utilities

![image-20240713170235779](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170235779.png)

#### 28.1.8.3 支持** **v4l2** **框架工具

如果读者想要使用摄像头等设备，需要查看摄像头数据或者设置摄像头的配置，则需要安装 v4l-utils 工具，请参考如下述配置路径来进行增加相应的包。

> -> Target packages
>
> -> Audio and video applications

![image-20240713170322746](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170322746.png)

依次选择如下配置项：

> -> Target packages
>
> -> Libraries
>
> -> Hardware handling

![image-20240713170359904](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170359904.png)

#### 28.1.8.4 支持** **can** **工具

如果读者，想要测试 can 设备，参考下述配置进行安装 can-utils 来进行 can 数据的发送和读写，测试 can 之前还需要安装 iproute2 命令来初始化配置 can 设备。

依次选择如下配置项：

> -> Target packages
>
> -> Networking applications

![image-20240713170448280](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170448280.png)

#### 28.1.8.5 支持** **ssh** **访问工具

如果读者，想通过 ssh 工具来远程登录开发板，或者使用开发板远程登录其他 ssh，则需要安装 openssh 工具包，配置过程如下：

> -> Target packages
>
> -> Networking applications

![image-20240713170522733](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170522733.png)

#### 28.1.8.6 支持** **4G** **拨号上网工具

 RK 3568 开发板可以直接安装配套的 pcie 接口 4G 上网模块，可以通过 ppp 协议进行拨号上网，如果需要使用 ppp 协议则需要安装 pppd 工具包，配置方式参考下图。

> -> Target packages
>
> -> Networking applications

![image-20240713170602036](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170602036.png)

#### 28.1.8.7 支持** **hci** **蓝牙工具

由于我们的开发板上蓝牙模块，如果使用蓝牙模块功能则要安装对应的工具包才可以，参考下述配置进行配置安装 bluez-utils 5.x 以及 bluez-tools 。

> -> Target packages
>
> -> Networking applications

![image-20240713170633464](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170633464.png)

#### 28.1.8.8 支持** **alsa** **声卡工具

ALSA 是 Advanced Linux Sound Architecture，高级 Linux 声音架构的简称，它在 Linux操作系统上提供了音频和 MIDI（Musical Instrument Digital Interface，音乐设备数字化接口）的支持。在 2.6 系列内核中，ALSA 已经成为默认的声音子系统，用来替换 2.4 系列内核中的OSS（Open Sound System，开放声音系统）。

ALSA 的主要特性包括：高效地支持从消费类入门级声卡到专业级音频设备所有类型的音频接口，完全模块化的设计， 支持对称多处理（SMP）和线程安全，对 OSS 的向后兼容，以及提供了用户空间的 alsa-lib 库来简化应用程序的开发。需要使用 aplay 等命令，请参考如下配置进行配置。

> Target packages
>
> ---> Audio and video applications
>
> ---> [*] alsa-utils --->

![image-20240713170719319](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170719319.png)

> Target packages
>
> -> Libraries
>
> -> Audio/Sound
>
> -> -*- alsa-lib ---> 此配置项下的文件全部选中

![image-20240713170740816](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170740816.png)

#### 28.1.8.9 支持** **wpa WIFI** **工具

如果需要使用开发板上的 wifi 模块进行上网等相关测试，则需要安装 iw 包来获取无线路由设备信息，并通过 wpa_supplicant 进行网络链接。

> -> Target packages
>
> -> Networking applications

![image-20240713170809176](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170809176.png)

> -> Target packages
>
> -> Networking applications

![image-20240713170830825](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170830825.png)

#### 28.1.8.10 支持** **Qt** **配置

**支持** **multimedia**

凭借 GStreamer，程序员可以很容易地创建各种多媒体功能组件，包括简单的音频回放，音频和视频播放，录音，流媒体和音频编辑。基于流水线设计，可以创建诸如视频编辑器、流媒体广播和媒体播放器等等的很多多媒体应用，我们需要参考如下配置目录进行配置依次选择如下配置项：

> -> Target packages
>
> -> Audio and video applications

![image-20240713170935535](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713170935535.png)

**支持** **tslib** **触摸**

Tslib 是嵌入式经常使用的第三方库，可以优化触摸识别，如果读者需要，可以按下图配置：

依次选择如下配置项：

> -> Target packages
>
> -> Libraries
>
> -> Hardware handling

![image-20240713171013734](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171013734.png)

**支持** **qt5**

升级虚拟机ubuntu的gcc

```bash
sudo add-apt-repository ppa:ubuntu-toolchain-r/test
sudo apt update
sudo apt install gcc-9 g++-9
sudo update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-9 90 --slave /usr/bin/g++ g++ /usr/bin/g++-9
gcc --version
```

我们可以直接使用 buildroot 来制作一个具有 qt 环境的文件系统，配置如下图：

依次选择如下配置项：

> -> Target packages
>
> -> Graphic libraries and applications (graphic/text)
>
> -> Qt5

![image-20240713171038779](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171038779.png)

下面的勾选只是举一个例子请根据个人需求进行配置

![image-20240713171053818](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171053818.png)

支持虚拟键盘：

![image-20240713171108241](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171108241.png)

支持 SQLite：

> -> Target packages
>
> -> Graphic libraries and applications (graphic/text)
>
> -> Qt5
>
> ->SQLoite 3 support (QT SQLite) ---->

![image-20240713171142212](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171142212.png)

#### 28.1.8.11 支持** **python3

Python 是一种面向对象的解释型语言,读者可以根据自己的需求选择编译安装 python 的模块，配置过程如下：

> -> Target packages
>
> -> Interpreter languages and scripting

![image-20240713171219028](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171219028.png)

#### 28.1.8.12 支持** **MQTT** **库

Mosqitto 是一款实现了消息推送协议 MQTT v1.1 的开源消息代理软件，提供轻量级的，支持可发布/可订阅的的消息推送模式，使设备对设备之间的短消息通信变得简单。读者可以根据需求是否需要来选择安装，其配置过程如下

> -> Target packages
>
> -> Networking applications

![image-20240713171254938](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171254938.png)

#### 28.1.8.13 支持** **opencv

> -> Target packages
>
> Libraries --->
>
> Graphics --->
>
> [*] opencv4 --->

![image-20240713171318682](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171318682.png)

#### 28.1.8.14 Buildroot** **下配置** **Busybox

busybox 也是基于 buildroot 制作的文件系统，所以我们 buildroot 里的 busybox 也可以进行配置。首先我们在 buildroot 源码目录下，使用命令“make busybox-menuconfig”，如下图所示：

![image-20240713171401748](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171401748.png)

在这里我们可以看到 busybox 版本是 1.35.0，然后就是我们之前看到过的 busybox 配置界面了，用户可根据自己需要配置，这里的配置方法同使用 busybox 构建文件系统方法一致，

![image-20240713171426923](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171426923.png)

然后我们使用命令“make busybox”即可单独编译 busybox。

![image-20240713171442118](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171442118.png)

最后编译完成以后使用命令“make”重新编译 buildroot，主要是对其进行打包，

![image-20240713171459991](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171459991.png)

重新编译完成以后查看 output/images 目录下 rootfs.tar 的创建时间是否为刚刚编译的，如果不是的话就删除掉 rootfs.tar，然后重新执行“make”重新编译一下即可。

#### 28.1.8.15 支持 自动获取IP地址网络

>  Target packages ---->
>
> Networking applications  --->
>
> dhcpcd

#### 28.1.8.16 Buildroot 编译

接着我们使用命令“make”编译 buildroot，期间他会自行下载一些软件源码，请保证网络可用。如下图所示：

![image-20240713171532162](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171532162.png)

最后编译完成

![image-20240713171550832](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171550832.png)

我们使用命令“ls output/images/”即可看到编译出来的文件系统。

![image-20240713171602201](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171602201.png)

如果想要下载默认支持的源码包，（**一般不下**），输入以下命令：

> make source

#### 28.1.8.17 制作文件系统镜像

在上面的章节中我们已经编译出了 rootfs.tar 文件系统，接下来我们就需要将文件系统源码打包成可以烧写到开发板的镜像。这里以 RK3568 开发板为例，我们将 rootfs.tar 拷贝到 123文件夹中，然后输入以下命令“tar -vxf rootfs.tar ”解压缩，如下图所示：

![image-20240713171645611](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171645611.png)

解压完毕，如下所示：

![image-20240713171700013](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171700013.png)

删除 rootfs.tar，如下所示，这样 123 文件夹里面包含了文件系统。

> rm -rf rootfs.tar

![image-20240713171722010](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171722010.png)

然后在 123 文件夹的同级目录，输入以下命令。制作自己的根文件系统，大小依据自己的根文件系统而定，注意依据 文件夹的大小来修改 count 值，：

> mkdir rootfs
>
> dd if=/dev/zero of=rootfs.img bs=1M count=1024
>
> mkfs.ext4 rootfs.img
>
> mount rootfs.img rootfs/
>
> cp -rfp 123/* rootfs/
>
> umount rootfs/
>
> e2fsck -p -f rootfs.img
>
> resize2fs -M rootfs.img

![image-20240713171752625](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171752625.png)

![image-20240713171759607](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171759607.png)

![image-20240713171805520](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713171805520.png)

这样 rootfs.img 就是最终的根文件系统映像文件了。

> ./xxx  --platform linuxfb

---

[总目录](总目录.md) · [上一篇：Qt交叉编译与部署](27-Qt交叉编译与部署.md) · [下一篇：镜像打包分区与upgrade_tool烧录](29-镜像打包分区与upgrade_tool烧录.md)
