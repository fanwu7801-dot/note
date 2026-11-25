# 26-根文件系统与BusyBox及Ubuntu制作

[总目录](总目录.md) · [上一篇：U-Boot基础与源码启动流程](25-U-Boot%E5%9F%BA%E7%A1%80%E4%B8%8E%E6%BA%90%E7%A0%81%E5%90%AF%E5%8A%A8%E6%B5%81%E7%A8%8B.md) · [下一篇：Qt交叉编译与部署](27-Qt%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E4%B8%8E%E9%83%A8%E7%BD%B2.md)

[TOC]

<a id="part-45"></a>

## 26.1 根文件系统介绍

一个完整的嵌入式 Linux 系统，包含 uboot，Linux 内核，根文件系统三个部分。其启动顺序为，在系统刚一上电的时候，先执行 uboot，由 uboot 引导内核，内核启动成功之后挂载根文件系统。根文件系统挂载成功以后，嵌入式 Linux 系统就启动成功了。在开发板上看到的现象是：用户可以在串口控制台上输入命令与 Linux 系统进行交互。

如何移植 uboot,如何移植 Linux 内核以及驱动程序的编写，之前已经给大家讲过。但是文件系统要如何构建这部分还没有给大家讲解，所以从这一期开始，我们来学习根文件系统相关的知识。

嵌入式 Linux 系统构成图：

![image-20240713152630010](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713152630010.png)

要想讲清楚是文件系统，可以将文件系统在字面上分为俩部分来理解，一部分是文件，一部分是系统。那文件系统是不是可以理解成是组织和管理文件的一个系统呢。所以有了文件系统以后，就可以轻松的操作存储在存储介质的文件。比如删除一个文件，新增一个文件等。文件系统的格式（类型）有多种，如 fat32 ext2 ext3 ntfs 等。

### 26.1.1 文件系统目录

Linux 文件系统中一般由如下的几个目录构成。这些目录用于不同的功能。

**1  /bin** **目录**

该目录下主要是存放 Linux 命令，这些可以被 root 和普通用户所使用，/bin 目录下常用的命令有：cat chgrp chmod cp ls sh kill mount umount 

**2 /sbin** **目录**

该目录下存放的是系统命令，只有系统管理员（俗称最高权限的 root）能够使用的命令，除此之外系统命令还可以存放在/usr/sbin,/usr/local/sbin 目录下。/sbin 目录下常用的命令有：shutdown reboot fdisk fsck init 等。

**3 /dev** **目录**

该目录下存放的是设备接口的文件，设备文件是 Linux 中特有的文件类型，在 Linux 系统下，一切皆文件。所以以文件的方式访问各种设备，即通过读写某个设备文件操作某个具体硬件。比如通过“/dev/ttySAC0”文件可以操作串口 0 等。

**4 /etc** **目录**

该目录下存放着系统主要的配置文件

**5 /lib** **目录**

Lib 是 library 的简称，也就是库的意思，因此此目录下存放着 Linux 所必须的库文件。

**6 /home** **目录**

系统默认的用户文件夹，它是可选的，对于每个普通用户，在/home 目录下都有一个以用户名命名的子目录，里面存放用户相关的配置文件。

**7 /root** **目录**

系统管理员（root）的主文件夹，即是根用户的目录，与此对应，普通用户的目录是/home 下的某个子目录。

**8 /usr** **目录**

usr 是 unix shared resources(共享资源)的缩写，用来存放用户的应用程序和文件。

**9 /var** **目录**

var 是 variable(变量)的缩写，/var 目录中存放可变的数据，如日志文件。

**10 /proc 目录**

这是一个空目录，常作为 proc 文件系统的挂接点

**11 /mnt** **目录**

用于临时挂载某个文件系统的挂接点，通常是空目录，也可以在里面创建一引起空的子目录，比如/mnt/cdram /mnt/hda1 。用来临时挂载光盘、移动存储设备等。

**12 /tmp** **目录**

用于存放临时文件，通常是空目录，一些需要生成临时文件的程序用到的/tmp 目录下。

### 26.1.2 什么是根文件系统

根文件系统也可以组织和管理文件，所以根文件系统也是文件系统。但是为什么多了一个根字呢？因为在 Linux 系统上没有盘符这个概念,是使用一个类似大树一样的结构来组织和管理的。这颗大树的最底端就叫做根，然后每个目录都是这个树干上的子目录。

