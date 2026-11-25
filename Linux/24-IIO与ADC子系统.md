# 24-IIO与ADC子系统

[总目录](总目录.md) · [上一篇：输入子系统与设备节点命名](23-%E8%BE%93%E5%85%A5%E5%AD%90%E7%B3%BB%E7%BB%9F%E4%B8%8E%E8%AE%BE%E5%A4%87%E8%8A%82%E7%82%B9%E5%91%BD%E5%90%8D.md) · [下一篇：U-Boot基础与源码启动流程](25-U-Boot%E5%9F%BA%E7%A1%80%E4%B8%8E%E6%BA%90%E7%A0%81%E5%90%AF%E5%8A%A8%E6%B5%81%E7%A8%8B.md)

> 版本基线：Linux 6.1，面向 RK SDK。保留已完成的接口勘误；源码摘录与板级资源仍需对照实际 SDK。构建和适配说明见 [Linux 6.1 适配说明](整理记录/Linux6.1适配说明.md)。

[TOC]

<a id="part-43"></a>

## 24.1 IIO子系统

**工业 I/O（IIO）**是专用于模数转换器（ADC）和数模转换器（DAC）的内核子系统。随着越来越多的具有不同代码实现的传感器（具有模拟到数字或数字到模拟，功能的测量设备）分散在内核源上，收集它们变得必要。这就是 IIO 框架以通用的方式所做的事情。自 2009 年以来，Jonathan Cameron 和 Linux-IIO 社区一直在开发它。

IIO 模型基于设备和通道架构：

- ​       设备代表芯片本身。它是层次结构的顶级。      
- ​       通道代表设备的单个采集线。设备可以具有一个或多个通道。例如，加速度计是具有  三个通道的装置，每个通道对应一个轴（X，Y 和 Z）。      

IIO 芯片是物理和硬件传感器 / 转换器。它作为字符设备（当支持触发缓冲时）暴露给用户空间，以及包含一组文件的 sysfs 目录条目，其中一些文件代表通道。单个通道用单个 sysfs 文件条目表示。

下面是从用户空间与 IIO 驱动程序交互的两种方式：

- ​       /sys/bus/iio/devices/iio:deviceX/: 表示传感器及其通道      
- ​       /dev/iio:deviceX: 表示导出设备事件和数据缓冲区的字符设备      

![img](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/66018bd3-7b37-4a0c-acbe-cd303625b832.png)

### 24.1.1 IIO 框架架构和布局

上图显示了如何在内核和用户空间之间组织 IIO 框架。驱动程序使用 IIO 核心公开的一组工具和 API 来管理硬件并向 IIO 核心报告处理。然后，IIO 子系统通过 sysfs 接口和字符设备将整个底层机制抽象到用户空间，用户可以在其上执行系统调用。

IIO API 分布在多个头文件中，如下所示：

```c
#include <linux/iio/iio.h>    /* mandatory */
#include <linux/iio/sysfs.h>  /* mandatory since sysfs is used */
#include <linux/iio/events.h> /* For advanced users, to manage iio events */
#include <linux/iio/buffer.h> /* mandatory to use triggered buffers */
#include <linux/iio/trigger.h>/* Only if you implement trigger in your driver (rarely used)*/
```

我们将描述和处理 IIO 框架的每个概念，例如

- ​       遍历其数据结构（设备，通道等）      
- ​       触发缓冲支持和连续捕获，以及其 sysfs 接口      
- ​       探索现有的 IIO 触发器      
- ​       以单次模式或连续模式捕获数据      
- ​       列出可用于帮助开发人员测试其设备的可用工具      

### 24.1.2 IIO 数据结构

IIO 设备在内核中表示为 struct iio_dev 结构体的一个实例，并由 struct iio_info 结构体描述。所有重要的 IIO 结构都在 include/linux/iio/iio.h 中定义。

#### 24.1.2.1 iio_dev 结构体

该结构代表 IIO 设备，描述设备和驱动程序。它告诉我们：

- 设备上有多少个通道？
- 设备可以在哪些模式下运行：单次，触发缓冲？
- 这个驱动程序可以使用哪些 hooks 钩子？

