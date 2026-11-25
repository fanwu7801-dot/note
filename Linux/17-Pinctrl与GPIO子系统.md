# 17-Pinctrl与GPIO子系统

[总目录](总目录.md) · [上一篇：设备树](16-%E8%AE%BE%E5%A4%87%E6%A0%91.md) · [下一篇：I2C子系统](18-I2C%E5%AD%90%E7%B3%BB%E7%BB%9F.md)

> 版本基线：Linux 6.1，面向 RK SDK。保留已完成的接口勘误；源码摘录与板级资源仍需对照实际 SDK。构建和适配说明见 [Linux 6.1 适配说明](整理记录/Linux6.1适配说明.md)。

[TOC]

<a id="part-35"></a>

## 17.1 pinmux 介绍

Pinmux（引脚复用）是指在系统中配置和管理引脚功能的过程。在许多现代集成电路中，单个引脚可以具有多个功能，例如作为 GPIO、UART、SPI 或 I2C 等。通过使用引脚复用功能，可以在这些不同的功能之间切换。

引脚复用通过硬件和软件的方式实现。硬件层面，芯片设计会为每个引脚提供多个功能的选择。这些功能通常由芯片厂商在芯片规格文档中定义。通过编程设置寄存器或开关，可以选择某个功能来连接引脚。这种硬件层面的配置通常是由引脚控制器（Pin Controller）或引脚复用控制器（Pin Mux Controller）负责管理。

软件层面，操作系统或设备驱动程序需要了解和配置引脚的功能。它们使用设备树（Device Tree）或设备树绑定（Device Tree Bindings）来描述和配置引脚的功能。在设备树中，可以指定引脚的复用功能，将其连接到特定的硬件接口或功能。操作系统或设备驱动程序在启动过程中解析设备树，并根据配置对引脚进行初始化和设置。

## 17.2 pinctrl 子系统

Linux 中的 pinctrl 子系统（Pin Control Subsystem）是一个用于管理和配置通用输入/输出（GPIO）引脚的框架。它提供了一种标准化的方法，以在 Linux 内核中对 GPIO 引脚进行配置、分配和控制，从而适应不同的硬件平台和设备。

pinctrl 子系统也符合 Linux 内核的设备模型规范，所以 pinctrl 子系统同样可以根据设备模型规范分为设备、驱动、总线和类四个部分，本章节将从设备和驱动两个部分来引入 pinctrl 子系统。

## 17.3 使用 pinctrl 设置复用关系

pinctrl（引脚控制）用于描述和配置硬件设备上的引脚功能和连接方式。它是设备树的一部分，用于在启动过程中传递引脚配置信息给操作系统和设备驱动程序，以便正确地初始化和控制引脚。

接下来将使用三个例子对客户端要用到的属性进行讲解。

例 1：

> node **{**
>
> ​	pinctrl**-**names **=** "default"**;**
>
> ​	pinctrl**-**0 **= <&**pinctrl_hog_1**>;**
>
> }

在例 1 中，pinctrl-names 属性定义了一个状态名称：default。

pinctrl-0 属性指定了第一个状态 default 对应的引脚配置。

<&pinctrl_hog_1> 是一个引脚描述符，它引用了一个名为 pinctrl_hog_1 的引脚控制器节点。这表示在 default 状态下，设备的引脚配置将使用 pinctrl_hog_1 节点中定义的配置。

例 2：

> node **{**
>
> ​		pinctrl**-**names **=** "default"**,** "wake up"**;**
>
> ​		pinctrl**-**0 **= <&**pinctrl_hog_1**>;**
>
> ​		pinctrl**-**1 **= <&**pinctrl_hog_2**>;**
>
> **}**

在例 2 中，pinctrl-names 属性定义了两个状态名称：default 和 wake up。

pinctrl-0 属性指定了第一个状态 default 对应的引脚配置，引用了 pinctrl_hog_1 节点。

pinctrl-1 属性指定了第二个状态 wake up 对应的引脚配置，引用了 pinctrl_hog_2 节点。

这意味着设备可以处于两个不同的状态之一，每个状态分别使用不同的引脚配置。

例 3：

> node **{**
>
> ​	pinctrl**-**names **=** "default"**;**
>
> ​	pinctrl**-**0 **= <&**pinctrl_hog_1 **&**pinctrl_hog_2**>;**
>
> **}**

在这个例子中，pinctrl-names 属性仍然定义了一个状态名称：default。

pinctrl-0 属性指定了第一个状态 default 对应的引脚配置，但与之前的例子不同的是，它引用了两个引脚描述符：pinctrl_hog_1 和 pinctrl_hog_2。

