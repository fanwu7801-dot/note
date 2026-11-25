# 34-Android系统构建与内核移植

[总目录](总目录.md) · [上一篇：USB通信](33-USB通信.md) · [下一篇：显示与触摸屏移植](35-显示与触摸屏移植.md)

[TOC]

<a id="part-49"></a>

> 本篇及第 35–37 篇以迅为 iTOP-RK3568、Android 11 原厂 SDK 的实测笔记为基线。前面 Linux 6.1 是另一套课程环境；本组旧 BSP 常以 4.19 为背景，实际以内核源码和板端 uname 为准。原实测构建命令、串口和外设配置保留，补充原理、工程流程与排查方法。
>
> 主线：34.3 以后使用原厂/迅为 SDK。34.2 的 AOSP x86_64 是独立学习环境，不用于直接生成本板镜像。新增说明和命令未在板上重新测试。

> sudo apt-get install uuid uuid-dev zlib1g-dev liblz-dev liblzo2-2 liblzo2-dev lzop \
> git-core curl u-boot-tools mtd-utils android-tools-fsutils openjdk-8-jdk device-tree-compiler \
> gdisk m4 libz-dev git gnupg flex bison gperf libsdl1.2-dev libesd-java libwxgtk3.0-dev \
> squashfs-tools build-essential zip curl libncurses5-dev zlib1g-dev pngcrush schedtool \
> libxml2 libxml2-utils xsltproc lzop libc6-dev schedtool g++-multilib lib32z1-dev \
> lib32ncurses5-dev lib32readline-dev gcc-multilib libswitch-perl libssl-dev unzip \
> zip liblz4-tool repo git ssh make gcc libssl-dev liblz4-tool vim expect \
> g++ patchelf chrpath gawk texinfo chrpath diffstat binfmt-support \
> qemu-user-static live-build bison flex fakeroot cmake gcc-multilib g++-multilib \
> unzip device-tree-compiler python-pip libncurses5-dev rsync subversion \
> sed make binutils  build-essential  gcc  g++  wget python libncurses5 bzr cvs git mercurial \
> patch gzip bzip2 perl tar cpio unzip rsync file bc wget qemu-user-static live-build -y

## 34.1 从 Android 分层理解板级适配

Android 是基于 Linux 内核的软件栈。对本课程来说，重点是让内核驱动、厂商 HAL、系统服务和应用形成完整链路，而不是把 Android 当作“加了桌面的普通 Linux 发行版”。

下图为原笔记保留的版本资料。它用于认识版本演进，本篇实际适配目标仍是 **Android 11**：

![image-20240713095606599](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713095606599.png)

### 34.1.1 AOSP、瑞芯微 BSP 和迅为 SDK 的关系

| 源码来源 | 提供什么 | 本次怎样使用 |
| --- | --- | --- |
| Google AOSP | Framework、运行时、原生服务、通用构建系统等 | 阅读 Android 机制，单独做模拟器学习 |
| Rockchip Android BSP | SoC 支持、内核/U-Boot、HAL 和厂商构建打包 | 理解 RK3568 平台实现及硬件接口 |
| 迅为板级 SDK | 核心板、底板和外设的适配及产品配置 | 本次实测和后续外设实验的工作基线 |

三者是不同层面的交付。AOSP 模拟器镜像不能直接拿来烧迅为板；将另一块 RK3568 板的镜像烧进来，也不自动具备本板的电源、引脚和外设配置。

“移植 Android 内核”在这里主要指：在已支持 RK3568 的 BSP 中适配迅为板级资源和外设，不是从零实现 CPU 支持。先让原版 SDK 构建、启动和外设基线可复现，再逐项修改。

### 34.1.2 Android 11 的各层负责什么

原笔记中的两幅架构图继续保留。第一幅属于较早的 Android 分层示意，不应把其中 Dalvik、旧 WebKit 等名称当作 Android 11 的全部现状：

![image-20240713095808437](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713095808437.png)

![image-20240713095827562](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713095827562.png)

| 层次 | 主要内容 | 外设调试时怎样用到 |
| --- | --- | --- |
| 应用 | Java/Kotlin 及可选 Native 代码，通过 API 请求功能 | 相机预览、联网、触摸响应 |
| Framework / 系统服务 | API、权限、生命周期和设备管理 | CameraService、WiFi 服务、输入和显示管理 |
| 原生服务与库 | C/C++ 服务、媒体、图形及系统库 | cameraserver、SurfaceFlinger、网络服务等 |
| ART 与核心库 | 运行应用字节码，结合解释、JIT、AOT 等机制 | 应用运行，不是设备树的替代品 |
| HAL / 厂商实现 | 将系统接口连接到特定硬件实现 | Camera、WiFi、显示合成等 |
| Linux 内核 | 驱动、内存、调度、网络、设备接口 | DRM、input、V4L2、USB、无线驱动 |
| 硬件 | RK3568、外设、电源与板级连线 | 决定真实 GPIO、接口、时钟及电压 |

JNI 用于连接 Java 与 Native 调用；跨进程通信经常使用 Binder。HAL 是职责和接口边界，不意味着所有 HAL 都由 Framework 在同一进程中直接加载一个 `.so`。Android 11 BSP 中常见 HIDL 服务及厂商扩展，具体按服务注册和源码确认。

Bionic 是 Android 的 C 库。应用、HAL 和系统工具的权限与运行库环境不同，因此“在一个 root shell 里能运行”并不等于“普通 App 或 HAL 进程一定能访问同一设备”。

### 34.1.3 从上电走到 Android 桌面

原笔记的进程关系图用于帮助理解各层的衔接：

![image-20240713102045638](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713102045638.png)

```text
BootROM / 前级引导
    → U-Boot：选择并加载本产品启动镜像
    → Linux：初始化内核，执行用户空间 init
    → Android init：分阶段准备挂载、SELinux 和系统服务
    → 原生服务、HAL、Zygote 等按配置启动
    → Zygote 创建 system_server 和应用进程
    → 系统服务完成相应启动工作，启动桌面应用
```

Linux 内核不负责解析 Android `init.rc`。它执行用户空间 init；Android init 再解析相应 rc 配置并管理服务。first-stage/second-stage init、fstab 和镜像布局之间有关联，不能把“启动 init”简化成“内核找到一个 init.rc 文件”。

Android 11 的音视频服务不应全部归为一个老式 `mediaserver` 进程；`cameraserver`、`audioserver` 等有各自职责。Launcher 也不应简单称为系统中固定的“第一个 App 进程”。

调试时按阶段观察：串口早期日志、内核日志、init/服务状态、Framework 日志、应用结果。Logo 正常只证明某个显示阶段正常，`adb` 能连接也不代表全部 Android 服务已启动完成。

## 34.2 AOSP 编译：作为独立学习环境

