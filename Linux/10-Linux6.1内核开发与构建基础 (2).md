# 10-Linux6.1内核开发与构建基础

[总目录](总目录.md) · [上一篇：RKNN模型转换与板端部署](9-RKNN%E6%A8%A1%E5%9E%8B%E8%BD%AC%E6%8D%A2%E4%B8%8E%E6%9D%BF%E7%AB%AF%E9%83%A8%E7%BD%B2.md) · [下一篇：字符设备驱动与文件操作](11-%E5%AD%97%E7%AC%A6%E8%AE%BE%E5%A4%87%E9%A9%B1%E5%8A%A8%E4%B8%8E%E6%96%87%E4%BB%B6%E6%93%8D%E4%BD%9C.md)

> 版本基线：Linux 6.1，面向 RK SDK。保留已完成的接口勘误；源码摘录与板级资源仍需对照实际 SDK。构建和适配说明见 [Linux 6.1 适配说明](整理记录/Linux6.1适配说明.md)。

[TOC]

<a id="part-19"></a>

Linux移植步骤
1. 下载Linux源码
2. 修改配置去适配自己的硬件
2. 裁剪-增加或删除功能
3. 编译-得到操作系统的镜像
4. 烧录

## 10.1 Linux操作系统介绍

Linux 是一种开源且免费的操作系统内核，是由芬兰计算机科学家 Linus Torvalds 于 1991  年开始编写，并在其后的几年中不断完善和发展而来。Linux  最初是作为个人电脑使用的，但现在已经成为了许多服务器、移动设备、超级计算机等各种类型的硬件设备上的主要操作系统。

嵌入式Linux的应用领域非常广泛，主要的应用领域有信息家电、PDA 、机顶盒、Digital Telephone、Answering Machine、Screen Phone 、数据网络、Ethernet Switches、Router、Bridge、Hub、Remote access servers、ATM、Frame relay 、远程通信、医疗电子、交通运输计算机外设、工业控制、航空航天领域等。

* Linux的组成：uboot，kernel内核， rootfs（root file system根文件系统）

  ![iShot2024-07-02 00.49.44](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/iShot2024-07-02%2000.49.44.png)

## 10.2 开发环境搭建

理解开发中的几个角色：

windows：写代码，烧录

ubuntu：编译，配置

开发板：运行自己的Linux系统

理解代码的来源：

1. Linux源
2. RK源
3. 迅为源
4. 自己的代码

### 10.2.1 安装ubuntu虚拟机

### 10.2.2 ubuntu设置

1. 启用root

   接下来需要设置root用户，在一些情况下，需要用到root权限，打开ubuntu的终端输入

   > sudo passwd

   然后输入ubuntu的密码，接着输入两次unix密码

   Unix密码就是root用户的登录密码，输入以下命令来检查有没有启用root用户

   > su root

   然后输入刚刚设置的Unix密码，可以看到用户名变成root，如下图所示，说明已经启用root成功了。

2. 设置下载源

   ![image-20240630181025625](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630181025625.png)

   ![image-20240630181050576](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630181050576.png)

   > apt-get upgrade：更新已安装的所有的软件
   >
   > **apt-get update：更新软件源列表（执行这个）**

3. 安装VMware Tools

4. 安装vim

   > apt-get install vim

5. 安装net-tools

   > apt install net-tools

5. 安装Samba

   Samba最大的功能就是可以用于Linux与windows系统共享文件夹，搭建SMB服务首先要保证windows和ubuntu网络互通，然后在ubuntu下载安装：

   > sudo apt-get install samba

   给需要共享的文件夹设置权限为777

   修改配置：

   > sudo vim /etc/samba/smb.conf

   添加内容如下:

   ```
   [samba]
   comment = smbshare home directory
   path = /home/richard/
   public = yes
   writeable = yes
   valid users = richard
   create mask = 0664
   directory mask = 0777
   force user = richard
   force group = richard
   available = yes
   unix charset = UTF-8
   dos charset = cp936
   ```
   
   改完配置文件后保存，然后使用命令设置用户密码
   
   > smbpasswd -a 用户名
   >
   > sudo smbpasswd -a richard
   
   命令重启 samba 服务:
   
   > sudo service smbd restart
   
   在 windows 上输入“win+r”弹出运行窗口，然后输入 ubuntu 的 IP访问:\\\\ip
   