这表示在 default 状态下，设备的引脚配置将使用 pinctrl_hog_1 和 pinctrl_hog_2 两个节点中定义的配置。这种方式可以将多个引脚控制器的配置组合在一起，以满足特定状态下的引脚需求。

## 17.4 pinctl 服务端

服务端是设备树中定义引脚配置的部分。它包含引脚组和引脚描述符，为客户端提供引脚配置选择。服务端在设备树中定义了 pinctrl 节点，其中包含引脚组和引脚描述符的定义。

这里以瑞芯微的 RK3568 为例进行 pinctrl 服务端的讲解，瑞芯微原厂 BSP 工程师为了方便用户通过 pinctrl 设置管脚的复用关系，将包含所有复用关系的配置写在了内核目录下的“arch/arm64/boot/dts/rockchip/rk3568-pinctrl.dtsi”设备树中，具体内容如下

![image-20240715204535145](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715204535145.png)

在 pinctrl 节点中就是每个节点的复用功能，然后我们以 uart4 的引脚复用为例进行讲解，uart4 的 pinctrl 服务端内容如下

![image-20240715204549419](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715204549419.png)

其中<3 RK_PB1 4 &pcfg_pull_up>和<3 RK_PB2 4 &pcfg_pull_up>分别表示将 GPIO3 的 PB1 引脚设置为功能 4，将 GPIO3 的 PB2 也设置为功能 4，且电器属性都会设置为上拉。

最后来看客户端对 uart4 服务端的引用，具体内容在内核源码目录“arch/arm64/boot/dts/rockchip/rk3568-evb1-ddr4-v10-linux.dts”

![image-20240715204733566](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715204733566.png)

通过在客户端中引用服务端的引脚描述符，设备树可以将客户端和服务端的引脚配置关联起来。这样，在设备树被解析和处理时，操作系统和设备驱动程序可以根据客户端的需求，查找并应用适当的引脚配置。

> 查看引脚复用情况：
>
> cat /sys/kernel/debug/pinctrl/pinctrl-rockchip-pinctrl/pinmux-pins

<a id="part-36"></a>

## 17.5 sysfs 文件系统控制 GPIO

GPIO 软件编程方式有多种，可以写驱动程序调用 GPIO 函数操作 GPIO，也可以直接通过操作寄存器的方式操作 GPIO，还可以通过 sysfs 方式实现对 GPIO 的控制。本章节我们来学习使用 sysfs 方式实现对 GPIO 的控制。

使用 sysfs 方式控制 gpio，首先需要底层驱动的支持，需要在 make menuconfig 图形化配置

界面中加入以下配置：

> Device Drivers
>
> ->GPIO Support
>
> ->/sys/class/gpio/xxxx

![image-20240715205459223](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715205459223.png)

sysfs 控制接口为/sys/class/gpio/export 和/sys/class/gpio/unexport。

![image-20240715205522041](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715205522041.png)

/sys/class/gpio/export 用 于 将 GPIO 控 制 从 内 核 空 间 导 出 到 用 户 空 间 。/sys/class/gpio/unexport 用于取消 GPIO 控制从内核空间到用户空间的导出。 export 和unexport，他们都是只写的。GpiochipX 代表 GPIO 控制器。

**export**：用于将指定编号的 GPIO 引脚导出。在使用 GPIO 引脚之前，需要将其导出，导出成功之后才能使用它。注意 export 文件是只写文件，不能读取，将一个指定的编号写入到 export 文件中即可将对应的 GPIO 引脚导出，以 GPIO0_PB7 为例（pin 计算值为 15）使用 export 文件进行导出(如果没有更换本章开始部分的内核设备树镜像，会导出不成功)，导出成功如下图所示：

![image-20240715205556494](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715205556494.png)

会发现在/sys/class/gpio 目录下生成了一个名为 gpio15 的文件夹（gpioX，X 表示对应的编 号），该文件夹就是导出来的 GPIO 引脚对应的文件夹，用于管理、控制该 GPIO 引脚。

**unexport**：将导出的 GPIO 引脚删除。当使用完 GPIO 引脚之后，需要将导出的引脚删除，同样该文件也是只写文件、不可读，使用 unexport 文件进行删除 GPIO0_PB7，删除成功如下图所示：

![image-20240715205623971](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715205623971.png)

可以看到之前生成的 gpio15 文件夹就会消失！

**需要注意的是，并不是所有 GPIO 引脚都可以成功导出，如果对应的 GPIO 已经被导出或者在内核中被使用了，那便无法成功导出，**导出失败如下图所示：

![image-20240715205646887](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715205646887.png)