Linux 系统上是用“/”来表示根，一般也叫做根目录。在根目录下有非常多的特定目录。这些由特定目录挂载（mount）在根目录下。那这些挂载在根目录下由特定目录（特定目录介绍见本篇后续的目录结构说明）构成的文件构建系统就叫做文件系统。

所以根文件系统是一个挂载在 Linux 根目录下的，有特定目录组成的文件系统。如下图所示：

![image-20240713152946001](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713152946001.png)

### 26.1.3 根文件系统制作工具

最简单的根文件系统一般使用 busybox 工具制作。除此之外，还可以使用 buildroot 工具和 yocto 工具构建根文件系统。当然也可以直接使用发行版 Linux 系统，如 Ubuntu 系统，Debian系统。这些文件系统之间的界限没有很明确的界定。以下大致列出一些根文件系统的特点，如下图所示：

![image-20240713153016125](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153016125.png)

接下来我们分别来看下这些文件系统。

**Buildroot**

Buildroot 是 Linux 平台上一个开源的嵌入式 Linux 系统自动构建框架。整个Buildroot 是由 Makefile 脚本和 Kconfig 配置文件构成的。你可以通过 Buildroot 配置编译出一个完整的可以直接烧写到机器上运行的 Linux 系统软件。这里我们只是使用buildroot 编译文件系统。

![image-20240713153048641](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153048641.png)

Buildroot 优势：

1 通过源码构建，有很大的灵活性

2 方便的交叉编译环境，可以进行快速构建

3 方便各系统组件配置及定制开发

**Yocto**

Yocto 和 Buildroot 一样, 是一套构建嵌入式系统的工具,但是两者的风格完全不同。Yocto project 是通过一个个单独的包(meta)来维护,比如有的包负责核心,有的包负责外围。有的包用于跑 Rockchip 的芯片,有的包用于安装上 Qt。

![image-20240713153136934](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153136934.png)

Yocto 的优缺点：

1 支持的架构多：ARM MIPS PPC 和其他架构。

2 通过 QEMU 完全支持各种设备仿真

3 灵活性： 公司以多种不同的方式使用 Yocto 项目。一个示例是创建内部 Linux 发行版，作为公司可以跨多个产品组使用的代码库。通过自定义和分层，项目组可以利用基础 Linux 发行版创建适合其产品需求的分发。

**Ubuntu**

Ubuntu 是一个流行的 Linux 发行版，是基于 Debian 的 unstable 版本加强而来，以“最好的 Linux 桌面系统”而闻名，近些年 Ubuntu 也推出了 Ubuntu Enterprise Linux, 在企业Linux 应用市场占有率也有较大提高。

优点：技术支持较好，用户界面友好，硬件的兼容性好，采用基于 Deb 的 ATP 包管理系统。

缺点：技术支持和更新服务是需要付费的, 服务器软件生态系统的规模和活力方面稍弱。

**Debian**

Debian GNU / Linux 是一款是由 GPL 和其他自由软件许可协议授权的自由软件组成的Linux 操作系统，由 Debian Project 组织维护。以其坚守 Unix 和自由软件的精神，以及其给予用户的众多选择而闻名。

优点：Debian 是极为精简而稳定的 Linux 发行版，有着干净的作业环境，采用基于 Deb的 ATP 包管理系统。

缺点：不提供专门技术支持，不包含封闭源代码软件；发行周期过长，稳定版本中软件过时。中文支持不是很完善。

<a id="part-48"></a>

## 26.2 Ubuntu 根文件系统制作

1. 下载ubuntu-base文件系统：

   > http://cdimage.ubuntu.com/

2. 新建一个目录，被解压到里面去

3. 安装qemu

   > sudo apt install qemu-user-static

4. 把虚拟机ubuntu中/usr/bin/qemu-aarch64-static复制到下载的ubuntu文件系统中的usr/bin

   > cp /usr/bin/qemu-aarch64-static ubuntu/usr/bin/

5. 把虚拟机ubuntu中/etc/resolv.conf复制到下载的ubuntu文件系统中的etc/

   > cp /etc/resolv.conf  ubuntu22/etc/