7. 安装依赖

   ```shell
   sudo apt-get install uuid uuid-dev zlib1g-dev liblz-dev liblzo2-2 liblzo2-dev lzop \
   git-core curl u-boot-tools mtd-utils openjdk-8-jdk device-tree-compiler \
   gdisk m4 libz-dev git gnupg flex bison gperf libsdl1.2-dev libesd-java \
   squashfs-tools build-essential zip curl libncurses5-dev zlib1g-dev pngcrush schedtool \
   libxml2 libxml2-utils xsltproc lzop libc6-dev schedtool g++-multilib lib32z1-dev \
   lib32ncurses5-dev lib32readline-dev gcc-multilib libswitch-perl libssl-dev unzip \
   zip liblz4-tool git ssh make gcc libssl-dev liblz4-tool vim expect \
   g++ patchelf chrpath gawk texinfo chrpath diffstat binfmt-support \
   qemu-user-static live-build bison flex fakeroot cmake gcc-multilib g++-multilib \
   unzip device-tree-compiler python3-pip libncurses5-dev rsync subversion \
   sed make binutils  build-essential  gcc  g++  wget python libncurses5 bzr cvs git mercurial \
   patch gzip bzip2 perl tar cpio unzip rsync file bc wget qemu-user-static live-build -y
   ```

5. 安装ssh

   > #安装ssh
   >
   > apt-get install openssh-server
   >
   > /etc/init.d/ssh start
   >
   > #打开配置文件
   >
   > vi /etc/ssh/sshd_config
   >
   > 找到“PermitRootLogin prohibit-password”修改成“PermitRootLogin yes”
   >
   > /etc/init.d/ssh restart

## 10.3 交叉编译

复制源码到ubuntu中，使用命令解压：

> tar -xvf rk356x_linux_20240430.tar.xz

![image-20240703094529146](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703094529146.png)

运行build.sh

图形界面编译

![image-20240630214939363](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630214939363.png)

![image-20240630215105682](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630215105682.png)

编译完成后会将生成的update.img文件存在rockdev中。

命令编译

> ./build.sh buildroot_update



> 有的厂商提供的Linux源码可能会把uboot, Kernel,rootfs 分开打包
>
> uboot：是Linux的引导程序，主要作用就是引导内核启动
>
> kernel：操作系统的内核，驱动主要就是在内核中运行，这也就是驱动开发工程师接触最多的
>
> 文件系统：系统开发工程师接触最多。

<a id="part-20"></a>

## 10.4 Linux源码介绍

![image-20240702202222258](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202222258.png)

> app : 存放上层应用程序的目录，主要是 qcamera/qfm/qplayer/settings 等一些应用程序。
>
> *buildroot ：基于 buildroot (2018.02-rc3) 开发的根文件系统。这是一个用来制作根文件系统的工具
>
> *build.sh ：编译用的脚本，使用方法后面会教。
>
> debian ：基于 debian 10 开发的根文件系统。
>
> device/rockchip ：存放每个平台的一些编译和打包固件的脚本和预备文件。
>
> docs ：存放 RK 开发指导文件、平台支持列表、工具使用文档、Linux 开发指南等。
>
> *envsetup.sh ：要修改文件系统时候要设置的环境脚本。
>
> external : 存放相关的库，包括音频，视频等。
>
> **kernel ：kernel 源码。
>
> *Makefile ：整个 SDK 包编译的 Makefile。
>
> mkfirmware.sh ：固件打包使用的脚本，默认在当前路径下的 rockdev 目录。
>
> *prebuilts : 存放交叉编译工具链。
>
> rkbin: 存放固件和工具。
>
> rkflash.sh : linux 下的系统烧录脚本。
>
> *rockdev：存放编译输出固件的目录(整个 SDK 包编译完成后就会创建)。
>
> tools ：存放固件和工具的目录。
>
> *u-boot ：U-boot 源码目录。
>
> yocto：基于 yocto gatesgarth 3.2 开发的根文件系统。

