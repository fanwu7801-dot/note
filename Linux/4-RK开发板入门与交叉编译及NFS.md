# 4-RK开发板入门与交叉编译及NFS

[总目录](总目录.md) · [上一篇：Linux串口编程与电气接口](3-Linux%E4%B8%B2%E5%8F%A3%E7%BC%96%E7%A8%8B%E4%B8%8E%E7%94%B5%E6%B0%94%E6%8E%A5%E5%8F%A3.md) · [下一篇：OpenCV](5-OpenCV.md)

[TOC]

<a id="part-6"></a>

## 4.1 交叉编译

1. 解压交叉编译器

   ```shell
   unzip gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu.zip
   ```

2. 配置环境变量

   ```shell
   vim ~/.bashrc
   export PATH=$PATH:~/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin/
   ```

   重新登录或source ~/.bashrc

3. 修改build.sh

   ```shell
   if [ ! -d "build" ]; then
       mkdir build
   fi
   cd build
   cmake -DCMAKE_C_COMPILER=aarch64-linux-gnu-gcc ..
   make 
   make install
   ```

<a id="part-7"></a>

## 4.2 开发板基本使用

### 4.2.1 硬件介绍

常见Linux开发板（芯片）：

*树莓派*（Raspberry Pi）是为学习计算机编程教育而设计，只有信用卡大小的微型电脑，其系统基于Linux。随着Windows 10 IoT的发布，用户可以用上运行Windows的树莓派。

代表型号：2B, 4B, 5B

![img](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/resize,m_lfit,limit_1,h_852.jpeg)

三星平台，

代表型号：4412,4418

龙芯中科，代表型号3A系列，2K系列

NXP平台：iMX6ULL,iMX6Q

ST：STM32MP157

瑞芯微(Rockchip)：RK3568，RK3588等

全志：TI113

**RK3568介绍**

![image-20240630145146756](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630145146756.png)

![image-20240630151028353](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630151028353.png)

### 4.2.2 使用命令点亮led

1. 连接硬件

2. 写命令

   > echo 1 > /sys/devices/platform/leds/leds/work/brightness

3. 修改日志输出等级

   > echo "4   4    1    7" >/proc/sys/kernel/printk

### 4.2.3 镜像整体烧写

开发板三种启动模式

| 模式        | 工具烧录 | 介绍                                                         |
| ----------- | -------- | ------------------------------------------------------------ |
| Normal 模式 | 不支持   | 此模式是正常启动的过程，各个组件依次加载，正常进入系统。系统引导 rootfs 启动，加载 rootfs，大多数的开发都是在这个模式调试的。 |
| Loader 模式 | 支持     | 在 Loader 模式下，可以进行固件的烧写，升级，可以通过工具单独烧写某一个分区镜像文件，方便调试。 |
| MaskRom 模  | 支持     | Flash 在未烧录固件时，芯片会引导进入 MaskRom 模式，可以进行初次固件的烧写;开发调试过程中若遇到 uboot 无法正常启动的情况，也可以进入 MaskRom 模式烧写固件。 |

进入Loader模式的方法：

> 使用双头 usb 线连接 iTop-3568 开发板到 PC 电脑上面，连接电源适配器到 开发板
>
> 1 按下 开发板的 vol+按键(按下不要松开),然后按下开发板的电源按键，启动开发板，这时烧写工具会提示发现新设备（此时可以松开 vol+按键了)，此时就进入了 Loader模式。
>
> 2 调试串口进入 uboot 命令行模式，可以执行以下命令进入 loader模式：rockusb 0 mmc 03
>
> 3 在板子开机状态下，进入系统后在调试串口或者 adb 命令行模式下执行以下命令进入 loader 模式：reboot loader
>
> 如果您的烧写工具没有发现新的设备，可以关闭烧写工具，在重新打开一遍烧写工具，然后重复一下上面的操作步骤。

安装驱动：DriverAssitant_v5.13