出现上图报错的原因是该 GPIO 已经被其他 GPIO 使用，需要在内核中找到使用 GPIO 的驱动，并取消该驱动才可以正常使用 GPIO。在使用 GPIO15 时，需要取消 Linux 内核源码中LED 灯的配置，如下所示：

![image-20240715205705709](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715205705709.png)

再次使用以下命令导出 GPIO0_PB7 引脚，导出成功之后进入 gpio15 文件夹

可以看到 gpio15 文件夹下分别有 active_low、device、direction、edge、power、subsystem、uevent、value 八个文件，需要关心的文件是 active_low、direction、edge 以及 value 这四个属性文件，接下来分别介绍这四个属性文件的作用：

**direction**：配置 GPIO 引脚为输入或输出模式。该文件可读、可写，读表示查看 GPIO 当前是输入还是输出模式，写表示将 GPIO 配置为输入或输出模式；读取或写入操作可取的值为"out"（输出模式）和"in"（输入模式）。

在“/sys/class/gpio/gpio15”目录下使用 cat 命令查看 direction 输入输出模式

默认状态下的输入输出状态为“in”,由于 direction 为可读可写，可以使用以下命令将模式

配置为输出，配置完成如下

> echo out > direction
>
> cat direction

**active_low**：用于控制极性得属性文件，可读可写，默认情况下为 0，使用 cat 命令进行文件内容的查看，如下图

>  cat active_low

当 active_low 等于 0 时， value 值若为 1 则引脚输出高电平，value 值若为 0 则引脚输出低电平。当 active_low 等于 1 时 ，value 值若为 0 则引脚输出高电平，value 值若为 1 则引脚输出低电平。

**edge**：控制中断的触发模式，该文件可读可写。在配置 GPIO 引脚的中断触发模式之前，需将其设置为输入模式，四种触发模式的设置如下

> 非中断引脚：**echo** "none" **>** edge
>
> 上升沿触发：**echo** "rising" **>** edge
>
> 下降沿触发：**echo** "falling" **>** edge
>
> 边沿触发： **echo** "both" **>** edge

**value:** 设置高低电平，如果我们要把这个管脚设置成高电平，我们只需要给 value 设置成 1即可，反之，则设置成 0。

## 17.6 GPIO 子系统 API 函数控制GPIO

在目前的 Linux 内核主线中，GPIO（通用输入/输出）子系统存在两个版本，这里将两个版本区分为新版本和旧版本。新版本 GPIO 子系统接口是基于描述符（descriptor-based）来实现的，而旧版本的 GPIO 子系统接口是基于整数（integer-based）来实现的，在 Linux 内核中为了保持向下的兼容性，旧版本的接口在最新的内核版本中仍然得到支持，而随着时间的推移，新版本的 GPIO 子系统接口会越来越完善，最终完全取代旧版本，所以在本课程中主要讲解新版本的 GPIO 子系统接口。

新的 GPIO 子系统接口需要与与设备树（Device Tree）结合使用。使用设备树和新的 GPIO接口可以更加灵活地配置和管理系统中的 GPIO 资源，提供了更好的可扩展性和可移植性。所以如果没有设备树，就无法使用新的 GPIO 接口。

那要如何对新旧 GPIO 子系统接口进行区分呢，一个明显的区别是新的 GPIO 子系统接口使用了以 "gpiod_"作为前缀的函数命名约定，而旧的 GPIO 子系统接口使用了以"gpio_"作为前缀的函数命名约定。

新的 GPIO 子系统接口是基于描述符（descriptor-based）来实现的，由 struct gpio_desc 结构体来表示，该结构体定义在内核源码的“drivers/gpio/gpiolib.h”目录下。

```shell
struct gpio_desc {
  struct gpio_device gdev; // GPIO 设备结构体
  unsigned long flags; // 标志位，用于表示不同的属性
  /* 标志位符号对应的位号 */
  #define FLAG_REQUESTED 0 // GPIO 已请求
  #define FLAG_IS_OUT 1 // GPIO 用作输出
  #define FLAG_EXPORT 2 // 受 sysfs_lock 保护的导出标志
  #define FLAG_SYSFS 3 // 通过/sys/class/gpio/control 导出的标志
  #define FLAG_ACTIVE_LOW 6 // GPIO 值为低电平时激活
  #define FLAG_OPEN_DRAIN 7 // GPIO 为开漏类型
  #define FLAG_OPEN_SOURCE 8 // GPIO 为开源类型
  #define FLAG_USED_AS_IRQ 9 // GPIO 连接到中断请求（IRQ）
  #define FLAG_IS_HOGGED 11 // GPIO 被独占占用
  #define FLAG_TRANSITORY 12 // GPIO 在休眠或复位时可能失去值
  /* 连接标签 */
  const char *label; // GPIO 的名称
  const char *name; // GPIO 的名称
};
```