## 10.5 系统编译

### 10.5.1 整体编译

1. 图形化界面编译

   首先在 linux 源码目录下输入以下命令进入编译的 UI 界面

   > ./build.sh

   ![image-20240702202415840](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202415840.png)

   然后选择第五个 all，就会进入到文件系统类型选择页面，如下所示

   ![image-20240702202437638](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202437638.png)

   ![image-20240702202454176](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202454176.png)

   ![image-20240702202516076](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202516076.png)

   在 rockdev 目录下就生成了打包完成的 update.img 镜像如下图所示：

   ![image-20240702202553597](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202553597.png)

2. 命令编译

   进入源码根目录执行以下命令自动完成所有的编译。如果想自动全编译 ubuntu 文件系统，

   输入以下命令：

   > ./build.sh buildroot_update
   >
   > ./build.sh ubuntu20_update
   >
   > ./build.sh ubuntu22_update

### 10.5.2 单独编译

1. 图形化界面

   ![image-20240702202808840](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702202808840.png)

   光标默认就在 uboot，所以直接回车即可开始 uboot 的编译。

   编译完成后生成 uboot.img 到 u-boot 目录。

   **其它的一样操作**

   内核：编译完成后映像文件会打包成 boot.img 放到 kernel目录。

2. 命令行

   在 linux 源码目录下输入以下命令编译 

   > #单独编译uboot
   >
   > ./build.sh uboot
   >
   > #单独编译内核
   >
   > ./build.sh kernel

### 10.5.3 单独烧写

以内核为例：从kernel目录中复制boot.img到烧录工具的image目录中

![image-20240703143330582](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703143330582.png)

<a id="part-21"></a>

## 10.6 内核裁剪

### 10.6.1 内核源码

![image-20240702203250300](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702203250300.png)

> *arch 存放不同平台体系相关代码
> block 存放块设备相关代码
> crypto 存放加密、压缩、CRC 校验等算法相关代码
> Documentation 存放相关说明文档，很多实用文档，包括驱动编写等
> *drivers 存放 Linux 内核设备驱动程序源码。该目录包含众多驱动，目录按照设备类别进行分类，如char、block 、input、i2c、spi、pci、usb 等。
>
> firmware 存放处理器相关的一些特殊固件
> fs 存放虚拟文件系统代码
> *include 存放内核所需、与平台无关的头文件
> init Linux 系统启动初始化相关的代码
> ipc 存放进程间通信代码kernel Linux 内核的核心代码，包含了进程调度子系统，以及和进程调度相关的模块。
> *lib 库文件代码， 实现需要在内核中使用的库函数，例如 CRC、FIFO、list、MD5等。
> mm 实现存放内存管理代码
> net 存放网络相关代码
> samples 存放提供的一些内核编程范例
> scripts 存放一些脚本文件
> security 存放系统安全性相关代码
> sound 存放声音、声卡相关驱动
> tools 一些常用工具，如性能剖析、自测试等
> usr 用于生成 initramfs 的代码。
> virt 提供虚拟机技术（KVM 等）的支持
> *kernel  内核的源码目录

在内核源码目录下输入以下命令，打开图形化配置界面。

> #配置架构，RK3568是arm64架构
>
> export ARCH=arm64
>
> #获取默认配置
>
> make rockchip_linux_defconfig
>
> #打开配置菜单
>
> make menuconfig
>
> #复制.config文件
>
> cp .config arch/arm64/configs/rockchip_linux_defconfig
>
> Device Drivers  --->  LED Support  --->LED Trigger support  ---> 
>
> cd /sys/class/leds/work/
>
> echo hearbeat > trigger
>
> echo none > trigger

