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

## 10.7 Makefile

make 工具是编译辅助工具， 用来解决使用命令编译工程非常繁琐的问题。
调用这个命令工具： 我们在 windows 上编程使用 ide ， 我们有图形界面， 有相应的按钮，比如说 build或者 run 来编译。 其实 make 这个编译辅助工具使用也是非常简单的， 我们在控制台上直接输入 make 命令，它就会自动调用 make 工具。

Makefile 就是描述了整个工程编译连接等规则的文件。 我们在终端输入完 make 命令之后， 调用 make工具， make 就会在当前目录按照文件名就会找 makefile 文件， Makefile 的命名必须是 makefile 或Makefile ， m 大写小写都是可以的。

![image-20240813143017997](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143017997.png)

### 10.7.1 Makefile语法

Makefile 文件是由一系列的规则组合而成的，格式如下：

> target（目标文件） ...: prerequisites（依赖的文件） ... 
>
> command（命令）
>
> ...
>
> ...

> main.o：main.c
>
> gcc -c main.c

这条规则的 main.o 是目标文件（将要生成的文件），main.c 是依赖的文件（生成 main.o 需要的文件），“gcc -c main.c”是生成 main.o 需要运行的命令。**Makefile 中每行的脚本如果有缩进的情况，必须使用“Tab”键缩进，切记不能使用空格缩进（这是 Makefile 的语法要求），大家一定要切记！**

![image-20240813143341095](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143341095.png)

![image-20240813143352633](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143352633.png)

![image-20240813143410689](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143410689.png)

然后我们输入命令“ make clean ”就可以直接执行 rm -rf *.o hello 命令。

但是，我们在当前目录下不能和 makefile 目标名一样的文件。比如我在当前目录下创建一个名为 clean的文件，然后执行“ make clean ”命令就会报错。

为了解决这个问题，makefile 引入了一个新的概念，叫做伪目标，我们使用伪目标来声明 clean 就可以避免与当前目录下的同名文件发生冲突。

伪目标格式;

.PHONY：目标

所以，我们可以把上面的代码修改成如下图所示：

![image-20240813143541986](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143541986.png)

然后我们在执行 make clean 命令。尽管当前目录下有 clean 同名文件， make clean 命令也可以执行成功。

### 10.7.2 Makefile** **变量和变量赋值

变量可以对许多地方使用，比如目标，依赖。或者命令。

变量的赋值可以使用：“ = ” “ ？= ” “ := ” “ += ”

变量的使用：通过$() 来完成变量的引用。

![image-20240813143625886](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143625886.png)

使用“ ：=” 给变量赋值，是立刻赋值，在执行 var：=aaa 的同时变量值已经被确定了，所以最后打印为 aaabbb，而不是 cccbbb，

![image-20240813143634784](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143634784.png)

使用“=”来赋值，是延迟赋值，使用它来赋值是 makefile 里面最后被指定的值。因为我们最后给变量var1 赋值为 ccc ,所以最后打印为 cccbbb ，而不是 aaabbb 

![image-20240813143727560](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143727560.png)

使用“?=”来赋值，如果 var1 变量前面没有被赋值，那么就给它赋值为 ccc ，如果前面已经赋值了，就适应前面的值，所以，打印为 aaabbb ,而不是 cccbbb

然后我们注释掉第一行代码，makefile 中的注释为 #

![image-20240813143752494](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143752494.png)

![image-20240813143806140](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143806140.png)

使用“+=”赋值是追加赋值，是在我们前面定义的好的字符串里面在添加进去新的字符串，所以运行会打印 aaa bbbccc 。不过中间会有空格.

### 10.7.3 自动化变量

自动化变量就是不用定义且会随着上下程序的不同而发生变化的变量叫做自动化变量。

这里介绍三个最常用的自动化变量：

![image-20240813143920399](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143920399.png)

![image-20240813143954742](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143954742.png)

使用这个 makefile 虽然也可以成功编译，但是，一旦编译的文件多了，如果我们还这样来编写 makefile就会变得非常复杂。所以，自动化变量就派上用场啦。

接下来我们一步一步的来简化这个 makefile 。

简化一：用变量表示依赖文件

![image-20240813143944143](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813143944143.png)

后面如果我们在增加依赖文件的话，我们直接在变量 var 后面增加就可以了。

