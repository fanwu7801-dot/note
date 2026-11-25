# 13-中断与Tasklet及线程化处理

[总目录](总目录.md) · [上一篇：并发与IO](12-%E5%B9%B6%E5%8F%91%E4%B8%8EIO.md) · [下一篇：工作队列与内核定时器](14-%E5%B7%A5%E4%BD%9C%E9%98%9F%E5%88%97%E4%B8%8E%E5%86%85%E6%A0%B8%E5%AE%9A%E6%97%B6%E5%99%A8.md)

> 版本基线：Linux 6.1，面向 RK SDK。保留已完成的接口勘误；源码摘录与板级资源仍需对照实际 SDK。构建和适配说明见 [Linux 6.1 适配说明](整理记录/Linux6.1适配说明.md)。

[TOC]

<a id="part-26"></a>

## 13.1 介绍

中断的执行需要快速响应，但并不是所有中断都能迅速完成。此外，Linux 中的中断不支持嵌套，意味着在正式处理中断之前会屏蔽其他中断，直到中断处理完成后再重新允许接收中断，如果中断处理时间过长，将会引发问题。

而为了让系统可以更好地处理中断事件，提高实时性和响应能力，将中断服务程序划分为上下文两部分：

中断上文是中断服务程序的第一部分，它主要处理一些紧急且需要快速响应的任务。中断上文的特点是执行时间较短，旨在尽快完成对中断的处理。这些任务可能包括保存寄存器状态、更新计数器等，以便在中断处理完成后能够正确地返回到中断前的执行位置。

中断下文是中断服务程序的第二部分，它主要处理一些相对耗时的任务。由于中断上文需要尽快完成，因此中断下文负责处理那些不能立即完成的、需要更多时间的任务。这些任务可能包括复杂的计算、访问外部设备或进行长时间的数据处理等。

### 13.1.1 中断子系统框架

一个完整的中断子系统框架可以分为四个层次，由上到下分别为用户层、通用层、硬件相关层和硬件层，每个层相关的介绍如下

> **用户层：**用户层是中断的使用者，主要包括各类设备驱动。这些驱动程序通过中断相关的接口进行中断的申请和注册。当外设触发中断时，用户层驱动程序会进行相应的回调处理，执行特定的操作。
>
> **通用层：**通用层也可称为框架层，它是硬件无关的层次。通用层的代码在所有硬件平台上都是通用的，不依赖于具体的硬件架构或中断控制器。通用层提供了统一的接口和功能，用于管理和处理中断，使得驱动程序能够在不同的硬件平台上复用。
>
> **硬件相关层：**硬件相关层包含两部分代码。一部分是与特定处理器架构相关的代码，比如ARM64 处理器的中断处理相关代码。这些代码负责处理特定架构的中断机制，包括中断向量表、中断处理程序等。另一部分是中断控制器的驱动代码，用于与中断控制器进行通信和配置。这些代码与具体的中断控制器硬件相关。
>
> **硬件层：**硬件层位于最底层，与具体的硬件连接相关。它包括外设与 SoC（系统片上芯片）的物理连接部分。中断信号从外设传递到中断控制器，由中断控制器统一管理和路由到处理器。硬件层的设计和实现决定了中断信号的传递方式和硬件的中断处理能力。

![image-20240709194651250](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240709194651250.png)

### 13.1.2 中断控制器 GIC

ARM GIC：

    GIC是ARM架构中的一部分，用于处理来自多个源的中断请求，并将其分发到多个处理器核心。
    GIC设计用于多核处理器系统，能够支持多个中断源和多个处理器核心之间的中断管理。
    GIC分为不同的版本，如GICv1（已弃用）、GICv2、GICv3和GICv4，每个版本都支持不同的中断处理特性和系统规模。
    GICv3引入了属性层次（affinity hierarchies），以支持更多的核心，并且增加了redistributor组件和LPI（Locality-Partitioned Interrupts）来处理消息中断。
    GIC通常集成在系统级芯片（SoC System On Chip）中，与CPU核心紧密集成，提供高效的中断处理。

NVIC：

    NVIC是Cortex-M系列微控制器中的中断控制器，专为单核或简单的多核系统设计。
    NVIC提供了中断优先级设置，支持抢占式和子优先级，允许中断嵌套。
    NVIC通常与Cortex-M内核紧密集成，提供快速的中断响应和处理。
    NVIC支持有限数量的中断源，适合中低端的微控制器应用，而不是为大型多核系统设计的。
    NVIC的设计相对简单，易于在微控制器中实现，通常用于嵌入式系统和简单的控制应用。
中断控制器 GIC（Generic Interrupt Controller）是中断子系统框架硬件层中的一个关键组件，用于管理和控制中断。它接收来自各种中断源的中断请求，并根据预先配置的中断优先级、屏蔽和路由规则，将中断请求分发给适当的处理器核心或中断服务例程。

GIC 是由 ARM 公司提出设计规范，当前有四个版本，GIC V1-v4。设计规范中最常用的，有3 个版本 V2.0、V3.1、V4.1，GICv3 版本设计主要运行在 Armv8-A, Armv9-A 等架构上。ARM 公司并给出一个实际的控制器设计参考，比如 GIC-400(支持 GIC v2 架构)、gic500(支持 GIC v3 架构)、GIC-600(支持 GIC v3 和 GIC v4 架构)。最终芯片厂商可以自己实现 GIC 或者直接购买 ARM提供的设计。

每个 GIC 版本及相应特性如下:

| 版本  | 关键特性                                                     | 常用核心                                                     |
| ----- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| GICv1 | -支持最多八个处理器核心（PE）<br />\- 支持最多 1020 个中断 ID | ARM Cortex-A5 MPCore<br/>ARM Cortex-A9 MPCore<br/>ARM Cortex-R7 MPCore |
| GICv2 | \- GICv1 的所有关键特性<br />-支持虚拟化                     | ARM Cortex-A7 MPCore<br/>ARM Cortex-A15 MPCore<br/>ARM Cortex-A53 MPCore<br/>ARM Cortex-A57 MPCore |
| GICv3 | - GICv2 的所有关键特性<br/>-支持超过 8 个处理器核心<br/>-支持基于消息的中断<br/>-支持超过 1020 个中断 ID<br/>- CPU 接口寄存器的系统寄存器访问<br/>-增强的安全模型，分离安全和非安全的 Group 1 中断 | ARM Cortex-A53MPCore<br/>ARM Cortex-A57MPCore<br/>ARM Cortex-A72 MPCore |
| GICv4 | - GICv3 的所有关键特性<br/>-虚拟中断的直接注入               | ARM Cortex-A53 MPCore<br/>ARMCortex-A57MPCore<br/>ARM Cortex-A72 MPCore |

在 RK3568 上使用的 GIC 版本为 GICv3，相应的中断控制器模型如下

![image-20240709195141278](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240709195141278.png)

GIC 中断控制器可以分为 Distributor 接口、Redistributor 接口和 CPU 接口，下面是每个部分的说明

**Distributor** **中断仲裁器：**

> 包含影响所有处理器核心中断的全局设置。包含以下编程接口：
>
> ●启用和禁用 SPI。
>
> ●设置每个 SPI 的优先级级别。
>
> ●每个 SPI 的路由信息。
>
> ●将每个 SPI 设置为电平触发或边沿触发。
>
> ●生成基于消息的 SPI。
>
> ●控制 SPI 的活动和挂起状态。
>
> ●用于确定在每个安全状态中使用的程序员模型的控制（亲和性路由或遗留模型）。

**Redistributor** **重新分配器**