![image-20240630203751096](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630203751096.png)

![image-20240630203850714](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630203850714.png)

![image-20240630214824636](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630214824636.png)

![image-20240630214857327](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630214857327.png)

<a id="part-8"></a>

## 4.3 ubuntu和开发板互传文件

> 前提：开发板和ubuntu在同一网络

1. ubuntu安装nfs

   > apt-get install nfs-kernel-server

2. 修改配置

   > vim /etc/exports
   >
   > #要共享的目录
   >
   > /home/richard/ *(rw,sync,no_root_squash)

   /：要共享的目录；这里示例导出 /home/richard/；请按自己的实际目录创建并替换。

   *：代表允许所有的网络段访问；

   rw：是可读写权限；

   sync：服务端在修改写入稳定存储后才回复请求；

   no_root_squash：是 Ubuntu nfs 客户端分享目录使用者的权限，如果客户端使用的是 root

   用户，那么对于该共享目录而言，该客户端就具有 root 权限；

   其他 Ubuntu nfs 常用的参数有：

   ro：只读访问

   async：允许服务端在写入稳定存储前回复请求

   secure：通常要求客户端请求来自小于 1024 的源端口；不表示链路加密

   insecure：也允许客户端使用非特权源端口；不是服务端固定监听 1024 以上端口

   wdelay：如果多个用户要写入 NFS 目录，则归组（默认）

   no_wdelay：如果多个用户要写入 NFS 目录，则立即写入，当使用 async 时，无需此设

   置

   hide：不自动穿越导出树中另行挂载的子文件系统；不等于隐藏普通子目录

   nohide：允许在支持该选项的 NFS 场景中穿越已导出的子文件系统；注意 NFS 版本与导出条件

   subtree_check：导出文件系统子目录时，检查文件是否位于导出的子树；现代 nfs-utils 通常默认 no_subtree_check

   no_subtree_check：关闭子树检查，但不取消正常文件权限检查

   all_squash：共享文件的 UID 和 GID 映射匿名用户 anonymous，适合公用目录

   no_all_squash：保留共享文件的 UID 和 GID（默认）

   root_squash root：用户的所有请求映射成如 anonymous 用户一样的权限（默认）

   no_root_squash：客户端 UID 0 不映射为匿名用户；作用于导出的目录，不等于获得服务端整个根文件系统的权限

   anonuid=xxx：指定 nfs 服务器/etc/passwd 文件中匿名用户多的 UID

   anongid=xxx：指定 nfs 服务器/etc/passwd 文件中匿名用户的 GID

3. 重启

   > #重启 rpcbind 服务
   >
   > /etc/init.d/rpcbind restart
   >
   > #重启 nfs 服务
   >
   > /etc/init.d/nfs-kernel-server restart
   >
   > #查看是否成功挂载 nfs 目录（这里也可能要重启 ubuntu 才会又挂载目录）
   >
   > showmount -e

4. 挂载

   在开发板串口终端使用以下命令挂载到 nfs 服务器

   > #buildroot
   >
   > mount -t nfs -o nfsvers=3,nolock 192.168.111.130:/home/richard/ /mnt/
   >
   > #ubuntu
   >
   > sudo mount -t nfs 192.168.166.30:/home/richard/ /mnt/
   >
   > 取消挂载
   >
   > umount /mnt
   >
   > sudo nmcli dev wifi connect "YOUR_SSID" password "YOUR_PASSWORD"
   >
   > sudo mount -t nfs 192.168.1.10:/home/topeet/ /mnt/

---

[总目录](总目录.md) · [上一篇：Linux串口编程与电气接口](3-Linux%E4%B8%B2%E5%8F%A3%E7%BC%96%E7%A8%8B%E4%B8%8E%E7%94%B5%E6%B0%94%E6%8E%A5%E5%8F%A3.md) · [下一篇：OpenCV](5-OpenCV.md)