简化二：

使用通配符 % ，和自动化变量 $< 、$@ 代替依赖和目标，简化完如下图所示：

![image-20240813144032040](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144032040.png)

简化三：

使用自动化变量 “$^”表示所有文件依赖的列表，简化完如下图所示：

![image-20240813144046761](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144046761.png)

### 10.7.4 wildcard** **函数

格式： $ (wildcard PATTEN)

功能： 展开指定的目录

举例：

在 /home/topeet/test 目录有一个“a.c”的 c 文件和一个 test 的文件夹，在/home/topeet/test/test 文件夹下有一个 “b.c”的文件。

我们在当前目录下创建的 makefile 里面写下如下代码，echo 前面加了@ 符号，echo 这个命令就不显示：

![image-20240813144139641](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144139641.png)

![image-20240813144146741](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144146741.png)

### 10.7.5 notdir** **函数

格式： $ (notdir $ (var) )

功能：去掉路径。

举例：

我们在上面的 makefile 中加上以下代码，因为上面的例子我们得到的结果是 ./a.c 和 ./test/b.c 是有路径的，我们可以直接使用这个变量。

![image-20240813144216149](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144216149.png)

![image-20240813144229005](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144229005.png)

因为 notdir 函数可以去掉路径，所以 /a.c 和 ./test/b.c 去掉路径就得到了 a.c 和 b.c

### 10.7.6 dir** **函数

格式： $(dir <names...>)

功能：取出目录，这里的目录指的是最后一个反斜杠/ 之前的部分，如果没有反斜杠/就返回当前。

举例：

我们在上面的例子中加入以下代码，如下图所示：

![image-20240813144306655](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144306655.png)

因为 var2 的值为 ./a.c 和 ./test/b.c ，所以取出目录就是 ./ 和 ./test ，如下图所示：

![image-20240813144318689](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144318689.png)

### 10.7.7 patsubst** **函数

