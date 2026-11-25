# 22-PWM子系统

[总目录](总目录.md) · [上一篇：设备树插件](21-%E8%AE%BE%E5%A4%87%E6%A0%91%E6%8F%92%E4%BB%B6.md) · [下一篇：输入子系统与设备节点命名](23-%E8%BE%93%E5%85%A5%E5%AD%90%E7%B3%BB%E7%BB%9F%E4%B8%8E%E8%AE%BE%E5%A4%87%E8%8A%82%E7%82%B9%E5%91%BD%E5%90%8D.md)

> 版本基线：Linux 6.1，面向 RK SDK。保留已完成的接口勘误；源码摘录与板级资源仍需对照实际 SDK。构建和适配说明见 [Linux 6.1 适配说明](整理记录/Linux6.1适配说明.md)。

[TOC]

<a id="part-40"></a>

## 22.1 PWM

**Pulse Width Modulation**： 脉冲宽度调制

### 22.1.1 RK3568 开发板 PWM 接口介绍

在 RK3568 数据手册中可以找到关于 PWM 接口的介绍， 具体如下所示：

![image-20250410192622724](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410192622724.png)

· 芯片内置 16 路 PWM 通道,可以独立控制和输出 PWM 波形。 并支持中断驱动,可以灵活响应中断事件。 · PWM 通道采用可编程的预分频器,可以先对总线时钟进行分频,然后再进行二次分频。 · PWM 通道内置了 32 位的定时/计数器功能。 · PWM 通道支持捕获模式,可以捕获外部输入信号的脉冲宽度等信息。 · PWM 通道支持连续输出模式和一次性输出模式。 · PWM 通道提供参考模式,可以输出各种占空比的波形。 · PWM 使用10位数据寄存器。

上面的 16 路 PWM 都属于硬件 PWM， 即由专门的 PWM 硬件模块来实现 PWM 输出， 关于硬件 PWM 的介绍如下所示：

硬件 PWM:

（ 1） 实现方式： 硬件 PWM 是由专门的 PWM 硬件模块实现 PWM 输出的方式。 （ 2） 优点: · CPU 占用低,PWM 输出由硬件模块自动完成,无需 CPU 介入。 · PWM 输出频率和分辨率高,可以达到高达 MHz 级的频率和 ns 级的分辨率。 · 输出波形稳定可靠,不易受 CPU 负载的影响。 （ 3） 缺点: · 需要专门的硬件 PWM 模块,成本较高。 · PWM 输出引脚受限,只能在预定义的引脚上输出。 iTOP-RK3568 关于硬件 PWM 引脚复用功能表如下所示， 可以根据该表格对 PWM 进行选用：

![image-20250410192754413](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410192754413.png)

¡

而当硬件 PWM 不够用的时候， 可以使用 GPIO 来模拟实现 PWM， 也可以称之为软件 PWM， 关于软件 PWM 的介绍如下所示：

软件 PWM: （1） 实现方式： 软件 PWM 是通过软件编程实现 PWM 输出的方式。 利用定时器中断或者循环计数的方式,在软件中控制输出引脚的高低电平切换时间,从而生成 PWM 波形。 （2） 优点: · 灵活性强,可以在任意 GPIO 引脚上生成 PWM 波形。 · 成本低,不需要额外的硬件 PWM 模块。 （3） 缺点: · CPU 占用较高,因为需要在中断服务程序或者循环中实时控制引脚电平。 · PWM 输出的频率和分辨率受 CPU 主频和中断响应时间的影响,无法高频高分辨率。 · 对 CPU 性能和实时性要求较高。 至此， 对于硬件 PWM 和软件 PWM 的介绍就完成了， 在后面的章节中会分别对硬件 PWM和软件 PWM 的使用进行讲解， 而在下一小节将对 PWM 实验所用到的外设 SG-90 舵机进行讲解。

### 22.1.2 PWM 子系统框架

整个 PWM 子系统可以用下面的框图来描述：

![image-20250410193000969](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193000969.png)

再上图中 PWM 子系统被划分为了三个层次， 分别为用户空间、 内核空间和硬件层， 内核空间包括 PWM 设备驱动层、 PWM 核心层和 PWM 适配器驱动层， 而本章的主要内容就是介绍PWM 子系统框架中的内核空间。

#### 22.1.2.1 PWM 设备驱动层

PWM 设备驱动层在 Linux 内核中扮演了一个关键的角色,它为上层应用程序提供了一个统一、 灵活和高效的 PWM 设备访问接口,大大简化了 PWM 设备的使用和集成,提高了整个系统的可扩展性和可维护性。 具体来说,PWM 设备驱动层包含以下几个关键部分: （1） pwm_device · 代表一个连接到 PWM 总线上的从设备。 · 包含从设备的 PWM 通道号、 所属的 PWM 控制器等信息。 （2） pwm_driver · 实现了具体 PWM 设备的驱动程序。 · 负责 PWM 设备的初始化、 配置、 启停等操作。 · 通过 pwm_chip 与 PWM 硬件设备进行交互。 · 向上层提供标准化的 PWM 设备访问接口。 （3） /dev/xxx 设备节点 · 为上层应用程序提供 PWM 设备访问的接口 · 通过打开/读写/控制设备节点,应用程序可以与 PWM 设备进行交互 · 内核 PWM 子系统负责将应用程序的操作转发到对应的 pwm_chip 驱动

#### 22.1.2.2 PWM 核心层