6. 把虚拟机ubuntu中/etc/apt/sources.list复制到下载的ubuntu文件系统中的etc/apt/

   ```shell
   deb http://mirrors.aliyun.com/ubuntu-ports/ jammy main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ jammy main restricted universe multiverse
   
   deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-security main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ jammy-security main restricted universe multiverse
   
   deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-updates main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ jammy-updates main restricted universe multiverse
   
   # deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-proposed main restricted universe multiverse
   # deb-src http://mirrors.aliyun.com/ubuntu-ports/ jammy-proposed main restricted universe multiverse
   
   deb http://mirrors.aliyun.com/ubuntu-ports/ jammy-backports main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ jammy-backports main restricted universe multiverse
   ```

   ```shell
   deb http://mirrors.aliyun.com/ubuntu-ports/ focal main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal main restricted universe multiverse
   
   deb http://mirrors.aliyun.com/ubuntu-ports/ focal-security main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-security main restricted universe multiverse
   
   deb http://mirrors.aliyun.com/ubuntu-ports/ focal-updates main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-updates main restricted universe multiverse
   
   # deb http://mirrors.aliyun.com/ubuntu-ports/ focal-proposed main restricted universe multiverse
   # deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-proposed main restricted universe multiverse
   
   deb http://mirrors.aliyun.com/ubuntu-ports/ focal-backports main restricted universe multiverse
   deb-src http://mirrors.aliyun.com/ubuntu-ports/ focal-backports main restricted universe multiverse
   ```

   

7. 挂载虚拟文件系统

   ```shell
   sudo mount -t proc /proc ubuntu22/proc
   sudo mount -t sysfs /sys ubuntu22/sys
   sudo mount -o bind /dev ubuntu22/dev
   sudo mount -o bind /dev/pts ubuntu22/dev/pts
   ```

8. chroot ubuntu22/

9. 安装软件包

   > chmod 1777 /tmp
   >
   > apt update
   >
   > apt install vim net-tools wget curl sudo  systemd openssh-server network-manager
   >
   > #qt
   >
   > apt install -y qtbase5-dev qtchooser qt5-qmake
   >
   > #桌面
   >
   > apt install -y ubuntu-desktop
   >
   > apt clean
   >
   > passwd  设置密码

10. exit

11. umount

    ```shell
    sudo umount ubuntu22/proc
    sudo umount ubuntu22/sys
    sudo umount ubuntu22/dev/pts
    sudo umount ubuntu22/dev
    ```

## 26.3 BusyBox 制作最小根文件系统

### 26.3.1 Busybox 工具简介

在制作文件系统的时候，可以使用“Busybox 工具”.

“BusyBox 工具”是一个集成了一百多个最常用 Linux 命令和工具的软件。BusyBox 包含了一些简单的工具，例如 ls、cat 和 echo 命令等等，还包含了一些更大、更复杂的工具，例 grep、find、mount 以及 telnet 命令。有些人将 BusyBox 称为 Linux 工具里的“瑞士军刀”。简单的说 BusyBox 就好像是个大工具箱，它集成压缩了 Linux 的许多工具和命令，也包含了 Android 系统自带的 shell。

“Busybox 工具”的官方网址是“http://www.busybox.net/”，这是一个开源的程序，并且一直在更新中，我们使用的版本是“busybox-1.33.1.tar.bz2”。下面我们来讲解一下如何使用 BusyBox 制作最小文件系统。

### 26.3.2 设置支持中文

首先拷贝“busybox-1.33.1.tar.bz2”到我们的虚拟机 Ubuntu 系统上，然后在 Ubuntu 命令行，执行“ tar -xvf busybox-1.33.1.tar.bz2”解压命令。

解压完成后，使用“ cd busybox-1.33.1”命令进入到前面解压出来的“busybox-1.33.1”文件夹中。

从 busybox1.17.0 以上之后，对 ls 命令不做修改是无法显示中文的。就算是内核设置了支持中文的话，在 shell 下用 ls 命令也是无法显示中文的，这是因为 busybox1.17.0 以后版本对中文的支持进行了限制。要想让 busybox1.17.0 以上支持中文，需做如下修改。

首先使用以下命令对 printable_string.c 文件进行修改，如下图所示：

> vim libbb/printable_string.c

![image-20240713153511708](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153511708.png)

然后查找函数 printable_string，我们可以看到在第 31,32 行和 45 行的操作，大于 0x7F的字符直接被 break 掉，或者直接被“？”代替了。所以就算是 linux 内核设置了支持中文，也是无法显示出来的。所以我们对这三行进行修改，注释掉对大于 0x7f 字符的相关操作。如图所示：

![image-20240713153533587](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153533587.png)

修改之后保存退出。然后使用命令“vim libbb/unicode.c”，对 unicode.c 文件进行修改，如下图所示：

![image-20240713153558658](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153558658.png)

