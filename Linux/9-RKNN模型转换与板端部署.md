# 9-RKNN模型转换与板端部署

[总目录](总目录.md) · [上一篇：PyTorch与YOLOv5训练及数据标注](8-PyTorch%E4%B8%8EYOLOv5%E8%AE%AD%E7%BB%83%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%87%E6%B3%A8.md) · [下一篇：Linux6.1内核开发与构建基础](10-Linux6.1%E5%86%85%E6%A0%B8%E5%BC%80%E5%8F%91%E4%B8%8E%E6%9E%84%E5%BB%BA%E5%9F%BA%E7%A1%80.md)

[TOC]

<a id="part-15"></a>

## 9.1 镜像整体烧写

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

安装驱动：DriverAssitant_v5.1.1

![image-20240630203751096](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630203751096.png)

![image-20240630203850714](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630203850714.png)

![image-20240630214824636](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630214824636.png)

![image-20240630214857327](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240630214857327.png)

> 测试
>
> cd /sys/class/leds/work/
>
> echo 0 > brightness
>
> echo 1 > brightness
>
> echo timer > trigger

<a id="part-16"></a>

## 9.2 ubuntu和开发板互传文件

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

   > mount -t nfs -o nfsvers=3,nolock 172.172.3.163:/home/richard/ /mnt/
   >
   > sudo mount -t nfs 172.172.12.230:/home/richard/ /mnt/


## 9.3 ubuntu和开发板互传文件

> 前提：开发板和ubuntu在同一网络

1. ubuntu安装nfs

   > apt-get install nfs-kernel-server

2. 修改配置

   > vim /etc/exports
   >
   > #要共享的目录
   >
   > /home/richard/ *(rw,sync,no_root_squash)

   /home/：要共享的目录；这里示例导出 /home/richard/；请按自己的实际目录创建并替换。

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

   > mount -t nfs -o nfsvers=3,nolock 172.172.3.116:/ /mnt/
   >
   > #ubuntu中执行以下命令
   >
   > sudo mount -t nfs 172.172.12.230:/home/richard/ /mnt/

<a id="part-17"></a>

## 9.4 交叉编译

交叉编译器在

> /prebuilts/gcc/linux-x86/aarch64/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin

配置一个环境变量

> vim /etc/profile
>
> 或
>
> 用户目录中的.bashrc
>
> export PATH=$PATH:/aa/rk356x_linux/prebuilts/gcc/linux-x86/aarch64/gcc-linaro-6.3.1-2017.05-x86_64_aarch64-linux-gnu/bin

编译程序：

> aarch64-linux-gnu-gcc  main.c

<a id="part-18"></a>