PWM 核心层是 Linux 内核中负责管理和控制 PWM 设备的重要组件。 它的主要作用如下: （1） PWM 设备管理 通过 struct pwm_device 统一描述 PWM 设备的信息,如设备名称、 所属控制器等。 为上层应用程序提供标准化的 PWM 设备访问 API。 （2） PWM 参数配置 提供 pwm_config 接口,用于配置 PWM 设备的工作参数,如周期、 占空比、 极性等。 将上层配置参数转换为底层硬件可以理解的形式,并通过适配器驱动进行设置。 （3） PWM 输出控制 提供 pwm_enable 和 pwm_disable 接口,用于控制 PWM 输出的开启和关闭。 负责调用适配器驱动程序的相应函数来执行实际的输出控制。 （3） PWM sysfs 接口 PWM 核心层还提供了一组基于 sysfs 的接口,用于上层应用程序对 PWM 设备进行配置和控制。 这些 sysfs 接口包括: /sys/class/pwm/pwmX/period: 设置 PWM 周期 /sys/class/pwm/pwmX/duty_cycle: 设置 PWM 占空比 /sys/class/pwm/pwmX/polarity: 设置 PWM 极性 /sys/class/pwm/pwmX/enable: 控制 PWM 输出的开启和关闭 通过读写这些 sysfs 文件,上层应用程序可以轻松地配置和控制 PWM 设备,无需直接调用内核 API。 总的来说, PWM 核心层是 Linux 内核中 PWM 子系统的重要组成部分,负责 PWM 设备的统一管理和控制,为上层应用程序提供了标准化的 PWM 设备访问接口,并集成了电源管理等高级特性,大大简化了 PWM 设备的使用。 在后面的章节中会对上述提到的两种 PWM 操作方法： 内核 PWM API 配置函数以及 PWM的 sysfs 的操作进行详细的讲解。

#### 22.1.2.3 PWM 适配器驱动层

PWM 适配器驱动层是连接 PWM 硬件和上层 PWM 核心层的关键组件,它负责对底层 PWM硬件进行抽象化封装,并适配不同类型的 PWM 设备,为上层提供标准化的硬件控制接口,同时还需要处理一些硬件相关的初始化、 状态管理和电源管理等任务。 这样的分层设计提高了 PWM子系统的可扩展性和可移植性。 PWM 适配器驱动层的具体作用如下所示： （1） 硬件抽象化 PWM 适配器驱动层负责对底层 PWM 硬件设备进行抽象化封装。 它定义了一组标准化的 pwm_chip 接口,包括设备初始化、 参数配置、 输出控制等功能。上层 PWM 核心层可以通过调用这些标准接口来间接控制底层 PWM 硬件,而不需要关注具体的硬件实现细节。 （2） 硬件适配 PWM适配器驱动程序需要实现 pwm_chip 接口中定义的各个函数,以适配底层PWM硬件的具体工作方式。 这些适配函数将上层 PWM 核心层的标准化请求,转换为底层硬件可以理解的操作指令。 通过这种适配层,PWM 核心层可以无缝地支持不同类型的 PWM 硬件设备。 （3） 硬件初始化 PWM 适配器驱动程序负责完成 PWM 硬件设备的初始化工作,包括 GPIO、 时钟、 电源等相关资源的配置和初始化。 在 PWM 设备注册时,适配器驱动会执行初始化操作,确保硬件设备处于可用状态。 （4） 状态管理 适配器驱动程序需要维护 PWM 硬件设备的当前状态,如设备是否已经被使能、 当前的工作参数等。 这些状态信息会反馈给上层 PWM 核心层,以确保核心层能够正确地控制和管理 PWM设备。

### 22.1.3 使用 sysfs 接口操作 pwm

在上一章节对于 PWM 子系统框架核心层的讲解中提到有两种操作 PWM 的方法， 分别是使用内核提供的 API 函数操作 PWM、 使用 sysfs 接口操作 PWM,在本章节将会对第二种方法使用 sysfs 接口操作 PWM 进行讲解。

#### 22.1.3.1 配置 PWM 设备树

要想操作 PWM， 首先需要将对应的 IO 口配置为 PWM 功能， 选用的 IO 口为 iTOP-RK3568背板 20 PIN GPIO 接口的 6 号引脚， 如下图所示：

![image-20250410193353135](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193353135.png)

根据 PWM 引脚服用表可知， PWM12_M1 功能引脚默认被复用为了串口 9， 如下图所示：

![image-20250410193409785](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193409785.png)

设备树中找到 uart9 节点， 将 status 从 okay 修改为 disabled， 修改完成如下图所示：

![image-20250410193448192](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193448192.png)

然后在该节点下面填充 pwm12 节点， 填充内容如下， 填充完成如下所示：

```c
&pwm12 {
	status = "okay";
	pinctrl-0 = <&pwm12m1_pins>;
};
```

编译烧写进入系统之后可以使用以下命令查看 pwm 设备信息，

> cat /sys/kernel/debug/pwm

![image-20250410193610816](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193610816.png)

根据 rk3568 的数据手册或者设备树可以得到 pwm12 的设备地址为 fe700000， 与上图的第一个设备相匹配， 就可以证明 PWM 配置成功了。

#### 22.1.3.2 使用 sysfs 操作 PWM

首先来到/sys/class/pwm/目录下， 如下图所示：

![image-20250410193704216](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193704216.png)

可以看到总共有四个设备， 匹配关系由下到上、 由小到大， 匹配关系如下所示：

> cat /sys/kernel/debug/pwm

![image-20250410193721160](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193721160.png)

PWM12_M1 对应为 pwmchip3， 进入 pwmchip3 目录之后如下图所示：

![image-20250410193746090](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193746090.png)

在这个目录下总共有七个文件分别为 device、 export、 npwm、 power、 subsystem、 uevent和 unexport。 需要关注的是 export、 npwm 以及 unexport 这三个属性文件， 下面一一进行介绍： npwm： 是一个只读属性， 读取该文件可以得知该 PWM 控制器下共有几路 PWM 输出，如下所示：

![image-20250410193810605](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193810605.png)

export： 在使用 PWM 之前， 通过 export 属性进行导出， 以下所示：

> echo 0 &gt; export

![image-20250410193836252](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193836252.png)

unexport： 当使用完 PWM 之后， 需要将导出的 PWM 删除， 譬如：

> echo 0 &gt; unexport

![image-20250410193904110](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410193904110.png)