打开之后查找函数 unicode_conv_to_printable2，我们可以看到 1022 行和 1030 行也对大于0x7f 的字符有对应操作，同样的我们对这两处做修改，如图所示，修改之后保存退出。

![image-20240713153619632](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153619632.png)

经过以上修改之后，源码就可以支持中文字符了，但还需要配置 busybox 来使能 unicode码，输入“make menuconfig”命令，进入“Busybox”的配置界面。依次选择如下配置项：

> Settings -->
>
> Support Unicode
>
> Check $LC_ALL, $LC_CTYPE and $LANG environment variables

![image-20240713153649020](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153649020.png)

接着使用左右反方向按键，选择“Exit”，回到“Busybox Configuration”界面。然后使用“->”“<-”按键，选择“Exit”，选择“Yes”保存配置

经过以上配置最小系统就可以支持中文了。

### 26.3.3 配置 busybox

接下来对 Busybox 进行编译配置，输入“ make menuconfig”命令，如下图，出现“Busybox” 的配置界面。

![image-20240713153733485](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153733485.png)

进入“Busybox”的配置界面。依次选择如下配置项：

> Settings -->
>
> Build Options
>
> Cross Compiler prefix

进入“Cross Compiler prefix”配置界面，如下图所示：

![image-20240713153808576](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153808576.png)

如下图，输入交叉编译工具。注意！ 交叉编译器的设置需要根据使用的开发板进行设置， RK3568 开发板，需要设置 RK3568 的交叉编译器，则输入“aarch64-linux-gnu-”。

![image-20240713153831791](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713153831791.png)

按“回车”返回到“Setting”配置界面，这时可以看到刚才我们设置的交叉编译工具.

选中“Installation Options”配置项,设置安装路径为../system

选中“Exit”按“回车”继续退出，直到弹出以下界面，选择“yes”保存退出，如下图所示。至此我们的 busybox 就设置好了。

### 26.3.4 编译 busybox

保存退出之后，我们需要设置临时环境变量如下图所示：

> export PATH=/usr/local/arm64/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin:$PATH

执行“make”进行编译，编译完成，接下来我们需要把编译生成的“二进制文件”安装到刚才我们指定的“../system”目录里面，安装二进制文件到“../system”目录，如下图，输入命令“ make install”。完成后如下图所示：

![image-20240713154022015](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713154022015.png)

然后使用“ cd ../system”命令，进入“../system”目录，查看里面安装的文件，如下图所示

![image-20240713154035004](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713154035004.png)

至此我们由 busybox 制作的文件系统就制作好了。但是还需要一些步骤来对该文件系统进行完善。

### 26.3.5 完善最小根文件系统

#### 26.3.5.1 创建必要文件夹

文件系统还需要新建“dev,etc,lib,mnt,proc,sys,tmp,var”文件夹

> mkdir dev etc lib mnt proc sys tmp var etc/init.d

#### 26.3.5.2 拷贝 lib 库文件

Busybox 编译生成的二进制文件是以动态链接库的形式运行，所以我们需要拷贝编译器里面的库文件到“lib”目录，使用以下命令：