> （1）struct gpio_device gdev 是一个 struct gpio_device 类型的字段，用于表示 GPIO 设备的相关信息。struct gpio_device 结构体通常包含设备的底层硬件控制器等信息。
>
> （2）unsigned long flags:用于表示 GPIO 的标志位，以表示不同的属性。通过使用位操作，每个标志位可以单独设置或清除。
>
> （3）第 5-14 行用于表示不同标志位的符号常量，与 flags 字段中的位号相对应。例如，在 flags 字段中的第 0 位表示FLAG_REQUESTED，第 1 位表示 FLAG_IS_OUT，以此类推
>
> （4）const char *label: 这是一个指向字符串的指针，表示 GPIO 的标签或名称。
>
> （5）const char *name: 这是一个指向字符串的指针，表示 GPIO 的名称

上面需要重点关注的是然后 struct gpio_device 结构体，该结构体同样定义在内核源码的“drivers/gpio/gpiolib.h”目录下，具体内容如下所示：

```c
struct gpio_device {
  int id; // GPIO 设备 ID
  struct device *dev; // 对应的设备结构体指针
  struct cdev chrdev; // 字符设备结构体
  struct device *mockdev; // 模拟设备结构体指针
  struct module *owner; // 拥有该 GPIO 设备的内核模块指针
  struct gpio_chip *chip; // 对应的 GPIO 芯片结构体指针
   struct gpio_desc *descs; // GPIO 描述符数组指针
  int base; // GPIO 编号的起始值
  u16 ngpio; // GPIO 的数量
  const char *label; // GPIO 设备的标签
  void *data; // 与 GPIO 设备相关的数据指针
  struct list_head list; // 用于将 GPIO 设备结构体连接到链表中
#ifdef CONFIG_PINCTRL
  /*
  * 如果启用了 CONFIG_PINCTRL 选项，GPIO 控制器可以选择描述它们在 SoC 中服务的实际引脚范围。
  * 此信息将由 pinctrl 子系统用于配置相应的 GPIO 引脚。
  */
  struct list_head pin_ranges; // 描述 GPIO 控制器引脚范围的链表
#endif
};
```

该结构体是用来描述 GPIO 设备的数据结构，关于该结构体的参数介绍如下所示：

> （1）int id:整型字段，表示 GPIO 设备的 ID。每个 GPIO 设备可以有一个唯一的 ID。
>
> （2）struct device *dev:指向 struct device 的指针，表示与 GPIO 设备相关联的设备结构体。
>
> （3）struct cdev chrdev: 字符设备结构体，用于实现 GPIO 设备的字符设备接口。
>
> （4）struct device *mockdev: 指向 struct device 的指针，用于表示 GPIO 设备的模拟设备结构体。
>
> （5）struct module *owner: 指向拥有该 GPIO 设备的内核模块的指针。
>
> （6）struct gpio_chip *chip: 指向 struct gpio_chip 的指针，表示与 GPIO 设备关联的 GPIO 芯片（GPIO 控制器）结构体。
>
> （7）struct gpio_desc *descs: 指向 struct gpio_desc 数组的指针，表示与 GPIO 设备关联的 GPIO 描述符。每个 GPIO 描述符用于描述 GPIO 的属性和状态。
>
> （8）int base: 表示 GPIO 编号的起始值。
>
> （9）u16 ngpio: 16 位无符号整型字段，表示 GPIO 的数量。
>
> （10）const char *label: 指向字符串的指针，表示 GPIO 设备的标签或名称。
>
> （11）void *data: 指向与 GPIO 设备相关的数据的指针，用于存储和访问与 GPIO 设备相关的自定义数据。
>
> （12）struct list_head list: 将 GPIO 设备结构体连接到链表中的字段，用于管理多个 GPIO 设备的列表。
>
> （13）struct list_head pin_ranges (仅在启用 CONFIG_PINCTRL 选项时存在): 用于描述 GPIO 控制器引脚范围的链表。如果配置了 GPIO 控制器的引脚范围，该链表将包含描述每个范围的元素。

在上面一系列的参数中，要重点关注的是 struct gpio_chip *chip 这一结构体，表示与 GPIO 设备关联的 GPIO 芯片（GPIO 控制器）结构体，该结构体定义在内核源码目录下的“include/linux/gpio/driver.h”文件中，