写入到 unexport 文件中的编号与写入到 export 文件中的编号是相对应的； 需要注意的是，export 文件和 unexport 文件都是只写的、 没有读权限。 再次使用以下命令导出 pwm0 目录， 导出成功之后进入该文件夹.

可以看到 pwm0 文件夹下分别有 capture、 duty_cycle、 enable、 period、 polarity、 power、uevent 七个文件， 而需要了解的文件是 duty_cycle、 enable、 period 以及 polarity 这四个属性文件， 接下来分别介绍这四个属性文件的作用： polarity： 用于 PWM 极性的查看， 有 normal 和 inversed 可选， normal 表示 PWM 信号为正极性,即高电平为有效信号， inversed 表示 PWM 信号为负极性,即低电平为有效信号。 period： 用于配置 PWM 周期， 可读可写； 写入一个字符串数字值， 以 ns（ 纳秒） 为单位 duty_cycle： 用于配置 PWM 的占空比， 可读可写； 写入一个字符串数字值， 同样也是以ns 为单位。 enable： 使能 PWM 输出通常配置好 PWM 之后， 再使能 PWM。 可读可写， 写入"0"表示禁止 PWM； 写入"1"表示使能 PWM。

### 22.1.4 pwm 控制器注册流程分析

在上一章中讲解了如何使用 sysfs 接口控制 PWM， 而在本章节中将会对 pwm 控制器注册流程进行分析。 首先来到 rk3568.dtsi 设备树， 找到 pwm 相关的节点如下所示：

![image-20250410194102910](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250410194102910.png)

根据 PWM 节点的 compatible 属性进行查找， 可以找到瑞芯微的 PWM 驱动路径为内核目录下的 drivers/pwm/pwm-rockchip.c， 然后来看该驱动程序的 probe 函数， 具体内容如下所示：

```c
static int rockchip_pwm_probe(struct platform_device *pdev)
{
    const struct of_device_id *id; // 设备树匹配 ID
    struct rockchip_pwm_chip *pc;  // PWM 芯片结构体
    struct resource *r;            // 资源信息
    int ret, count;                // 返回值和计数变量
    // 检查设备树匹配
    id = of_match_device(rockchip_pwm_dt_ids, &pdev->dev);
    if (!id)
        return -EINVAL;
    // 分配 PWM 芯片结构体
    pc = devm_kzalloc(&pdev->dev, sizeof(*pc), GFP_KERNEL);
    if (!pc)
        return -ENOMEM;
    // 获取内存资源并映射 IO 地址
    r = platform_get_resource(pdev, IORESOURCE_MEM, 0);
    pc->base = devm_ioremap(&pdev->dev, r->start, resource_size(r));
    if (IS_ERR(pc->base))
        return PTR_ERR(pc->base);
    // 获取 PWM 总线时钟
    pc->clk = devm_clk_get(&pdev->dev, "pwm");
    if (IS_ERR(pc->clk))
    {
        pc->clk = devm_clk_get(&pdev->dev, NULL);
        if (IS_ERR(pc->clk))
        {
            ret = PTR_ERR(pc->clk);
            if (ret != -EPROBE_DEFER)
                dev_err(&pdev->dev, "Can't get bus clk: %d\n", ret);
            return ret;
        }
    }
    // 获取 APB 时钟 count = of_count_phandle_with_args(pdev->dev.of_node, "clocks", "#clock-cells");
    if (count == 2)
        pc->pclk = devm_clk_get(&pdev->dev, "pclk");
    else
        pc->pclk = pc->clk;
    if (IS_ERR(pc->pclk))
    {
        ret = PTR_ERR(pc->pclk);
        if (ret != -EPROBE_DEFER)
            dev_err(&pdev->dev, "Can't get APB clk: %d\n", ret);
        return ret;
    }
    // 使能总线时钟 ret = clk_prepare_enable(pc->clk);
    if (ret)
    {
        dev_err(&pdev->dev, "Can't prepare enable bus clk: %d\n", ret);
        return ret;
    }
    // 使能 APB 时钟
    ret = clk_prepare(pc->pclk);
    if (ret)
    {
        dev_err(&pdev->dev, "Can't prepare APB clk: %d\n", ret);
        goto err_clk;
    }
    // 获取引脚控制器
    pc->pinctrl = devm_pinctrl_get(&pdev->dev);
    if (IS_ERR(pc->pinctrl))
    {
        dev_err(&pdev->dev, "Get pinctrl failed!\n");
        return PTR_ERR(pc->pinctrl);
    }
    // 获取引脚控制器的活动状态 pc->active_state = pinctrl_lookup_state(pc->pinctrl, "active");
    if (IS_ERR(pc->active_state))
    {
        dev_err(&pdev->dev, "No active pinctrl state\n");
        return PTR_ERR(pc->active_state);
    }
    // 设置驱动数据 platform_set_drvdata(pdev, pc);
    // 初始化 PWM 芯片结构体
    pc->data = id->data;
    pc->chip.dev = &pdev->dev;
    pc->chip.ops = &rockchip_pwm_ops;
    pc->chip.base = -1;
    pc->chip.npwm = 1;
    pc->clk_rate = clk_get_rate(pc->clk);
    // 如果支持极性设置, 则使用带有极性的 of_pwm_xlate 函数
    if (pc->data->supports_polarity)
    {
        pc->chip.of_xlate = of_pwm_xlate_with_flags;
        pc->chip.of_pwm_n_cells = 3;
    }
    // 检查是否为中心对齐模式 pc->center_aligned =
        device_property_read_bool(&pdev->dev, "center-aligned");
    // 添加 PWM 芯片
    ret = pwmchip_add(&pc->chip);
    if (ret < 0)
    {
        dev_err(&pdev->dev, "pwmchip_add() failed: %d\n", ret);
        goto err_pclk;
    }
    // 如果 PWM 未启用,
        则禁用总线时钟 if (!pwm_is_enabled(pc->chip.pwms))
            clk_disable(pc->clk);
    return 0;
err_pclk:
    clk_unprepare(pc->pclk);
err_clk:
    clk_disable_unprepare(pc->clk);
    return ret;
}
```