```c
struct iio_dev {
   /* Linux 6.1 字段节选，其余省略 */
   int modes;
   /* 当前模式通过 iio_device_get_current_mode() 查询 */
   struct device dev;
   struct iio_buffer *buffer;
   int scan_bytes;
   const unsigned long *available_scan_masks;
   const unsigned long *active_scan_mask;
   bool scan_timestamp;
   struct iio_trigger *trig;
   struct iio_poll_func *pollfunc;
   struct iio_chan_spec const *channels;
   int num_channels;
   const char *name;
   const struct iio_info *info;
   const struct iio_buffer_setup_ops *setup_ops;
   /* 字符设备等内部状态由 IIO 核心管理 */
};
```

完整的结构在 IIO 头文件中定义。我们将不感兴趣的字段在此处删除。

- modes: 这表示设备支持的不同模式。支持的模式有：

- - ​        INDIO_DIRECT_MODE 表示设备提供的 sysfs 接口。       
  - ​        INDIO_BUFFER_TRIGGERED 表示设备支持硬件触发器。使用 iio_triggered_buffer_setup（）函数设置触发缓冲区时，此模式会自动添加到设备中.       
  - ​        INDIO_BUFFER_HARDWARE 表示设备具有硬件缓冲区。       
  - ​        INDIO_ALL_BUFFER_MODES 是上述两者的联合。       

- 当前模式：Linux 6.1 通过 iio_device_get_current_mode(indio_dev) 查询，不访问旧的 currentmode 字段。

- dev: 这表示 IIO 设备所依赖的 struct 设备（根据 Linux 设备型号）。

- buffer: 这是您的数据缓冲区，在使用触发缓冲区模式时会推送到用户空间。使用 iio_triggered_buffer_setup 函数启用触发缓冲区支持时，它会自动分配并与您的设备关联。

- scan_bytes: 这是捕获并馈送到缓冲区的字节数。当从用户空间使用触发缓冲区时，缓冲区应至少为 indio-> scan_bytes 字节大。

- available_scan_masks: 这是允许的位掩码的可选数组。使用触发缓冲器时，可以启用通道捕获并将其馈入 IIO  缓冲区。如果您不想允许某些通道启用，则应仅使用允许的通道填充此数组。以下是为加速度计（带有 X，Y 和 Z 通道）提供扫描掩码的示例：

```c
/* 0 是列表结束标记，不是第二个合法扫描配置。
 * 0x7 表示提供三通道扫描组合；用户请求子集时，核心还可能选用
 * 包含该子集的扫描组合并过滤数据，不能据此断言只能开全或全关。 */





static const unsigned long my_scan_masks[] = {0x7, 0};
indio_dev->available_scan_masks = my_scan_masks;
```

- active_scan_mask: 这是启用通道的位掩码。只有来自这些通道的数据能被推入缓冲区。例如，对于 8 通道 ADC  转换器，如果只启用第一个（0），第三个（2）和最后一个（7）通道，则位掩码将为  0b10000101（0x85）。active_scan_mask 将设置为 0x85。然后，驱动程序可以使用 for_each_set_bit 宏遍历每个设置位，根据通道获取数据，并填充缓冲区。
- scan_timestamp: 这告诉我们是否将捕获时间戳推入缓冲区。如果为 true，则将时间戳作为缓冲区的最后一个元素。时间戳大 8 字节（64 位）。
- trig: 这是当前设备触发器（支持缓冲模式时）。
- pollfunc: 这是在接收的触发器上运行的函数。
- channels: 这表示通道规范结构，用于描述设备具有的每个通道。
- num_channels: 这表示通道中指定的通道数。
- name: 这表示设备名称。
- info: 来自驱动程序的回调和持续信息。
- setup_ops: 启用 / 禁用缓冲区之前和之后调用的回调函数集。这个结构在 include /linux/iio /iio.h 中定义，如下所示：

```c
struct iio_buffer_setup_ops {
    int (* preenable) (struct iio_dev *);
    int (* postenable) (struct iio_dev *);
    int (* predisable) (struct iio_dev *);
    int (* postdisable) (struct iio_dev *);
    bool (* validate_scan_mask) (struct iio_dev *indio_dev,
                                 const unsigned long *scan_mask);
};
```

- setup_ops: 如果未指定，则 IIO 内核使用 drivers /iio/buffer /industrialio-triggered-buffer.c 中定义的缺省 iio_triggered_buffer_setup_ops。
- 字符设备：由 IIO 核心管理，Linux 6.1 驱动不要访问旧版 iio_dev.chrdev 字段。