> 本节保留原笔记选择的 Android 11 AOSP 版本，目的是阅读 Framework 和使用模拟器。迅为板上的外设适配从 34.3 开始，使用原厂/板厂 SDK；两套源码目录分开保存。

### 34.2.1 准备宿主机与源码

原课堂环境为 x86_64 Ubuntu 18.04，虚拟机内存不少于 16 GiB、磁盘预留约 300 GB。它是当时的环境记录，实际空间和并行编译所需内存取决于源码、输出目录及产品目标；SDK 推荐环境优先于随意升级主机工具。

AOSP Android 源码下载的时候，下载完毕大约是 200G 左右，建议使用虚拟机进行编译。

电脑硬件要求如下所述：

> CPU：X86 CPU，核数越多越好
>
> 内存：不少于 16GB（针对虚拟机）
>
> 存储: 不少于 300GB
>
> Ubuntu 版本：Ubuntu18.04
>
> 操作系统中交换分区：6G 以上

如果物理内存只有16G，需要设置交换内存：

在开始之前，使用命令检查一下您的 ubuntu 的 swap 分区。

> sudo swapon --show

通过以下命令创建一个用于 swap 的文件

> sudo swapoff -a
>
> sudo fallocate -l 5G /swapfile

执行以下命令为 swapfile 文件设置正确的权限：

> sudo chmod 600 /swapfile

使用 mkswap 实用程序在文件上设置 Linux SWAP 区域：

> sudo mkswap /swapfile

sudo vim /etc/fstab

在/etc/fstab 文件最后添加如下内容：

> /swapfile swap swap defaults 0 0

使用以下命令激活 swap 文件：

> sudo swapon /swapfile

使用 swapon 或 free 命令验证 SWAP 是否处于活动状态，如下所示:

> sudo swapon --show
>
> sudo free -h

内存不足时可以降低并行度；swap 会明显增加 I/O 开销，不是替代充足内存的方案。不要为了编译直接关闭全部现有 swap，或覆盖已经在使用的 `/swapfile`；如确需添加 swap，先按主机现有配置单独处理。

![image-20240713104047626](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713104047626.png)

安装 repo 启动器的一种方式如下，在 Linux 主机执行；下面不替你更改 Git 全局身份配置：

```bash
mkdir -p "$HOME/bin"
curl -L --fail https://storage.googleapis.com/git-repo-downloads/repo \
    -o "$HOME/bin/repo"
chmod u+x "$HOME/bin/repo"
export PATH="$HOME/bin:$PATH"

export AOSP_WORK="$HOME/aosp-android11"
mkdir -p "$AOSP_WORK"
cd "$AOSP_WORK"
repo init -u https://android.googlesource.com/platform/manifest \
    -b android-security-11.0.0_r55
repo sync -j2
```

这是原笔记所选的历史 Android 11 ref，不表示当前最新分支。repo 管理一组 Git 仓库及其 manifest；`repo init` 选择清单，`repo sync` 同步清单中的各项目。需要镜像源时按镜像站当前文档替换地址，不把失效的旧 `git://` 地址当作唯一方式。

AOSP 的下载和构建入口是 `source.android.com`；`developer.android.com` 主要面向应用开发文档。

![image-20240713104620189](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713104620189.png)

![image-20240713104824596](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713104824596.png)

### 34.2.2 选择目标并构建

在 AOSP 顶层、使用 Bash 执行：

```bash
source build/envsetup.sh
lunch aosp_x86_64-eng
make -j12
```

`12` 沿用原笔记的示例并行度，应按主机内存调整。Android 11 的 lunch 名称通常为 `产品-构建类型`，例如这里的 `aosp_x86_64-eng`；产品名和类型之间是连字符，不写成 `aosp_x86_64_eng`。

| 构建类型 | 理解方式 |
| --- | --- |
| user | 面向发布，调试和 root 能力受限；是否开启/授权 ADB 还取决于产品设置 |
| userdebug | 接近 user 的基础上加入调试能力，通常用于板级调试，可支持 `adb root` |
| eng | 开发用途，包含更多调试设置；不等于只能运行在模拟器 |

`source` 影响当前 shell；新开终端需要重新加载环境并选择目标。`lunch` 不会自动把 x86 目标变成 RK3568 目标。

![image-20240713110349042](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713110349042.png)

### 34.2.3 理解输出并启动模拟器

常见输出位于 `out/target/product/generic_x86_64/`，以实际 lunch 目标为准：

| 文件 | 基本用途 |
| --- | --- |
| system.img | Android 系统文件所在的镜像之一 |
| userdata.img | 用户数据区映像 |
| ramdisk.img | 启动阶段所需 ramdisk 内容，具体取决于目标 |
| 其他输出 | 内核、验证元数据及其他分区文件，依产品布局而定 |

挂载和用户空间启动由内核、init、fstab 等协作完成，不应解释成“所有镜像都由一个 init.c 解析”。AOSP 输出格式也不能直接套到 RK3568 的 vendor、resource 或整机升级包上。

对应模拟器构建完成后，在同一构建环境中按该分支支持的方式启动：

```bash
emulator
```

虚拟机中需要合适的硬件虚拟化/KVM 或受支持的替代方式；显卡和模拟器加速参数随宿主环境变化。原学习截图保留用于对照，不把其中某个旧加速选项作为所有主机必需设置：

![image-20240713110531585](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713110531585.png)

![image-20240713110701407](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713110701407.png)