在第 4 行创建了一个 struct rockchip_pwm_chip 类型的指针变量， 它主要用于描述 Rockchip 系列 SoC 上的 PWM 控制器的硬件特性和配置信息， 具体内容如下所示：

```c
struct rockchip_pwm_chip {
  struct pwm_chip chip; // 通用 PWM 控制器芯片接口
  struct clk *clk; // PWM 控制器的主时钟
  struct clk *pclk; // PWM 控制器的外设时钟
  struct pinctrl *pinctrl; // PWM 控制器的引脚复用控制器
  struct pinctrl_state *active_state; // PWM 控制器当前使用的引脚状态
  const struct rockchip_pwm_data *data; // 特定于 Rockchip SoC 的 PWM 控制器配置信息
  void __iomem *base; // PWM 控制器寄存器空间的内核虚拟地址
  unsigned long clk_rate; // PWM 控制器当前使用的时钟频率
  bool vop_pwm_en; // 标识 VOP (视频输出处理器) 是否也使能了 PWM 功能
  bool center_aligned; // 标识 PWM 控制器是否支持中心对齐模式
  bool oneshot; // 标识 PWM 控制器是否支持单次触发模式
};
```

其中第二行的 struct pwm_chip 结构体是 PWM 子系统中对 PWM 控制器的一种抽象和封装。 它将 PWM 控制器的基本信息和操作函数集中到一个结构体中,方便上层 PWM 框架进行管理和调用， 该结构体定义在 include/linux/pwm.h 文件中， 具体内容如下所示：

```c
struct pwm_chip {
  struct device *dev; // PWM 控制器所属的设备
  struct list_head list; // PWM 控制器所在的全局链表
  const struct pwm_ops *ops; // PWM 控制器的操作函数集
  int base; // PWM 控制器的寄存器基地址偏移
  unsigned int npwm; // PWM 控制器提供的 PWM 通道数量
  struct pwm_device *pwms; // PWM 通道设备数组
  struct pwm_device * (*of_xlate)(struct pwm_chip *pc,const struct of_phandle_args *args);
  unsigned int of_pwm_n_cells; // 设备树中 PWM 属性描述所需的属性数量
};
```

关于结构体中每个成员的注释已经进行了添加， 其中第四行表示 PWM 控制器的操作函数集， 具体内容如下所示：

```c
struct pwm_ops {
  int (*request)(struct pwm_chip *chip, struct pwm_device *pwm);
  void (*free)(struct pwm_chip *chip, struct pwm_device *pwm);
  int (*config)(struct pwm_chip *chip, struct pwm_device *pwm,
  int duty_ns, int period_ns);
  int (*config_extend)(struct pwm_chip *chip, struct pwm_device *pwm,
  u64 duty_ns, u64 period_ns);
  int (*set_polarity)(struct pwm_chip *chip, struct pwm_device *pwm,
  enum pwm_polarity polarity);
  int (*capture)(struct pwm_chip *chip, struct pwm_device *pwm,
  struct pwm_capture *result, unsigned long timeout);
  int (*enable)(struct pwm_chip *chip, struct pwm_device *pwm);
  void (*disable)(struct pwm_chip *chip, struct pwm_device *pwm);
  int (*get_output_type_supported)(struct pwm_chip *chip,
  struct pwm_device *pwm);
  int (*set_output_type)(struct pwm_chip *chip, struct pwm_device *pwm,
  enum pwm_output_type output_type);
  int (*set_output_pattern)(struct pwm_chip *chip,
  struct pwm_device *pwm,
  struct pwm_output_pattern *output_pattern);
  int (*apply)(struct pwm_chip *chip, struct pwm_device *pwm,
  struct pwm_state *state);
  void (*get_state)(struct pwm_chip *chip, struct pwm_device *pwm,
  struct pwm_state *state);
  #ifdef CONFIG_DEBUG_FS
  void (*dbg_show)(struct pwm_chip *chip, struct seq_file *s);
  #endif
  struct module *owner;
};
```

然后回到 drivers/pwm/pwm-rockchip.c 文件中找到 rockchip_pwm_ops 操作集， 可以发现瑞芯微只实现了状态获取和申请两个函数， 具体内容如下所示：

```c
static const struct pwm_ops rockchip_pwm_ops = {
  .get_state = rockchip_pwm_get_state,
  .apply = rockchip_pwm_apply,
  .owner = THIS_MODULE,
};
```

而 PWM 还可以实现输入捕获的功能， 但瑞芯微只实现了这两个操作集函数， 所以要想用上 PWM 的输入捕获， 就需要我们自己编写驱动了， 在本篇内容的最后一个章节， 将会编写晚上 PWM 输入捕获驱动， 然后我们继续回到 drivers/pwm/pwm-rockchip.c 驱动的 probe 函数的讲解：

第 8-16 行： 检查设备树匹配情况并分配 PWM 芯片结构体。 第 18-22 行： 获取内存资源并映射 IO 地址。 第 36-62 行： 获取 PWM 总线时钟和 APB 时钟, 并使能这些时钟。 第 64-76 行： 获取引脚控制器并获取活动状态。 第 81-97 行： 初始化 PWM 芯片结构体, 包括支持极性设置和中心对齐模式的配置。 第 99-109： 将 PWM 芯片添加到系统中, 如果 PWM 未启用则禁用总线时钟。 在第 100 行调用了 pwmchip_add 函数将 PWM 控制器添加到 PWM 子系统中， pwmchip_add 函数定义在 drivers/pwm/core.c 文件中， 具体内容如下所示：