> cp -r  gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/aarch64-linux-gnu/libc/lib/* . /lib/

#### 26.3.5.3 创建 rcS 文件

然后我们需要创建/etc/init.d/rcS 文件 ，在 system 目录下使用“vim etc/init.d/rcS”命令建立“rcS”文件，并在“rcS”文件输入下面的内容。

```shell
#! /bin/sh
PATH=/sbin:/bin:/usr/sbin:/usr/bin:/usr/local/bin:$PATH
runlevel=S
prevlevel=N
umask 022
export PATH runlevel prevlevel
/bin/hostname woniu
mount -a
mkdir /dev/pts
mount -t devpts devpts /dev/pts
echo /sbin/mdev > /proc/sys/kernel/hotplug
mkdir -p /var/empty
mkdir -p /var/log
mkdir -p /var/log/boa
mkdir -p /var/lock
mkdir -p /var/run
mkdir -p /var/tmp
syslogd
/etc/rc.d/init.d/netd start
mkdir /mnt/disk
sleep 1
echo "*************************************" >/dev/ttyFIQ0
echo "http://woniuxy.com" > /dev/ttyFIQ0
echo "*************************************" > /dev/ttyFIQ0
```

下面我们来分析每一句命令的作用。

> 第 1 行表示该文件为一个 shell 脚本。
>
> 第 2 行和后面的第 6 行指定了 PATH 环境变量，PATH 这个环境变量是 linux 系统内部定义的一个环境变量，含义是操作系统去执行程序时会默认到 PATH 指定的各个目录下去寻找。如果找不到就认定这个程序不存在，如果找到了就去执行它。将一个可执行程序的目录导出到 PATH，可以让我们不带路径来执行这个程序。
>
> rcS 中为什么要先导出 PATH？就是因为我们希望一旦进入命令行下时，PATH 环境变量中就有默认的/bin /sbin /usr/bin /usr/sbin 这几个常见的可执行程序的路径，这样我们进入命令行后就可以 ls、cd 等直接使用了。
>
> 第 3 行和第 6 行指定了 runlevel 环境变量，runlevel=S 表示将系统设置为单用户模式。
>
> 第 5 行指定当前用户在创建文件时的默认权限。
>
> 第 6 行导出环境变量
>
> 第 7 行设置机器名字为woniu
>
> 第 8 行 mount -a 是挂载所有的应该被挂载的文件系统，在 busybox 中 mount -a 时 busybox会去查找一个文件/etc/fstab 文件，这个文件按照一定的格式列出来所有应该被挂载的文件系统（包括了虚拟文件系统），在这里我们还没有创建，下面会进行创建。
>
> 第 9 和 10 行，创建目录/dev/pts，然后将 devpts 挂载到/dev/pts 目录中。
>
> 第 11 和 12 行，使用 mdev 来管理热插拔设备，Linux 内核就可以在/dev 目录下自动创建设备节点. 
>
> 第 13 行到 18 行，在对应的目录下创建相应的文件。
>
> 第 19 行 syslogd 记录系统或应用程序产生的各种信息，并把信息写到日志中
>
> 第 20 行启动 netd 服务，我们在之后会创建这个文件
>
> 第 21 行在 mnt 下创建 disk 文件夹，方便外部设备（U 盘，TF 卡）的挂载。
>
> 第 22 行设置本地回环 lo 为 127.0.0.1。
>
> 第 23 行执行 ifconfig-eth0 脚本配置网络，在下面的步骤中会创建这个脚本。

修改完成之后，我们需要使用命令“chmod 777 rcS”，来给予文件可执行权限。

#### 26.3.5.4 创建 fstab 文件

文件 fstab 包含了你的电脑上的存储设备及其文件系统的信息。它是决定一个硬盘（分区）被怎样使用或者说整合到整个系统中的唯一文件。

这个文件的全路径是/etc/fstab。它只是一个文本文件，你能够用你喜欢的编辑器打开它，但是必须是 root 用户才能编辑它。同时 fsck、mount、umount 的等命令都利用该程序。

具体来说： 用 fstab 可以自动挂载各种文件系统格式的硬盘、分区、可移动设备和远程设备等。 对于 Windows 与 arch 双操作系统用户，用 fstab 挂载 FAT 格式和 NTFS 格式的分区，可以在 Linux 中共享 windows 系统下的资源。

让我们对 fstab 的用法进行一个详细的了解。

/etc/fstab 由下面的 fields 组成 (fields 之间以空格或 tab 分开):

> <file system> <dir> <type> <options> <dump> <pass>

> <file systems> - 存储设备的标识 (i.e. /dev/sda1). 
>
> <dir> - 告诉 mount 命令应该将文件设备挂载到哪里。
>
> <type> - 定义了要挂载的设备或是分区的文件系统类型，支持许多种不同的文件系统，如ext2, ext3, reiserfs, xfs, jfs, smbfs, iso9660, vfat, ntfs, swap 以及 auto。 'auto' 类型使 mount 命令对这文件系统类型进行猜测，这对于如 CDROM 和 DVD 之类的可移动设备是非常有用的。
>
> <options> - 定义了不同文件系统的特殊参数，不同文件系统的参数不尽相同。其中一些比较通用的参数有以下这些：
>
> <dump> dump utility 用来决定何时作备份. 安装之后 ( ArchLinux 默认未安装 ), dump会检查其内容，并用数字来决定是否对这个文件系统进行备份。允许的数字是 0 和 1 。0 表示忽略， 1 则进行备份。大部分的用户是没有安装 dump 的 ，对他们而言 <dump> 应设为0。
>
> <pass> fsck 读取 <pass> 的数值来决定需要检查的文件系统的检查顺序。允许的数字是 0, 1, 和 2。根目录应当获得最高的优先权 1, 其它所有需要被检查的设备设置为 2. 0 表示设备不会被 fsck 所检查。

在对 fstab 有了一定了解之后，我们使用命令“vim etc/fstab”创建 fstab 文件，并写入以下内容：

> \#<file system> <dir> <type> <options> <dump> <pass>
>
> proc /proc proc  defaults 0 0
>
> tmpfs /tmp tmpfs defaults 0 0
>
> sysfs /sys sysfs defaults 0 0

![image-20240713154649816](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713154649816.png)

修改完成之后，我们需要使用命令“chmod 777 fstab”，来给予文件可执行权限.

#### 26.3.5.5 创建 inittab 文件

init 进程为内核加载文件系统的第一个进程，一般称为 0 号进程，init 进程启动后会自动读取 inittab。

inittab 文件中每一行的格式如下所示：（busybox 的根目录下的 example 文件夹下有详尽的inittab 文件范例）

> <id>:<runlevel>:<action>:<process>

尽管此格式与传统的 Sytem V init 类似，但是，id 在 BusyBox 的 init 中具有不同的意义。对 BusyBox 而言，id 用来指定启动进程的控制 tty。如果所启动的进程并不是可以交互的 shell，例如 BusyBox 的 sh（ash），应该会有个控制 tty，如果控制 tty 不存在，Busybox 的 sh 会报错。BusyBox 将会完全忽略 runlevel 字段，所以空着它就行了，你也许会问既然没用保留着它干吗，我想大概是为了和传统的 Sytem V init 保持一致的格式吧。process 字段用来指定所执行程式的路径，包括命令行选项。action 字段用来指定下面表中 8 个可应用到 process 的动作之一。

> **sysinit**   为 init 提供初始化命令行的路径
>
> **respawn**   每当相应的进程终止执行便会重新启动
>
> **askfirst**     类似 respawn，不过它的主要用途是减少系统上执行的终端应用程序的数量。它将会促使 init 在控制台上显示“Please press Enter to active this console ”的信息，并在重新启动之前等待用户按下 enter 键
>
> **wait** 告诉 init 必须等到相应的进程完成之后才能继续执行
>
> **once** 仅执行相应的进程一次，而且不会等待它完成
>
> **ctraldel** 当按下 Ctrl+Alt+Delete 组合键时，执行相应的进程
>
> **shutdown** 当系统关机时，执行相应的进程
>
> **restart** 当 init 重新启动时，执行相应的进程，通常此处所执行的进程就是 init 本身

文件根据此配置文件来执行后续的步骤。我们在/etc 目录下使用命令“vim etc/inittab”命令，创建 inittab 文件，在该文件中我们输入以下内容：

```shell
::sysinit:/etc/init.d/rcS
console::askfirst:-/bin/sh
::restart:/sbin/init
::shutdown:/bin/umount -a -r
::shutdown:/sbin/swapoff -a
```

第 1 行，系统启动以后运行/etc/init.d/rcS 这个脚本文件。

第 2 行，将 console 作为控制台终端，也就是 ttySTM0。

第 3 行，重启的话运行/sbin/init。

第 4 行，关机的时候执行/bin/umount，也就是卸载各个文件系统。

第 5 行，关机的时候执行/sbin/swapoff，也就是关闭交换分区。

保存退出之后，使用命令“chmod 777 inittab”，修改该文件的权限

#### 26.3.5.6 创建 passwd 文件

然后使用“ vim etc/passwd”命令在“etc”目录建立“passwd”文件，passwd 用来是用来保存用户的信息的，在“passwd”文件中输入下面的内容。

```shell
root:x:0:0:root:/:/bin/sh
bin:*:1:1:bin:/bin:
daemon:*:2:2:daemon:/sbin:
nobody:*:99:99:Nobody:/:
```

passwd 文件是用来保存用户的信息的，是一个纯文本文件。

> name：用户名。
>
> password：密码（已经加密）
>
> uid：UID（用户标识）,操作系统自己用的
>
> gid：GID 组标识。
>
> comment：用户全名或本地帐号
>
> home：用户的主目录的绝对路径
>
> shell：登录使用的 Shell，就是对登录命令进行解析的工具

保存退出之后，使用命令“chmod 777 passwd”，修改该文件的权限

#### 26.3.5.7 创建 profile 文件

然后使用“ vim etc/profile”命令在“etc”目录建立“profile”文件，profile 用来设置我们的环境变量，在“profile”文件中输入下面的内容。

```
USER="`id -un`" LOGNAME=$USER
PS1='[$USER@$HOSTNAME]:$PWD# '
PATH=$PATH
HOSTNAME=`/bin/hostname` 
export USER LOGNAME PS1 PATH
```

保存并退出“profile”文件，使用“chmod 777 profile”命令修改“profile”文件的权限

#### 26.3.5.8 创建 eth0-setting 和 eth1-setting 文件

在 etc 目录下，使用命令“vim eth0-setting”，创建 eth0-setting 文件，并输入以下内容：

```
IP=192.168.1.230
Mask=255.255.255.0
Gateway=192.168.1.1
DNS=192.168.1.1
MAC=08:90:90:90:90:90
```

然后在 etc 目录下，使用命令“vim eth1-setting”，创建 eth1-setting 文件，并输入以下内容：

```
IP=192.168.1.231
Mask=255.255.255.0
Gateway=192.168.1.1
DNS=192.168.1.1
MAC=BE:C8:1D:14:82:1D
```

> IP：开发板启动后默认设置的 IP 地址，IP 地址为 192.168.1.230 和 192.168.1.231
>
> Mask：开发板启动后默认设置的掩码，掩码为 255.255.255.0
>
> Gateway：开发板启动后默认配置的网关，网关为 192.168.1.1
>
> DNS：开发板启动后默认设置的 DNS，DNS 为 192.168.1.1
>
> MAC：开发板启动后默认设置的 MAC 地址，MAC 地址为 08:90:90:90:90:90
>
> MAC 地址和作者保持一致即可，其余网络信息大家依据自己的网络情况设置即可，

保存并退出“eth0-setting”文件，使用“chmod 777 eth0-setting”命令修改“profile”文件的权限

#### 26.3.5.9 创建 ifconfig-eth0 和 ifconfig-eth1 文件

在/etc 目录下使用“cd init.d”命令进入 init.d 文件夹

然后使用命令“vim ifconfig-eth0”创建 ifconfig-eth0 文件，并写入以下内容

```shell
#!/bin/sh
echo -n Try to bring eth0 interface up......>/dev/ttyFIQ0
if [ -f /etc/eth0-setting ] ; then
  source /etc/eth0-setting
  if grep -q "^/dev/root / nfs " /etc/mtab ; then
    echo -n NFS root ... > /dev/ttyFIQ0
  else
      ifconfig eth0 down
      ifconfig eth0 hw ether $MAC
      ifconfig eth0 $IP netmask $Mask up
      route add default gw $Gateway
	fi
	echo nameserver $DNS > /etc/resolv.conf
else
  if grep -q "^/dev/root / nfs " /etc/mtab ; then
  	echo -n NFS root ... > /dev/ttyFIQ0
  else
  	/sbin/ifconfig eth0 192.168.253.12 netmask 255.255.255.0 up
  fi
fi
echo Done >/dev/ttyFIQ0
```

然后使用命令“vim ifconfig-eth1”创建 ifconfig-eth1 文件，并写入以下内容：

```shell
#!/bin/sh
echo -n Try to bring eth0 interface up......>/dev/ttyFIQ0
if [ -f /etc/eth1-setting ] ; then
  source /etc/eth1-setting
  if grep -q "^/dev/root / nfs " /etc/mtab ; then
    echo -n NFS root ... > /dev/ttyFIQ0
  else
    ifconfig eth1 down
    ifconfig eth1 hw ether $MAC
    ifconfig eth1 $IP netmask $Mask up
    route add default gw $Gateway
  fi
  echo nameserver $DNS > /etc/resolv.conf
else
  if grep -q "^/dev/root / nfs " /etc/mtab ; then
    echo -n NFS root ... > /dev/ttyFIQ0
  else
    /sbin/ifconfig eth0 192.168.253.12 netmask 255.255.255.0 up
  fi
fi
echo Done >/dev/ttyFIQ0
```

ifconfig-eth0 和 ifconfig-eth1 是网络配置文件，工作流程就是读取我们创建的 eth0-setting和 eth1-setting 网络信息文件来设置网络，如果 eth0-setting 或者 eth1-setting 配置文件不存在，就使用默认配置。

保存退出之后，使用命令“chmod 777 ifconfig-eth0 ifconfig-eth1“，修改文件的权限

#### 26.3.5.10 创建 mdev.conf 文件

在 etc 目录下，使用命令“vim mdev.conf”新建 mdev.conf 文件,因为我们在 rcS 文件里面配置了热拔插功能，但是还需要 mdev.conf 配合，mdev.conf 文件是 U 盘 sd 卡的热拔插文件，我们在 mdev.conf 输入以下内容：

```
sd[a-z][0-9] 0:0 666 @ /etc/hotplug/udisk_inserting

sd[a-z] 0:0 666 $ /etc/hotplug/udisk_removing
```

接着使用命令“mkdir hotplug”在 etc 目录下创建 hotplug 文件夹.

然后使用命令“cd hotplug”进入 hotplug 文件夹，然后在 hotplug 文件夹下使用命令“vim udisk_inserting”建立 udisk_inserting 文件夹并在里面输入以下内容：

```shell
#!/bin/sh
echo "usbdisk insert!" > /dev/console
if [ -e "/dev/$MDEV" ] ; then
  mkdir -p /mnt/usbdisk/$MDEV
  mount /dev/$MDEV /mnt/usbdisk/$MDEV
  echo "/dev/$MDEV mounted in /mnt/usbdisk/$MDEV">/dev/console
fi
```

保存退出后，在 hotplug 文件夹下使用命令“vim udisk_removing”建立 udisk_removing 文件夹并在里面输入以下内容：

```shell
#!/bin/sh
echo "usbdisk remove!" > /dev/console
umount -l /mnt/usbdisk/sd*
rm -rf /mnt/usbdisk/sd*
```

保存退出后，在 hotplug 目录下使用命令“chmod 777 *”修改文件权限。

#### 26.3.5.11 创建 mtab 文件

返回 etc 目录下，我们需要在 etc 目录下创建 mtab 文件，/etc/mtab 是当前的分区挂载情况，记录的是当前系统已挂载的分区。每次挂载/卸载分区时会更新/etc/mtab 文件中的信息。所以在 ifconfig-eth0 文件里面我们就是通过这个/etc/mtab 来判断当前的文件系统是不是 nfs 网络文件系统。

mtab 文件是个链接文件，我们在 etc 目录下输入命令“ln -s /proc/mounts mtab”把他链接到/proc/mounts

#### 26.3.5.12 创建 netd 文件

netd 文件是用用来配合 profile 文件里面的/etc/rc.d/init.d/netd start 的这行代码来启动 netd服务的。这里我们就来一起创建这个文件。

（1）在 etc 目录使用命令“mkdir rc.d”建立文件夹“rc.d”然后使用“cd rc.d” 命令进入到刚才建立的“rc.d” 文件夹 ，接下来在“rc.d” 目录下使用“mkdir init.d” 命令建立“init.d” 文件夹， 使用“cd init.d” 命令进入到刚才建立的“init.d” 文件夹。

（2）在“ init.d”目录下， 使用“vi netd” 命令建立“ netd” 文件，然后使用“chmod 777 netd” 命令修改“ netd” 文件的权限为 777。

vim etc/init.d/netd

```shell
#!/bin/sh
base=inetd
# See how we were called.
case "$1" in
  start)
  	/usr/sbin/$base
  ;;
  stop)
    pid=`/bin/pidof $base`
    if [ -n "$pid" ]; then
    	kill -9 $pid
    fi
  ;;
esac
exit 0
```

### 26.3.6 构建文件系统镜像

返回上一目录，使用命令“mkdir rootfs”,rootfs 用来挂载之后制作制作出来的 rootfs.ext4，

然后使用命令“du system”命令来查看 system 文件大小，可以看到该文件系统的大小为18M，如下图所示：

![image-20240713160257295](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713160257295.png)

所以我们镜像大小在这里设置为 30M，使用命令如下

> dd if=/dev/zero of=rootfs.img bs=1M count=250
>
> mkfs.ext4 -L rootfs rootfs.img

建立一个大小为 30M 的 ext4 磁盘

接下来使用 mount 命令将 rootfs.ext4 挂载到 rootfs 目录下

> sudo mount ./rootfs.img rootfs

然后拷贝我们制作的文件系统到 rootfs 目录下

> sudo cp -r ./system/* ./rootfs

拷贝完成后，使用命令“umount rootfs”，进行解除挂载

> sudo umount rootfs

![image-20240713160421343](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240713160421343.png)

接一来烧录运行测试。

---

[总目录](总目录.md) · [上一篇：U-Boot基础与源码启动流程](25-U-Boot%E5%9F%BA%E7%A1%80%E4%B8%8E%E6%BA%90%E7%A0%81%E5%90%AF%E5%8A%A8%E6%B5%81%E7%A8%8B.md) · [下一篇：Qt交叉编译与部署](27-Qt%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E4%B8%8E%E9%83%A8%E7%BD%B2.md)