打开 menuconfig 图形化配置界面以后，可以使用以下方式进行操作.

![image-20240702210402983](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240702210402983.png)

修改内核日志输出级别：

 Kernel hacking  --->   printk and dmesg options  ---> 

![image-20240703150413832](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703150413832.png)

修改led触发配置

Device Drivers  ---> [\*] LED Support  ---> -*-   LED Trigger support  ---> 

![image-20240703150707462](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703150707462.png)

<a id="part-22"></a>

## 10.8 驱动开发HelloWorld

### 10.8.1 搭建开发环境

vscode设置

```text
{
    "configurations": [
        {
            "name": "Win32",
            "includePath": [
                "W:\\home\\rk3568\\linuxsrc\\rk356x_linux\\kernel\\include",
                "W:\\home\\rk3568\\linuxsrc\\rk356x_linux\\kernel\\arch\\arm64\\include", 
                "W:\\home\\rk3568\\linuxsrc\\rk356x_linux\\kernel\\arch\\arm64\\include\\generated\\",
                "${workspaceFolder}/**"
            ],
            "defines": [
                "_DEBUG",
                "UNICODE",
                "_UNICODE"
            ],
            "compilerPath": "C:\\mingw64\\bin\\gcc.exe",
            "cStandard": "c17",
            "cppStandard": "gnu++17",
            "intelliSenseMode": "windows-gcc-x64"
        }
    ],
    "version": 4
}
```

### 10.8.2 编写代码

```c
#include <linux/module.h>

static int __init helloworld_init(void) //驱动入口函数
{
	printk(KERN_EMERG "helloworld_init\r\n");//注意：内核打印用 printk 而不是 printf
	return 0;
}
static void __exit helloworld_exit(void) //驱动出口函数
{
	printk(KERN_EMERG "helloworld_exit\r\n");
}
module_init(helloworld_init); //注册入口函数
module_exit(helloworld_exit); //注册出口函数
MODULE_LICENSE("GPL v2"); //同意 GPL 开源协议
MODULE_AUTHOR("lzy"); //作者信息
```

> 在同级目录中的Makefile中添加obj-y        += hello_woniu.o    
>
> * hello_woniu是自己的驱动文件名

### 10.8.3 将驱动编译为模块

1. 准备交叉编译器

   > gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu

2. 设置交叉编译器的环境变量，可以实现在任意地方都可以直接使用交叉编译器

   > 1. 打开/etc/profile： vim /etc/profile
   >
   > 2. 在最后添加： 
   >
   >    export PATH=$PATH:/home/driver/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/
   >
   > 3. source profile  让它生效

3. 编写Makefile

   ```makefile
   ccflags-y := -Wall -Wno-error=unused-result -Wno-error=unused-function -Wno-error=missing-braces
   export ARCH=arm64
   export CROSS_COMPILE=aarch64-none-linux-gnu-
   obj-m+=hello_ko.o 
   KDIR:=/home/richard/rk3568-linux-6.1-stan-rkr6/kernel
   PWD?=$(shell pwd)
   all:
   	make -C $(KDIR) M=$(PWD) modules
   clean:
   	make -C $(KDIR) M=$(PWD) clean
   ```
   
   > 第 1 行设置 ARCH 变量为 arm64
   >
   > 第 2 行设置交叉编译器前缀为 aarch64-linux-gnu- 
   >
   > 第 3 行 obj-m += <文件>：将指定的文件（需要是以.o 结尾）设为编译时以模块形式编译
   >
   > 第 4 行是设备树内核的源码路径，请大家根据实际内核路径进行修改。
   >
   > 第 5 行是获取当前目录的变量
   >
   > 第 7 行是编译 make 操作，会进入内核源码的路径，然后把当前路径下的代码编译成模块。
   >
   > 第 9 行是清除编译文件
   