```c
int pwmchip_add(struct pwm_chip *chip)
{
    return pwmchip_add_with_polarity(chip, PWM_POLARITY_NORMAL);
}
int pwmchip_add_with_polarity(struct pwm_chip *chip,
                              enum pwm_polarity polarity)
{
    struct pwm_device *pwm;
    unsigned int i;
    int ret;
    // 检查 chip 结构体的有效性
    if (!chip || !chip->dev || !chip->ops || !chip->npwm)
        return -EINVAL;
    // 检查 pwm_ops 结构体的有效性
    if (!pwm_ops_check(chip->ops))
        return -EINVAL;
    // 获取全局 pwm_lock 互斥锁
    mutex_lock(&pwm_lock);
    // 为 chip 分配 PWM 设备索引号
    ret = alloc_pwms(chip->base, chip->npwm);
    if (ret < 0)
        goto out;
    // 动态分配 chip->npwm 个 pwm_device 结构体
    chip->pwms = kcalloc(chip->npwm, sizeof(*pwm), GFP_KERNEL);
    if (!chip->pwms)
    {
        ret = -ENOMEM;
        goto out;
    }
    // 保存分配的 PWM 设备索引号 chip->base = ret;
    // 初始化每个 PWM 设备
    for (i = 0; i < chip->npwm; i++)
    {
        pwm = &chip->pwms[i];
        pwm->chip = chip;
        pwm->pwm = chip->base + i;
        pwm->hwpwm = i;
        pwm->state.polarity = polarity;
        pwm->state.output_type = PWM_OUTPUT_FIXED;
        // 如果 chip->ops->get_state 存在,则获取当前 PWM 设备的状态
        if (chip->ops->get_state)
            chip->ops->get_state(chip, pwm, &pwm->state);
        // 将 PWM 设备添加到全局 PWM 设备树中
        radix_tree_insert(&pwm_tree, pwm->pwm, pwm);
    }
    // 标记分配的 PWM 设备为已使用 bitmap_set(allocated_pwms, chip->base, chip->npwm);
    // 将 PWM 控制器添加到全局 PWM 控制器链表
    INIT_LIST_HEAD(&chip->list);
    list_add(&chip->list, &pwm_chips);
    ret = 0;
    // 如果内核开启了 Device Tree 支持,则注册 PWM 控制器到 Device Tree
    if (IS_ENABLED(CONFIG_OF))
        of_pwmchip_add(chip);
out:
    // 释放全局 pwm_lock 互斥锁
    mutex_unlock(&pwm_lock);
    // 如果添加成功,则在 sysfs 中导出 PWM 控制器
    if (!ret)
        pwmchip_sysfs_export(chip);
    return ret;
}
```

这个函数的主要作用是初始化一个新的 PWM 控制器,并在第 62 行调用 list_add 函数将其添加到 PWM 子系统的管理中。

### 22.1.5 pwm 子系统 API 讲解

#### 22.1.5.1 pwm_config 函数

（1） 函数原型:

```c
int pwm_config(struct pwm_device *pwm, int duty_ns, int period_ns);
```

pwm_config(pwm, duty_ns, period_ns) 的单位均为纳秒；duty_ns 是有效态持续时间，不是百分数。正常极性下有效态为高电平，反相极性下有效态为低电平。函数成功返回 0，失败返回负 errno。Linux 6.1 仍保留这个兼容辅助函数；需要同时设置周期、占空时间、极性和使能状态时，推荐下一节的 pwm_state 接口。

#### 22.1.5.2 pwm_state 与 pwm_apply_state

Linux 6.1 使用下面的状态接口统一设置极性、周期、有效时间和使能状态，不再使用旧的 pwm_set_polarity：

```c
struct pwm_state state;
pwm_init_state(pwm, &state);
state.period = 1000000;       /* 1 ms */
state.duty_cycle = 500000;    /* 50% */
state.polarity = PWM_POLARITY_NORMAL;
state.enabled = true;
ret = pwm_apply_state(pwm, &state); /* 检查负 errno */
```

该接口一次提交完整状态；是否无毛刺切换由具体控制器能力决定。









#### 22.1.5.3 pwm_enable 函数

（ 1） 函数原型:

```c
int pwm_enable(struct pwm_device *pwm);
```

（ 2） 函数作用: 使能 PWM 信号， 即开始输出 PWM 信号。 （ 3） 函数参数: struct pwm_device \*pwm: 指向 PWM 设备结构体的指针。 （ 4） 返回值: 成功时返回 0。 失败时返回负数， 表示具体的错误码。 （ 5） 详细讲解: pwm_enable 函数用于使能 PWM 信号。 调用此函数后， PWM 控制器开始输出配置好的PWM 信号。 这个函数通常在 pwm_config 之后调用， 以确保 PWM 信号参数已经正确配置。

#### 22.1.5.4 pwm_disable 函数

（ 1） 函数原型:

```c
void pwm_disable(struct pwm_device *pwm);
```

（ 2） 函数作用: 关闭 PWM 信号， 即停止输出 PWM 信号。 （ 3） 函数参数: struct pwm_device \*pwm: 指向 PWM 设备结构体的指针。 （ 4） 返回值: 无返回值。 （5） 详细讲解: pwm_disable 函数用于关闭 PWM 信号。 调用此函数后， PWM 控制器停止输出 PWM信号。 这在不需要 PWM 信号时非常有用， 可以节省电力或防止不必要的信号输出。

#### 22.1.5.5 devm_pwm_get 函数

Linux 6.1 通过消费者设备的固件节点查找 pwms / pwm-names：

```c
struct pwm_device *devm_pwm_get(struct device *dev, const char *con_id);
```

成功返回 PWM 描述对象，失败返回 ERR_PTR，应使用 IS_ERR/PTR_ERR 并传播 -EPROBE_DEFER。devm 管理对象释放不等于替驱动关闭 PWM 输出，卸载时仍应设置禁用状态。









#### 22.1.5.6 驱动代码

设备树

```c
	woniu_pwm:woniu_pwm{
		compatible = "woniu_pwm";
        pwms = <&pwm0 0 1000000 0>; /* 1 ms，正常极性；核对控制器 #pwm-cells */
		pwm-names = "backlight";
	};
```