> 部署时的 NFS 挂载步骤见 [NFS部署环境](9-RKNN%E6%A8%A1%E5%9E%8B%E8%BD%AC%E6%8D%A2%E4%B8%8E%E6%9D%BF%E7%AB%AF%E9%83%A8%E7%BD%B2.md#part-16)；模型转换、编译和板端运行放在本篇。


## 9.5 神经网络处理器

### 9.5.1 NPU

NPU（Nerual Processing Unit）是一种专门用于加速神经网络计算的处理器。

在深度学习技术刚开始流行的时候，人们主要使用通用计算设备，如 CPU 和 GPU，来执行神经网络计算。但是，随着神经网络的复杂度和规模不断增加，传统的计算设备已经不能满足快速、高效地执行神经网络计算的需求。因此，研究人员开始探索如何设计一种专门用于加速神经网络计算的处理器，这就是 NPU 的由来。

早期的 NPU 主要是基于 FPGA（Field Programmable Gate Array可编程阵列逻辑）实现的。FPGA 是一种可编程逻辑器件，可以通过编程实现各种不同的电路功能。由于 FPGA 具有高度的灵活性和可编程性，可以用于实现各种不同类型的神经网络处理器。2010 年，斯坦福大学的研究人员提出了一种基于 FPGA 的神经网络加速器，可以实现高效的神经网络计算。此后，越来越多的研究人员开始尝试使用 FPGA 实现 NPU。

随着深度学习技术的不断发展和普及，NPU 的研究和开发也取得了越来越多的进展。2013年，Google 发布了一篇论文，介绍了一种名为“Tensor Processing Unit”（TPU）的定制芯片，专门用于加速深度学习模型的训练和推理。TPU 采用了特定的硬件架构和优化算法，可以实现高效、低功耗的神经网络计算。TPU 的成功引起了业界的广泛关注，也促进了 NPU 的发展。随后，其他公司也开始研发自己的 NPU。2015 年，华为发布了一款名为“Kirin 950”的处理器，集成了一种名为“Neural Processing Unit”（NPU）的模块，用于加速神经网络计算。2018年，华为推出了全新的“昇腾”（Ascend）系列处理器，其中包括专门用于加速深度学习计算的NPU 模块。同年，英伟达推出了名为“TensorCore”的加速器，用于加速深度学习模型的训练和推理。

随着 NPU 技术的不断发展和普及，越来越多的公司开始将 NPU 集成到自己的芯片中，以加速神经网络计算。例如，苹果公司在 2017 年发布的 A11 芯片中集成了神经网络处理器，用于支持人脸识别等功能。而瑞芯微为了满足人工智能的需要，瑞芯微的处理器也逐渐集成了NPU，而瑞芯微处理器内置的 NPU，就被称之为 RKNPU。

![image-20240725213338794](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725213338794.png)

### 9.5.2 RKNPU 介绍

到目前为止，RKNPU 已经经过了几代的发展，趋近成熟。RK3399pro 和 RK1808 初次引入了 RKNPU，相比传统的 CPU 和 GPU 相比传统的 CPU 和 GPU，在深度学习运算能力上有比较大幅度的提升。接下来在 RV1109 和 RV1126 上使用了第二代 NPU，提升了 NPU 的利用率。第三代 NPU 应用在 RK3566 和 RK3568 上，搭载全新 NPU 自研架构，而 RK3588 搭载的为第四代 NPU,提高了带宽利用率，支持了多核扩展。RKNPU 具体发展过程如下图所示：

![image-20240725213510102](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725213510102.png)

RKNPU1.0 和 RKNPU2.0 被划分为了 RKNPU，而 RKNPU3.0、RKNPU4.0 和 RKNPU5.0 被划分为了 RKNPU2,RKNPU 和 RKNPU2 所使用的 SDK 和工具套件不同，在后续的讲解中会再次进行说明。

**RK3568特性：**

（1）NPU 支持以下特性：

（2）使用 AHB 接口配置 NPU

（3）使用 AXI 接口从内存中获取数据

（4）支持 int8、int16、float16、Bfloat16 操作

（5）每个周期可进行 512 个 int8 MAC 操作

（6）每个周期可进行 128 个 int16 MAC 操作

（7）每个周期可进行 128 个 float16 MAC 操作

（8）每个周期可进行 128 个 bfloat16 MAC 操作

（9）每个核心有 256KB 的内部缓存

（10）支持转换的模型：TensorFlow、Caffe、Tflite、Pytorch、Onnx NN 等。

![image-20240725213625500](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725213625500.png)

**AHB/AXI 接口**

AXI 主接口（AXI Master Interface）用于从连接到 SoC AXI 互联的内存中获取数据。AXI 是一种高性能、低延迟、可扩展的总线接口，常用于连接处理器和外设，并支持多个主设备和从设备。AXI 主接口通常用于从内存中获取数据，例如从 DRAM 或其他存储器中读取程序和数据，并将其传输到处理器或其他外设中进行处理和计算。

AHB 从接口（AHB Slave Interface）用于访问寄存器进行配置、调试和测试。AHB 是一种标准化的系统总线接口，通常用于连接处理器、内存和外设等硬件电路。AHB 从接口通常用于访问寄存器，例如控制和配置处理器、外设和其他硬件电路的参数和状态，以实现系统的配置、调试和测试。

在 SoC 系统中，AXI 主接口和 AHB 从接口通常被用于连接处理器、内存、外设和其他硬件电路，以实现数据传输、控制和配置等功能。AXI 接口通常用于高速数据传输和处理，而 AHB接口通常用于配置、调试和测试等低速控制操作。

**卷积神经网络加速单元（CNA）**

卷积神经网络加速单元（Convolutional Neural Network Accelerator，CNA）是 RKNPU 中重要的组成部分之一。包括卷积预处理控制器、NPU 内部缓存区、序列控制器、乘加运算单元和累加器，下面对各个部分进行介绍：

（1）卷积预处理控制器

卷积预处理控制器是 CNA 中用于预处理卷积计算的硬件单元，可以对输入的模型权重进行解压缩之后加载进 NPU 的内部缓冲区，并且可以判断零节点加速运算速度，最后将要推理的数据加载进 NPU 的内部缓冲区中。

（2）NPU 内部缓存区（Internal Buffer）

NPU 内部缓存区是 CNA 中用于存储中间计算结果的缓存区。它可以高效地存储和管理卷积神经网络中的各种数据，包括输入数据、卷积核、卷积结果等。NPU 内部缓存区采用了多级缓存和数据重用技术，可以高效地利用计算资源和存储资源，从而进一步提高计算速度和效率。

（3）序列控制器（Sequence Controller）

序列控制器是 CNA 中用于控制卷积计算序列的硬件单元。它可以根据卷积神经网络的结构和参数，自动地配置和控制 CNA 中各个硬件单元的工作模式和参数。序列控制器还可以实现卷积计算的并行化和流水化，从而提高计算速度和效率。

（4）乘加运算单元（Multiply-Accumulate Unit，MAC）

乘加运算单元是 CNA 中用于执行卷积计算的硬件单元。它可以对输入数据和卷积核进行乘法和累加运算，从而得到卷积计算结果。乘加运算单元采用了高度并行的设计，可以同时执行多个卷积计算操作，从而大大提高计算速度和效率。

（5）累加器（Accumulator）

累加器是 CNA 中用于累加卷积计算结果的硬件单元。它可以高效地累加卷积计算结果，从而得到最终的输出结果。累加器可以采用多种精度，可以适应不同的计算精度要求。

**数据处理单元（Data Processing Unit）**

数据处理单元（Data Processing Unit）主要处理单个数据的计算，例如 Leaky ReLU、ReLU、ReluX、Sigmoid、Tanh 等。它还提供了一些功能，例如 Softmax、转置、数据格式转换等。

数据处理单元是一种硬件电路，用于加速神经网络的计算过程。它通常被用于处理前向计算过程中的单个数据，例如卷积层和全连接层中的激活函数计算。不同的激活函数需要不同的计算操作，例如 ReLU 需要计算 max(0,x)，Sigmoid 需要计算 1/(1+exp(-x))，而数据处理单元可以通过硬件电路来实现这些计算操作，从而提高神经网络的计算性能和效率。

除了激活函数计算之外，数据处理单元还提供了一些其他的函数，例如 Softmax、转置、数据格式转换等。这些函数通常被用于神经网络模型的构建和优化过程中，例如将模型的输出转换为概率分布、重新排列张量的维度、将数据从一种格式转换为另一种格式等。

**平面处理单元（Planar Processing Unit）**

平面处理单元（Planar Processing Unit）主要提供对数据处理单元的输出数据进行平面操作的功能，例如平均池化、最大值池化、最小值池化等。

平面处理单元是一种硬件电路，用于加速神经网络的计算过程。它通常被用于对数据处理单元的输出数据进行平面操作，例如在卷积神经网络中，对卷积层的输出进行池化操作，以降低数据维度和减少计算量。平面处理单元可以通过硬件电路来实现这些操作，从而提高神经网络的计算性能和效率。

平面处理单元支持多种平面操作，例如平均池化、最大值池化、最小值池化等。这些操作可以通过不同的参数来控制池化窗口的大小和步幅等，从而适应不同的应用场景和要求。

### 9.5.3 NPU应用领域

RKNPU（Rockchip NPU）是一种专门用于深度学习应用的高性能处理器，并且在多个应用场景中都有广泛的应用。以下是一些常见的 RKNPU 应用场景：

![image-20240725213940106](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725213940106.png)

## 9.6 RKNPU 推理软件框架

### 9.6.1 推理软件框架

![image-20240725215853957](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725215853957.png)

**(1)RKNPU 硬件层**

关于 RKNPU 硬件层在上个章节已经进行了讲解，这里就不再进行过多的赘述。

**(2)RKNPU 驱动层**

RKNPU 的驱动层是连接上层应用和 RKNPU 硬件的桥梁。驱动层的主要作用是将应用程序需要推理的内容提交给 RKNPU 进行计算，从而加速神经网络的训练和推理过程。具体来说，

驱动层需要完成以下任务：

硬件初始化：驱动层需要初始化 RKNPU 硬件，包括设置寄存器、分配内存等操作，以确保 RKNPU 可以正常工作。

数据传输：驱动层需要将数据从主机内存传输到 RKNPU 内存中，以便进行计算。在计算完成后，驱动层还需要将计算结果传输回主机内存。

计算任务调度：驱动层需要根据应用程序的需求，管理和分配 RKNPU 的计算资源，以确保多个计算任务之间不会互相干扰。

**(3)RKNPU 应用层**

RKNPU 应用层由 AI 应用程序、RKNN API 以及运行时所需要的库所组成。

开发者通过调用瑞芯微提供好的 API 接口进行 AI 应用的开发，瑞芯微分别提供了 C 语言和Python 语言这两种 API 帮助开发者进行嵌入式设备部署，Python 语言提供的接口较为简单，旨在帮助用户进行前期的模型检测、测试以及应用调试，而要想得到更好的效果从而真正应用到实际项目中就要使用 C API 接口了。

而无论是由 C API 接口还是 Python 的 API 接口编写的应用程序，要想实际运行都需要相应的动态库，动态库包含这些 API 的具体实现，这些动态库由瑞芯微所提供。而我们只需要根据瑞芯微所提供的 API 编写对应的应用程序即可。

### 9.6.2 RKNN 模型

RKNN（Rockchip Neural Network）是瑞芯微公司开发的一种神经网络模型格式，它可以将常见的深度学习模型转换为适用于瑞芯微的 AI 加速器 RKNPU 的模型格式。RKNN 模型的优点是在保证精度的同时，可以实现高效的推理和低功耗的计算。下面是 RKNN 模型的详细介绍：

RKNN 模型的文件格式：RKNN 模型使用自定义的文件格式来表示神经网络模型。它将神经网络模型划分为两个部分：静态部分和动态部分。静态部分包括模型的网络结构和权重，而动态部分包括输入输出的形状和类型等信息。使用这种格式可以减少模型的存储空间和加载时间。

RKNN 模型的转换工具：为了将其他常见的深度学习模型转换为 RKNN 模型，瑞芯微提供了一个转换工具 RKNN-Toolkit2。该工具支持将 TensorFlow、Caffe、MXNet 等框架训练出来的模型转换为 RKNN 模型，并且支持对模型进行量化、融合等优化操作，以提高运行效率。

RKNN 模型的部署和推理：RKNN 模型可以通过 RKNPU 硬件进行高效的推理。在部署 RKNN模型时，开发者需要使用 RKNPU 提供的 SDK，并调用相应的 API 接口来加载和运行 RKNN 模型。由于 RKNPU 硬件的优化，RKNN 模型可以实现高效的推理和低功耗的计算。

![image-20240725220022396](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725220022396.png)

### 9.6.3 RKNN Toolkit2

RKNN-Toolkit2 资料包中有四个目录，分别为 docs、examples、packages 和 rknn_toolkit_lite2，

docs 目录包含了 RKNN-Toolkit2 的使用文档，包括更新记录、两个 Python 环境所需的依赖项、RKNN 算子支持列表、快速入门指南以及使用指导手册。

examples 目录包含了 RKNN-Toolkit2 的一些示例代码，用于演示 RKNN-Toolkit2 的一些功能。通过运行该示例代码，可以帮助用户更好的理解和掌握 RKNN-Toolkit2 的具体功能和使用方法。

packages 目录提供了 Python3.6 和 Python3.8 两个版本的安装包，分别对应 X86 平台的ubuntu18 和 ubuntu20 两个发行版 Linux 操作系统。

而 rknn_toolkit_lite2 属于 RKNN-Toolkit2 的一个阉割版，会在下一小节进行讲解和对比。

下面对 RKNN-Toolkit2 进行简单的介绍：RKNN-Toolkit2 是瑞芯微为用户提供的、在 PC端 ubuntu 平台进行模型转换、推理和性能评估的开发套件，用户通过该工具提供的 Python 接口可以便捷地完成以下功能：

>  模型转换: 支持 Caffe、TensorFlow、TensorFlow Lite、ONNX、DarkNet、PyTorch 等模型转为 RKNN 模型，并支持 RKNN 模型导入导出，RKNN 模型能够在 Rockchip NPU 平台上加载使用
>
>  量化功能: 支持将浮点模型量化为定点模型，目前支持的量化方法为非对称量化 ( asymmetric_quantized-8 及 asymmetric_quantized-16 )，并支持混合量化功能 。 asymmetric_quantized-16 目前版本暂不支持
>
>  模型推理: 能够在 PC 上模拟 NPU 运行 RKNN 模型并获取推理结果或将 RKNN 模型分发到 Rockchip NPU 设备上进行推理并获取推理结果
>
>  性能评估和内存评估: 将 RKNN 模型分发到 Rockchip NPU 设备上运行，以评估模型在实际设备上运行时的性能和内存使用信息
>
>  量化精度分析: 该功能将给出模型量化前后每一层推理结果与浮点模型推理结果的余弦距离，以便于分析量化误差是如何出现的，为提高量化模型的精度提供思路
>
>  模型加密功能：使用指定的加密等级将 RKNN 模型整体加密。因为 RKNN 模型的加密是在 NPU 驱动中完成的，使用加密模型时，与普通 RKNN 模型一样加载即可，NPU 驱会自动对其进行解密。

### 9.6.4 RKNN Toolkit lite2

RKNN Toolkit lite2 相 较 于 RKNN-Toolkit2 多 了 一 个 lite 后 缀 ， 可 以 简 单 的 理 解 为RKNN-Toolkit2 的阉割版，只保留了推理的功能,可以帮助用户在开发板端进行模型的初步部署和测试。

RKNN-Toolkit lite2 资料包中有三个目录，分别为 docs、examples 和 packages。docs 目录包含了 RKNN-Toolkit lite2 的使用文档。

examples 目录包含了 RKNN-Toolkit lite2 的示例代码，由于 RKNN-Toolkit2 lite2 的使用较为简单所以只提供了一个示例。

packages 目录提供了 Python3.7 和 Python3.9 两个版本的安装包，需要注意的是这里的安装包架构为 aarch64，即需要安装在 RK3568 或者 RK3588 的 ubuntu 等发行版 Linux 操作系统上。

最后对 RKNN-Toolkit2 和 RKNN-Toolkit lite2 进行对比，对比如下：

（1）提供的语言接口都是 Python 语言。

（2）RKNN-Toolkit2 提供的安装包架构为 X86_64，运行在日常使用的 PC 电脑上，一般情况下安装在虚拟机 ubuntu 上，而 RKNN-Toolkit lite2 提供的安装包架构为 aarch64，运行在RK3568 或者 RK3588 开发板上。

（3）RKNN-Toolkit2 可以进行模型转换、推理和性能评估，而 RKNN-Toolkit lite2 只保留了推理功能，用于模型的初步部署和调试。

![image-20240725220419297](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725220419297.png)

### 9.6.5 RKNPU2 SDK

RKNPU2 SDK 资料包中有 3 个目录，分别为 docs、examples 和 runtime。

docs 目录包含了 RKNPU2 SDK 的使用文档，包括 RKNN 算子支持列表、快速入门指南以及使用指导手册。

examples 目录包含了 RKNPU2 SDK 的一些示例代码和第三方库。通过这些示例代码，可以帮助我们更快速的掌握 RKNPU2 所提供的一些 C API 接口和使用流程。

runtime目录用于存放API运行时依赖的动态库和头文件，并且提供了一个名为rknn_server的可执行程序，在后面 RKNN-Toolkit2 连板推理时会用到。

RKNPU2 SDK 和 RKNN-Toolkit lite2 要实现的功能相同，都是在开发板部署 RKNN 模型，然后进行推理，只是相较于 RKNN-Toolkit lite2 提供了更多的接口，调用起来较为复杂，但可以获得更好的运行效果。

![image-20240725220454214](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725220454214.png)

### 9.6.6 学习步骤

无论使用 RKNPU2 SDK 提供的 C API 接口进行 RKNN 模型部署，还是使用 RKNN-Toolkit lite2提供的 Python API 接口进行 RKNN 模型部署，在此之前，都需要先使用 RKNN Toolkit2 将网络模型转换为 RKNN 模型，或者对模型进行精度分析等操作，所以在 RKNPU2 开发阶段，首先要学习 RKNN-Toolkit 2 的使用。

RKNN-Toolkit 2 的学习分为以下几个步骤，搭建 RKNN-Toolkit 2 开发环境、讲解 RKNN-Toolkit2 提供的 API 接口并测试常用功能、对 RKNN 模型构建、精度分析、性能评估、内存评估以及

RKNN 模型加载等重要接口进行单独讲解。

在 RKNPU 开发过程中，RKNN-Toolkit 2 就是用来构建并且评测 RKNN 模型的，得到符合我们大致预期的 RKNN 模型之后就可以进行项目的部署了，模型部署分为 RKNN-Toolkit lite2 部署和 RKNPU2 SDK 部署，由于 RKNN-Toolkit lite2 提供的接口与 RKNN-Toolkit 2 提供接口相似，且数量较少，主要用于初期调试，所以我们首先会讲解 RKNN-Toolkit lite2 部署，包括 RKNN-Toolkitlite2API 接口讲解、RKNN-Toolkit lite2 使用环境搭建、RKNN-Toolkit lite2 例程测试。

RKNN-Toolkit lite2 讲解完成之后就到了最难的 RKNPU2 SDK 提供的 C API 接口讲解了，C API根据处理数据时的方法可以分为 0 拷贝 API 和通用 API，首先会根据例程讲解两种 API 的使用框架、随后对瑞芯微提供的 C API 例程进行介绍，凭借这些例程可以帮助我们后期进行快速开发，在例程的讲解中会对出现的各个 C API 进行详细的讲解。

![image-20240725220613868](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240725220613868.png)

## 9.7 RKNN Toolkit2 环境搭建

### 9.7.1 安装conda

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

然后在用户目录下新建.condarc 文件，并输入以下内容：

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

经过上面的步骤之后就会将 conda 镜像地址更改为清华源，可以极大的提高安装软件的速度。

### 9.7.2 创建 RKNN 虚拟环境

为了避免环境后续学习中环境的冲突问题，这里使用 conda 创建 RKNN 虚拟环境，使用命令如下所示：

> conda create -n rknn python=3.8

命令执行之后，首先会要求安装一系列软件包，输入 y 确认即可.

然后使用“ conda activate rknn”激活相应得 rknn 环境，如下图所示：

![image-20240726124825321](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240726124825321.png)

可以看到，标识符由“base”变成了“rknn”,

### 9.7.3 安装依赖软件和工具包

然后将 rknn_toolkit2-1.4.0_22dcfef4-cp38-cp38-linux_x86_64.whl 和 requirements_cp38-1.4.0.txt 文件拷贝到虚拟机 ubuntu 上。

首先使用以下命令安装 numpy ，安装过程如下图所示：

> pip3 install numpy==1.16.6 -i https://pypi.tuna.tsinghua.edu.cn/simple
>
> pip3 install numpy==1.16.6 -i https://mirrors.aliyun.com/pypi/simple

![image-20240726124951924](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240726124951924.png)

然后安装瑞芯微提供的 requirements_cp38-1.4.0.txt 文件所记录的依赖包，安装过程如下图所示：

>  把requirements中所有的>=改为==
>
>  pip install -r requirements_cp38-1.4.0.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
>
>  pip install -r requirements_cp38-1.4.0.txt -i https://mirrors.aliyun.com/pypi/simple
>
>  pip install -r requirements_cp38-1.6.0.txt -i https://mirrors.aliyun.com/pypi/simple

![image-20240726124959140](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240726124959140.png)

最后安装瑞芯微提供的 rknn_toolkit2-1.6.0 版本的软件包，安装完成如下图所示：

> pip install rknn_toolkit2-1.6.0+81f21f4d-cp38-cp38-linux_x86_64.whl -i https://mirrors.aliyun.com/pypi/simple

![image-20240726125025938](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240726125025938.png)

至此，RKNN 的虚拟环境就创建完成了。

### 9.7.4 可能遇到的问题

1. setuptools版本不对

   ![image-20240729103238505](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240729103238505.png)

   ```shell
   1. 卸载原来的setuptools
   pip uninstall setuptools
   2. 安装setuptools
   pip install setuptools==49.6.0 -i https://mirrors.aliyun.com/pypi/simple
   ```

   ![image-20240729104139749](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240729104139749.png)

   ```
   修改文件
   miniconda3/envs/rknn/lib/python3.8/site-packages/distutils-precedence.pth
   在import os;后面加一个换行
   ```

   ![image-20240729104448485](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240729104448485.png)

2. glibc版本不对

   ![image-20240729104703003](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240729104703003.png)
   
   1. 使用root身份, 解压glibc2.29的解压包
   
   2. 进入glibc安装包目录
   
   3. 创建一个build目录
   
   4. 进入build目录
   
   5. 配置
   
      ```
      ../configure --prefix=/usr/local --disable-sanity-checks
      ```
   
   7. 编译make
   
   8. 安装 make install
   
   9. 安装完成以后进入以下目录,ll查看动态库文件
   
      ```shell
      cd /lib/x86_64-linux-gnu
      ```
   
   10. 复安装的glibc2.29
   
       ```
       cp /usr/local/lib/libm-2.29.so /lib/x86_64-linux-gnu/
       ```
   
   11. 连接
   
       ```
       ln -sf libm-2.29.so libm.so.6
       ```
   
## 9.8 连板推理
   
   1. 复制需要文件
   
      ![image-20240729120603105](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240729120603105.png)
   
   2. ubuntu上安装adb
   
      ```
      sudo apt-get install adb
      ```
   
   3. 复制连板推理的服务端到开发板上
   
      ![image-20240729121326961](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240729121326961.png)
   
   4. 复制动态库文件到开发板上
   
      Linux/librknn_api/${BOARD_ARCH}/librknnrt.so到/usr/lib目录
   
   5. 运行
   
      ```
      ./start_rknn.sh
      ```
   


## 9.9 模型转换

1. 创建一个rknn虚拟环境

   ```shell
   conda create -n rknn python=3.8
   conda activate rknn
   ```

2. 安装ToolKit

   ```shell
   cd rknn-toolkit2-master/rknn-toolkit2/packages/
   pip install -r requirements_cp38-1.6.0.txt
   pip install toolkit......whl
   ```

3. 把pt模型转为onnx模型

   ```shell
   #切换到yolo环境
   conda activate yolo
   # 可以将模型路径修改为自己训练保存的模型路径
   python export.py --weights yolov5s.pt(替换成自己的模型) --img 640 --batch 1 --include onnx
   ```
   
   **这一步必须要修改yolov5的源码**

   修改models/yolo.py，修改class Detect(nn.Module):的forward函数

   ```c
   # def forward(self, x):
       #     z = []  # inference output
       #     for i in range(self.nl):
       #         x[i] = self.m[i](x[i])  # conv
       #         bs, _, ny, nx = x[i].shape  # x(bs,255,20,20) to x(bs,3,20,20,85)
       #         x[i] = x[i].view(bs, , self.no, ny, nx).permute(0, 1, 3, 4, 2).contiguous()
       #
       #         if not self.training:  # inference
       #             if self.grid[i].shape[2:4] != x[i].shape[2:4] or self.onnx_dynamic:
       #                 self.grid[i] = self._make_grid(nx, ny).to(x[i].device)
       #
       #             y = x[i].sigmoid()
       #             if self.inplace:
       #                 y[..., 0:2] = (y[..., 0:2] * 2. - 0.5 + self.grid[i]) * self.stride[i]  # xy
       #                 y[..., 2:4] = (y[..., 2:4] * 2) ** 2 * self.anchor_grid[i]  # wh
       #             else:  # for YOLOv5 on AWS Inferentia https:///ultralytics/yolov5/pull/2953
       #                 xy = (y[..., 0:2] * 2. - 0.5 + self.grid[i]) * self.stride[i]  # xy
       #                 wh = (y[..., 2:4] * 2) ** 2 * self.anchor_grid[i].view(1, , 1, 1, 2)  # wh
       #                 y = torch.cat((xy, wh, y[..., 4:]), -1)
       #             z.append(y.view(bs, -1, self.no))
       #
       #     return x if self.training else (torch.cat(z, 1), x)
   
       # 有的修改是这一版本，但是这一版本会导致最终部署在RK3568开发板上是出现测试结果出错
       # 出现重复框选，选框混乱，置信度高于1的错误。
       # def forward(self, x):
       #     z = []  # inference output
       #     for i in range(self.nl):
       #         x[i] = self.m[i](x[i])  # conv
       #     return x
       
       def forward(self, x):
           z = []  # inference output
           for i in range(self.nl):
               if os.getenv('RKNN_model_hack', '0') != '0':
                   x[i] = torch.sigmoid(self.m[i](x[i]))  # conv
   
           return x
   ```
   
   将export.py文件中的run函数下的语句：

   ```c
   shape = tuple((y[0] if isinstance(y, tuple) else y).shape)  # model output shape
   ```
   
   改为：

   ```c
   shape = tuple(y[0].shape)  # model output shape
   ```
   
   并且在代码开头添加：

   ```c
   import os
   os.environ['RKNN_model_hack'] = 'npu_2'
   ```
   
4. 下载rknn_model_zoo

5. 把onnx模型转为rknn模型

   ```shell
   #解压
   #切换成rknn环境
   conda activate rknn
   #进入以下目录
   cd rknn_model_zoo/examples/yolov5/python/
   # 执行转换
   python convert.py yolov5.onnx(换成上一步转换的onnx模型) rk3568
   # 成生的rknn模型在../model/
   ```



## 9.10 rknn图像识别

### 9.10.1 编译

根据指定平台修改 `build-linux_<TARGET_PLATFORM>.sh`中的交叉编译器所在目录的路径 `TOOL_CHAIN`，例如修改成

```sh
export TOOL_CHAIN=~/opt/tool_chain/gcc-9.3.0-x86_64_aarch64-linux-gnu/host
```

然后执行：

```sh
./build-linux_<TARGET_PLATFORM>.sh
```

### 9.10.2 推送执行文件到板子


将 install/rknn_yolov5_demo_Linux 拷贝到板子的/userdata/目录.

- 如果使用rockchip的EVB板子，可以使用adb将文件推到板子上：

```
adb push install/rknn_yolov5_demo_Linux /userdata/
```

- 如果使用其他板子，可以使用scp等方式将install/rknn_yolov5_demo_Linux拷贝到板子的/userdata/目录

### 9.10.3 运行

```sh
adb shell
cd /userdata/rknn_yolov5_demo_Linux/

export LD_LIBRARY_PATH=./lib
./rknn_yolov5_demo model/<TARGET_PLATFORM>/yolov5s-640-640.rknn model/bus.jpg
```

Note: Try searching the location of librga.so and add it to LD_LIBRARY_PATH if the librga.so is not found on the lib folder.
Using the following commands to add to LD_LIBRARY_PATH.

```sh
export LD_LIBRARY_PATH=./lib:<LOCATION_LIBRGA.SO>
```

---

[总目录](总目录.md) · [上一篇：PyTorch与YOLOv5训练及数据标注](8-PyTorch%E4%B8%8EYOLOv5%E8%AE%AD%E7%BB%83%E5%8F%8A%E6%95%B0%E6%8D%AE%E6%A0%87%E6%B3%A8.md) · [下一篇：Linux6.1内核开发与构建基础](10-Linux6.1%E5%86%85%E6%A0%B8%E5%BC%80%E5%8F%91%E4%B8%8E%E6%9E%84%E5%BB%BA%E5%9F%BA%E7%A1%80.md)