```c
struct gpio_chip {
  const char *label; // GPIO 芯片标签
  struct gpio_device gpiodev; // GPIO 设备
  struct device *parent; // 父设备指针
  struct module *owner; // 拥有者模块指针
  int (*request)(struct gpio_chip *chip, unsigned offset);// 请求 GPIO
  void (*free)(struct gpio_chip *chip, unsigned offset); // 释放 GPIO
  int (*get_direction)(struct gpio_chip *chip, unsigned offset); // 获取 GPIO 方向
  int (*direction_input)(struct gpio_chip *chip, unsigned offset); // 设置 GPIO 为输入
  int (*direction_output)(struct gpio_chip *chip, unsigned offset, int value); // 设置 GPIO 为输出
  int (*get)(struct gpio_chip chip, unsigned offset); // 获取 GPIO 值
  int (*get_multiple)(struct gpio_chip chip, unsigned long *mask, unsigned long *bits); // 获取多个 GPIO 的值
  void (*set)(struct gpio_chip chip, unsigned offset, int value); // 设置 GPIO 值
  void (*set_multiple)(struct gpio_chip chip, unsigned long mask, unsigned long *bits); // 设置多个 GPIO的值
  int (*set_config)(struct gpio_chip *chip, unsigned offset, unsigned long config); // 设置 GPIO 配置
  int (*to_irq)(struct gpio_chip chip, unsigned offset); // 将 GPIO 转换为中断
  void (*dbg_show)(struct seq_file *s, struct gpio_chip chip); // 在调试信息中显示 GPIO
  int base; // GPIO 编号的基准值
  u16 ngpio; // GPIO 的数量
  const char *const *names; // GPIO 的名称数组
	.......... 
};
```

struct gpio_chip *chip 这一结构体用于描述 GPIO 芯片的属性和操作函数，可以通过函数指针调用相应的函数来请求、释放、设置、获取 GPIO 的状态和数值等操作，从而实现对 GPIO 的控制和管理，需要注意的是这个结构体中的一系列函数都不需要我们来填充，这些工作都是由芯片原厂工程师来完成的，我们只需要学会新 gpio 子系统相应 API 函数的使用即可。

### 17.6.1 相关函数

**获取** **GPIO** **描述符**

struct gpio_desc *gpiod_get 是 Linux 内核中用于获取 GPIO 描述符的函数。下面是对该函数的详细介绍：

> **函数原型：**
>
> struct gpio_desc *__must_check gpiod_get(struct device *dev,const char *con_id,enum gpiod_flags flags);
>
> **头文件：**
>
> \#include <linux/gpio/consumer.h>
>
> **参数：**
>
> dev：指向设备结构体的指针，表示与 GPIO 相关联的设备。
>
> con_id：连接标识符（connection identifier），用于标识所需的 GPIO 连接。通常由设备树（Device Tree）或其他设备描述信息定义
>
> flags 属于 `enum gpiod_flags`：
>
> - `GPIOD_ASIS`：保留当前方向与值。
> - `GPIOD_IN`：输入。
> - `GPIOD_OUT_LOW` / `GPIOD_OUT_HIGH`：输出，初始化为逻辑 0 / 1。
> - `GPIOD_OUT_LOW_OPEN_DRAIN` / `GPIOD_OUT_HIGH_OPEN_DRAIN`：上述输出状态并要求开漏。
>
> `GPIO_ACTIVE_LOW` 来自设备树等映射信息，不是此处的 GPIOF_* 标志。逻辑值与实际电平的关系受 active-low 配置影响。










>
> **函数功能：**
>
> 获取与给定设备和连接标识符（con_id）相关联的 GPIO 描述符。
>
> **返回值：**
>
> 成功返回描述符；失败返回 `ERR_PTR(-errno)`，必须用 `IS_ERR()` 判断、用 `PTR_ERR()` 取错误码，不能只判断 NULL。

在 Linux 内核中还有另外三个同样是获取 GPIO 描述符资源的函数，三个函数内容如下所示：

> struct gpio_desc *****gpiod_get_index**(**struct device *****dev**,** const char *****con_id**,** unsigned int idx**,** enum gpiod_flags flags**);**
>
> struct gpio_desc *****gpiod_get_optional**(**struct device *****dev**,** const char *****con_id**,** enum gpiod_flags flags**);**
>
> struct gpio_desc *****gpiod_get_index_optional**(**struct device *****dev**,** const char *****con_id**,** unsigned int index**,** enum gpiod_flags flags**);**