4. 编译驱动模块

   有了 Makefile 以后，输入“make”命令就可以编译 helloworld 驱动模块.编译完生成 helloworld.ko 目标文件就是我们需要的内核模块。内核模块是以 ko 为后缀名.

   ![image-20240703170106231](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703170106231.png)

5. 将驱动模块加载进内核

   将内核文件发送到开发板,在 Linux 系统启动以后使用“insmod”命令加载驱动模块。在加载驱动模块的时候会执行驱动入口的函数，也就是helloworld 程 序 中 的 helloworld_init 函 数 ， 所 以 可 以 看 到 打 印 出 来 的 字 符 串 信 息“helloworld_init”。

   > insmod helloworld.ko

   ![image-20240703173938534](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703173938534.png)

6. 卸载驱动

   如果要卸载 helloworld 内核模块，可以通过“rmmod helloworld”命令来卸载驱动模块，同理在卸载驱动模块的时候会执行驱动出口的函数，所以可以看到驱动出口函数打印出来的字符串信息“helloworld_exit”

   > rmmod helloworld

   ![image-20240703173913047](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703173913047.png)

7. 列出所有驱动

   lsmod 命令可以列出已经载入 Linux 内核模块，在 helloworld 驱动加载之后，查看内核中加载的模块。

   > lsmod 

   ![image-20240703170649913](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703170649913.png)

## 10.9 在 Linux 6.1 开发板上安装并使用 modprobe

模块必须用与板端运行内核匹配的 SDK 配置、生成头文件和 Module.symvers 构建；同为 6.1 并不代表模块 ABI 自动兼容。先把编译出的 woniu.ko 传到板端 /tmp，再在板端执行：

```shell
uname -r
modinfo /tmp/woniu.ko
KREL=$(uname -r)
sudo install -D -m 0644 /tmp/woniu.ko "/lib/modules/$KREL/extra/woniu.ko"
sudo depmod -a "$KREL"
sudo modprobe woniu
dmesg | tail -n 30
```

> -D：自动创建目标路径中缺失的目录。
> 例如目标 /lib/modules/$KREL/extra/woniu.ko，如果 extra/ 目录不存在，-D 会先把 /lib/modules/$KREL/extra/ 建出来，再复制文件。没有 -D 的话，目录不存在就会报错。
>
> -m 0644：设置目标文件的权限模式（mode）。
> 0644 = rw-r--r--，即属主可读写，组和其他人只读。对内核模块 .ko 来说这是标准权限。
>
> -a：处理所有模块（all），而不只是新加的。它会扫描 /lib/modules/$KREL/ 下的模块，分析符号依赖，重新生成 modules.dep、modules.alias、modules.symbols 等文件。

目录使用真实的 uname -r（含厂商后缀），不要写死 6.1.118。depmod 参数是内核版本，不是“版本/模块目录”。modules.builtin 等来自同一内核构建/安装过程，不应通过 touch 空文件伪造；SDK 镜像若缺少模块元数据，应补齐匹配构建的输出。

| 特性              | insmod                                                       | modprobe                                                     |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **依赖关系**      | **不处理**依赖关系。你必须手动按顺序加载依赖的模块。         | **自动处理**依赖关系。它会查找并先加载目标模块所依赖的所有其他模块。 |
| **模块路径**      | 需要提供**完整的模块路径和文件名**（如 `.ko` 文件）。        | 只需要提供**模块名**（如 `nvidia`），它会到标准路径（如 `/lib/modules/$(uname -r)/`）中查找。 |
| **配置文件**      | **不读取**任何配置文件。                                     | **读取**配置文件（如 `/etc/modprobe.d/` 下的文件、`/etc/modprobe.conf`），可以处理别名、黑名单和模块参数。 |
| **智能卸载**      | 对应的卸载命令是 `rmmod`，它同样不处理依赖关系。             | 对应的卸载命令是 `modprobe -r`，在卸载模块时会尝试同时卸载其不再被使用的依赖模块。 |
| **使用场景**      | 低级操作、调试、当 `modprobe` 不工作时、需要加载非标准路径模块时。 | **日常管理和标准操作**的首选工具。                           |
| **安全性/便利性** | 低。容易因遗漏依赖而导致加载失败或系统不稳定。               | 高。更安全、更便捷，减少了管理员的负担。                     |