> 对于每个连接的处理器核心（PE），都有一个重新分配器（Redistributor）。重新分配器提供以下编程接口：
>
> ●启用和禁用 SGI（软件生成的中断）和 PPI（处理器专用中断）。
>
> ●设置 SGI 和 PPI 的优先级级别。
>
> ●将每个 PPI 设置为电平触发或边沿触发。
>
> ●将每个 SGI 和 PPI 分配给一个中断组。
>
> ●控制 SGI 和 PPI 的状态。
>
> ●对支持关联 LPI（Locality-specific Peripheral Interrupt）的中断属性和挂起状态的内存中的数据结构进行基址控制。
>
> ●支持与连接的处理器核心的电源管理。

**CPU** **接口**

>每个重新分配器都连接到一个 CPU 接口。CPU 接口提供以下编程接口：
>
>●通用控制和配置，用于启用中断处理。
>
>●确认中断。
>
>●执行中断的优先级降低和停用。
>
>●为处理器核心设置中断优先级屏蔽。
>
>●定义处理器核心的抢占策略。
>
>●确定处理器核心最高优先级的挂起中断。

### 13.1.3 中断类型

GIC-V3 支持四种类型的中断，分别是 SGI、PPI、SPI 和 LPI，每个中断类型的介绍如下

> SGI（Software Generated Interrupt，软件生成中断）：SGI 是通过向 GIC 中的 SGI 寄存器写入来生成的中断。它通常用于处理器之间的通信，允许一个 PE 发送中断给一个或多个指定的 PE，中断号 ID0 - ID15 用于 SGI。
>
> PPI（Private Peripheral Interrupt，私有外设中断）：针对特定 PE 的外设中断。不与其他 PE共享，中断号 ID16 - ID31 用于 PPI。
>
> SPI（Shared Peripheral Interrupt，共享外设中断）：全局外设中断，可以路由到指定的处理器核心（PE）或一组 PE，它允许多个 PE 接收同一个中断。中断号 ID32 - ID1019 用于 SPI，
>
> LPI（Locality-specific Peripheral Interrupt，特定局部外设中断）：LPI 是 GICv3 中引入的一种中断类型，与其他类型的中断有几个不同之处。LPI 总是基于消息的中断，其配置存储在内存表中，而不是寄存器中。

![image-20240709195611784](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240709195611784.png)

中断处理的状态机如下图

![image-20240709195627693](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240709195627693.png)

> Inactive（非活动状态）：中断源当前未被触发。
>
> Pending（等待状态）：中断源已被触发，但尚未被处理器核心确认。
>
> Active（活动状态）：中断源已被触发，并且已被处理器核心确认。
>
> Active and Pending（活动且等待状态）：已确认一个中断实例，同时另一个中断实例正在等待处理。
>
> 每个外设中断可以是以下两种类型之一：
>
> **边沿触发（**Edge-triggered**）：**
>
> 这是一种在检测到中断信号上升沿时触发的中断，然后无论信号状态如何，都保持触发状态，直到满足本规范定义的条件来清除中断。
>
> **电平触发（**Level-sensitive**）：**
>
> 这是一种在中断信号电平处于活动状态时触发的中断，并且在电平不处于活动状态时取消触发。

### 13.1.4 中断号

在 linux 内核中，我们使用 IRQ number 和 HW interrupt ID 两个 ID 来标识一个来自外设的中断

**IRQ number**：CPU 需要为每一个外设中断编号，我们称之 IRQ Number。这个 IRQ number是一个虚拟的 interrupt ID，和硬件无关，仅仅是被 CPU 用来标识一个外设中断。

**HW interrupt ID**：对于 GIC 中断控制器而言，它收集了多个外设的 interrupt request line 并向上传递，因此，GIC 中断控制器需要对外设中断进行编码。GIC 中断控制器用 HW interrupt ID来标识外设的中断。如果只有一个 GIC 中断控制器，那 IRQ number 和 HW interrupt ID 是可以一一对应的，如下图

![image-20240709195927201](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240709195927201.png)

但如果是在 GIC 中断控制器级联的情况下，仅仅用 HW interrupt ID 就不能唯一标识一个外设中断，还需要知道该 HW interrupt ID 所属的 GIC 中断控制器（HW interrupt ID 在不同的Interrupt controller 上是会重复编码的）。

![image-20240709200116558](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20240709200116558.png)

这样，CPU 和中断控制器在标识中断上就有了一些不同的概念，但是，对于驱动工程师而言，我们和 CPU 视角是一样的，我们只希望得到一个 IRQ number，而不关系具体是那个 GIC中断控制器上的那个 HW interrupt ID。这样一个好处是在中断相关的硬件发生变化的时候，驱动软件不需要修改。因此，linux kernel 中的中断子系统需要提供一个将 HW interrupt ID 映射到IRQ number 上来的机制，也就是 irq domain。

## 13.2 中断api

### 13.2.1 request_irq

request_irq 函数是在 Linux 内核中用于注册中断处理程序的函数。它用于请求一个中断号（IRQ number）并将一个中断处理程序与该中断关联起来。下面是对 request_irq 函数的详细介绍：

> **函数原型：**
>
> int request_irq(unsigned int irq, irq_handler_t handler, unsigned long flags, const char * name, void *dev);
>
> **头文件**：
>
> \#include <linux/interrupt.h>
>
> **函数作用：**
>
> request_irq 函数的主要功能是请求一个中断号，并将一个中断处理程序与该中断号关联起来。当中断事件发生时，与该中断号关联的中断处理程序会被调用执行。
>
> **参数含义：**
>
> irq：要请求的中断号（IRQ number）。
>
> handler：指向中断处理程序的函数指针。
>
> flags：标志位，用于指定中断处理程序的行为和属性，如中断触发方式、中断共享等。
>
> name：中断的名称，用于标识该中断。
>
> dev：指向设备或数据结构的指针，可以在中断处理程序中使用。
>
> 返回值：
>
> 成功：返回 0。
>
> 失败：负数，表示中断请求失败，返回的负数值表示错误代码。

irq 参数用来指定要请求的中断号，中断号需要通过 gpio_to_irq 函数映射 GPIO 引脚来获得（gpio_to_irq 函数接下来会进行介绍）。

irq_handler_t handler 参数是一个函数指针，指向了中断处理程序的函数。中断处理程序是在中断事件发生时调用的函数，用于处理中断事件（关于中断处理程序会在下个小节进行详细的讲解）。

unsigned long flags：中断处理程序的标志位

这个参数用于指定中断处理程序的行为和属性，如中断触发方式、中断共享等。可以使用不同的标志位进行位运算来组合多个属性。常用的标志位包括

> IRQF_TRIGGER_NONE：不显式指定触发类型，沿用固件或已有 IRQ 配置；不代表禁用中断。
>
>IRQF_TRIGGER_RISING：上升沿触发方式，表示中断在信号上升沿时触发。
>
>IRQF_TRIGGER_FALLING：下降沿触发方式，表示中断在信号下降沿时触发。
>
>IRQF_TRIGGER_HIGH：高电平触发方式，表示中断在信号为高电平时触发。
>
>IRQF_TRIGGER_LOW：低电平触发方式，表示中断在信号为低电平时触发。
>
>IRQF_SHARED：中断共享方式，表示中断可以被多个设备共享使用。

### 13.2.2 gpio_to_irq

gpio_to_irq 函数用于将 GPIO 引脚的编号（GPIO pin number）转换为对应的中断请求号（interrupt request number）。

> **函数原型：**
>
> unsigned int gpio_to_irq(unsigned int gpio);
>
> **头文件**：
>
> \#include <linux/gpio.h>
>
> **函数功能：**
>
> gpio_to_irq 是一个用于将 GPIO 引脚映射到对应中断号的函数。它的作用是根据给定的 G
>
> PIO 引脚号，获取与之关联的中断号。
>
> **参数说明：**
>
> gpio：要映射的 GPIO 引脚号。
>
> **返回值：**
>
> 成功：返回值为该 GPIO 引脚所对应的中断号。
>
> 失败：返回值为负数，表示映射失败或无效的 GPIO 引脚号。