用于为 IIO 设备分配内存的函数是 iio_device_alloc（）：

```c
struct iio_dev *iio_device_alloc(struct device *parent, int sizeof_priv);
struct iio_dev *devm_iio_device_alloc(struct device *parent, int sizeof_priv);




```

dev 是为其分配 iio_dev 的设备，sizeof_priv 是用于为任何私有结构分配的内存空间。这样，传递每个设备（私有）数据结构非常简单。如果分配失败，该函数返回 NULL：

```c
struct iio_dev *indio_dev;
struct my_private_data *data;
indio_dev = iio_device_alloc(&pdev->dev, sizeof(*data)); /* 在 platform probe 中 */
if (!indio_dev)
          return -ENOMEM;
/*data is given the address of reserved momory for private data */
data = iio_priv(indio_dev);
```

在分配 IIO 设备存储器之后，下一步是填充不同的字段。完成后，必须使用 iio_device_register 函数向 IIO 子系统注册设备：

```c
/* Linux 6.1 中是宏封装，调用形式如下： */
ret = iio_device_register(indio_dev);
/* 或使用 devm_iio_device_register(&pdev->dev, indio_dev) 管理注销。 */


```

在执行此功能后，设备将准备好接受来自用户空间的请求。反向操作（通常在释放函数中完成）是 iio_device_unregister（）：

```c
void iio_device_unregister(struct iio_dev *indio_dev)
// void devm_iio_device_unregister(struct device * dev, struct iio_dev * indio_dev)
```

一旦取消注册，iio_device_alloc 分配的内存可以用 iio_device_free 释放：

```c
void iio_device_free(struct iio_dev *iio_dev)
/* 使用 devm 分配时交由设备生命周期清理，不调用普通 iio_device_free。 */
```

给定 IIO 设备作为参数，可以通过以下方式检索私有数据：

```c
 struct my_private_data *the_data = iio_priv(indio_dev);
```

#### 24.1.2.2 iio_info 结构体

struct iio_info 结构用于声明 IIO 内核使用的钩子，以读取 / 写入通道 / 属性值：

```c
struct iio_info {
           /* Linux 6.1 无 driver_module 字段 */
            const struct attribute_group *attrs;
            int (*read_raw)(struct iio_dev *indio_dev,
               struct iio_chan_spec const *chan,
               int *val, int *val2, long mask);

            int (*write_raw)(struct iio_dev *indio_dev,

                struct iio_chan_spec const *chan,

                int val, int val2, long mask);
             /* 其他回调省略 */

};
```

- 模块所有者：Linux 6.1 由 iio_device_register/devm_iio_device_register 的宏封装传入，不在 iio_info 初始化器中设置 driver_module。
- attrs: 这表示设备属性。
- read_raw：用户读取通道 sysfs 属性时调用。mask 是 IIO_CHAN_INFO_RAW、IIO_CHAN_INFO_SCALE 等枚举选择值，不是供逐位测试的 info_mask 位图；回调填写 val/val2 并返回 IIO_VAL_* 格式码，失败返回负 errno。
- write_raw: 这是用于将值写入设备的回调。例如，可以使用它来设置采样频率。

以下代码显示了如何设置 struct iio_info 结构：

```c
static const struct iio_info iio_dummy_info = {
    /* 模块所有者由注册宏处理 */
    .read_raw = &iio_dummy_read_raw,
    .write_raw = &iio_dummy_write_raw,
    /* 其他回调省略 */
};

/*
 * Provide device type specific interface functions and
 * constant data. 提供设备类型特定的接口功能和常量数据。
 */
indio_dev->info = &iio_dummy_info;
```

#### 24.1.2.3 IIO channels

通道代表单条采集线。例如加速度计具有 3 个通道（X，Y，Z），因为每个轴代表单个采集线。struct iio_chan_spec 是表示和描述内核中单个通道的结构：