## 10.12 Kconfig

图形化配置界面中的每一个界面都会对应一个 Kconfig 文件。所以图形化配置界面的每一级菜单是由 Kconfig 文件来决定的。

图形化配置界面有很多菜单。所以就会有很多 Kconfig 文件，这也就是为什么我们会在内核源码的每个子目录下，都会看到 Kconfig 文件的原因。

1. mainmenu

   mainmenu 顾名思义就是主菜单，也就是我们输入完“make menuconfig”以后默认打开的

   界面，mainmenu 用来设置主菜单的标题。

   > mainmenu "Linux/$(ARCH) $(KERNELVERSION) Kernel Configuration"

   ![image-20240703223420516](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703223420516.png)

2. source

   source 用于读取另一个 Kconfig 文件，比如“source "init/Kconfig"”就是读取 init 目录下的Kconfig 文件。

3. menu/endmenu

   menu/endmenu 条目用于生成菜单，如下所示，生成了 Watchdog Timer Support的菜单。

   ```shell
   menu "Watchdog Timer Support" 
   config HW_WATCHDOG
   bool
   config WDT
   bool "Enable driver model for watchdog timer drivers" depends on DM
   help
   Enable driver model for watchdog timer. At the moment the API.
   ...... 
   endmenu
   ```

   menu 之后的字符串是菜单名，“menu”是菜单开始的标志，“endmenu”是菜单结束的标志，这俩个是成对出现的。“menu”和“endmenu”之间有很多 config 条目。在 kernel 目录下输入 make menuconfig，如下图（图 7-6）所示，可以看到上述代码描述的"Watchdog TimerSupport"菜单。

   进入“ Watchdog Timer Support ---> ”可以看到很多 config 定义的条目

4. if/endif 

   语句是一个条件判断，定义了一个 if 结构。

   当没有选中 "Enable CAN" 选项时，下面通过 if 判断的 Enable CAN1 选项并不会显示出来。当上一级菜单选中 "Enable CAN" 时，Enable CAN1 选项才会显示。

   ```shell
   menu "Hardware Drivers Config" 
   	menuconfig BSP_USING_CAN
   	bool "Enable CAN" 
   	default n
   	select RT_USING_CAN
   	if BSP_USING_CAN
   		config BSP_USING_CAN1
   			bool "Enable CAN1" default n
   	endif
   endmenu
   ```

5. choice/endchooice

   choice 条目将多个类似的配置选项组合到一起，供用户选择，用户选择是从“choice”开始，从“endchoice”结束，“choice”和“endchoice”之间有很多的 config 条目，这些 config 条目是提供用户选择的。

   ```shell
   choice
     bool "Parade TrueTouch Gen5 MultiTouch Protocol" 
     depends on TOUCHSCREEN_CYPRESS_CYTTSP5
     default TOUCHSCREEN_CYPRESS_CYTTSP5_MT_B
     help
     	This option controls which MultiTouch protocol will be used to
     	report the touch events. 
   config TOUCHSCREEN_CYPRESS_CYTTSP5_MT_A
     bool "Protocol A" 
     help
     	Select to enable MultiTouch touch reporting using protocol A
     	on Parade TrueTouch(tm) Standard Product Generation4 touchscreen
     	controller. 
    config TOUCHSCREEN_CYPRESS_CYTTSP5_MT_B
     bool "Protocol B" 
     help
     	Select to enable MultiTouch touch reporting using protocol B
     	on Parade TrueTouch(tm) Standard Product Generation4 touchscreen
     	controller. 
   endchoice
   ```

   我们在内核目录下输入 make menuconfig 可以看到，如下（图 7-10）所示，“Parade TrueTouchGen5 MultiTouch Protocol”是 choice 选项名称，“Protocol B”是 Kconfig 里面默认选择的。“-->”代表此菜单能进入，需要键盘操作进入。

   ![image-20240703224459969](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703224459969.png)

   进入“Parade TrueTouch Gen5 MultiTouch Protocol”后，可以看到多选项提供给用户进行选择.

   ![image-20240703224508322](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703224508322.png)