### 13.2.3 free_irq

free_irq 函数用于释放之前通过 request_irq 函数注册的中断处理程序。它的作用是取消对中断的注册并释放相关的系统资源。下面是关于该函数的详细解释：

> **函数原型：**
>
> void free_irq(unsigned int irq, void *dev_id);
>
> **头文件：**
>
> \#include <linux/interrupt.h>
>
> **函数功能：**
>
> free_irq 函数用于释放之前通过 request_irq 函数注册的中断处理程序。它会取消对中断的
>
> 注册并释放相关的系统资源，包括中断号、中断处理程序和设备标识等。
>
> **参数说明：**
>
> irq：要释放的中断号。
>
> dev_id：设备标识，用于区分不同的中断请求。它通常是在 request_irq 函数中传递的设备
>
> 特定数据指针。
>
> **返回值：**
>
> free_irq 函数没有返回值。

**中断服务函数**

中断处理程序是在中断事件发生时自动调用的函数。它负责处理与中断相关的操作，例如读取数据、清除中断标志、更新状态等。

### 13.2.4 irqreturn_t handler

irqreturn_t handler(int irq, void *dev_id) 是一个典型的中断服务函数的函数原型。下面对该函数原型及其参数进行详细解释：

> **函数原型：**
>
> irqreturn_t handler(int irq, void *dev_id);
>
> **函数功能：**
>
> handler 函数是一个中断服务函数，用于处理特定中断事件。它在中断事件发生时被操作系统或硬件调用，执行必要的操作来响应和处理中断请求。
>
> **参数说明：**
>
> irq：表示中断号或中断源的标识符。它指示引发中断的硬件设备或中断控制器。
>
> dev_id：是一个 void 类型的指针，用于传递设备特定的数据或标识符。它通常用于在中断处理程序中区分不同的设备或资源。
>
> **返回值：**
>
> irqreturn_t 是一个特定类型的枚举值，用于表示中断服务函数的返回状态。它可以有以下几种取值：
>
> IRQ_NONE：表示中断服务函数未处理该中断，中断控制器可以继续处理其他中断请求。
>
> IRQ_HANDLED：表示中断服务函数已成功处理该中断，中断控制器无需进一步处理。
>
> IRQ_WAKE_THREAD：表示中断服务函数已处理该中断，并且请求唤醒一个内核线程来继续执行进一步的处理。这在一些需要长时间处理的中断情况下使用。

在处理程序中，通常需要注意以下几个方面

> （1）处理程序应该尽可能地快速执行，以避免中断丢失或过多占用 CPU 时间。
>
> （2）如果中断源是共享的，处理程序需要处理多个设备共享同一个中断的情况。
>
> （3）处理程序可能需要与其他部分的代码进行同步，例如访问共享数据结构或使用同步机制来保护临界区域。
>
> （4）处理程序可能需要与其他线程或进程进行通信，例如唤醒等待的线程或发送信号给其他进程。

实验代码

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/gpio.h>
#include <linux/interrupt.h>

#define GPIO_PIN 101

// 中断处理函数
static irqreturn_t gpio_irq_handler(int irq, void *dev_id)
{
    printk(KERN_INFO "Interrupt occurred on GPIO %d\n", GPIO_PIN);
    printk(KERN_INFO "This is irq_handler\n");
    return IRQ_HANDLED;
}

static int __init interrupt_init(void)
{
    int irq_num;

    printk(KERN_INFO "Initializing GPIO Interrupt Driver\n");

    // 将GPIO引脚映射到中断号
    irq_num = gpio_to_irq(GPIO_PIN);
    printk(KERN_INFO "GPIO %d mapped to IRQ %d\n", GPIO_PIN, irq_num);

    // 请求中断
    if (request_irq(irq_num, gpio_irq_handler, IRQF_TRIGGER_RISING, "irq_test", NULL) != 0) {
        printk(KERN_ERR "Failed to request IRQ %d\n", irq_num);

        // 请求中断失败，释放GPIO引脚
        gpio_free(GPIO_PIN);
        return -ENODEV;
    }
    return 0;
}

static void __exit interrupt_exit(void)
{
    int irq_num = gpio_to_irq(GPIO_PIN);

    // 释放中断
    free_irq(irq_num, NULL);
    printk(KERN_INFO "GPIO Interrupt Driver exited successfully\n");
}

module_init(interrupt_init);
module_exit(interrupt_exit);

MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("woniu");
```

## 13.3 中断申请流程

### 13.3.1 request_irq 函数

中断申请使用的是 request_irq 函数，它用于请求一个中断号（IRQ number）并将一个中断处理程序与该中断关联起来，它定义在内核源码的“/include/linux/interrupt.h”目录下，具体定义如下所示：

```c
request_irq(unsigned int irq, irq_handler_t handler, unsigned long flags, const char *name, void *dev)
{
	return request_threaded_irq(irq, handler, NULL, flags, name, dev);
}
```

从上面的内容可以得到 request_irq()函数实际上是调用了 request_threaded_irq()函数来完成中断申请的过程。request_threaded_irq()函数提供了线程化的中断处理方式，可以在中断上下文中执行中断处理函数。

### 13.3.2 request_threaded_irq 函数

request_threaded_irq 函数是 Linux 内核提供的一个功能强大的函数，用于请求分配一个中断，并将中断处理程序与该中断关联起来。该函数的主要作用是在系统中注册中断处理函数，以响应对应中断的发生。以下是 request_threaded_irq 函数的功能和作用的详细介绍：

> （1）中断请求：request_threaded_irq 函数用于请求一个中断。它会向内核注册对应中断号的中断处理函数，并为该中断分配必要的资源。中断号是标识特定硬件中断的唯一标识符。
> （2）中断处理函数关联：通过 handler 参数，将中断处理函数与中断号关联起来。中断处理函数是一个预定义的函数，用于处理中断事件。当中断发生时，内核将调用该函数来处理中断事件。
> （3）线程化中断处理：request_threaded_irq 函数还支持使用线程化中断处理函数。通过指定 thread_fn 参数，可以在一个内核线程上下文中异步执行较长时间的中断处理或延迟敏感的工作。这有助于避免在中断上下文中阻塞时间过长。
> （4）中断属性设置：通过 irqflags 参数，可以设置中断处理的各种属性和标志。例如，可以指定中断触发方式（上升沿、下降沿、边沿触发等）、中断类型（边沿触发中断、电平触发中断等）以及其他特定的中断行为。
>
> （5）设备标识关联：通过 dev_id 参数，可以将中断处理与特定设备关联起来。这样可以在中断处理函数中访问与设备相关的数据。设备标识符可以是指向设备结构体或其他与设备相关的数据的指针。
> （6）错误处理：request_threaded_irq 函数会返回一个整数值，用于指示中断请求的结果。如果中断请求成功，返回值为 0；如果中断请求失败，则返回一个负数错误代码，表示失败的原因。

request_threaded_irq 函数定义在内核源码目录下的“/kernel/irq/manage.c”文件中，具体内容如下所示：

```c
int request_threaded_irq(unsigned int irq, irq_handler_t handler,
irq_handler_t thread_fn, unsigned long irqflags, const char *devname, void *dev_id) {
	struct irqaction *action;// 中断动作结构体指针
	struct irq_desc *desc;// 中断描述符指针
	int retval;// 返回值
	// 检查中断号是否为未连接状态
	if (irq == IRQ_NOTCONNECTED)
	return -ENOTCONN;
	// 检查中断标志的有效性
	if (((irqflags & IRQF_SHARED) && !dev_id) ||
	(!(irqflags & IRQF_SHARED) && (irqflags & IRQF_COND_SUSPEND)) ||
	((irqflags & IRQF_NO_SUSPEND) && (irqflags & IRQF_COND_SUSPEND)))
	return -EINVAL;
	// 根据中断号获取中断描述符
	desc = irq_to_desc(irq);
	if (!desc)
	return -EINVAL;
	// 检查中断设置是否可以进行中断请求，以及是否为每个 CPU 分配唯一设备 ID
	if (!irq_settings_can_request(desc) || WARN_ON(irq_settings_is_per_cpu_devid(desc)))
	return -EINVAL;
	// 如果未指定中断处理函数，则使用默认的主处理函数
	if (!handler) {
		if (!thread_fn)
		return -EINVAL;
		handler = irq_default_primary_handler;
	}
	// 分配并初始化中断动作数据结构
	action = kzalloc(sizeof(struct irqaction), GFP_KERNEL);
	if (!action)
	return -ENOMEM;
	action->handler = handler;// 中断处理函数
	action->thread_fn = thread_fn;// 线程处理函数
	action->flags = irqflags;// 中断标志
	action->name = devname;// 设备名称
	action->dev_id = dev_id;// 设备 ID
	// 获取中断的电源管理引用计数
	retval = irq_chip_pm_get(&desc->irq_data);
	if (retval < 0) {
		kfree(action);
		return retval;
	}// 设置中断并将中断动作与中断描述符关联
	retval = __setup_irq(irq, desc, action);// 处理中断设置失败的情况
	if (retval) {
		irq_chip_pm_put(&desc->irq_data);
		kfree(action->secondary);
		kfree(action);
	}
	#ifdef CONFIG_DEBUG_SHIRQ_FIXME
	if (!retval && (irqflags & IRQF_SHARED)) {
		unsigned long flags;
		disable_irq(irq);
		local_irq_save(flags);
		handler(irq, dev_id);
		local_irq_restore(flags);
		enable_irq(irq);
	}
	#endif
	return retval; // 返回设置中断的结果
}
```

### 13.3.3 irq_desc 结构体

irq_desc 结构体是 Linux 内核中用于描述中断的数据结构之一。每个硬件中断都有一个对应的 irq_desc 实例，它用于记录与该中断相关的各种信息和状态。该结构体的主要功能是管理中断处理函数、中断行为以及与中断处理相关的其他数据。

以下是 irq_desc 结构体的主要作用和功能

> （1）中断处理函数管理：irq_desc 结构体中的 handle_irq 字段保存中断处理函数的指针。当硬件触发中断时，内核会调用该函数来处理中断事件。
> （2）中断行为管理：irq_desc 结构体中的 action 字段是一个指向中断行为列表的指针。中断行为是一组回调函数，用于注册、注销和处理与中断相关的事件。
> （3）中断统计信息：irq_desc 结构体中的 kstat_irqs 字段是一个指向中断统计信息的指针。该信息用于记录中断事件的发生次数和处理情况，可以帮助分析中断的性能和行为。
> （4）中断数据管理：irq_desc 结构体中的 irq_data 字段保存了与中断相关的数据，如中断号、中断类型等。这些数据用于识别和管理中断。
> （5）通用中断数据管理：irq_desc 结构体中的 irq_common_data 字段保存了与中断处理相关的通用数据，如中断控制器、中断屏蔽等。这些数据用于处理和控制中断的行为。
>
> （6）中断状态管理：irq_desc 结构体中的其他字段用于管理中断的状态，如嵌套中断禁用计数、唤醒使能计数等。这些状态信息帮助内核跟踪和管理中断的状态变化。

通过使用 irq_desc 结构体，内核可以有效地管理和处理系统中的硬件中断。它提供了一个统一的接口，用于注册和处理中断处理函数、管理中断行为，并提供了必要的信息和数据结构来监视和控制中断的行为和状态。

irq_desc 结构体定义在内核源码目录的“include/linux/irqdesc.h”文件，具体内容如下

```c
struct irq_desc {
	struct irq_common_data irq_common_data;
	/* 通用中断数据 */
	struct irq_data irq_data;
	/* 中断数据 */
	unsigned int __percpu *kstat_irqs;
	/* 中断统计信息 */
	irq_flow_handler_t handle_irq;
	/* 中断处理函数 */
	#ifdef CONFIG_IRQ_PREFLOW_FASTEOI
	irq_preflow_handler_t preflow_handler;
	/* 预处理中断处理函数 */
	#endif
	struct irqaction*action;
	* IRQ action list */
	unsigned int status_use_accessors;
	unsigned int core_internal_state__do_not_mess_with_it;
	/* 内核内部状态标志位，请勿修改 */
	unsigned int depth;
	/* 嵌套中断禁用计数 */
	unsigned int wake_depth;
	/* 嵌套唤醒使能计数 */
	unsigned int tot_count;
	unsigned int irq_count;
	/* 用于检测损坏的 IRQ 计数 */
	unsigned long last_unhandled;
	/* 未处理计数的老化计时器 */
	unsigned int irqs_unhandled;
	/* 未处理的中断计数 */
	atomic_t threads_handled;
	/* 处理中断的线程计数 */
	int threads_handled_last;
	raw_spinlock_t lock;
	/* 自旋锁 */
	struct cpumask *percpu_enabled;
	/* 指向每个 CPU 的使能掩码 */
	const struct cpumask *percpu_affinity;
	/* 指向每个 CPU 亲和性掩码 */
	#ifdef CONFIG_SMP
	const struct cpumask *affinity_hint;
	/* CPU 亲和性提示 */
	struct irq_affinity_notify *affinity_notify;
	/* CPU 亲和性变化通知 */
	#ifdef CONFIG_GENERIC_PENDING_IRQ
	cpumask_var_t pending_mask;
	/* 等待处理的中断掩码 */
	#endif
	#endif
	unsigned long threads_oneshot;
	atomic_t threads_active;
	/* 活动中的线程计数 */
	wait_queue_head_t wait_for_threads;
	/* 等待线程的等待队列头 */
	#ifdef CONFIG_PM_SLEEP
	unsigned int nr_actions;
	unsigned int no_suspend_depth;
	unsigned int cond_suspend_depth;
	unsigned int force_resume_depth;
	#endif
	#ifdef CONFIG_PROC_FS
	struct proc_dir_entry *dir;
	/* proc 文件系统目录项 */
	#endif
	#ifdef CONFIG_GENERIC_IRQ_DEBUGFS
	struct dentry *debugfs_file;
	/* 调试文件系统文件 */
	const char *dev_name;
	/* 设备名称 */
	#endif
	#ifdef CONFIG_SPARSE_IRQ
	struct rcu_head rcu;
	struct kobject kobj;
	/* 内核对象 */
	#endif
	struct mutex request_mutex;
	/* 请求互斥锁 */
	int parent_irq;
	/* 父中断号 */
	struct module *owner;
	/* 模块拥有者 */
	const char *name;
	/* 中断名称 */
}
____cacheline_internodealigned_in_smp;
```

### 13.3.4 irqaction 结构体

irqaction 结构体是 Linux 内核中用于描述中断行为的数据结构之一。它用于定义中断处理过程中的回调函数和相关属性。irqaction 结构体的主要功能是管理与特定中断相关的行为和处理函数。

以下是 irqaction 结构体的主要作用和功能

> （1）中断处理函数管理：irqaction 结构体中的 handler 字段保存中断处理函数的指针。该函数在中断发生时被调用，用于处理中断事件。
> （2）中断处理标志管理：irqaction 结构体中的 flags 字段用于指定中断处理的各种属性和标志。这些标志控制中断处理的行为，例如触发方式、中断类型等。
> （3）设备标识符管理：irqaction 结构体中的 dev_id 字段用于保存与中断处理相关的设备标识符。它可以是指向设备结构体或其他与设备相关的数据的指针，用于将中断处理与特定设备关联起来。
> （4）中断行为链表管理：irqaction 结构体中的 next 字段是一个指向下一个 irqaction 结构体的指针，用于构建中断行为的链表。这样可以将多个中断处理函数链接在一起，以便在中断发生时按顺序调用它们。

通过使用 irqaction 结构体，内核可以灵活地定义和管理与特定中断相关的行为和处理函数。它提供了一个统一的接口，用于注册和注销中断处理函数，并提供了必要的属性和数据结构来控制中断处理的行为和顺序。

irqaction 体定义在内核源码的“include/linux/interrupt.h”文件中如下

```c
struct irqaction {
	irq_handler_t handler;
	// 中断处理函数
	void *dev_id;
	// 设备 ID
	void __percpu *percpu_dev_id;
	// 每个 CPU 的设备 ID
	struct irqaction*next;
	// 下一个中断动作结构体
	irq_handler_t thread_fn;
	// 线程处理函数
	struct task_struct *thread;
	// 线程结构体指针
	struct irqaction*secondary;
	// 次要中断动作结构体
	unsigned int irq;
	// 中断号
	unsigned int flags;
	// 中断标志
	unsigned long thread_flags;
	// 线程标志
	unsigned long thread_mask;
	// 线程掩码
	const char *name;
	// 设备名称
	struct proc_dir_entry *dir;
	// proc 文件系统目录项指针
}
____cacheline_internodealigned_in_smp;
```

<a id="part-27"></a>

## 13.4 中断下半部 Tasklet

Tasklet 是基于软中断的中断下半部机制。同一个 tasklet 实例不会同时在多个 CPU 上执行；不同 tasklet 实例、硬中断和进程上下文之间仍可能并发访问共享数据，需要相应同步。Tasklet 回调不能睡眠，也不适合长时间占用 CPU。

在 Linux 内核中，tasklet 结构体的定义位于 include/linux/interrupt.h 头文件中。其原型如下：

```c
struct tasklet_struct
{
	struct tasklet_struct *next;
	unsigned long state;
	atomic_t count;
	bool use_callback;
	union {
		void (*func)(unsigned long data);
		void (*callback)(struct tasklet_struct *t);
	};
	unsigned long data;
};
typedef struct tasklet_struct tasklet_t;
```

tasklet_struct 结构体包含以下成员：

> next:指向下一个tasklet的指针，用于形成链表结构，以便内核中可以同时管理多个tasklet。
>
> state:表示 tasklet 的当前状态。
>
> count：禁用计数；大于 0 时禁止执行，disable/enable 需要配对，不是对象引用计数。
>
> func:指向 tasklet 绑定的函数的指针，该函数将在 tasklet 执行时被调用。
>
> data:传递给 tasklet 绑定函数的参数

此外，为了方便，还定义了 tasklet_t 类型作为 struct tasklet_struct 的别名。这样我们可以使用 tasklet_t 来声明 tasklet 变量，而不是直接使用 struct tasklet_struct。

### 13.4.1 静态初始化函数

在 Linux 内核中，有一个用于静态初始化 tasklet 的宏函数：DECLARE_TASKLET。这个宏函数可以帮助我们更方便地进行 tasklet 的静态初始化。

宏函数的原型如下：

> \#define DECLARE_TASKLET(name, _callback)     \
>
> struct tasklet_struct name = {        \
>
>   .count = ATOMIC_INIT(0),       \
>
>   .callback = _callback,        \
>
>   .use_callback = true,        \
>
> }

Linux 6.1 的 DECLARE_TASKLET(name, callback) 只有两个参数，callback 的签名为 void callback(struct tasklet_struct *t)，默认处于启用状态。

如果 tasklet 初始化函数为非使能状态，使用以下宏定义：

```c
/* Linux 6.1：初始化为禁用状态，也只有两个参数 */
DECLARE_TASKLET_DISABLED(my_tasklet, my_tasklet_handler);
```

使用前须通过 tasklet_enable 配对解除禁用，回调仍接收 struct tasklet_struct 指针。





下面是一个示例，展示了如何使用 DECLARE_TASKLET 宏函数进行 tasklet 的静态初始化：

```C
#include <linux/interrupt.h>
// 定义 tasklet 处理函数
void my_tasklet_handler(struct tasklet_struct *t)
{
  // Tasklet 处理逻辑
  // ... 
}
// 静态初始化 tasklet
DECLARE_TASKLET(my_tasklet, my_tasklet_handler);
// 驱动程序的其他代码
```

DECLARE_TASKLET 声明并初始化一个对象，退出时同样可以 tasklet_kill 等待结束。初始化方式不决定是否能 kill；动态分配的对象还需由所属驱动释放。Linux 6.1 也保留 tasklet_init(t, func, data) 旧式接口，其回调为 void func(unsigned long)，不要把两套回调签名混用；新代码可用 tasklet_setup(t, callback)。

### 13.4.2 动态初始化函数

在 Linux 内核中，可以使用 tasklet_init 函数对 tasklet 进行动态初始化。该函数原型为：

> void tasklet_init**(**struct tasklet_struct *****t**,** void **(\***func**)(**unsigned long**),** unsigned long data**);**

其中，t 是指向 tasklet 结构体的指针，func 是 tasklet 的处理函数，data 是传递给处理函数的参数

以下是一个示例，tasklet_init 函数进行动态初始化如下

```C
#include <linux/interrupt.h>
// 定义 tasklet 处理函数
void my_tasklet_handler(unsigned long data)
{
  // Tasklet 处理逻辑
  // ... 
}
// 声明 tasklet 结构体
static struct tasklet_struct my_tasklet;
// 初始化 tasklet
tasklet_init(&my_tasklet, my_tasklet_handler, 0);
// 驱动程序的其他代码
```

在示例中，我们首先定义了 my_tasklet_handler 作为 tasklet 的处理函数。然后，声明了一个名为 my_tasklet 的 tasklet 结构体。接下来，通过调用 tasklet_init 函数，进行动态初始化。

`tasklet_init()` 初始化已有对象，不负责分配对象内存。停止使用时，应先阻止新的调度，再使用 `tasklet_kill()` 等待待处理或正在执行的 tasklet 结束；对象若由驱动动态分配，最后由驱动释放。

### 13.4.3 关闭函数

在 Linux 内核中，可以使用 tasklet_disable 函数来关闭一个已经初始化的 tasklet。该函数的原型如下：

> void tasklet_disable**(**struct tasklet_struct *****t**);**

其中，t 是指向 tasklet 结构体的指针。

以下是一个示例，使用 tasklet_disable 函数来关闭 tasklet。

```C
#include <linux/interrupt.h>
// 定义 tasklet 处理函数
void my_tasklet_handler(unsigned long data)
{
  // Tasklet 处理逻辑
  // ... 
}
// 声明 tasklet 结构体
static struct tasklet_struct my_tasklet;
// 初始化 tasklet
tasklet_init(&my_tasklet, my_tasklet_handler, 0);
// 关闭 tasklet
tasklet_disable(&my_tasklet);
// 驱动程序的其他代码
```

在上述示例中，我们首先定义了 my_tasklet_handler 作为 tasklet 的处理函数。然后，声明了一个名为 my_tasklet 的 tasklet 结构体，并使用 tasklet_init 函数对其进行初始化。最后，通过调用 tasklet_disable 函数，我们关闭了 my_tasklet。

关闭 tasklet 后，即使调用 tasklet_schedule 函数触发 tasklet，tasklet 的处理函数也不会再被执行。这可以用于临时暂停或停止 tasklet 的执行，直到再次启用（通过调用 tasklet_enable函数）。

`tasklet_disable()` 不释放对象。之后可用配对的 `tasklet_enable()` 恢复；最终退出时先停止调度来源，再执行 `tasklet_kill()`，并自行管理对象内存。

### 13.4.4 使能函数

在 Linux 内核中，可以使用 tasklet_enable 函数来使能（启用）一个已经初始化的 tasklet。该函数的原型如下：

> void tasklet_enable**(**struct tasklet_struct *****t**)**;

其中，t 是指向 tasklet 结构体的指针.

以下是一个示例，展示如何使用 tasklet_enable 函数来使能 tasklet：

```C
#include <linux/interrupt.h>
// 定义 tasklet 处理函数
void my_tasklet_handler(unsigned long data)
{
  // Tasklet 处理逻辑
  // ... 
}
// 声明 tasklet 结构体
static struct tasklet_struct my_tasklet;
// 初始化 tasklet
tasklet_init(&my_tasklet, my_tasklet_handler, 0);
// 初始化后默认已启用；disable/enable 必须配对
tasklet_disable(&my_tasklet);
// 暂停期间的操作
tasklet_enable(&my_tasklet);