```c
struct iio_chan_spec {
        enum iio_chan_type type;
        int channel;
        int channel2;
        unsigned long address;
        int scan_index;
        struct {
            charsign;
            u8 realbits;
            u8 storagebits;
            u8 shift;
            u8 repeat;
            enum iio_endian endianness;
        } scan_type;
        long info_mask_separate;
        long info_mask_shared_by_type;
        long info_mask_shared_by_dir;
        long info_mask_shared_by_all;
        const struct iio_event_spec *event_spec;
        unsigned int num_event_specs;
        const struct iio_chan_spec_ext_info *ext_info;
        const char *extend_name;
        const char *datasheet_name;
        unsigned modified:1;
        unsigned indexed:1;
        unsigned output:1;
        unsigned differential:1;

    };
```

各个参数意义：

- type: 这指定了通道的测量类型。在电压测量的情况下，它应该是 IIO_VOLTAGE。对于光传感器，它是 IIO_LIGHT。对于加速度计，使用  IIO_ACCEL。所有可用类型都在 include /uapi/linux /iio/types.h 中定义，如 enum  iio_chan_type。要为给定转换器编写驱动程序，请查看该文件以查看每个通道所属的类型。
- channel: 这指定.indexed 设置为 1 时的通道索引。
- channel2: 这指定.modified 设置为 1 时的通道修饰。
- modified: 这指定是否将修饰符应用于此通道属性名称。在这种情况下，修饰符设置在.channel2  中。（例如，IIO_MOD_X，IIO_MOD_Y，IIO_MOD_Z 是关于 xyz 轴的轴向传感器的修改器）。可用修饰符列表在内核 IIO  头中定义为枚举 iio_modifier。修饰符只会破坏 sysfs 中的通道属性名称，而不是值。
- indexed: 这指定通道属性名称是否具有索引。如果是，则在.channel 字段中指定索引。
- scan_index and scan_type: 当使用缓冲区触发器时，这些字段用于标识缓冲区中的元素。scan_index  设置缓冲区内捕获的通道的位置。具有较低 scan_index 的通道将放置在具有较高索引的通道之前。将.scan_index 设置为 - 1  将阻止通道进行缓冲捕获（scan_elements 目录中没有条目）。

暴露给用户空间的通道 sysfs 属性以位掩码的形式指定。根据共享信息，可以将属性设置为以下掩码之一：

- info_mask_separate 将属性标记为特定于此通
- info_mask_shared_by_type 将该属性标记为由相同类型的所有通道共享。导出的信息由相同类型的所有通道共享。
- info_mask_shared_by_dir 将属性标记为由同一方向的所有通道共享。导出的信息由同一方向的所有通道共享。
- info_mask_shared_by_all 将属性标记为所有通道共享，无论其类型或方向如何。导出的信息由所有渠道共享。用于枚举这些属性的位掩码都在 include /linux/iio /iio.h 中定义：

```c
enum iio_chan_info_enum {
    IIO_CHAN_INFO_RAW = 0,
    IIO_CHAN_INFO_PROCESSED,
    IIO_CHAN_INFO_SCALE,
    IIO_CHAN_INFO_OFFSET,
    IIO_CHAN_INFO_CALIBSCALE,
    [...]
    IIO_CHAN_INFO_SAMP_FREQ,
    IIO_CHAN_INFO_FREQUENCY,
    IIO_CHAN_INFO_PHASE,
    IIO_CHAN_INFO_HARDWAREGAIN,
    IIO_CHAN_INFO_HYSTERESIS,
    [...]
};
```

字节序字段应为以下之一：

```c
enum iio_endian {
      IIO_CPU,
      IIO_BE,
      IIO_LE,
};
```

通道属性命名约定

属性的名称由 IIO 核心自动生成，具有以下模式：{direction} _ {type} _ {index} _ {modifier} _ {info_mask}：

- ​       direction 方向对应于属性方向，根据 drivers /iio/industrialio-core.c 中的 struct iio_direction 结构：      

```c
static const char * const iio_direction[] = {
   [0] = "in",
   [1] = "out", 
}; 
```

* type 对应于通道类型，根据 char 数组 const iio_chan_type_name_spec：      

```c
static const char * const iio_chan_type_name_spec[] = {
   [IIO_VOLTAGE] = "voltage",
   [IIO_CURRENT] = "current",
   [IIO_POWER] = "power",
   [IIO_ACCEL] = "accel",
   [...]
   [IIO_UVINDEX] = "uvindex",
   [IIO_ELECTRICALCONDUCTIVITY] = "electricalconductivity",
   [IIO_COUNT] = "count",
   [IIO_INDEX] = "index",
   [IIO_GRAVITY]  = "gravity",
};
```