6. comment

   comment 语句出现在界面的第一行，用于定义一些提示信息。

   > comment "Compiler: $(CC_VERSION_TEXT)" 

​	![image-20240703224555215](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703224555215.png)

7. config

   使用关键字 config 来定义一个新的选项

   ```shell
   config HELLOWORLD
   	bool “hello world support” 
   	default y
   	help
   		hello world
   ```

   如上所示，使用 config 关键字定义了一个“helloworld”选项，每个选项都必须指定类型，类型包括 bool，tristate,string,hex,int。最常见的是 bool,tristate,string 这三个。

   > bool 类型取值只有“y”和“n”
   >
   > tristate 类型的变量取值有 3 种：“y”,“n”,“m”
   >
   > string 类型取值为字符串
   >
   > hex 类型取值为十六进制的数据
   >
   > int 类型取值为十进制的数据

   help 表示帮助信息，当我们在图形化界面按下 h 按键，弹出来的就是 help 的内容。

8. depends on

   Kconfig 中 depends on 关键字用来指定依赖关系，当依赖的选项被选中时，当前的配置选项的信息才会在菜单中显示出来，才能操作该选项的内容。举例来说，如下所示，选项 A 依赖选项 B，只有当选项 B 被选中时，选项 A 才可以被选中。

   ```shell
   config A
   depends on B
   ```

9. select

   Kconfig 中 select 关键字用来表示反向依赖关系，当指定当前选项被选中时，此时 select 后面的选项也会被自动选中。举个例子来说，如下所示，在选项 A 被选中的情况下，选项 B 自动被选中。

   ```shell
   config A
   select on B
   ```

10. menuconfig

    menuconfig 可以认为是 config 中的升级版。menuconfig 也是一个正常的配置项，通过自己的配置值来决定另外一组配置项是否作为子菜单的形式显示出来并供用户配置。

    ```shell
    menuconfig NETDEVICES
    default y if UML
    depends on NET
    bool "Network device support"
    ---help---
    if NETDEVICES
    config MII
    tristate
    config NET_CORE
    default y
    bool "Network core driver support"
    ---help--- 
    You can say N here if you do not intend to use any of the
    networking core drivers (i.e. VLAN, bridging, bonding, etc.)
    ```

    以上代码中通过 menuconfig 配置了一个 bool 类型的配置项，在图形化配置界面中显示.

    ![image-20240703224954308](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703224954308.png)

    当我们选中"Network device support"配置项时，其子菜单被显示出来.

    ![image-20240703225012206](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240703225012206.png)

## 10.13 .config

我们在图形化配置界面配置好了以后，会得到一个.config 配置文件。在编译内核的时候会根据这个.config 文件来编译内核。这样是不是就实现了通过图像化界面的配置来配置内核呀。用通俗的话来说，Kconfig 就是饭店的菜单，.config 就是客人点完的菜。然后厨师会根据客人点的菜，也就是.config 来做菜，对应的操作就是编译内核。

那.config 是如何产生的呢？对应上面的例子就是要有服务员给我们点菜呀。

当我们使用 make menuconfig 的时候，会通过 mconf 程序去解析 Kconfig 文件，然后生成对应的配置文件.config。所以这个 mconf 就是服务员。