```

上述示例先初始化，然后配对调用 `tasklet_disable()` 和 `tasklet_enable()`；不要对默认已启用的 tasklet 无配对地调用 enable。

使能 tasklet 后，如果调用 tasklet_schedule 函数触发 tasklet，则 tasklet 的处理函数将会被执行。这样，tasklet 将开始按计划执行其处理逻辑。

使能不是创建新的调度请求；若禁用期间已经 schedule，待处理 tasklet 在恢复使能后可以执行。卸载时应先停止调度来源，保证任务已启用并可完成，再调用 `tasklet_kill()`；该函数本身不释放 tasklet 对象的内存。

### 13.4.5 调度函数

在 Linux 内核中，可以使用 tasklet_schedule 函数来调度（触发）一个已经初始化的 tasklet执行。该函数的原型如下：

> void tasklet_schedule**(**struct tasklet_struct *****t**);**

其中，t 是指向 tasklet 结构体的指针。

以下是一个示例，展示如何使用 tasklet_schedule 函数来调度 tasklet 执行：

```C
#include <linux/interrupt.h>
// 定义 tasklet 处理函数
void my_tasklet_handler(unsigned long data)
{
  // Tasklet 处理逻辑
  // ... 
}
// 声明 tasklet 结构体
static struct tasklet_struct my_tasklet;
// 初始化 tasklet
tasklet_init(&my_tasklet, my_tasklet_handler, 0);
// 调度 tasklet 执行
tasklet_schedule(&my_tasklet);
// 驱动程序的其他代码
```

在上述示例中，我们首先定义了 my_tasklet_handler 作为 tasklet 的处理函数。然后，声明了一个名为 my_tasklet 的 tasklet 结构体，并使用 tasklet_init 函数对其进行初始化。最后，通过调用 tasklet_schedule 函数，我们调度（触发）了 my_tasklet 的执行。

需要注意的是，调度 tasklet 只是将 tasklet 标记为需要执行，并不会立即执行 tasklet 的处理函数。实际的执行时间取决于内核的调度和处理机制。

### 13.4.6 销毁函数

在 Linux 内核中，可以使用 tasklet_kill 函数来销毁一个已经初始化的 tasklet，释放相关资源。该函数的原型如下：

> void tasklet_kill**(**struct tasklet_struct *****t**);**

其中，t 是指向 tasklet 结构体的指针。

以下是一个示例，展示如何使用 tasklet_kill 函数来销毁 tasklet：

```C
#include <linux/interrupt.h>
// 定义 tasklet 处理函数
void my_tasklet_handler(unsigned long data)
{
  // Tasklet 处理逻辑
  // ... 
}
// 声明 tasklet 结构体
static struct tasklet_struct my_tasklet;
// 初始化 tasklet
tasklet_init(&my_tasklet, my_tasklet_handler, 0);
tasklet_disable(&my_tasklet);
// 销毁 tasklet
tasklet_kill(&my_tasklet);
// 驱动程序的其他代码
```

`tasklet_kill()` 等待任务退出，不释放对象内存；卸载前还需停止中断等调度来源，避免退出后再次 schedule。

`tasklet_kill()` 等待任务退出，不释放对象内存；卸载前还需停止中断等调度来源，避免退出后再次 schedule。

`tasklet_kill()` 等待任务退出，不释放对象内存；卸载前还需停止中断等调度来源，避免退出后再次 schedule。

`tasklet_kill()` 等待任务退出，不释放对象内存；卸载前还需停止中断等调度来源，避免退出后再次 schedule。

**实验代码**

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
// #include <linux/delay.h>

int irq;
struct tasklet_struct mytasklet;

// 定义tasklet处理函数
void mytasklet_func(unsigned long data)
{
  printk("data is %ld\n", data);
  // msleep(3000);
}

// 中断处理函数
irqreturn_t test_interrupt(int irq, void *args)
{
  printk("This is test_interrupt\n");
  tasklet_schedule(&mytasklet); // 调度tasklet执行
  return IRQ_RETVAL(IRQ_HANDLED);
}
// 模块初始化函数
static int interrupt_irq_init(void)
{
  int ret;
  irq = gpio_to_irq(101); // 将GPIO转换为中断号
  printk("irq is %d\n", irq);

  // 请求中断
  ret = request_irq(irq, test_interrupt, IRQF_TRIGGER_RISING, "test", NULL);
  if (ret < 0)
  {
    printk("request_irq is error\n");
    return -1;
  }
  // 初始化tasklet
  tasklet_init(&mytasklet, mytasklet_func, 1);
  return 0;
}
// 模块退出函数
static void interrupt_irq_exit(void)
{

  free_irq(irq, NULL);
  tasklet_disable(&mytasklet); // 使能tasklet（可选）
  tasklet_kill(&mytasklet);   // 销毁tasklet
  printk("bye bye\n");
}

module_init(interrupt_irq_init); // 指定模块的初始化函数
module_exit(interrupt_irq_exit); // 指定模块的退出函数

MODULE_LICENSE("GPL");   // 模块使用的许可证
MODULE_AUTHOR("woniu"); // 模块的作者
```