- ​       lindex 索引模式取决于是否设置了通道.indexed 字段。如果设置，索引将从.channel 字段中获取，以替换 {index} 模式。      
- ​       modifier 模式取决于通道所设置的.modified 字段。如果设置，修饰符将从.channel2 字段中获取，{modifier} 模式将根据 char 数组 struct iio_modifier_names 结构替换：      

```c
static const char * const iio_modifier_names[] = {
   [IIO_MOD_X] = "x",
   [IIO_MOD_Y] = "y",
   [IIO_MOD_Z] = "z",
   [IIO_MOD_X_AND_Y] = "x&y",
   [IIO_MOD_X_AND_Z] = "x&z",
   [IIO_MOD_Y_AND_Z] = "y&z",
   [...]
   [IIO_MOD_CO2] = "co2",
   [IIO_MOD_VOC] = "voc",
};
```

l info_mask 取决于 char 数组 iio_chan_info_postfix 中的通道信息掩码，私有或共享索引值：

```c
/* relies on pairs of these shared then separate依赖于这些共享的对,然后分离*/
static const char * const iio_chan_info_postfix[] = {
   [IIO_CHAN_INFO_RAW] = "raw",
   [IIO_CHAN_INFO_PROCESSED] = "input",
   [IIO_CHAN_INFO_SCALE] = "scale",
   [IIO_CHAN_INFO_CALIBBIAS] = "calibbias",
   [...]
   [IIO_CHAN_INFO_SAMP_FREQ] = "sampling_frequency",
   [IIO_CHAN_INFO_FREQUENCY] = "frequency",
   [...]
};
```

### 24.1.3 通道区分

当每种通道类型有多个数据通道时，您可能会遇到麻烦。困境将是：如何识别它们。有两种解决方案：索引和修饰符。

使用索引：给定具有一个通道线的 ADC 器件，不需要索引。通道定义如下：

```c
static const struct iio_chan_spec adc_channels[] = {
                {
                        .type = IIO_VOLTAGE,
                        .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),

               },
}
```

由前面描述的通道产生的属性名称将是 in_voltage_raw。

```shell
/sys/bus/iio/devices/iio:deviceX/in_voltage_raw
```

现在让我们看一下有 4 个甚至 8 个通道的转换器。我们如何识别它们？解决方案是使用索引。将.indexed 字段设置为 1 将使用.channel 值替换 {index} 模式来替换通道属性名称：

```c
 static const struct iio_chan_spec adc_channels[] = {
        {
                .type = IIO_VOLTAGE,
                .indexed = 1,
                .channel = 0,
                .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),

        },

        {
                .type = IIO_VOLTAGE,
                .indexed = 1,
                .channel = 1,
                .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
        },
        {
                .type = IIO_VOLTAGE,
                .indexed = 1,
                .channel = 2,
                .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
        },
        {
                .type = IIO_VOLTAGE,
                .indexed = 1,
                .channel = 3,
                .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
        },
}
```

生成的通道属性为：

```shell
/sys/bus/iio/devices/iio:deviceX/in_voltage0_raw
/sys/bus/iio/devices/iio:deviceX/in_voltage1_raw
/sys/bus/iio/devices/iio:deviceX/in_voltage2_raw
/sys/bus/iio/devices/iio:deviceX/in_voltage3_raw
```

使用修饰符：给定一个带有两个通道的光传感器 - 一个用于红外光，一个用于红外和可见光，没有索引或修改器，属性名称将为  in_intensity_raw。在这里使用索引可能容易出错，因为使用 in_intensity0_ir_raw 和  in_intensity1_ir_raw 是没有意义的。使用修饰符将有助于提供有意义的属性名称。通道的定义如下：

```shell
static const struct iio_chan_spec mylight_channels[] = {

        {
                .type = IIO_INTENSITY,
                .modified = 1,
                .channel2 = IIO_MOD_LIGHT_IR,
                .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
                .info_mask_shared_by_all = BIT(IIO_CHAN_INFO_SAMP_FREQ),
        },
        {
                .type = IIO_INTENSITY,
                .modified = 1,
                .channel2 = IIO_MOD_LIGHT_BOTH,
                .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),
                .info_mask_shared_by_all = BIT(IIO_CHAN_INFO_SAMP_FREQ),
        },
        {
                .type = IIO_LIGHT,
                .info_mask_separate = BIT(IIO_CHAN_INFO_PROCESSED),
                .info_mask_shared_by_all =BIT(IIO_CHAN_INFO_SAMP_FREQ),

        },
       }
```