mconf 程序源码在内核源码 scripts/kconfig 目录下，如下图所示，这里不对 Kconfig 文件的解析流程进行分析，感兴趣的同学可以自行分析下 mconf 的源码。

有了.config 配置文件以后，内核就可以根据这个配置文件来编译内核，比如控制某些驱动编译进内核，或者控制某些驱动不编译内核。

## 10.14 defconfig

defconfig 文件和.config 文件都是 linux 内核的配置文件，defconfig 文件在内核源码的arch/$(ARCH)/configs 目录下，是 Linux 系统默认的配置文件。

比如说瑞芯微平台 Linux 源码默认的配置文件为：kernel/arch/arm64/configs/rockchip_linux_defconfig。

如果.config 文件存在，make menuconfig 界面的默认配置也就是当前.config 文件的配置，

如果修改了图形化配置界面的设置并保存，那么.config 文件会被更新。

如果.config 文件不存在，使用命令“make XXX_defconfig”命令会根据 arch/$(ARCH)/configs目录下的 XXX_defconfig 自动生成.config。make menuconfig 界面的默认配置则为 defconfig 文件中的默认配置，比如说瑞芯微平台 Linux 内核源码目录下输入“make rockchip_linux_defconfig” 会自动生成.config 文件。那么此时 rockchip_linux_defconfig 的配置项和.config 的配置项是相同的。

## 10.15 自定义菜单实验

### 10.15.1 添加菜单

1. 在kernel/drivers/下创建一个woniu目录

2. 在kernel/drivers/char/Kconfig文件中添加

   > source "drivers/woniu/Kconfig"

3. 在kernel/drivers/woniu目录中添加Kconfig文件

   > touch Kconfig

4. 在新建的Kconfig文件中添加以下内容：

   ```shell
   menu "config kunkun"
   config LOOK
   bool "shuai bu shuai"
   default y
   help
           shuai
   
   config HOBBY
   string "ai hao"
   default ctrl
   help
           kunkun
   
   endmenu
   ```

5. 在内核菜单中make menuconfig就可以看到新的菜单

   >  Device Drivers  ---> Character devices  ---> 

   ![image-20240704155533306](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240704155533306.png)

   ![image-20240704155544064](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240704155544064.png)

### 10.15.2 为菜单关联驱动

> obj-m和obj-y是两个变量，这两个变量中存储了要编译的驱动。
>
> obj-y 里面存储的是要编译进内核的驱动
>
> obj-m 面存储的是要编译成模块的驱动

1. 在kernel/drivers/woniu目录中创建Makefile文件，并添加以下内容

   > obj-$(CONFIG_LOOK) += helloworld.o
   >
   > #$()中的是CONFIG_自己的菜单配置中config后面的值

2. 在上级目录的Makefile文件中添加以下内容

   > obj-y                           += woniu/

3. 进入菜单，配置驱动，复制.config文件覆盖默认配置文件
4. 再一次编译内核，可以看到已经将helloworld.o文件编译出来了

![image-20240704165034196](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240704165034196.png)

5. 烧录镜像，启动开发板，可以看到有输出驱动中的内容。说明驱动已经被编译进了内核

   ![image-20240704165131209](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240704165131209.png)

> 驱动是编译进内核还是编译成模块？
>
> 如果在生产环境，而且希望驱动能自动加载，那就编译进内核。
>
> 在开发阶段，一般都编译成模块。

---

[总目录](总目录.md) · [上一篇：RKNN模型转换与板端部署](9-RKNN%E6%A8%A1%E5%9E%8B%E8%BD%AC%E6%8D%A2%E4%B8%8E%E6%9D%BF%E7%AB%AF%E9%83%A8%E7%BD%B2.md) · [下一篇：字符设备驱动与文件操作](11-%E5%AD%97%E7%AC%A6%E8%AE%BE%E5%A4%87%E9%A9%B1%E5%8A%A8%E4%B8%8E%E6%96%87%E4%BB%B6%E6%93%8D%E4%BD%9C.md)