## 13.5 软中断

打开 Linux 源码 linux_sdk/kernel/include/linux/interrupt.h 文件，如下所示：

```c
enum
{
	HI_SOFTIRQ=0, 
	TIMER_SOFTIRQ, 
	NET_TX_SOFTIRQ, 
	NET_RX_SOFTIRQ, 
	BLOCK_SOFTIRQ,
	IRQ_POLL_SOFTIRQ, 
	TASKLET_SOFTIRQ, 
	SCHED_SOFTIRQ, 
	HRTIMER_SOFTIRQ, /* Unused, but kept as tools rely on the numbering. Sigh! */
	RCU_SOFTIRQ, /* Preferable RCU should always be the last softirq */
	NR_SOFTIRQS
};
```

以上代码定义了一个枚举类型，用于标识软中断的不同类型或优先级。每个枚举常量对应 一个特定的软中断类型。

以下是每个枚举常量的含义：

> HI_SOFTIRQ：高优先级软中断  
> TIMER_SOFTIRQ：定时器软中断
> NET_TX_SOFTIRQ：网络传输发送软中断 
> NET_RX_SOFTIRQ：网络传输接收软中断 
> BLOCK_SOFTIRQ：块设备软中断
> IRQ_POLL_SOFTIRQ：中断轮询软中断 
> TASKLET_SOFTIRQ：任务软中断
>
> SCHED_SOFTIRQ：调度软中断
>
> HRTIMER_SOFTIRQ, /* Unused, but kept as tools rely on the numbering. Sigh! */ *
>
> *RCU_SOFTIRQ,     /* Preferable RCU should always be the last softirq */
>
> NR_SOFTIRQS：表示软中断的总数，用于指示软中断类型的数据

中断号的优先级越小，代表优先级越高。在驱动代码中，我们可以使用 Linux 驱动代码中 上述的软中断，当然我们也可以自己添加软中断。我们添加一个自定义的软中断，如下所示， TEST_SOFTIRQ 为自定义添加的软中断。