属性结果：

```shell
l /sys/bus/iio/devices/iio:deviceX/in_intensity_ir_raw 用于测量IR强度的通道
l /sys/bus/iio/devices/iio:deviceX/in_intensity_both_raw用于测量红外和可见光的通道
l /sys/bus/iio/devices/iio:deviceX/in_illuminance_input用于处理后的数据
l /sys/bus/iio/devices/iio:deviceX/sampling_frequency 用于采样频率，由所有人共享
```

这也适用于加速度计，我们将在案例研究中进一步了解。现在，让我们总结一下我们到目前为止在虚拟 IIO 驱动程序中讨论过的内容。

### 24.1.4 驱动代码

```c
#include <linux/init.h>
#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/platform_device.h>
#include <linux/interrupt.h>
#include <linux/of.h>
#include <linux/iio/iio.h>
#include <linux/iio/sysfs.h>
#include <linux/iio/events.h>
#include <linux/iio/buffer.h>


#define FAKE_VOLTAGE_CHANNEL(num)                  \
   {                                               \
         .type = IIO_VOLTAGE,                      \
         .indexed = 1,                             \
         .channel = (num),                         \
         .address = (num),                         \
         .info_mask_separate = BIT(IIO_CHAN_INFO_RAW),   \
         .info_mask_shared_by_type = BIT(IIO_CHAN_INFO_SCALE) \
   }



struct my_private_data {
    int foo;
    int bar;
    struct mutex lock;
};

static int fake_read_raw(struct iio_dev *indio_dev,
                         const struct iio_chan_spec *channel,
                         int *val, int *val2, long mask)
{
    switch (mask) {
    case IIO_CHAN_INFO_RAW:
        *val = channel->channel; /* 模拟数据，非真实 ADC 采样 */
        return IIO_VAL_INT;
    case IIO_CHAN_INFO_SCALE:
        *val = 3300; /* mV */
        *val2 = 12;
        return IIO_VAL_FRACTIONAL_LOG2; /* 3300 / 2^12 mV/LSB */
    default:
        return -EINVAL;
    }
}













static const struct iio_chan_spec fake_channels[] = {
   FAKE_VOLTAGE_CHANNEL(0),
   FAKE_VOLTAGE_CHANNEL(1), 
   FAKE_VOLTAGE_CHANNEL(2),
   FAKE_VOLTAGE_CHANNEL(3),

};

static const struct of_device_id iio_dummy_ids[] = {
    { .compatible = "packt,iio-dummy-random", },
    { /* sentinel */ }
};

static const struct iio_info fake_iio_info = {
   .read_raw = fake_read_raw,
   /* Linux 6.1 无 driver_module 字段；注册宏会传入模块所有者。 */

};

static int my_pdrv_probe (struct platform_device *pdev)
{
    struct iio_dev *indio_dev;
    struct my_private_data *data;
   indio_dev = devm_iio_device_alloc(&pdev->dev, sizeof(*data));

   if (!indio_dev) {
         dev_err(&pdev->dev, "iio allocation failed!\n");
         return -ENOMEM;
   }

   data = iio_priv(indio_dev);
   mutex_init(&data->lock);
   indio_dev->dev.parent = &pdev->dev;
   indio_dev->info = &fake_iio_info;
   indio_dev->name = KBUILD_MODNAME;
   indio_dev->modes = INDIO_DIRECT_MODE;
   indio_dev->channels = fake_channels;
   indio_dev->num_channels = ARRAY_SIZE(fake_channels);
    /* 仅演示 direct mode；available_scan_masks 应是数组指针，不能赋整数 0xF。 */
    return devm_iio_device_register(&pdev->dev, indio_dev);
}









static struct platform_driver mypdrv = {
    .probe      = my_pdrv_probe,
    /* devm 管理注册与分配，无需显式 remove */
    .driver     = {
        .name     = "iio-dummy-random",
        .of_match_table = of_match_ptr(iio_dummy_ids),  
        .owner    = THIS_MODULE,
    },
};
module_platform_driver(mypdrv);
MODULE_AUTHOR("woniu");
MODULE_LICENSE("GPL");
```