带 index 的 API 用于选择同一 GPIO 属性中的第几个引脚。optional API 仅在没有指定该 GPIO 时返回 NULL；实际获取失败仍返回 ERR_PTR，包括应向上传递的 `-EPROBE_DEFER`。不带 optional 的版本在缺少必需 GPIO 时也返回错误指针。





**释放** **GPIO** **描述符**

gpiod_put() 函数是 Linux 内核中用于释放 GPIO 描述符资源的函数。下面是对该函数的详细介绍：

> **函数原型：**
>
> void gpiod_put(struct gpio_desc *desc);
>
> **头文件：**
>
> \#include <linux/gpio/consumer.h>
>
> **参数：**
>
> desc：指向要释放的 GPIO 描述符的指针。
>
> **功能：**
>
> gpiod_put() 函数用于释放之前通过 gpiod_get() 或类似函数获取的 GPIO 描述符。
>
> **返回值：**
>
> 无返回值。

### 17.6.2 实验

新版本的 gpio 子系统 api 接口要与设备树结合才能使用，所以需要在设备树中将用于获取 GPIO 描述符的引脚复用为 GPIO 模式。为了让教程更贴近于实战，这里选择 RK3568 开发板背面 20Pin GPIO 座子的 1 号引脚，右边对应的丝印为 I2C3_SDA_M0，这里的丝印表示该引脚可以复用为 I2C3 的 SDA 功能，而在当前的设备树源码中这个引脚是没有任何复用的，该引脚的具体位置如下所示：

![image-20240715211133757](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715211133757.png)

在前面 pinctrl 的章节中已经学习了如何将一个管脚复用为 GPIO，首先我们需要确定该引脚的 GPIO 编号，来到 RK3568 开发板的底板原理图，找到 J39 GPIO 底座，如下图所示：

![image-20240715211156822](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715211156822.png)

可以看到 1 号管脚的网络标号为 I2C3_SDA_M0，然后打开核心板原理图，根据这个网络标号进行搜索，查找到的核心板内容如下所示：

![image-20240715211216804](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240715211216804.png)

左侧为该引脚的一些复用功能，箭头指向的部分为接下来要用到的 GPIO 引脚编号 GPIO1_ A0，然后对设备树进行内容的添加，从而将该引脚复用为 GPIO 的功能。

首先根据上图中的复用功能查看设备树中是否已经对该引脚进行了复用，在确保该引脚无任何复用之后，对 rk3568-evb1-ddr4-v10.dtsi 设备树进行内容的添加，在根节点的结尾添加以下内容

```
my_gpio:gpiol_a0 {
  compatible = "mygpio";
  my-gpios = <&gpio1 RK_PA0 GPIO_ACTIVE_HIGH>;
  pinctrl-names = "default";
  pinctrl-0 = <&my_gpio_ctrl>;
};
```

compatible: 用于指定设备的兼容性字符串，与驱动程序中的值相匹配。

my-gpios 的 &gpio1 指向 GPIO 控制器，RK_PA0 是该 bank 内的引脚编号，GPIO_ACTIVE_HIGH 表示逻辑有效态对应物理高电平；它不等于设置上电默认电平。输出初值还需由方向/初始化配置决定。

pinctrl-names 和 pinctrl-0: 用于指定引脚控制器（pinctrl）的配置。pinctrl-names 表示引脚控制器配置的名称，这里为 "default"。pinctrl-0 指定了与该配置相关联的引脚控制器句柄，这里为 &mygpio_ctrl。

然后找到 pinctrl 节点，在节点尾部添加以下内容，

```
mygpio {
  my_gpio_ctrl: my-gpio-ctrl {
  	rockchip,pins = <1 RK_PA0 RK_FUNC_GPIO &pcfg_pull_none>;
  };
};
```

rockchip,pins 的四个字段分别为 bank 编号 1、bank 内引脚 RK_PA0、复用功能 RK_FUNC_GPIO、引脚配置 &pcfg_pull_none。

至此，关于设备树相关的修改就完成了，保存退出之后，编译内核，然后将生成的 boot.img镜像烧写到开发板上即可。

驱动代码

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/mod_devicetable.h>
#include <linux/gpio/consumer.h>

struct gpio_desc *mygpio1;  // GPIO 描述符指针
struct gpio_desc *mygpio2;  // GPIO 描述符指针
int num;  // GPIO 编号