驱动

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/mod_devicetable.h>
#include <linux/of.h>
#include <linux/pwm.h>

struct pwm_device * pwm_dev;

//设备和驱动匹配成功时执行
static int my_probe(struct platform_device *pdev)
{
    struct pwm_state state;
    pwm_dev = devm_pwm_get(&pdev->dev, "backlight");
    if (IS_ERR(pwm_dev))
        return dev_err_probe(&pdev->dev, PTR_ERR(pwm_dev), "get PWM failed\n");
    pwm_init_state(pwm_dev, &state);
    state.period = 1000000;
    state.duty_cycle = 500000;
    state.polarity = PWM_POLARITY_NORMAL;
    state.enabled = true;
    return pwm_apply_state(pwm_dev, &state);
}

static int my_remove(struct platform_device *pdev)
{
    struct pwm_state state;
    int ret;
    pwm_get_state(pwm_dev, &state);
    state.enabled = false;
    ret = pwm_apply_state(pwm_dev, &state);
    if (ret) dev_warn(&pdev->dev, "disable PWM failed: %d\n", ret);
    return 0; /* Linux 6.1 platform_driver.remove 返回 int */
}




























static void my_shutdown(struct platform_device * pdev){
	printk(KERN_INFO "my_shutdown\n");
}
static int my_suspend(struct platform_device * pdev, pm_message_t state){
	printk(KERN_INFO "my_suspend\n");
	return 0;
}
static int my_resume(struct platform_device * pdev){
	printk(KERN_INFO "my_resume\n");
	return 0;
}

struct of_device_id match_table[] = {
	{
		.compatible = "woniu_pwm", //设备树中的compatible字段
	},
	{},
};

//平台驱动
static struct platform_driver my_driver = {
	.probe = my_probe,
	.remove = my_remove,
	.shutdown = my_shutdown,
	.suspend = my_suspend,
	.resume = my_resume,
	.driver = {
		.name = "woniu_pwm",   //平台总线上和设备和驱动靠name来匹配
		.owner = THIS_MODULE,
		.of_match_table = match_table,
	},
};

//入口函数
static int my_init(void){
	int ret;
	//向平台总线上注册驱动
	ret = platform_driver_register(&my_driver);
	if(ret<0){
		printk(KERN_ERR "platform_driver_register failed\n");
		return ret;
	}
	return 0;
}
//出口函数
static void my_exit(void){
	platform_driver_unregister(&my_driver);
}