加载上述模块后，我们将有以下输出，显示我们的设备确实对应于我们已注册的平台设备:

```shell
  ~# ls -l /sys/bus/iio/devices/
lrwxrwxrwx 1 root root 0 Jul 31 20:26 iio:device0 -> ../../../devices/platform/iio-dummy-random.0/iio:device0
lrwxrwxrwx 1 root root 0 Jul 31 20:23 iio_sysfs_trigger -> ../../../devices/iio_sysfs_trigger
```

下面的列表显示了此设备的通道及其名称，这些通道与我们在驱动程序中描述的内容完全对应:

```shell
~# ls /sys/bus/iio/devices/iio\:device0/
dev in_voltage2_raw name uevent
in_voltage0_raw in_voltage3_raw power
in_voltage1_raw in_voltage_scale subsystem
~# cat /sys/bus/iio/devices/iio:device0/name
iio_dummy_random
```

### 24.1.5 adc驱动

1. 设备树

   ```c
   	my_adc: my-adc {
   		compatible = "my-adc-test";
   		io-channels = <&saradc 4>;
   		io-channel-names = "adc-test";
   	};
   ```

2. 驱动，**不能在定时器中读adc**

   ```c
   #include <linux/module.h>
   #include <linux/kernel.h>
   #include <linux/platform_device.h>
   #include <linux/mod_devicetable.h>
   #include <linux/of.h>
   #include <linux/pwm.h>
   #include <linux/gpio/consumer.h>
   #include <linux/input.h>
   #include <linux/timer.h>
   #include <linux/iio/consumer.h>
   #include <linux/workqueue.h>
   
   struct iio_channel * iio_chan;
   int val;
   
   static void my_work_func(struct work_struct *work);
   
   //创建一个延时的工作
   DECLARE_DELAYED_WORK(my_work, my_work_func);
   
   static void my_work_func(struct work_struct *work){
   	iio_read_channel_raw(iio_chan, &val);
   	printk(KERN_INFO "adc value is %d\n", val);
   	schedule_delayed_work(&my_work, 2000);
   }
   
   //设备和驱动匹配成功时执行
   static int my_probe(struct platform_device * pdev){
   	printk(KERN_INFO "my_probe................^_^\n");
   	int i,ret;
   	iio_chan = iio_channel_get(&pdev->dev, "adc-test");
   	schedule_delayed_work(&my_work, 1000); //延时1s执行my_work_func
   	return 0;
   }
   
   //在设备或驱动移除时执行
   static int my_remove(struct platform_device * pdev){
   	printk(KERN_INFO "my_remove\n");
   	iio_channel_release(iio_chan);
       cancel_delayed_work_sync(&my_work);
   	return 0;
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
   		.compatible = "woniu-adc", //设备树中的compatible字段
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
   		.name = "woniu_adc",   //平台总线上和设备和驱动靠name来匹配
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

## 24.2 adc键盘

   ```c
   #include <dt-bindings/input/rk-input.h>
   	woniu_adc: woniu_adc {
   		compatible = "woniu-adc";
   		io-channels = <&saradc 4>;
   		io-channel-names = "adc-test";
   		//未按下时adc最大值
   		release-threshold = <100>;
   		a{
   			//键对应的值
   			val = <KEY_A>;
   			min = <200>;
   			max = <350>;
   		};
   		b{
   			val = <KEY_B>;
   			min = <351>;
   			max = <500>;
   		};
   		c{
   			val = <KEY_C>;
   			min = <501>;
   			max = <600>;
   		};
   		backspace{
   			val = <KEY_BACKSPACE>;
   			min = <601>;
   			max = <1000>;
   		};
   	};
   ```

---

[总目录](总目录.md) · [上一篇：输入子系统与设备节点命名](23-%E8%BE%93%E5%85%A5%E5%AD%90%E7%B3%BB%E7%BB%9F%E4%B8%8E%E8%AE%BE%E5%A4%87%E8%8A%82%E7%82%B9%E5%91%BD%E5%90%8D.md) · [下一篇：U-Boot基础与源码启动流程](25-U-Boot%E5%9F%BA%E7%A1%80%E4%B8%8E%E6%BA%90%E7%A0%81%E5%90%AF%E5%8A%A8%E6%B5%81%E7%A8%8B.md)