//平台设备初始化函数
// 平台设备初始化函数
static int my_platform_probe(struct platform_device *dev)
{
    printk("This is my_platform_probe\n");

    // 获取可选的GPIO描述符
    mygpio1 = gpiod_get_optional(&dev->dev, "my", 0);
    if (IS_ERR(mygpio1)) return PTR_ERR(mygpio1);
    if (!mygpio1) return -ENOENT;



    num = desc_to_gpio(mygpio1);
    printk("num is %d\n", num);

    // 释放GPIO描述符
    gpiod_put(mygpio1);

    // 获取指定索引的GPIO描述符
    mygpio2 = gpiod_get_index(&dev->dev, "my", 0, 0);
    if (IS_ERR(mygpio2)) {
        printk("gpiod_get_index error\n");
        return -2;
    }
    num = desc_to_gpio(mygpio2);
    printk("num is %d\n", num);

    return 0;
}

// 平台设备的移除函数
static int my_platform_remove(struct platform_device *pdev)
{
    printk(KERN_INFO "my_platform_remove: Removing platform device\n");

    // 清理设备特定的操作
    // ...

    return 0;
}


const struct of_device_id of_match_table_id[]  = {
	{.compatible="mygpio"},
};

// 定义平台驱动结构体
static struct platform_driver my_platform_driver = {
    .probe = my_platform_probe,
    .remove = my_platform_remove,
    .driver = {
        .name = "my_platform_device",
        .owner = THIS_MODULE,
		.of_match_table =  of_match_table_id,
    },
};

// 模块初始化函数
static int __init my_platform_driver_init(void)
{
    int ret;

    // 注册平台驱动
    ret = platform_driver_register(&my_platform_driver);
    if (ret) {
        printk(KERN_ERR "Failed to register platform driver\n");
        return ret;
    }

    printk(KERN_INFO "my_platform_driver: Platform driver initialized\n");

    return 0;
}

// 模块退出函数
static void __exit my_platform_driver_exit(void)
{
    // 注销平台驱动
	gpiod_put(mygpio2);
    platform_driver_unregister(&my_platform_driver);

    printk(KERN_INFO "my_platform_driver: Platform driver exited\n");
}