//注册驱动的入口函数，
module_init(my_init);
//注册驱动的出口函数
module_exit(my_exit);
//开源协议
MODULE_LICENSE("GPL");
MODULE_AUTHOR("woniu");
```

### 22.1.6 软件PWM

在前面的章节中分别使用 sysfs 和内核 API 函数对硬件 PWM 进行控制， 而当硬件 PWM 不够用的时候， 可以使用 GPIO 来模拟实现 PWM， 也可以称之为软件 PWM， 软件 PWM 是通过软件编程实现 PWM 输出的方式， 利用定时器中断或者循环计数的方式,在软件中控制输出引脚的高低电平切换时间,从而生成 PWM 波形。 在本章节中将通过模拟 PWM 来实现 LED 灯光亮度的调节。

#### 22.1.6.1 高精度定时器介绍

软件 PWM 可以用 hrtimer 定时翻转 GPIO。hrtimer 使用 ktime_t 表示时间，常用 CLOCK_MONOTONIC 单调时钟；纳秒是表示单位，并不保证 GPIO 边沿具有纳秒级精度。中断延迟、系统负载及 GPIO 控制器都会引入抖动，稳定 PWM 优先使用硬件 PWM。

以下为概念性字段摘录，完整布局以目标 BSP 的 include/linux/hrtimer.h 为准：

```c
struct hrtimer {
    struct timerqueue_node node;
    ktime_t _softexpires;
    enum hrtimer_restart (*function)(struct hrtimer *);
    struct hrtimer_clock_base *base;
    u8 state;
    /* 其余字段省略 */
};
```











高精度定时器工作流程如下:

工作流程：先调用 hrtimer_init 初始化并设置回调；用 ktime_set/ns_to_ktime 构造时间，用 hrtimer_start 入队启动。回调返回 HRTIMER_NORESTART 表示停止；周期任务可先 hrtimer_forward/forward_now 再返回 HRTIMER_RESTART。hrtimer_cancel 取消定时器并等待正在执行的回调完成。hrtimer_start_range_ns 的 delta_ns 是允许的时间松弛范围，用于合并唤醒，并非增大参数就提高精度。

#### 22.1.6.2 高精度定时器 API

##### 22.1.6.2.1 hrtimer_init

hrtimer_init() 函数用于初始化一个高精度定时器(struct hrtimer)。 它会设置定时器所使用的时钟源和定时器的工作模式。 函数原型:

```c
void hrtimer_init(struct hrtimer *timer, clockid_t clockid, enum hrtimer_mode mode);
```

函数参数: （1） struct hrtimer \*timer: 这是指向 hrtimer 结构体的指针。 hrtimer 结构体包含了定时器的状态、 回调函数以及其他相关数据。 （2） clockid_t clock_id: 指定定时器使用的时钟。 常见的值包括： CLOCK_MONOTONIC: 系统级的单调时钟， 从某个未指定的时间点开始， 不能被设置。 CLOCK_REALTIME: 系统级的实时时钟。 CLOCK_BOOTTIME: 类似于 CLOCK_MONOTONIC， 但包括挂起时间。 CLOCK_TAI: 国际原子时。 （3） enum hrtimer_mode mode: 指定定时器的模式。 模式包括： HRTIMER_MODE_ABS: 绝对模式， 定时器将在绝对时间触发。 HRTIMER_MODE_REL: 相对模式， 定时器将在相对时间后触发。 HRTIMER_MODE_PINNED: 定时器绑定到特定的 CPU。 HRTIMER_MODE_SOFT: 使用软中断上下文。

##### 22.1.6.2.2 ktime_set 与 hrtimer_set_expires

Linux 6.1 没有本节原先写的 `hrtimer_set(timer, time, mode)` 接口。`ktime_set(seconds, nanoseconds)` 构造时间值；`hrtimer_set_expires(timer, expires)` 只设置到期值，不负责启动。通常直接用下面的 hrtimer_start 示例即可。

```c
ktime_t interval = ktime_set(0, 1000000); /* 1 ms */
/* my_timer 已初始化并设置回调后： */
hrtimer_start(&my_timer, interval, HRTIMER_MODE_REL);
```















##### 22.1.6.2.3 hrtimer_start

hrtimer_start 函数用于启动高分辨率定时器。 它会将定时器添加到内核的定时器队列中。 函数原型:

```c
void hrtimer_start(struct hrtimer *timer, ktime_t time, const enum hrtimer_mode mode);
```

参数说明: （1） struct hrtimer \*timer： 指向要启动的 hrtimer 结构体的指针。 （2） ktime_t time： 定时器到期时间， 可以是绝对时间或相对时间。 （3） enum hrtimer_mode mode： 定时器模式， 指定是相对模式还是绝对模式。 返回值: 无（void）。 使用示例:

```c
/* 假设 my_callback 为已定义的回调。 */
struct hrtimer my_timer;
ktime_t interval = ktime_set(0, 1000000);
hrtimer_init(&my_timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
my_timer.function = my_callback;
hrtimer_start(&my_timer, interval, HRTIMER_MODE_REL);


```

##### 22.1.6.2.4 hrtimer_forward

hrtimer_forward 函数用于将定时器的到期时间向前推进一个指定的时间间隔。 该函数通常在定时器回调函数中使用， 以实现周期性定时器。

函数原型:

```c
u64 hrtimer_forward(struct hrtimer *timer, ktime_t now, ktime_t interval);
```

参数说明: struct hrtimer \*timer： 指向要推进的 hrtimer 结构体的指针。 ktime_t now： 当前时间。 ktime_t interval： 推进的时间间隔。 返回值: 返回跨过的周期数（overruns），不是新的到期时间；本函数更新到期时间但不负责重新入队。 使用示例:

```c
enum hrtimer_restart my_timer_callback(struct hrtimer *timer)
{
  ktime_t now = hrtimer_cb_get_time(timer);
  ktime_t interval = ktime_set(0, 1000000); // 1 毫秒
  hrtimer_forward(timer, now, interval); // 推进定时器
  return HRTIMER_RESTART;
}
```

##### 22.1.6.2.5 hrtimer_cancel

hrtimer_cancel 函数用于取消已经启动的高分辨率定时器。 如果定时器正在等待超时， 则将其从队列中移除。 函数原型:

```c
int hrtimer_cancel(struct hrtimer *timer);
```

参数说明: struct hrtimer \*timer： 指向要取消的 hrtimer 结构体的指针。 返回值: 如果定时器正在活动中， 返回 1。 如果定时器已经停止， 返回 0。

#### 22.1.6.3 驱动代码

```c
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/mod_devicetable.h>
#include <linux/gpio/consumer.h>
#include <linux/slab.h>
#include <linux/interrupt.h>
#include <linux/of_irq.h>
#include <linux/input.h>
#include <linux/workqueue.h>
#include <linux/delay.h>
#include <linux/pwm.h>
#include <linux/cdev.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/timer.h>
#include <linux/hrtimer.h>

int i = 0;
ktime_t time;
//高精度定时器的函数
static enum hrtimer_restart	my_hrtimer_function(struct hrtimer * hrtimer){
    printk("timer %d\n", i++);
    //让定时器跳到下一个定时节点
    //ktime_t now = hrtimer_cb_get_time(hrtimer);   //获取一下当前的时间
    //ktime_t interval = ktime_set(0, 100000000); // 100 ms
    hrtimer_forward(hrtimer, hrtimer_cb_get_time(hrtimer), time); // 推进定时器
    return HRTIMER_RESTART;
}

struct hrtimer timer;

static int my_hrtimer_init(void)
{
    int ret;
    //初始化hrtimer
    hrtimer_init(&timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
    // 周期为 1 秒
    time = ktime_set(1, 0);

    //在初始化后再来赋目标函数
    timer.function = my_hrtimer_function;
    //启动hrtimer
    hrtimer_start(&timer, time, HRTIMER_MODE_REL);
    return 0;
}

static void my_hrtimer_exit(void)
{
    hrtimer_cancel(&timer);
}

module_init(my_hrtimer_init);
module_exit(my_hrtimer_exit);
MODULE_LICENSE("GPL v2");
MODULE_AUTHOR("woniu");
```

![20250728104231](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/20250728104231.png)

![](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/20250728104231.png)

![img](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/O1CN01rSDcFy1L65SiZ2qqh_!!2086061249.jpg)

![image-20250728104641913](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250728104641913.png)

![image-20250728105817822](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250728105817822.png)

#### 22.1.6.4 hrtimer 实现 PWM 驱动

本示例用于单设备教学，只接受二进制 unsigned int 占空比 1～99；不能用 echo 文本设置。GPIO 必须支持非睡眠访问，GPIO 翻转有调度抖动。这里限制占空比和周期以避免零长度定时间隔；0%/100% 输出应另走恒定电平路径。

设备树

```c
	woniu_pwm: woniu-pwm{
		compatible = "woniu_pwm";
        pwm-gpios = <&gpio4 RK_PC6 GPIO_ACTIVE_HIGH>;
		period = <20000000>;
	};
```

驱动

```c
#include <linux/module.h>
#include <linux/hrtimer.h>
#include <linux/of_platform.h>
#include <linux/cdev.h>
#include <linux/fs.h>
#include <linux/uaccess.h>
#include <linux/io.h>
#include <linux/gpio/consumer.h>
#include <linux/hrtimer.h>
#include <linux/math64.h>
#include <linux/err.h>
struct hrtimer timer;
ktime_t time;

char kbuf[100];
dev_t dev_num;
struct cdev my_dev;
struct class * pwm_class;
struct device * pwm_device;
unsigned int pwm_duty = 10;  //占空比是10%
u32 pwm_period;
struct gpio_desc * pwm_gpio;
//标识当前pwm是高还是低
int pwm_high = 1;

//用于响应用户空间中的write函数
static ssize_t pwm_write (struct file * file, const char __user * buf, size_t size, loff_t * offset){
    unsigned int duty;
    if (size != sizeof(duty)) return -EINVAL;
    if (copy_from_user(&duty, buf, sizeof(duty))) return -EFAULT;
    if (duty == 0 || duty >= 100) return -ERANGE;
    WRITE_ONCE(pwm_duty, duty);
    return sizeof(duty);


}

//用于响应用户空间中的read函数
static ssize_t pwm_read (struct file * file, char __user * buf, size_t size, loff_t * offset){
    unsigned int duty = READ_ONCE(pwm_duty);
    return simple_read_from_buffer(buf, size, offset, &duty, sizeof(duty));



}

static int pwm_open (struct inode * inode, struct file * file){
    printk("pwm_open calpwm......\n");
    return 0;
}

static int pwm_release (struct inode * inode, struct file * file){
    printk("pwm_release calpwm......\n");
    return 0;
}

struct file_operations pwm_fops = {
    .owner = THIS_MODULE,
    .write = pwm_write,
    .read = pwm_read,
    .open = pwm_open,
    .release = pwm_release,
};

static enum hrtimer_restart pwm_callback(struct hrtimer *timer)
{
    u32 duty = READ_ONCE(pwm_duty);
    u64 high_ns = div_u64((u64)pwm_period * duty, 100);
    u64 interval_ns;
    pwm_high = !pwm_high;
    gpiod_set_value(pwm_gpio, pwm_high);
    interval_ns = pwm_high ? high_ns : pwm_period - high_ns;
    hrtimer_forward_now(timer, ns_to_ktime(interval_ns));
    return HRTIMER_RESTART;
}













/**
 * 当驱动和设备树中的compatible匹配时，就会调用pwm_probe函数。
 */
static int pwm_probe(struct platform_device * pdev){
    int ret;
    ret = of_property_read_u32(pdev->dev.of_node, "period", &pwm_period);
    if (ret) return ret;
    if (pwm_period < 100) return -EINVAL;
    pwm_gpio = devm_gpiod_get(&pdev->dev, "pwm", GPIOD_OUT_LOW);
    if (IS_ERR(pwm_gpio)) return PTR_ERR(pwm_gpio);
    if (gpiod_cansleep(pwm_gpio)) return -EINVAL;
    hrtimer_init(&timer, CLOCK_MONOTONIC, HRTIMER_MODE_REL);
    timer.function = pwm_callback;
    ret = alloc_chrdev_region(&dev_num, 0, 1, "woniu-pwm");
    if (ret) return ret;
    cdev_init(&my_dev, &pwm_fops);
    my_dev.owner = THIS_MODULE;
    ret = cdev_add(&my_dev, dev_num, 1);
    if (ret) goto err_number;
    pwm_class = class_create(THIS_MODULE, "woniu_pwm");
    if (IS_ERR(pwm_class)) { ret = PTR_ERR(pwm_class); goto err_cdev; }
    pwm_device = device_create(pwm_class, NULL, dev_num, NULL, "pwm_dev");
    if (IS_ERR(pwm_device)) { ret = PTR_ERR(pwm_device); goto err_class; }
    pwm_high = 1;
    gpiod_set_value(pwm_gpio, 1);
    time = ns_to_ktime(div_u64((u64)pwm_period * READ_ONCE(pwm_duty), 100));
    hrtimer_start(&timer, time, HRTIMER_MODE_REL);
    return 0;
err_class:
    class_destroy(pwm_class);
err_cdev:
    cdev_del(&my_dev);
err_number:
    unregister_chrdev_region(dev_num, 1);
    return ret;






































}
static int pwm_remove(struct platform_device * pdev){
    hrtimer_cancel(&timer);
    gpiod_set_value(pwm_gpio, 0);
    //注销设备节点
    device_destroy(pwm_class, dev_num);
    //注销设备类
    class_destroy(pwm_class);
    //注销字符设备
    cdev_del(&my_dev);
    //释放设备号
    unregister_chrdev_region(dev_num, 1);
    return 0;
}

struct of_device_id pwm_of_match[] = {
    {
        .compatible = "woniu_pwm",
    },
    {},
};

struct platform_driver pwm_driver = {
   .probe = pwm_probe,
   .remove = pwm_remove,
   .driver = {
        .name = "pwm_drv",
        .owner = THIS_MODULE,
        .of_match_table = pwm_of_match,
   },
};

static int woniu_init(void)
{
    return platform_driver_register(&pwm_driver);



}

static void woniu_exit(void){
    platform_driver_unregister(&pwm_driver);
}

//驱动的入口函数
module_init(woniu_init);
//驱动的出口函数
module_exit(woniu_exit);
//驱动的开源协议
MODULE_LICENSE("GPL");
//驱动的作者
MODULE_AUTHOR("woniu");
```

---

[总目录](总目录.md) · [上一篇：设备模型和总线](20-%E8%AE%BE%E5%A4%87%E6%A8%A1%E5%9E%8B%E5%92%8C%E6%80%BB%E7%BA%BF.md) · [下一篇：输入子系统与设备节点命名](23-%E8%BE%93%E5%85%A5%E5%AD%90%E7%B3%BB%E7%BB%9F%E4%B8%8E%E8%AE%BE%E5%A4%87%E8%8A%82%E7%82%B9%E5%91%BD%E5%90%8D.md)