构建概念参见 [AOSP Build Android](https://source.android.com/docs/setup/build/building)。该网站会更新，Android 11 的实际目标和脚本以所检出分支为准。


<a id="part-50"></a>

## 34.3 编译瑞芯微/迅为 Android 11 SDK

### 34.3.1 瑞芯微原厂源码目录介绍

在阅读目录前，先按原笔记建立一次本板 SDK 的构建基线。以下在 **SDK 顶层 Bash** 执行：

```bash
source javaenv.sh
java -version
source build/envsetup.sh
lunch rk3568_r-userdebug

```

`javaenv.sh` 是原笔记所在 SDK 提供的环境入口，不是每套 AOSP 都有的标准脚本。原课堂检查了 Java 1.8 环境；Android 构建还可能使用分支内预置 JDK，因此不能推断“所有 Android 11 必须把全局 Java 切到 1.8”。

使用普通开发用户构建，先记录 SDK 版本、产品目标和工具链，再复现 34.5 的完整构建命令。

![image-20241223170851979](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20241223170851979.png)

构建过程中原 SDK 会提示检查 IO-Domain：

![image-20240713111053919](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713111053919.png)

原笔记保存了下面两组配置作为对照：

```dts
   &pmu_io_domains {
     status = "okay";
     pmuio1-supply = <&vcc3v3_pmu>;
     pmuio2-supply = <&vcc3v3_pmu>;
     vccio1-supply = <&vccio_acodec>;
     vccio3-supply = <&vccio_sd>;
     vccio4-supply = <&vcc_3v3>;
     vccio5-supply = <&vcc_3v3>;
     vccio6-supply = <&vcc_3v3>;
   	vccio7-supply = <&vcc_3v3>;
   };
   
   &pmu_io_domains {
           status = "okay";
           pmuio2-supply = <&vcc3v3_pmu>;
           vccio1-supply = <&vccio_acodec>;
           vccio3-supply = <&vccio_sd>;
           vccio4-supply = <&vcc_1v8>;
           vccio5-supply = <&vcc_3v3>;
           vccio6-supply = <&vcc_1v8>;
           vccio7-supply = <&vcc_3v3>;
   };
```

IO-Domain 描述对应引脚组的真实供电电压。这里两组记录中的 `vccio4`、`vccio6` 已有 3.3 V 与 1.8 V 的差别，**不能得出“全部选择 3.3 V 即可”的结论**。按当前核心板/底板原理图、实际电源及这次选用的 DTS 核对；原脚本的确认输入不替你修改 DTS。

这两段作为原记录保留，不是要求把两个节点当作一套新的通用模板一起粘贴。选择的 regulator、实际电压和对应供电域必须一致。原厂 [IO-Domain 指南](../u盘资料/必须/15开发板原厂文档/docs/Common/IO-DOMAIN/Rockchip_Developer_Guide_Linux_IO_DOMAIN_CN.pdf) 可用于理解方法；其中旧芯片的域名列表不能替代 RK3568 本身的绑定和原理图。

#### 34.3.1.1 顶层目录分析

![image-20240713111538071](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713111538071.png)

| 目录/文件 | 作用与本次用途 |
| --- | --- |
| `art/` | ART 运行时实现 |
| `bionic/` | Android C 库、动态链接器等；C++ 标准库由 libc++ 等组件提供，不应理解为 Android 不支持 C++ 异常或 STL |
| `bootable/` | 常见的 recovery 等源码位置；Bootloader 则可能由厂商放在独立 `u-boot/` 等目录，按 SDK 树确认 |
| `build/`、`build.sh` | AOSP 构建系统及厂商顶层构建脚本 |
| `device/` | 产品与板级配置，重点看 Rockchip 产品选择 |
| `kernel/` | 本 BSP 内核、设备树及外设驱动 |
| `hardware/` | HAL 相关实现/接口；Android 11 的 HIDL 接口重点看顶层 `hardware/interfaces/` |
| `vendor/` | 厂商组件、配置、预编译库及产品资源 |
| `frameworks/` | Framework、原生图形/媒体和系统服务等 |
| `system/` | init、ADB、日志、网络等基础组件；Android 常用 Toybox，不能默认所有命令来自 BusyBox |
| `packages/` | 系统应用、服务、提供器等 |
| `external/` | 第三方项目，例如网络、图形和工具依赖 |
| `libcore/`、`libnativehelper/` | Java 核心库与 JNI 辅助实现 |
| `prebuilts/` | 分支提供的工具链、JDK、SDK 等预编译工具与资源 |
| `cts/`、`test/`、`platform_testing/` | 兼容性及平台测试；CTS 与 Google 商业服务授权不是同一件事 |
| `development/`、`tools/` | 开发辅助工具，具体子项随版本变化 |
| `out/` | 中间文件与产品输出，不作为永久源码修改的位置 |
| `rockdev/` | 此版 Rockchip 脚本汇集镜像和打包资源的位置 |

例如查看 Native 异常可结合 `development/scripts/stack` 和 tombstone，调试代码入口优先用 `rg` 搜索构建模块和调用关系。目录名提供线索，最终以当前 manifest、文件和构建规则为准。


#### 34.3.1.2 out 目录

编译 android 完毕，会生成 out 目录，目录下主要有俩个子目录，host 当前编译主机需要用到的工具和库，一般都是 x86 架构的。

另外一个就是 target 目录，就是目标机器运行所需要二进制文件，普遍都是arm 架构的二进制文件，该目录一般都是存放编译的中间文件，如.o 文件，以及目标文件，包含 strip 和 unstrip 的。同时对这些文件进行分门别类的进行存放。生成的中间文件:

```text
tree -L out/target/product/rk3568_r/obj

├── APPS :内置 app 的中间编译文件

├── CONFIG

├── ETC ：etc 的中间编译文件，一般都会最终生成到 system/etc 或者 vendor/etc目录

├── EXECUTABLES ：可执行的中间编译文件

├── FAKE

├── JAVA_LIBRARIES ：java jar 库的中间编译文件

├── PACKAGING ：镜像打包时的中间编译文件

├── RENDERSCRIPT_BITCODE

├── SHARED_LIBRARIES ：动态库的中间编译文件

└── STATIC_LIBRARIES：静态库的中间编译文件
```

#### 34.3.1.3 system 目录

Android 作为 Linux 系统，在构建最小系统时，需要 PID 1 的 init 进程，依赖库，二进制工具 linux 命令，以及各种守护进程等，system 目录就提供了这些东西，该目录大部分都是 C/C++代码。

```text
├── apex：apexd 守护进程源码，负责处理 apex 安装包的。

├── bpf

├── bpfprogs

├── bt：Android bluedroid 协议栈

├── ca-certificates

├── chre：Context Hub Runtime Environment (CHRE),用于平衡大小核运行不同程序的场景， 提供 api，保证小 型的本机应用程序（称为 nanoapps ）在低功耗处理器上执行。

├── connectivity：包含 wificond 进程，该进程通过标准 nl80211 命令与 WLAN驱动程序进行通信

├── core：包含各种依赖库，adb，init 进程源码，lmkd，logcat, toolbox

├── extras：各种额外的命令工具，比如 su，memtrack(追踪 graphic 相关内存)，playwav 命令，以及一些测 试代码

├── gatekeeper：防护程序，如锁屏密码等。

├── gsid：通用系统镜像守护进程

├── hardware：网络相关的 HIDL 描述文件。

├── hwservicemanager：管理 HIDL binderized HAL 服务，使用 hwbinder；并非所有 HAL 都由它统一管理，也不要与 vndbinder 混为一谈。 

├── incremental_delivery

├── iorap：iorap 用于缩短应用程序的启动时间，该目录包含 iorapd 守护进程和相应的库文件。

├── keymaster

├── libartpalette

├── libfmq

├── libhidl:硬件接口定义语言依赖库

├── libhwbinder:hwbinder 依赖库

├── libsysprop

├── libufdt

├── libvintf

├── linkerconfig

├── media:包括 alsa、audio、camera 相关的头文件

├── memory

├── netd:Android 中专门负责网络管理和控制的后台守护进程，如管理 DNS，设置防火墙，带宽控制

├── nfc

├── nvram

├── security

├── sepolicy:selinux 权限策略配置目录

├── server_configurable_flags

├── teeui

├── testing

├── timezone

├── tools:aidl，hidl 可执行程序的源码路径

├── update_engine:负责 A/B 升级的核心逻辑代码。

└── vold：Volume 守护进程，用来管理 Android 中存储类的热拔插事件，如设备增加，删除，修改等事件处理。
```

#### 34.3.1.4 frameworks 目录

```text
── av：audio/video， 如音视频解码器，录屏工具， 摄像头框架相关代码, 多媒体框架供上层程序调用的 java API，连接 java 和 C/C++的 jni 部分, 在framework/base/media 下

│ ├── apex

│ ├── camera：libcamera_client 共享库，是 camera 框架部分的 client 代码

│ ├── CleanSpec.mk

│ ├── cmds：包括录屏工具，stagefright 进程。

│ ├── drm

│ ├── include

│ ├── MainlineFiles.cfg

│ ├── media：提供音视频编解码的各种库和工具，后台进程如 audioserver, mediaserver(通过 binder 的进程间通信方式来完成其他进程（如音乐播放器）的请求)

│ ├── MODULE_LICENSE_APACHE2

│ ├── NOTICE

│ ├── OWNERS

│ ├── PREUPLOAD.cfg

│ ├── services：多媒体相关的后台服务， 如 cameraservice,audioflinger

│ └── tools

├── base：基础核心代码

├── compile：包含 libbcc,mclinker(llvm 编译器的插件) slang(Renderscript 语言的编译器)

├── ex:Android 内部使用的公共类，如联系人、小部件、io, 以及全新的相机框架 Camera2 的部分代码。


├── layoutlib:布局相关

├── libs

├── minikin：Android 原生字体，连体字效果

├── ml：机器视觉

├── multidex：多 dex 加载器，大多数 App，解压其 apk 后，一般只有一个classes.dex 文件，采用 MultiDex 的 App 解压后可以看到有 classes.dex，classes2.dex，… classes(N).dex

├── native：c/c++本地语言编写的相关工具源码和特定硬件控制的头文件，如bugreport, dumpstate, 各种 硬件的访问权限声明. 

├── opt：一些 UI 插件和 java 后台服务，如 timezonepicker，datetimepicker，colorpicker， 网络服务，如 EthernetService， WifiService, 电话服务 telephony

├── rs：渲染脚本 rendor script

├── support.md -> ../prebuilts/sdk/current/androidx-README.md

└── wilhelm：基于 Khronos 的 OpenSL ES/OpenMAX AL 的 audio/multimedia实现
```

其中 base 目录是中应用框架层的主要核心代码，目录结构解释如下所示

```text
── Android.bp

├── Android.mk

├── apct-tests

├── apex

├── api：主要是 txt 文件， 声明了 android 应用框架层的类、属性和资源

├── ApiDocs.bp

├── CleanSpec.mk

├── cmds：开机启动的进程代码和命令（脚本），著名的 zygote 进程代码和启动动画代码就在此处。

├── config

├── core：

├ ├── java：Android 应用开发锁依赖的各种包，四大组件代码就在此，如android/app/Activity.java，android/app/Service.java，android/content/ContentProvider.java， ./android/content/BroadcastReceiver.java

├ ├── jni：服务于 android 系统 java 核心代码所需要的 jni，被编译成libandroid_runtime.so

├ ├── proto

├ ├── res:系统中所需要的各种资源，图片，字符串，尺寸，布局文件等。

├ ├──TEST_MAPPING

├ ├── tests

├ └── xsd

├── data：系统默认的铃声，字体， 根文件系统 etc 目录部分配置文件，触摸需要的 kl, kcm 文件等。

├── docs

├── drm：Digital Rights Management(数字版权管理) ，应用根据与受版权保护的内容关联的许可限制来管理 自己的内容，从而达到保护应用内容的知识产权。

├── errorprone

├── framework-jarjar-rules.txt

├── graphics：为应用提供的 android.graphics 包，提供基本的图形原语（如画点画线，设置图形上下文等） 另外和图形相关的包：android.view 图形事件机制和 android.widget 包提供开发图形用户界面的控件

├── identity

├── keystore：提供 android.security.keystore 包, 应用可以通过 KeyStore API生成密钥、使用密钥签名, keystorek 可以保护密钥材料免遭未经授权的使用

├── libs：大部分都是 c/c++代码，编译成 so， 如 Canvas 的 drawing 操作转换为 OpenGL 的操作的 libhwui.so

├── location：定位相关接口，被 App 调用的，API 包是 android.location

├── lowpan：提供 android.net.lowpan 报，提供基于 IPv6 的低速无线个域网的API, lowpan 功能与 Zigbee 类似

├── media：多媒体相关接口，被 App 调用的， 包含 MediaPlayer 代码

├── mime

├── mms

├── MODULE_LICENSE_APACHE2

├── native：部分硬件相关的 jni 库：如 sensor, net, 存储管理， 最后合并在libandroid.so 中

├── nfc-extras

├── non-updatable-api

├── NOTICE

├── obex：蓝牙文件传输 obex 协议

├── opengl：提供 android.opengl 包, 提供 android 2D/3D 图形处理各种 API

├── packages：著名的 SystemUI，彩蛋，锁屏，SettingProvider(系统设置数据提供者)

├── pathmap.mk

├── PREUPLOAD.cfg

├── proto

├── rs：提供 android.renderscript 包，RenderScript 是 Android 平台上的一种类 C 脚本语言，用于渲染绘图

├── samples

├── sax

├── services：android 开机启动的大部分后台服务，如 PMS, AMS, WMS 等

├── startop

├── StubLibraries.bp

├── telecomm

├── telephony

├── test-base

├── test-legacy

├── TEST_MAPPING

├── test-mock

├── test-runner

├── tests

├── tools：提供应用开发的各种工具和脚本：如 aapt

└── wifi：提供 android.net.wifi 包，如 wifi 扫描， p2p，hotspot2 相关 API
```

#### 34.3.1.5 libcore 目录

Libcore 提供 Android 系统中支持众多 Java 标准的库，例如 java.lang 包

```text
├── Android.bp

├── AndroidTest-core-tests.xml

├── apex

├── benchmarks

├── check-ojluni-files

├── CleanSpec.mk

├── dalvik：dalvik 虚拟机相关包

├── dom：文档对象模型，用于解析 xml

├── expectations

├── harmony-tests

├── JavaLibrary.bp

├── json:json 串在 Java 中的支持

├── jsr166-tests

├── known_oj_tags.txt

├── libandroidio.map.txt

├── libart：art 运行时部分相关包

├── LICENSE

├── luni ：Java 基础包、扩展包、组织提供的类库等，luni 实际上是 lang、util、net 、 io 这 4 个 内 容 头 字 母 的 组 合 ， 通 过 文 件luni/src/module/java/module-info.java 可以导出的所有类

├── metrictests

├── mmodules

├── NativeCode.bp

├── non_openjdk_java_files.bp

├── NOTICE

├── nullability_annotated_classes.txt

├── nullability_warnings.txt

├── ojluni：Open JDK 版的 Java 包，android7.0 之后就开始用这个开源的 java api

├── openjdk_java_files.bp

├── OWNERS

├── PREUPLOAD.cfg

├── support

├── TEST_MAPPING

├── test-rules

├── tools

└── xml：一种轻量级的 xml 解析工具
```

### 34.3.2 从目录定位本次外设修改

上面的目录树保留原 SDK 的阅读笔记，不同交付版本的子目录会变化。实际找代码时，优先按当前 product 和相关构建规则向下追：

| 位置 | 本次重点 |
| --- | --- |
| `device/rockchip/rk356x/` | 产品、BoardConfig、内核配置和 DTS 选择 |
| `kernel/` | defconfig/fragment、设备树、DRM/input/V4L2/USB/无线驱动 |
| `frameworks/opt/net/wifi/libwifi_hal/` | 本版 BSP 的 WiFi 识别和模块选择扩展 |
| `hardware/`、`vendor/rockchip/` | HAL、厂商库和产品配置，以实际项目为准 |
| `out/target/product/rk3568_r/` | 编译产物与目标文件布局 |
| `rockdev/Image-rk3568_r/` | 本版脚本汇集的镜像；核对是否为最新构建输出 |

Android.mk 是传统 Make 模块描述；Android.bp 通常由 Soong 处理。顶层构建会综合产品规则、模块依赖和复制规则。某个文件在源码树中存在，不等于已经被当前产品打包。

<a id="part-51"></a>

## 34.4 Android 内核构建与板级本地化

### 34.4.1 单独编译内核与重新打包 boot.img

原笔记的方法一是在 **Android SDK 顶层**运行：

```bash
./build.sh -CKA
```

这是本版 SDK 的组合构建命令。原记录中 `-C` 选择 Clang，内核更新还需要配合 Android 启动镜像打包；其他选项和输出规则以这版 `build.sh` 为准。完整构建先形成基线，再使用下面的快速流程。

原笔记中被拆成多行引用的 `CC=... LD=...` 属于同一条 make 命令，不能每行分别执行。按原路径、工具版本和目标恢复为：

```bash
# 在 Android SDK 顶层，先已按本产品建立过可启动的 boot.img 基线。
export ANDROID_SDK="$(pwd)"
export RK_ANDROID_CLANG="$ANDROID_SDK/prebuilts/clang/host/linux-x86/clang-r383902b/bin"

test -x "$RK_ANDROID_CLANG/clang"
test -x "$RK_ANDROID_CLANG/ld.lld"
test -s "$ANDROID_SDK/rockdev/Image-rk3568_r/boot.img"

# 初始化配置；已有需要保留的 .config 时，不必每轮调试都重新生成。
make -C "$ANDROID_SDK/kernel" ARCH=arm64 \
    CC="$RK_ANDROID_CLANG/clang" \
    LD="$RK_ANDROID_CLANG/ld.lld" \
    rockchip_defconfig android-11.config

make -C "$ANDROID_SDK/kernel" ARCH=arm64 \
    CC="$RK_ANDROID_CLANG/clang" \
    LD="$RK_ANDROID_CLANG/ld.lld" \
    BOOT_IMG="$ANDROID_SDK/rockdev/Image-rk3568_r/boot.img" \
    rk3568-evb1-ddr4-v10.img
```

上面保留原笔记的参考 EVB 目标。完成 34.4.2 的本地化以后，应将配置改为本产品实际选用的 `itop_rockchip_defconfig`、`itop_android-11.config`，并使用对应的 `itop_rk3568-evb1-ddr4-v10.img`；先核对该 SDK 构建规则支持这些目标。

`BOOT_IMG` 指向已构建的前置 Android boot.img，供本 BSP 的打包流程更新内核和 resource 等内容。它不是将一个裸 `Image` 改名为 boot.img，也不是所有主线 Linux 都支持的通用 make 参数。不提供或提供错误的基线，可能产生无法按本产品正常启动的映像；是否进入 recovery 取决于具体打包和启动配置，不是必然结果。

原笔记对应的输出为 `kernel/boot.img`，完整 SDK 流程还会在 `rockdev/Image-rk3568_r/` 管理打包文件。每轮先看构建日志与输出时间/哈希，确认要更新的正是新生成文件。

为了缩短日常修改后的循环，可以在 **kernel 目录**保存下面的构建脚本；配置初始化单独执行，避免每次运行脚本覆盖 menuconfig 修改：

```bash
#!/usr/bin/env bash
set -euo pipefail

kernel_dir="$(pwd)"
sdk_dir="$(cd .. && pwd)"
clang_dir="$sdk_dir/prebuilts/clang/host/linux-x86/clang-r383902b/bin"
base_boot="$sdk_dir/rockdev/Image-rk3568_r/boot.img"

# 已完成板级本地化时，改成自己的 .img 目标。
image_target="rk3568-evb1-ddr4-v10.img"

test -f "$kernel_dir/Makefile"
test -s "$kernel_dir/.config"
test -x "$clang_dir/clang"
test -x "$clang_dir/ld.lld"
test -s "$base_boot"

make ARCH=arm64 CC="$clang_dir/clang" LD="$clang_dir/ld.lld" \
    BOOT_IMG="$base_boot" "$image_target"
```

该脚本按原笔记恢复了命令组织，尚未在你的 SDK 中重新执行。若该分支还要求指定 binutils/CROSS_COMPILE 或其他变量，应沿 `build.sh` 的真实调用补齐，不替换为前面独立 Linux 6.1 课程的任意工具链。


### 34.4.2 内核本地化

通过本章的学习，我们将掌握将半导体厂商提供的内核源码移植到我们自己的平台上。瑞芯微提供的内核源码是在瑞芯微官方的 rk3568_evb 开发板上运行的，所以我们肯定是以 rk3568_evb 开发板作为参考，然后将内核源码移植到iTOP-RK3568 开发板上。

**添加开发板默认配置文件**

1. 输入以下命令使能编译环境：

   ```bash
   source javaenv.sh
   
   source build/envsetup.sh
   
   lunch rk3568_r-userdebug
   ```

2. 首先查看默认的内核配置，我们输入以下命令

   ```bash
   get_build_var PRODUCT_KERNEL_CONFIG
   ```

   ![image-20240713151015281](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151015281.png)

   由上图可知，内核默认的配置文件为 rockchip_defconfig 和 android-11.config

3. 确定两个配置文件相对 SDK 的路径，输入以下命令查找

   ```bash
   find -name rockchip_defconfig
   
   find -name android-11.config
   ```

   ![image-20240713151050004](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151050004.png)

   由上图可知，因为 rk3568 是 arm64 架构，所以 rockchip_defconfig 的绝对路径是kernel/arch/arm64/configs/rockchip_defconfig。但是另一个确定不了，我们可以编译 内 核 看 看 是 否 有 相 关 打 印 信 息 ， 编 译 打 印 日 志 ， 如 下 所 示 ， 所 以android-11.config 的绝对路径是 kernel/kernel/configs/android-11.config

   ![image-20240713151118008](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151118008.png)

4. 将 rockchip_defconfig 和 android-11.config 重新复制一份，分别命名为itop_rockchip_defconfig 和 itop_android-11.config，命令如下：

   ```bash
   cd kernel/arch/arm64/configs/
   
   cp rockchip_defconfig itop_rockchip_defconfig
   
   cd - 
   
   cd kernel/kernel/configs/
   
   cp android-11.config itop_android-11.config
   ```

   ![image-20240713151145316](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151145316.png)

5. 我们进入 device 目录下，配置编译规则，然后查找 rockchip_defconfig，命令如下：

   ```bash
   cd device
   
   rg -n "rockchip_defconfig"
   ```

   ![image-20240713151229092](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151229092.png)

   由上图可知 rockchip/rk356x/BoardConfig.mk:PRODUCT_KERNEL_CONFIG ?=rockchip_defconfig 是有用信息。打开 device/rockchip/rk356x/BoardConfig.mk 文件，修改为如下图所示：

   ![image-20240713151257345](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151257345.png)

6. 然后我们进入 device 目录下，查找“android-11.config”，输入如下命令：

   ![image-20240713151317357](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151317357.png)

   由上图可知 rockchip/common/BoardConfig.mk:PRODUCT_KERNEL_CONFIG +=android-11.config 是有用信息。打开 device/rockchip/common/BoardConfig.mk 文件，修改为如下所示：

   ![image-20240713151339364](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151339364.png)

**添加开发板默认设备树**

添加适合迅为开发板的设备树文件，进入 kernel/arch/arm64/boot/dts/rockchip/目录下，复制一份 rk3568-evb1-ddr4-v10.dts，然后将其重命名为itop_rk3568-evb1-ddr4-v10.dts

![image-20240713151422152](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151422152.png)

添加设备树编译规则，输入以下命令查找 rk3568-evb1-ddr4-v10.dts

```bash
cd device/

rg -n "rk3568-evb1-ddr4-v10"
```

![image-20240713151454765](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151454765.png)

修改 rockchip/rk356x/BoardConfig.mk 文件，修改如下所示：

![image-20240713151507092](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151507092.png)

修改 rockchip/rk356x/rk3568_r/BoardConfig.mk 文件，

![image-20240713151518695](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713151518695.png)

这样编译 linux 的时候就可以从 itop_rk3568-evb1-ddr4-v10.dts 编译出itop_rk3568-evb1-ddr4-v10.dtb 文件了。

### 34.4.3 本地化后的变量还要核对最终值

原笔记把基础配置复制为 `itop_rockchip_defconfig`，把 Android 片段复制为 `itop_android-11.config`，把板级 DTS 复制为 `itop_rk3568-evb1-ddr4-v10.dts`。这些文件名应保留并由当前产品真正引用。

对应原笔记中的两处配置修改，概念上是让产品选择本板基础配置，并让公共 Android 追加规则引用本板片段：

```makefile
# 对照当前产品和实际文件所在位置维护，避免同时保留旧片段。
PRODUCT_KERNEL_CONFIG ?= itop_rockchip_defconfig
PRODUCT_KERNEL_CONFIG += itop_android-11.config
PRODUCT_KERNEL_DTS := itop_rk3568-evb1-ddr4-v10
```

这是把原截图中的变量关系写成文字示例，不是建议在同一个未知文件末尾重复添加全部三行。先查各变量已有定义和包含顺序，再用 `get_build_var` 确认最终结果。设备树目标有的规则不带 `.dts` 扩展名，以本 SDK 的构建脚本为准。

<a id="part-52"></a>

## 34.5 实测 SDK 构建命令与调试串口

### 34.5.1 先复现本板的两条常用命令

在已选择正确产品的 **Android SDK 顶层**，原笔记记录的整体构建命令为：

```bash
./build.sh -AUCKu
```

原笔记的内核相关构建命令为：

```bash
./build.sh -ACK
```

这组大小写组合属于此版厂商脚本，不是 AOSP 的通用选项。保留实测命令，并通过本版 `build.sh` 的 usage、getopts 和构建日志确认它实际执行了哪些构建/打包步骤；不要用 Linux SDK 中的 `./build.sh kernel` 替代。

原笔记“编写 rockdev 下的 boot.img”按上下文应为“烧写/更新构建产出的 boot.img”。操作前确认源文件和实际目标分区；更新方式参考第 29 篇及本产品 AndroidTool 配置，不在已有 Android 分区布局上套用独立 Linux 系统的三分区偏移。

### 34.5.2 保留本板 FIQ Debugger 的实测配置

以下片段位于原记录的 `rk3568-android.dtsi`。串口选择、引脚和 115200 波特率按你的实测值保留：

```dts
   //rk3568-android.dtsi中19行
   	fiq-debugger {
   		compatible = "rockchip,fiq-debugger";
   		rockchip,serial-id = <2>;
   		rockchip,wake-irq = <0>;
   		/* If enable uart uses irq instead of fiq */
   		rockchip,irq-mode-enable = <1>;
   		rockchip,baudrate = <115200>;  /* Only 115200 and 1500000 */
   		interrupts = <GIC_SPI 252 IRQ_TYPE_LEVEL_LOW>;
   		pinctrl-names = "default";
   		pinctrl-0 = <&uart2m0_xfer>;
   		status = "okay";
   	};
```

### 34.5.3 为什么只改终端波特率不一定够

BootROM/DDR 或 SPL、U-Boot、Linux 的普通串口驱动、FIQ Debugger 和用户态终端可能分别设置串口及波特率。

这份 Android BSP 中 `fiq-debugger` 是 Rockchip 的调试路径，不能仅凭 `serial-id = <2>` 就认定所有 Linux 控制台一定叫 `ttyS2`；实际可能涉及 `ttyFIQ0` 等命名，以 dmesg 和启动参数为准。

修改时核对：物理串口接线及电平、UART pinmux、Bootloader 日志配置、FIQ 节点、`chosen/stdout-path`、最终 `/proc/cmdline`。只在某一阶段乱码，往往说明阶段间的波特率尚未统一；正常进入 ADB 后没有串口登录提示，也不等于内核没有启动。


## 34.6 认识本 BSP 的配置、产物和启动镜像

### 34.6.1 产品配置怎样选择内核和设备树

在已加载环境、选择 `rk3568_r-userdebug` 的 **SDK 顶层 Bash** 中查看：

```bash
get_build_var TARGET_PRODUCT
get_build_var TARGET_BUILD_VARIANT
get_build_var PRODUCT_KERNEL_CONFIG
get_build_var PRODUCT_KERNEL_DTS
get_build_var TARGET_OUT_VENDOR
```

变量是否存在、取值和使用位置由该 SDK 决定。遇到空值时，沿产品 Makefile 和脚本查找，不以文件名猜最终配置：

```bash
rg -n 'PRODUCT_KERNEL_CONFIG|PRODUCT_KERNEL_DTS|BOOT_IMG' \
    device/rockchip build.sh kernel/Makefile
```

| 层次 | 作用 |
| --- | --- |
| 产品选择 | lunch 选择具体 product 和构建类型 |
| BoardConfig / 产品 Makefile | 指定内核配置、DTS、分区、HAL、包和文件复制 |
| defconfig / fragment | 表达希望启用的内核功能及 Android 需求 |
| 最终 .config | Kconfig 处理依赖之后，实际用于构建的结果 |
| 顶层 DTS + 包含文件 | 合并 SoC 资源、公共板级资源和当前板卡覆盖 |
| 打包与复制规则 | 决定构建产物进入哪个最终镜像 |

`?=` 通常只在变量尚未定义时赋值，`+=` 追加，`:=` 进行立即展开赋值；实际读取顺序还决定哪个值最终生效。直接修改一个被覆盖的公共变量，可能看不到预期结果。

### 34.6.2 各类镜像的职责

| 产物 | 本 BSP 中的理解方式 |
| --- | --- |
| Image | ARM64 Linux 裸内核映像，不是完整 Android boot.img |
| DTB / DTBO | 硬件描述及可选覆盖；本产品是否使用独立 dtbo 分区需检查 |
| resource.img | Rockchip BSP 的资源封装，可涉及 DTB、Logo 等，具体看本分支 |
| boot.img | Android 启动容器；本笔记的打包流程会组合/更新内核与相关启动资源 |
| recovery.img | 恢复环境的镜像；内容与大小必须匹配产品布局 |
| system / vendor 等镜像 | Android 系统和厂商组件，HAL、模块、IQ、权限等按打包规则进入相应镜像 |
| super.img | 仅在启用相应动态分区方案时出现，不能推断本板必然使用 |
| update.img | Rockchip 整机升级包，包内有哪些项目由产品打包清单决定 |

Android 不同启动镜像版本和 BSP 对 DTB/resource 的组织不同。原笔记中“更新 boot.img 可更新本产品内核和设备树”应限定到本版构建流程，不能解释成所有 Android 11 设备的 DTB 都一定封装在同一位置。

### 34.6.3 哪类修改需要更新哪部分

| 修改 | 需要核对的产物 |
| --- | --- |
| 内核 C 代码、内建驱动、内核配置 | 内核及本产品启动镜像 |
| 板级 DTS | 实际启动使用的 DTB/资源/boot 或对应 dtbo，按构建日志确认 |
| 模块驱动 | 匹配的 .ko、安装目录；必要时还要更新内核或模块依赖信息 |
| WiFi HAL、Camera HAL | 对应用户态库/服务及其所在镜像 |
| IQ、IDC、固件、init rc、权限配置 | 实际安装它们的镜像和目标路径 |
| 分区大小 | 构建变量、打包布局、设备上实际分区需一致 |

例如，35 篇修改的 Panel 设备树不能只停留在源码中；36 篇 WiFi HAL 修改也不会通过单独更新 boot.img 自动生效；37 篇换 IQ 文件应落实到相应 vendor 打包规则。

## 34.7 内核配置与设备树怎样做到可复现

### 34.7.1 保存 menuconfig 的有效修改

本 BSP 使用“基础 defconfig + Android 配置片段”。`menuconfig` 修改的是最终 `.config`；下一次重新生成配置，可能又被基础配置或后续 fragment 改回去。

可以按以下步骤记录一次驱动修改：

1. 保存修改前的最终 `.config`，确认目标驱动所属 Kconfig。
2. 在本产品环境中启用功能，重新构建并检查最终配置。
3. 比较前后差异，找到真正需要持久保存的配置项和依赖。
4. 将差异放回本产品维护的配置来源，再重新生成，确认结果保持一致。

在 **kernel 目录**可用：

```bash
cp .config /tmp/rk3568-android11.config.before
make ARCH=arm64 menuconfig
scripts/diffconfig /tmp/rk3568-android11.config.before .config
```

如果 kernel 使用分离输出目录，应检查该目录中的 `.config`，而不是误读源码树里的旧文件。不要把包含全部结果的 `.config` 直接覆盖精简的 Android fragment。

### 34.7.2 板级 DTS 尽量集中描述差异

`rk3568.dtsi` 描述 SoC 资源；参考板和公共 `.dtsi` 继续补充板级资源；本产品顶层 DTS 决定包含关系和最终覆盖。

优先在本板维护的文件中处理屏幕、触摸、无线和摄像头差异，减少对其他产品共用资源的影响。遇到同名属性被多次设置，检查合并后的结果；`status = "okay"` 也不自动满足供电、时钟、pinctrl 和驱动依赖。

运行时 DT 可辅助确认实际加载内容：

```sh
adb shell cat /proc/device-tree/model
adb shell cat /proc/cmdline
```

设备树属性可能以 NUL 结尾，二进制 cells 也不是可直接当文本读的数字。需要分析时可从允许读取的 `/sys/firmware/fdt` 或 `/proc/device-tree` 提取，再在有 `dtc` 的主机上反编译；该节点是否存在及访问权限依内核配置而定。

### 34.7.3 构建、更新、运行要对应上

一次完整循环应留下：源码差异 → 构建命令和日志 → 新产物的时间/哈希 → 实际更新的分区/文件 → 运行版本及设备行为。

在 Linux 构建主机可记录：

```bash
sha256sum kernel/boot.img
stat kernel/boot.img
```

上板后同时检查 `uname -a`、产品 build 信息、设备树 model 及相关驱动日志。只看烧录工具提示成功，不能证明下载的是最新文件；只看版本号，也不一定能区分两次同版本构建。

## 34.8 Android 的 init、权限、HAL 与文件部署

### 34.8.1 init rc 管理的是用户空间服务

Android init 根据对应阶段及触发条件解析 rc，启动服务并设置权限、目录等。HAL 或厂商守护进程需要有正确的可执行路径、用户/组、接口声明及 SELinux 配置。

定位本 SDK 实际定义：

```bash
rg -n 'camera|wifi|wpa_supplicant|hwcomposer' \
    device/rockchip vendor/rockchip --glob '*.rc' --glob '*.xml'
```

目录名和服务名以该 BSP 为准。不能仅因为看见 `rkaiq_3A_server` 在 Linux SDK 中运行，就在 Android 的 init 中再添加一份相同实例。

### 34.8.2 驱动可用和 HAL 可用是两层验收

| 内核层证据 | Android 层还要检查 |
| --- | --- |
| 触摸 event 节点产生坐标 | InputReader 分类、IDC、显示 viewport |
| WiFi 建立无线接口 | 厂商识别/模块选择、HAL、supplicant 和网络服务 |
| 摄像头可以 V4L2 采集 | Camera Provider、camera ID、流配置、IQ 和权限 |
| DRM 输出画面 | HWC、SurfaceFlinger、模式选择和亮度管理 |

很多“Linux 下正常，Android 下不正常”发生在后面这层，但仍要先证明两边运行的内核、驱动和设备树确实一致。

### 34.8.3 处理 Permission denied 时分清原因

设备文件的 UID/GID、传统访问位、进程所属用户/组、应用权限和 SELinux 都可能影响访问。

```sh
adb shell id
adb shell getenforce
adb shell ls -lZ /dev/video0
adb shell ls -lZ /dev/input
adb logcat -b all -d > android-permission.log
```

`/dev/video0` 只是演示路径，换成实际出错的节点。检查拒绝日志中的进程、对象和操作，并定位该产品的 ueventd、文件上下文及策略来源。手工 `chmod` 可能在重启后丢失，也不能替代 SELinux 策略；全局 permissive 不作为最终适配结果。

## 34.9 ADB、日志与 Android 11 调试环境

### 34.9.1 先确认板端版本与构建类型

在 **主机终端**：

```sh
adb devices -l
adb shell getprop ro.build.version.release
adb shell getprop ro.build.type
adb shell getprop ro.build.fingerprint
adb shell uname -a
adb shell cat /proc/version
adb shell getprop sys.boot_completed
```

连接多台设备时用 `adb -s 序列号` 指定目标。`userdebug` 常提供 `adb root`，但还要满足该 BSP 的 adbd、授权及调试设置；普通 user 版不能据此推断具有同样权限。

### 34.9.2 内核日志与用户空间日志分开抓

```sh
adb shell dmesg > kernel-android11.log
adb logcat -b all -d > logcat-android11.log
adb shell dumpsys display > display-state.txt
adb shell dumpsys input > input-state.txt
adb shell dumpsys wifi > wifi-state.txt
adb shell dumpsys media.camera > camera-state.txt
```

`dmesg` 可能需要 root；服务名和工具选项以本机为准。没有进入 Android 的故障主要看串口，而不是等待 logcat；已经进入 Android 的 HAL/应用故障需要同时看 logcat 和内核日志。

把“开机”“点击开关”“开始预览”等动作的时间与日志对应起来，再定位最先失败的层次。

### 34.9.3 调试 vendor 中的文件

在自己的 userdebug 开发板上，先尝试：

```sh
adb root
adb wait-for-device
adb remount
```

如果工具提示验证或 overlayfs 条件未满足，按实际输出和此 BSP 的开发流程处理。AOSP Android 11 的对应说明给出的常见流程为：

```sh
adb root
adb disable-verity
adb reboot
adb wait-for-device
adb root
adb remount
```

这会改变开发板的验证/挂载状态，只用于需要这类修改的调试环境；本次整理没有连接开发板执行。若当前产品已允许直接 remount，不需要重复关闭验证。相关流程参见 [Android 11 OverlayFS 与 adb remount](https://android.googlesource.com/platform/system/core/+/refs/heads/android11-release/fs_mgr/README.overlayfs.md)。

手工替换文件适合缩短试验循环，最终仍需将配置、HAL、IQ 或 IDC 文件接入 SDK 的复制/安装规则，重新构建并冷启动验证。

## 34.10 把四篇讲义组织成完整适配过程

### 34.10.1 建议的实验顺序

| 步骤 | 目标与讲义 |
| --- | --- |
| 1 | 本篇：固定 SDK、产品和工具链，原版能构建和启动 |
| 2 | 本篇：明确本板 defconfig、fragment、DTS 及实际 boot.img |
| 3 | [显示与触摸](35-显示与触摸屏移植.md)：DSI/Panel、触摸事件、Android 坐标映射 |
| 4 | [WiFi](36-以太网与WiFi移植.md)：RTL8723DU 驱动、HAL 识别和联网；以太网部分保留原讲义 |
| 5 | [摄像头](37-摄像头移植与采集验证.md)：Sensor、媒体链路、IQ 与 Android 相机 |
| 6 | 形成可重建镜像、修改说明和复测记录 |

本篇保留原笔记的实测命令；新增的步骤用于解释和补全工程过程，不将新增内容标记成已经上板通过。

### 34.10.2 每项改动留下四类证据

保存代码/配置差异、构建环境和命令、实际部署的产物与哈希、运行日志与功能结果。相同名称的源码目录或镜像不能代替版本记录。

本次只读参考了你提供的原厂资料。原厂 Linux 软件、WiFi 和 VI 指南多涉及 4.19 或更早 BSP，其中 Linux 用户空间的脚本不能直接当作 Android 11 服务配置：

| 资料 | 用途 |
| --- | --- |
| 原始第 34–37 篇笔记 | 迅为 RK3568、Android 11 的构建和外设实测基线 |
| [Rockchip Linux 软件开发指南](../u盘资料/必须/15开发板原厂文档/docs/Rockchip_Developer_Guide_Linux_Software_CN.pdf) | BSP、内核、设备树和镜像等通用概念；不是 Android build.sh 选项的替代手册 |
| [AOSP Build Android](https://source.android.com/docs/setup/build/building) | 构建环境、目标和构建类型概念 |
| [Android 11 init 文档](https://android.googlesource.com/platform/system/core/+/refs/heads/android11-release/init/README.md) | init 语法、服务和触发机制 |
| [Android 11 OverlayFS 文档](https://android.googlesource.com/platform/system/core/+/refs/heads/android11-release/fs_mgr/README.overlayfs.md) | userdebug 文件更新和 remount 的条件 |
| 第 35–37 篇末尾原厂资料 | 显示、WiFi、VI/ISP 的对应原理与排查方法 |

本次检查命令片段语法、章节/链接和已验证配置的保留情况，未重新执行完整 SDK 构建、烧录或硬件功能测试。



---

[总目录](总目录.md) · [上一篇：USB通信](33-USB通信.md) · [下一篇：显示与触摸屏移植](35-显示与触摸屏移植.md)