格式： $(patsubst 原文件，目标文件，文件列表）

功能：替换文件后缀

举例

我们在上面的例子中加入以下代码，如下图所示：

![image-20240813144342619](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144342619.png)

这个函数会把 var1 变量的 a.c 和 b.c 的 .c 后缀替换为 .o ，如下图所示：

![image-20240813144357432](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144357432.png)

但是这个替换并不会改变当前目录下的后缀名。这个函数能做什么呢？我们可以用这个函数来替换我们的后缀名，进行其他的操作，这个函数都是会配合其他函数来用的。

替换我们可以使用这个函数，也可以使用 $(var：a=b) 这个格式来替换，var 代表我们要替换的文件的名字，a 是原文件，b 是目标文件。我们来改一下上面的代码，如下图所示：

![image-20240813144413912](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144413912.png)

![image-20240813144420587](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144420587.png)

### 10.7.8 foreach** **函数

格式：$（foreach <var>,<list>,<text>）

功能:把参数<list>中的单词逐一取出放到参数<var>所指定的变量中，然后再执行<text> 所包含的表达式。每一次 <text> 会返回一个字符串

![image-20240813144445351](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144445351.png)

因为 var2 变量的值为 ./ 和 ./test ，所以先把 ./ 取出来放在 n 变量，然后再执行 wildcard 函数取出 ./test 和 ./test 下面的 c 文件的路径。所以执行结果如下图所示：

![image-20240813144501888](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240813144501888.png)

<a id="part-23"></a>

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

目录使用真实的 uname -r（含厂商后缀），不要写死 6.1.118。depmod 参数是内核版本，不是“版本/模块目录”。modules.builtin 等来自同一内核构建/安装过程，不应通过 touch 空文件伪造；SDK 镜像若缺少模块元数据，应补齐匹配构建的输出。























| 特性              | insmod                                                       | modprobe                                                     |
| ----------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| **依赖关系**      | **不处理**依赖关系。你必须手动按顺序加载依赖的模块。         | **自动处理**依赖关系。它会查找并先加载目标模块所依赖的所有其他模块。 |
| **模块路径**      | 需要提供**完整的模块路径和文件名**（如 `.ko` 文件）。        | 只需要提供**模块名**（如 `nvidia`），它会到标准路径（如 `/lib/modules/$(uname -r)/`）中查找。 |
| **配置文件**      | **不读取**任何配置文件。                                     | **读取**配置文件（如 `/etc/modprobe.d/` 下的文件、`/etc/modprobe.conf`），可以处理别名、黑名单和模块参数。 |
| **智能卸载**      | 对应的卸载命令是 `rmmod`，它同样不处理依赖关系。             | 对应的卸载命令是 `modprobe -r`，在卸载模块时会尝试同时卸载其不再被使用的依赖模块。 |
| **使用场景**      | 低级操作、调试、当 `modprobe` 不工作时、需要加载非标准路径模块时。 | **日常管理和标准操作**的首选工具。                           |
| **安全性/便利性** | 低。容易因遗漏依赖而导致加载失败或系统不稳定。               | 高。更安全、更便捷，减少了管理员的负担。                     |

## 10.10 驱动传参

### 10.10.1 驱动模块传参介绍

驱动模块传参是一种可以随时向内核模块传递、修改参数的方法。例如可以传递串口驱动的波特率、数据位数、校验位、停止位等参数，进行功能的设置，以此节省编译模块的时间，大大提高调试速度。

Linux 内核提供了 module_param(name, type, perm)、module_param_array(name, type, nump, perm)宏和 module_param_string(name, string, len, perm)宏，分别进行基本类型、数组和字符串参数的传递。它们定义在 “内核源码/include/linux/moduleparam.h”文件中(在module.h 文件中已经对 export.h 进行引用，所以不需要单独引用 moduleparam.h 文件),

```c
#define module_param(name, type, perm) \
module_param_named(name, name, type, perm)
#define module_param_array(name, type, nump, perm) \
module_param_array_named(name, name, type, nump, perm)
#define module_param_string(name, string, len, perm) \
static const struct kparam_string __param_string_##name \ = { len, string }; \ __module_param_call(MODULE_PARAM_PREFIX, name, \
&param_ops_string, \
.str = &__param_string_##name, perm, -1, 0);\ __MODULE_PARM_TYPE(name, "string")
```

以上宏定义中的 module_param ()函数可以用来进行基本类型参数的传递，传入的三个参数定义如下：

> name：模块参数的名称
>
> type： 模块参数的数据类型
>
> perm： 模块参数的访问权限

参数 type 可以取以下任意一种情况:

> bool **:** 布尔型
>
> inbool **:** 布尔反值
>
> charp**:** 字符指针（相当于 char *,不超过 1024 字节的字符串）
>
> short**:** 短整型
>
> ushort **:** 无符号短整型
>
> int **:** 整型
>
> uint **:** 无符号整型
>
> long **:** 长整型
>
> ulong**:** 无符号长整型。

参数 perm 表示该参数在 sysfs 文件系统中所对应的文件节点的属性，其权限定义在“内核源码/include/linux/stat.h”文件中。可以用宏定义和数字法两种方式来表示。详细宏定义如下所示：

> \#define S_IRUSR 00400 /*文件所有者可读*/
>
> \#define S_IWUSR 00200 /*文件所有者可写*/
>
> \#define S_IXUSR 00100 /*文件所有者可执行*/
>
> \#define S_IRGRP 00040 /*与文件所有者同组的用户可读*/
>
> \#define S_IWGRP 00020 /*与文件所有者同组的用户可写*/
>
> \#define S_IXGRP 00010 /*与文件所有者同组的用户可执行*/
>
> \#define S_IROTH 00004 /*与文件所有者不同组的用户可读*/
>
> \#define S_IWOTH 00002 /*与文件所有者不同组的用户可写*/
>
> \#define S_IXOTH 00001 /*与文件所有者不同组的用户可可执行*/

如果要传递数组类型参数可以使用 module_param_array ()函数，相较于 module_param ()函数多了n_para参数，用来表示传递参数个数;n_para参数值会根据输入的参数个数而改变,n_para的最终值为传递的数组元素个数。最后是 module_param_string(name, string, len, perm)函数，用来传递字符串类型的变量，四个参数的定义如下所示：

> name：外部传入的参数名，即加载模块时的传入值
>
> string:内部的变量名，即程序内定义的参数名
>
> len:以 string 命名的 buffer 大小(可以小于 buffer 的大小，但是没有意义)
>
> perm:模块参数的访问权限

### 10.10.2 驱动模块传参实验

```c
#include <linux/init.h>
#include <linux/module.h>
static int number;//定义 int 类型变量 number
static char *name;//定义 char 类型变量 name
static int para[8];//定义 int 类型的数组
static char str1[10];//定义 char 类型字符串 str1
static int n_para;//定义 int 类型的用来记录 module_param_array 函数传递数组元素个数的变量 n_para
module_param(number, int, S_IRUGO);//传递 int 类型的参数 number，S_IRUGO 表示权限为可读
module_param(name, charp, S_IRUGO);//传递 char 类型变量 name
module_param_array(para , int , &n_para , S_IRUGO);//传递 int 类型的数组变量 para
module_param_string(str, str1 ,sizeof(str1), S_IRUGO);//传递字符串类型的变量 str1
static int __init parameter_init(void)//驱动入口函数
{
	static int i;
	printk(KERN_EMERG "%d\n",number);
	printk(KERN_EMERG "%s\n",name);
  for(i = 0; i < n_para; i++)
  {
    printk(KERN_EMERG "para[%d] : %d \n", i, para[i]);
  }
	printk(KERN_EMERG "%s\n",str1);
	return 0;
}
static void __exit parameter_exit(void)//驱动出口函数
{
	printk(KERN_EMERG "parameter_exit\n");
}
module_init(parameter_init);//注册入口函数
module_exit(parameter_exit);//注册出口函数
MODULE_LICENSE("GPL v2");//同意 GPL 开源协议
MODULE_AUTHOR("woniu"); //作者信息
```

以上代码将传递 int 类型参数 number、char 类型参数 name、int 类型的数组 para 和 char类型字符串 str1，并在驱动入口函数中，对各个参数进行打印。在下一小节会进行驱动加载测试。

驱动模块传参的命令格式：

> insmod 对应的模块 参数

> insmod parameter.ko number=100 name="woniu" para=0,1,2,3,4,5,6,7 str="niubi"

## 10.11 导出内核模块符号

### 10.11.1 内核模块符号导出介绍

驱动程序编译生成的 ko 文件是相互独立的，即模块之间变量或者函数在正常情况下无法进行互相访问。而一些复杂的驱动模块需要分层进行设计，这时候就需要用到内核模块符号导出。

内核符号导出指的是在内核模块中导出相应的函数和变量，在加载模块时被记录在公共内核符号表中，以供其他模块调用。符号导出所使用的宏为 EXPORT_SYMBOL(sym)和 EXPORT_SYMBOL_GPL(sym)。它们定义在 “内核源码/include/linux/export.h”文件中（在 module.h 文件中已经对 export.h 进行引用，所以不需要单独引用 export.h 文件）,详细定义如下

```c
#define EXPORT_SYMBOL(sym) __EXPORT_SYMBOL(sym, "")
#define EXPORT_SYMBOL_GPL(sym) __EXPORT_SYMBOL(sym, "_gpl")
```

EXPORT_SYMBOL(sym)和 EXPORT_SYMBOL_GPL(sym)两个宏使用方法相同，而 EXPORT_SYMBOL_GPL(sym)导出的模块只能被 GPL 许可的模块使用，所以绝大多数的情况都使用 EXPORT_SYMBOL(sym)进行符号导出。sym 为函数的唯一参数，表示要导出的函数或变量名称。

### 10.11.2 内核模块符号导出实验

```c
#include <linux/init.h>
#include <linux/module.h>
int num = 10;//定义参数 num
EXPORT_SYMBOL(num);//导出参数 num
int add(int a, int b)//定义数学函数 add()，用来实现加法
{
	return a + b;
}
EXPORT_SYMBOL(add);//导出数学函数 add()
static int __init math_init(void)//驱动入口函数
{
	printk("math_moudle init\n");
return 0;
}
static void __exit math_exit(void)//驱动出口函数
{
	printk("math_module exit\n");
}
module_init(math_init);//注册入口函数
module_exit(math_exit);//注册出口函数
MODULE_LICENSE("GPL");//同意 GPL 开源协议
MODULE_AUTHOR("woniu");//作者信息
```

```c
#include <linux/init.h>
#include <linux/module.h>
extern int num;//导入 int 类型变量 num
extern int add(int a, int b);//导入函数 add
static int __init hello_init(void)//驱动入口函数
{
	static int sum;
	printk("num = %d\n", num);//打印 num 值
	sum = add(3, 4);//使用 add 函数进行 3+4 的运算
	printk("sum = %d\n", sum);//打印 add 函数的运算值
return 0;
}
static void __exit hello_exit(void)//驱动出口函数
{
	printk("Goodbye hello module\n");
}
module_init(hello_init);//注册入口函数
module_exit(hello_exit);//注册出口函数
MODULE_LICENSE("GPL");//同意 GPL 开源协议
MODULE_AUTHOR("woniu");//作者信息
```

程序导入了 int 类型的变量 num 和 add()函数，并在驱动入口函数中打印相应了 num 的参数值并对 add()函数进行了调用。

```makefile
export ARCH=arm64#设置平台架构
export CROSS_COMPILE=aarch64-linux-gnu-#交叉编译器前缀
obj-m := mathmodule.o
obj-m += hello.o
KDIR :=/home/topeet/Linux/linux_sdk/kernel #这里是你的内核目录
PWD ?= $(shell pwd)
all:
	make -C $(KDIR) M=$(PWD) modules #make 操作
clean:
	make -C $(KDIR) M=$(PWD) clean #make clean 操作
```

对于 Makefile 的内容注释已在上图进行添加，这里要注意的是在 hello.c 代码中使用了mathmodule.c 所导出的符号，所以 mathmodule.c 要在 hello.c 之前进行编译，即第 3 行和第 4行顺序不能交换。

然后使用命令“make”进行驱动的编译,编译完后会生成 hello.ko 和 mathmodule.ko 目标文件.

这里要注意的是，由于 hello.ko 依赖于 mathmodule.ko，所以 mathmodule.ko 需要先加载，分别使用以下命令进行模块的加载（加载顺序不能变）。

```shell
insmod mathmodule.ko
insmod hello.ko
```

![image-20240704142408515](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240704142408515.png)

可以看到 hello.ko 驱动加载的时候，mathmodule.ko 模块中定义的 num 参数值和调用 sum()函数的后正确的返回值都被打印了出来。至此内核模块符号导出实验就完成了。

最后可以输入以下命令进行驱动的卸载

```shell
rmmod hello.ko
rmmod mathmodule.ko
```

![image-20240704142429233](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240704142429233.png)

注意：由于 hello.ko 文件使用了 mathmodule.ko 导出的符号，所以要先卸载 hello.ko，卸载完成之后再卸载 mathmodule.ko。

<a id="part-24"></a>

> 1. 把驱动编译成模块：适合驱动开发
> 2. 把驱动编译进内核：适合生产环境

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

<a id="part-60"></a>

## 10.16 编译6.1内核

1. 下载：

   > https://cdn.kernel.org/pub/linux/kernel/v6.x/

1. 解压

2. 设置环境变量

   ```shell
   export ARCH=arm64
   export CROSS_COMPILE=aarch64-linux-gnu-
   make defconfig
    make -j8 Image dtbs
   ```

3. 打包

`defconfig` 只用于上游内核的基础构建；本板是否可启动取决于具体 DTS、驱动、固件和 U-Boot 支持。下面制作的是存放 Image/DTB 的 ext4 文件系统镜像，并不等同于 Android boot.img。先将本板对应的 Image、DTB 放进 my_kernel，后面的 U-Boot 加载文件名必须与实际文件一致。

   ```shell
   fallocate -l 64M kernel.img
   mkfs.ext4 kernel.img
   mkdir kernel_tmp
   mount kernel.img kernel_tmp/
   cp my_kernel/* kernel_tmp/
   umount kernel_tmp
   ```

---

[总目录](总目录.md) · [上一篇：RKNN模型转换与板端部署](9-RKNN%E6%A8%A1%E5%9E%8B%E8%BD%AC%E6%8D%A2%E4%B8%8E%E6%9D%BF%E7%AB%AF%E9%83%A8%E7%BD%B2.md) · [下一篇：字符设备驱动与文件操作](11-%E5%AD%97%E7%AC%A6%E8%AE%BE%E5%A4%87%E9%A9%B1%E5%8A%A8%E4%B8%8E%E6%96%87%E4%BB%B6%E6%93%8D%E4%BD%9C.md)