module_init(my_platform_driver_init);
module_exit(my_platform_driver_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("woniu");
```

### 17.6.3 GPIO 操作函数

**获取** **GPIO** **的方向**

> （1）函数原型：
> int gpiod_get_direction(struct gpio_desc *desc);
> （2）头文件：
> #include <linux/gpio/consumer.h>
> （3）参数：
> desc：指向 GPIO 描述符的指针。
> （4）函数功能：
> gpiod_get_direction 函数用于获取 GPIO 的方向，即判断 GPIO 是输入还是输出。
> （5）返回值：
> 成功返回 0 表示输出、1 表示输入；失败返回负 errno。不要把 libgpiod 用户态枚举常量套用于内核 gpiod_get_direction。

该函数的作用是获取给定 GPIO 描述符所代表的 GPIO 的方向。通过该函数，可以确定 GPIO是配置为输入还是输出。返回值可以用于进一步判断和处理 GPIO 的方向相关逻辑。

**配置** **GPIO** **的方向**

> （1）函数原型：
> int gpiod_direction_input(struct gpio_desc *desc);
> int gpiod_direction_output(struct gpio_desc *desc, int value);
> （2）头文件：
> #include <linux/gpio/consumer.h>
> （3）参数：
> desc：指向 GPIO 描述符的指针。
> value 是初始逻辑值 0/1，受 active-low 映射影响；需要直接控制物理值时区分 raw API。
> （4）函数功能：
> gpiod_direction_input 函数用于配置 GPIO 的方向为输入。
> gpiod_direction_output 函数用于配置 GPIO 的方向为输出，并可指定初始输出值。
> （5）返回值：
>
> 返回值为整型，表示配置 GPIO 方向的结果。
>
> 如果成功配置 GPIO 方向，返回值为 0。
>
> 如果配置失败，返回值为负数，表示错误码。

这两个函数用于配置 GPIO 的方向。gpiod_direction_input 将给定的 GPIO 描述符所代表的GPIO 配置为输入模式。而 gpiod_direction_output 将 GPIO 配置为输出模式，并可以指定初始输出值。

**读取** **GPIO** **的电平状态**

> （1）函数原型：
> int gpiod_get_value(const struct gpio_desc *desc);
> （2）头文件：
> #include <linux/gpio/consumer.h>
> （3）参数：
> desc：指向 GPIO 描述符的指针。
> （4）函数功能：
> gpiod_get_value 函数用于读取 GPIO 的电平状态。
> （5）返回值：
> 返回值为整型，表示 GPIO 的电平状态。
> 如果成功读取到 GPIO 的电平状态，返回值为 0 或 1，分别表示低电平和高电平。
> 如果读取失败，返回值为负数，表示错误码。

该函数用于读取给定 GPIO 描述符所代表的 GPIO 的电平状态。通过调用该函数，可以获取 GPIO 当前的电平状态，以便进一步处理和判断 GPIO 的状态。

**设置** **GPIO** **的电平状态**

> （1）函数原型：
> void gpiod_set_value(struct gpio_desc *desc, int value);
> （2）头文件：
> #include <linux/gpio/consumer.h>
> （3）参数：
> desc：指向 GPIO 描述符的指针。
> value：要设置的 GPIO 的电平状态，可以是 0 或 1。
> （4）函数功能：
> gpiod_set_value 函数用于设置 GPIO 的电平状态。
> （5）返回值：无（void）
> 该函数用于设置给定 GPIO 描述符所代表的 GPIO 的电平状态。通过调用该函数，您可以将 GPIO设置为特定的电平状态，以便控制外部设备或执行其他相关操作

value 参数表示要设置的 GPIO 的电平状态，可以是 0 或 1。当 value 为 0 时，表示设置GPIO 为低电平；当 value 为 1 时，表示设置 GPIO 为高电平。该函数没有返回值，因为它只是执行设置操作而不需要返回任何结果。在使用该函数之前，需要确保 GPIO 已经被正确地配置为输出模式。

**将** **GPIO** **描述符转换为中断编号**

> （1）函数原型：
> int gpiod_to_irq(const struct gpio_desc *desc);
> （2）头文件：
> #include <linux/gpio/consumer.h>
> （3）参数：
> desc：指向 GPIO 描述符的指针。
> （4）函数功能：
> gpiod_to_irq 函数用于将 GPIO 描述符转换为中断号。
> （5）返回值：
> 返回值为整型，表示中断号。
> 如果成功将 GPIO 描述符转换为中断号，返回值为大于等于 0 的中断号。
> 如果转换失败，返回值为负数，表示错误码。

该函数用于将给定 GPIO 描述符所代表的 GPIO 转换为对应的中断号。

### 17.6.4 实验

```c
#include <linux/module.h>
#include <linux/platform_device.h>
#include <linux/mod_devicetable.h>
#include <linux/gpio/consumer.h>

struct gpio_desc *mygpio1;  // GPIO 描述符指针
struct gpio_desc *mygpio2;  // GPIO 描述符指针
int num;  // GPIO 编号

//平台设备初始化函数
static int my_platform_probe(struct platform_device *dev)
{
    printk("This is mydriver_probe\n");

    mygpio1 = gpiod_get_optional(&dev->dev, "my", 0);
    if (mygpio1 == NULL) {
        printk("gpiod_get_optional error\n");
        return -1;
    }
    num = desc_to_gpio(mygpio1);
    printk("num is %d\n", num);

    gpiod_put(mygpio1);

    mygpio2 = gpiod_get_index(&dev->dev, "my", 0, 0);
    if (IS_ERR(mygpio2)) {
        printk("gpiod_get_index error\n");
        return -2;
    }
    num = desc_to_gpio(mygpio2);
    printk("num is %d\n", num);

    return 0;
}

// 平台设备的移除函数
static int my_platform_remove(struct platform_device *pdev)
{
    printk(KERN_INFO "my_platform_remove: Removing platform device\n");

    // 清理设备特定的操作
    // ...

    return 0;
}


const struct of_device_id of_match_table_id[]  = {
	{.compatible="mygpio"},
};

// 定义平台驱动结构体
static struct platform_driver my_platform_driver = {
    .probe = my_platform_probe,
    .remove = my_platform_remove,
    .driver = {
        .name = "my_platform_device",
        .owner = THIS_MODULE,
		.of_match_table =  of_match_table_id,
    },
};

// 模块初始化函数
static int __init my_platform_driver_init(void)
{
    int ret;

    // 注册平台驱动
    ret = platform_driver_register(&my_platform_driver);
    if (ret) {
        printk(KERN_ERR "Failed to register platform driver\n");
        return ret;
    }

    printk(KERN_INFO "my_platform_driver: Platform driver initialized\n");

    return 0;
}

// 模块退出函数
static void __exit my_platform_driver_exit(void)
{
    // 注销平台驱动
	gpiod_put(mygpio2);
    platform_driver_unregister(&my_platform_driver);

    printk(KERN_INFO "my_platform_driver: Platform driver exited\n");
}

module_init(my_platform_driver_init);
module_exit(my_platform_driver_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("woniu");
```

---

[总目录](总目录.md) · [上一篇：设备树](16-%E8%AE%BE%E5%A4%87%E6%A0%91.md) · [下一篇：I2C子系统](18-I2C%E5%AD%90%E7%B3%BB%E7%BB%9F.md)