```c
enum {
  HI_SOFTIRQ=0,
  TIMER_SOFTIRQ,
  NET_TX_SOFTIRQ,
  NET_RX_SOFTIRQ,
  BLOCK_SOFTIRQ,
  IRQ_POLL_SOFTIRQ, 
  TASKLET_SOFTIRQ,    
  SCHED_SOFTIRQ,
  HRTIMER_SOFTIRQ, /* Unused, but kept as tools rely on the numbering. Sigh! */
  RCU_SOFTIRQ,         /* Preferable RCU should always be the last softirq */
  TEST_SOFTIRQ,    //添加的自定义软中断
  NR_SOFTIRQS 
};
```

这里要注意：尽管我们添加一个自定义的软中断非常简单，但是 Linux 内核的开发者并不 希望我们这样去做，如果我们要用软中断，建议使用 tasklet 。虽然 Linux 内核开发者不建议自 定义软中断，但是我们抱着学习的态度，了解学习下软中断还是很有必要的。上述修改之后， 重新编译内核源码，接下来我们来学习下软中断的使用方法。

### 13.5.1 软中断接口函数

软中断的接口函数非常简单，介绍如下所示：

1. 注册软中断，使用 open_softirq 函数，函数原型如下所示：

> void open_softirq**(**int nr**,**void **(\***action**)(**struct softirq_action ***));**

函数的参数如下所示：

> nr: 软中断的编号或优先级。它是一个整数，表示要注册的软中断的标识符。
>
> action: 指向一个函数的指针，这个函数将作为软中断的处理程序。该函数接受一个 struct
>
> softirq_action 类型的参数。

2. 触发软中断，使用 raise_softirq 函数，函数原型如下所示：

> void raise_softirq**(**unsigned int nr**);**

函数的参数如下所示：

> nr: 软中断的编号或优先级。它是一个整数，表示要注册的软中断的标识符。

3. 在禁用硬件中断的情况下，触发软中断使用 raise_softirq_irqoff 函数，函数原型如下所示：

> void raise_softirq_irqoff**(**unsigned int nr**);**

函数的参数如下所示：

> nr: 软中断的编号或优先级。它是一个整数，表示要注册的软中断的标识符。

4. 修改linux内核原码，导出raise_softirq和open_softirq

   > 位置/kernel/kernel/softirq.c

实验代码

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
// #include <linux/delay.h>

int irq;

// 软中断处理程序
void testsoft_func(struct softirq_action *softirq_action)
{
  printk("This is testsoft_func\n");
}

irqreturn_t test_interrupt(int irq, void *args)
{
  printk("This is test_interrupt\n");
  raise_softirq(TEST_SOFTIRQ); // 触发软中断
  return IRQ_RETVAL(IRQ_HANDLED);
}

static int interrupt_irq_init(void)
{
  int ret;
  irq = gpio_to_irq(101); // 将GPIO映射为中断号
  printk("irq is %d\n", irq);
  // 请求中断
  ret = request_irq(irq, test_interrupt, IRQF_TRIGGER_RISING, "test", NULL);
  if (ret < 0)
  {
    printk("request_irq is error\n");
    return -1;
  }
  // 注册软中断处理函数
  open_softirq(TEST_SOFTIRQ, testsoft_func);
  return 0;
}

static void interrupt_irq_exit(void)
{
  free_irq(irq, NULL); // 释放中断
  printk("bye bye\n");
}

module_init(interrupt_irq_init);
module_exit(interrupt_irq_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("woniu");
```

## 13.6 软中断tasklet 分析

Tasklet 是 Linux 内核中的一种软中断机制，它可以被看作是一种轻量级的延迟处理机制。 它是通过软中断控制结构来实现的，因此也被称为软中断。本章节我们来从代码层面分析一下 为什么 tasklet 是一个特殊的软中断呢？

软中断处理函数的定义内核源码 kernel/kernel/softirq.c 文件中

```c
void __init softirq_init(void)
{
	int cpu;
  // 初始化每个可能的 CPU 的 tasklet_vec 和 tasklet_hi_vec
  // 将 tail 指针设置为对应的 head 指针的初始位置
  for_each_possible_cpu(cpu) {
    per_cpu(tasklet_vec, cpu).tail = &per_cpu(tasklet_vec, cpu).head;
    per_cpu(tasklet_hi_vec, cpu).tail = &per_cpu(tasklet_hi_vec, cpu).head;
  }
  // 注册 TASKLET_SOFTIRQ 软中断，并指定对应的处理函数为 tasklet_action
  open_softirq(TASKLET_SOFTIRQ, tasklet_action);
  // 注册 HI_SOFTIRQ 软中断，并指定对应的处理函数为 tasklet_hi_action
  open_softirq(HI_SOFTIRQ, tasklet_hi_action);
}
```

下面开始对上述代码详细解释：

> for_each_possible_cpu(cpu)：遍历每个可能的 CPU。在多核系统中，此循环用于初始化每个 CPU 的 tasklet_vec 和 tasklet_hi_vec。
>
> per_cpu(tasklet_vec, cpu).tail = &per_cpu(tasklet_vec, cpu).head;：将每个 CPU 的 tasklet_vec的 tail 指针设置为对应的 head 指针的初始位置。这样做是为了确保 tasklet_vec 的初始状态是空的。
>
> per_cpu(tasklet_hi_vec, cpu).tail = &per_cpu(tasklet_hi_vec, cpu).head; ： 将 每 个 CPU 的tasklet_hi_vec 的 tail 指针设置为对应的 head 指针的初始位置。这样做是为了确保tasklet_hi_vec 的初始状态是空的。
>
> open_softirq(TASKLET_SOFTIRQ, tasklet_action);：注册 TASKLET_SOFTIRQ 软中断，并指定对应的处理函数为tasklet_action。这样，在TASKLET_SOFTIRQ被触发时，将会调用tasklet_action函数来处理相应的任务。
>
> open_softirq(HI_SOFTIRQ, tasklet_hi_action);：注册 HI_SOFTIRQ 软中断，并指定对应的处理函数为 tasklet_hi_action。这样，在 HI_SOFTIRQ 被触发时，将会调用 tasklet_hi_action 函数来处理相应的任务。

在执行__init softirq_init 函数时，会触发 TASKLET_SOFTIRQ，然后会调用 tasklet_action 函数，tasklet_action 函数如下所示：

```c
static __latent_entropy void tasklet_action(struct softirq_action *a)
{
	tasklet_action_common(a, this_cpu_ptr(&tasklet_vec), TASKLET_SOFTIRQ);
}
```

上述函数中调用了 tasklet_action_common 函数，如下所示：

```c
static __latent_entropy void tasklet_action(struct softirq_action *a)
{
	tasklet_action_common(a, this_cpu_ptr(&tasklet_vec), TASKLET_SOFTIRQ);
}
```

tasklet_action_common 函数，如下所示：

```c
static void tasklet_action_common(struct softirq_action *a, struct tasklet_head *tl_head, unsigned int softirq_nr) {
	struct tasklet_struct *list;
	// 禁用本地中断
	local_irq_disable();
	// 获取 tasklet_head 中的任务链表
	list = tl_head->head;
	// 清空 tasklet_head 中的任务链表
	tl_head->head = NULL;
	// 将 tail 指针重新指向 head 指针的位置
	tl_head->tail = &tl_head->head;
	// 启用本地中断
	local_irq_enable();
	// 遍历任务链表，处理每一个 tasklet
	while (list) {
		struct tasklet_struct *t = list;
		// 获取下一个 tasklet，并更新链表
		list = list->next;
		if (tasklet_trylock(t)) {
			// 尝试获取 tasklet 的锁
			if (!atomic_read(&t->count)) {
				// 检查 count 计数器是否为 0
				if (!test_and_clear_bit(TASKLET_STATE_SCHED, &t->state))
				BUG();
				// 如果 state 标志位不正确，则发生错误
				t->func(t->data);
				// 执行 tasklet 的处理函数
				tasklet_unlock(t);
				// 解锁 tasklet
				continue;
			}
			tasklet_unlock(t);
			// 解锁 tasklet
		}
		// 禁用本地中断
		local_irq_disable();
		// 将当前 tasklet 添加到 tasklet_head 的尾部
		t->next = NULL;
		*tl_head->tail = t;
		// 更新 tail 指针
		tl_head->tail = &t->next;
		// 触发软中断
		__raise_softirq_irqoff(softirq_nr);
		// 启用本地中断
		local_irq_enable();
	}
}
```

在上面的代码中，tasklet_action_common()函数对任务链表中的每个 tasklet 进行处理。它 首先禁用本地中断，获取任务链表头指针，清空任务链表，并重新设置尾指针。然后它循环遍 历任务链表，对每个 tasklet 进行处理。如果 tasklet 的锁获取成功，并且计数器为 0 ，它将执 行 tasklet 的处理函数，并清除状态标志位。如果锁获取失败或计数不为 0 ，它将 tasklet 添加 到任务链表的尾部，并触发指定的软中断。最后，它启用本地中断，完成任务处理过程。

那么 tasklet 在什么时候加到链表里面的呢？tasklet 是通 tasklet_schedule_common()函数 加入到链表中的。如下所示：

```c
static void __tasklet_schedule_common(struct tasklet_struct *t, struct tasklet_head __percpu *headp, unsigned int softirq_nr) {
	struct tasklet_head *head;
	unsigned long flags;
	// 保存当前中断状态，并禁用本地中断
	local_irq_save(flags);
	// 获取当前 CPU 的 tasklet_head 指针
	head = this_cpu_ptr(headp);
	// 将当前 tasklet 添加到 tasklet_head 的尾部
	t->next = NULL;
	*head->tail = t;
	// 更新 tasklet_head 的尾指针
	head->tail = &(t->next);
	// 触发指定的软中断
	raise_softirq_irqoff(softirq_nr);
	// 恢复中断状态
	local_irq_restore(flags);
}
```

通过上述代码，  tasklet_schedule_common()函数将 tasklet 成功添加到链表的末尾。 当软中断被触发时，系统会遍历链表并处理每个 tasklet。因此，在添加到链表后，tasklet 将在适当的时机被系统调度和执行。

经过上述分析，所以说 tasklet 是一个特殊的软中断。

内核开发者不希望我们去添加软中断的软中断号，更希望我们使用 tasklet。那么 tasklet 相比自己添加软中断有哪些优点和缺点呢？

使用Tasklet 相比自己添加软中断有一些优点和缺点。以下是它们的比较：

优点：

> 1. 简化的接口和编程模型：Tasklet 提供了一个简单的接口和编程模型，使得在内核中 处理延迟工作变得更加容易。相比自己添加软中断，Tasklet提供了更高级的抽象。
>
> 2. 低延迟：Tasklet在软中断上下文中执行，避免了内核线程的上下文切换开销，因此 具有较低的延迟。这对于需要快速响应的延迟敏感任务非常重要。
>
> 3. 自适应调度：Tasklet 具有自适应调度的特性，当多个 Tasklet 处于等待状态时，内 核会合并它们以减少不必要的上下文切换。这种调度机制可以提高系统的效率。

缺点：

> 1. 无法处理长时间运行的任务：Tasklet 适用于短时间运行的延迟工作，如果需要处理 长时间运行的任务，可能会阻塞其他任务的执行。对于较长的操作，可能需要使用工作队列或 内核线程来处理。
>
> 2. 缺乏灵活性：Tasklet 的执行受限于软中断的上下文，不适用于所有类型的延迟工作。 某些情况下，可能需要更灵活的调度和执行机制，这时自定义软中断可能更加适合。
>
> 3. 配置。如果需要大量的延迟工作处理，可能会受到Tasklet数量的限制。资源限制：Tasklet 的数量是有限的，系统中可用的Tasklet 数量取决于架构和内核

Tasklet 和软中断都属于不能睡眠的执行上下文，处理应尽量短。需要阻塞等待或较复杂处理时可选择工作队列或线程化中断；不能把自定义软中断当作长时间任务的一般解决方案。

<a id="part-29"></a>

## 13.7 中断线程化

中断线程化把较长的处理放入 IRQ 内核线程。硬中断发生后，主处理函数 `handler` 仍在硬中断上下文执行，通常只完成确认/屏蔽等必要操作，再返回 `IRQ_WAKE_THREAD` 唤醒 `thread_fn`。

`thread_fn` 受调度器管理，可以在合适条件下睡眠；使用 `IRQF_ONESHOT` 时，线程处理期间相关中断线路保持屏蔽。中断线程仍会与其他线程、硬中断竞争 CPU 和共享数据，所以需要同步，不能保证减少所有切换开销，也不能保证应用线程不再被中断。













### 13.7.1 中断线程化接口函数

request_threaded_irq 是 Linux 内核中用于请求并注册一个线程化的中断处理函数的函数。

> int request_threaded_irq**(**unsigned int irq**,** irq_handler_t handler**,**irq_handler_t thread_fn**,** unsigned long irqflags**,** const char *****devname**,** void *****dev_id**);**

**参数说明**

> **irq**：中断号，表示要请求的中断线路。
>
> **handler**：是在发生中断时首先要执行的处理程序，非常类似于顶半上部，该函数最后会返回 IRQ_WAKE_THREAD 来唤醒中断，一般 handler 设为 NULL，用系统提供的默认处理。
>
> **thread_fn**：线程化的中断处理函数，非常类似于底半部。如果此处设置为 NULL 则表示没有使用中断线程化。
>
> **irqflags**：中断标志，用于指定中断的属性和行为。
>
> **devname**：中断的名称，用于标识中断请求的设备。
>
> **dev_id**：设备标识符，用于传递给中断处理函数的参数。
>
> **函数返回值**
>
> 函数返回一个整数值，表示中断请求的结果。如果中断请求成功，返回值为 0，否则返回一个负数错误代码。

实验代码

```c
#include <linux/module.h>
#include <linux/init.h>
#include <linux/interrupt.h>
#include <linux/gpio.h>
#include <linux/delay.h>
#include <linux/workqueue.h>

int irq;

// 中断处理函数的底半部（线程化中断处理函数）
irqreturn_t test_work(int irq, void *args)
{
  // 执行底半部的中断处理任务
  msleep(1000);
  printk("This is test_work\n");
  return IRQ_RETVAL(IRQ_HANDLED);
}
// 中断处理函数的顶半部
irqreturn_t test_interrupt(int irq, void *args)
{
  printk("This is test_interrupt\n");
  // 将中断处理工作推迟到底半部
  return IRQ_WAKE_THREAD;
}

static int interrupt_irq_init(void)
{
  int ret;
  irq = gpio_to_irq(101); // 将GPIO映射为中断号
  printk("irq is %d\n", irq);
  // 用于请求并注册一个线程化的中断处理函数
  ret = request_threaded_irq(irq, test_interrupt, test_work, IRQF_TRIGGER_RISING, "test", NULL);
  if (ret < 0)
  {
    printk("request_irq is error\n");
    return -1;
  }

  return 0;
}

static void interrupt_irq_exit(void)
{
  free_irq(irq, NULL); // 释放中断
  printk("bye bye\n");
}

module_init(interrupt_irq_init);
module_exit(interrupt_irq_exit);

MODULE_LICENSE("GPL");
MODULE_AUTHOR("woniu");
```

---

[总目录](总目录.md) · [上一篇：并发与IO](12-%E5%B9%B6%E5%8F%91%E4%B8%8EIO.md) · [下一篇：工作队列与内核定时器](14-%E5%B7%A5%E4%BD%9C%E9%98%9F%E5%88%97%E4%B8%8E%E5%86%85%E6%A0%B8%E5%AE%9A%E6%97%B6%E5%99%A8.md)
