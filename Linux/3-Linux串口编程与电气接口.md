# 3-Linux串口编程与电气接口

[总目录](总目录.md) · [上一篇：CMake](2-CMake.md) · [下一篇：RK开发板入门与交叉编译及NFS](4-RK%E5%BC%80%E5%8F%91%E6%9D%BF%E5%85%A5%E9%97%A8%E4%B8%8E%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%8F%8ANFS.md)

> 版本基线：Linux 6.1，面向 RK SDK。保留已完成的接口勘误；源码摘录与板级资源仍需对照实际 SDK。构建和适配说明见 [Linux 6.1 适配说明](整理记录/Linux6.1适配说明.md)。

[TOC]

<a id="part-5"></a>

## 3.1 串口编程

> dmesg 用于查看内核输出

为了控制串口通信， 我们需要进行串口编程。 在 Linux 系统中， 可以使用文件 I/O 操作和ioctl 操作来进行串口编程。 文件 I/O 操作可以用于读取和写入串口数据， ioctl 操作可以用于设置串口参数、 控制流控制和获取串口状态等操作。

在嵌入式设备中， 串口设备通常以字符设备节点的形式出现在 Linux 系统中。 在 Linux 系统中， 每个设备都由一个设备节点（device node） 来表示， 设备节点是与设备相关联的一个文件， 以/dev 目录下的文件形式存在。

串口设备节点通常以 tty 开头， 具体命名方式根据串口的类型和数量不同而不同。 开发板系统启动之后， 使用以下命令打印终端设备节点， 如下图所示：

```c
ls /dev/tty*
```

![image-20250412183232557](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412183232557.png)

dev/ttyX（X 是一个数字编号， 譬如 0、 1、 2、 3 等） 设备节点： tty 是 teletype 的简称，在 Linux 中， /dev/ttyX 代表的都是本地终端， Linux 内核在初始化时所生成的 63 个本地终端， 包括/dev/tty1~/dev/tty63 一共 63 个本地终端， 可以是连接到开发板的 LCD 显示器、 键盘和鼠标等。

串口终端设备节点： 从开发板原理图可以了解到， 在 iTOP-3568 开发板上有四个串口， 分别 UART2、 UART4、 UART7、 UART9， 其中 UART2 为串口调试终端， 对应的设备节点为/dev/ttyFIQ0,其他三个串口 UART4、 UART7、 UART9 分别对应/dev/ttyS4、 /dev/ttyS7、 /dev/ttyS9。
基于 USB 的虚拟串口： ttyGS0 以及 ttyUSBX（X 是一个数字编号， 譬如 0、 1、 2、 3 等）都是 USB 的虚拟串口， 其中 ttyGS0 为烧写 usb 虚拟出的串口， 在系统启动之后可以在 windows终端通过“adb shell”命令进入开发板控制台。 ttyUSBX 在这里为 4G 模块的虚拟串口。

### 3.1.1 struct termios 结构体

struct termios 是 Linux 内核中用于描述终端设备（包括串口设备） 参数的结构体。 它定义在 <linux/termios.h> 头文件中， 包含了多个字段， 用于配置和管理终端设备的属性和行为，包括了输入输出波特率、 数据位、 校验位、 停止位等。 其定义如下：

```c
struct termios {
  tcflag_t c_iflag; // 输入模式标志
  tcflag_t c_oflag; // 输出模式标志
  tcflag_t c_cflag; // 控制模式标志
  tcflag_t c_lflag; // 本地模式标志
  cc_t c_cc[NCCS]; // 控制字符数组
};
```

下面是 struct termios 结构体的一些重要字段：

* tcflag_t c_iflag： 该字段包含了输入模式标志， 用于配置终端设备的输入行为， 如输入控制
  字符、 输入数据处理等。
* tcflag_t c_oflag： 该字段包含了输出模式标志， 用于配置终端设备的输出行为， 如输出数据
  处理、 输出控制字符等。
* tcflag_t c_cflag： 该字段包含了控制模式标志， 用于配置终端设备的控制参数， 如波特率、
  数据位数、 停止位数、 校验位等。
* tcflag_t c_lflag： 该字段包含了本地模式标志， 用于配置终端设备的本地操作以及输入输出
  行为。
* cc_t c_cc[NCCS]： 该字段包含了特殊控制字符数组， 用于配置终端设备的控制字符， 如终
  端的擦除字符、 结束字符、 停止字符等。

**输入模式**

在这个结构体中， 最重要的 c_iflag， 可以控制模式控制终端设备的硬件特性， 譬如对于串口来说， 该字段比较重要， 可设置串口波特率、 数据位、 校验位、 停止位等硬件特性。 通过设置 struct termios 结构中 c_cflag 成员的标志对控制模式进行配置。 可用于 c_iflag 成员的标志如下所示：

![image-20250412183459779](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412183459779.png)

**输出模式**

输出模式控制输出字符的处理方式， 即由应用程序发送出去的字符数据在传递到串口或屏幕之前是如何处理的。 可用于 c_oflag 成员的宏如下所示：

![image-20250412183546419](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412183546419.png)

**控制模式**

在这个结构体中， 最重要的就是 c_cflag ， 可以控制模式控制终端设备的硬件特性， 譬如对于串口来说， 该字段比较重要， 可设置串口波特率、 数据位、 校验位、 停止位等硬件特性。通过设置 struct termios 结构中 c_cflag 成员的标志对控制模式进行配置。 可用于 c_cflag 成员的标志如下所示：

![image-20250412183740383](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412183740383.png)

**本地模式**

本地模式用于控制终端的本地数据处理和工作模式。 通过设置 struct termios 结构体中c_lflag 成员的标 志对本地模式进行配置。 可用于 c_lflag 成员的标志如下所示：

![image-20250412183820638](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412183820638.png)

**特殊控制字符**

特殊控制字符是一些字符组合， 如 Ctrl+C、 Ctrl+Z 等， 当用户键入这样的组合键， 终端会采取特殊处理方式。 struct termios 结构体中 c_cc 数组将各种特殊字符映射到对应的支持函数。 每个字符位置（数组下标） 由对应的宏定义的， 如下所示

![image-20250412183847853](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412183847853.png)

在以上所列举的这些宏定义中， TIME 和 MIN 值只能用于非规范模式， 可用于控制非规范模式下 read()调用的一些行为特性， 后面再向大家介绍。

### 3.1.2 串口控制函数

串口控制函数是用于管理和控制串口设备的函数， 在 Linux 系统中主要通过 ioctl() 系统调用来实现。 以下是一些常用的串口控制函数及其功能：

#### 3.1.2.1 tcgetattr()函数

tcgetattr()： 该函数用于获取终端设备的属性， 包括输入模式、 输出模式、 控制模式和本地模式等。 通过该函数可以获取当前串口设备的配置参数。
tcsetattr() 函数是在 Linux 中用于设置终端设备的属性的函数， 通常用于对串口设备的参数进行配置。 该函数的原型如下：

```c
int tcgetattr(int fd, struct termios *termios_p);
```

其中， 参数说明如下：
fd： 是指向打开的串口设备文件描述符的指针， 用于标识要进行属性设置的串口设备。

termios_p： 是一个指向 struct termios 结构体的指针， 包含了要设置的终端属性。 struct termios
结构体中包含了串口的配置参数， 如波特率、 数据位、 停止位、 校验位、 流控制等。

#### 3.1.2.2 tcsetattr()函数

tcsetattr() 函数是 Linux 系统中用于设置终端设备属性的函数， 常用于配置串口设备的参数。 该函数的声明如下：

```c
int tcsetattr(int fd, int optional_actions, const struct termios *termios_p);
```

参数解释：
fd： 是指向已打开串口设备的文件描述符的指针， 用于指定要设置属性的串口设备。
optional_actions： 表示属性设置的动作选项， 可以是以下值之一：

* TCSANOW： 立即改变属性。
* TCSADRAIN： 等待输出缓冲区数据发送完毕后再改变属性。
* TCSAFLUSH： 清空输入输出缓冲区后再改变属性。

termios_p： 是一个指向 struct termios 结构体的指针， 包含了要设置的终端属性， 包括波特率、数据位、 停止位、 校验位、 流控制等。
通过调用 tcsetattr() 函数， 可以实现对串口设备参数的灵活配置。 常见的终端属性设置包括：

* 设置波特率： 通过在 termios_p 结构体中设置正确的输入和输出波特率来指定串口通信的
  速率。
* 设置数据位、 停止位和校验位： 通过在 termios_p 结构体中设置正确的数据位、 停止位和
  校验位来匹配串口设备的配置。
* 配置流控制： 通过设置硬件流控制和软件流控制来控制串口数据的流动。

在调用 tcsetattr() 函数时， 需要注意指定合适的 optional_actions 参数， 以确保属性设置的动作符合需求。 正确地配置串口设备的属性可以保障数据通信的成功和稳定。

#### 3.1.2.3 cfgetispeed()和 cfgetospeed()函数

在 Linux 系统中， 没有标准的 cfgetispeed() 和 cfgetospeed() 函数。 这两个函数通常是在类 Unix 系统中的 <termios.h> 头文件中定义。 它们的作用是用于获取终端设备的输入和输出波特率。 这两个函数的功能介绍如下：

````c
cfgetispeed(const struct termios *termios_p)
````

该函数用于获取终端设备的输入波特率。
参数 termios_p 是一个指向 struct termios 结构体的指针， 包含了终端设备的属性信息。
返回值为表示输入波特率的整数值（波特率常用的单位是波特/秒） 。

```c
cfgetospeed(const struct termios *termios_p)
```

该函数用于获取终端设备的输出波特率。
参数 termios_p 是一个指向 struct termios 结构体的指针， 包含了终端设备的属性信息。
返回值为表示输出波特率的整数值。

这两个函数用于从终端属性结构体中提取输入和输出波特率的值， 以便应用程序可以了解当前终端设备的波特率设置。 在使用这两个函数时， 需要注意传入正确的 struct termios 结构体指针， 以确保获取准确的波特率信息。
在 Linux 系统中， 获取终端设备的波特率信息通常通过其他方式实现， 如结合使用tcgetattr() 函数获取终端属性结构体， 并从中提取波特率信息。

#### 3.1.2.4 cfsetispeed()和 cfsetospeed()函数

cfsetispeed() 和 cfsetospeed()： 这两个函数分别用于设置输入波特率和输出波特率。 可以通过这两个函数来指定串口设备的通信速率。
cfsetispeed()函数的作用如下：

```c
cfsetispeed(struct termios *termios_p, speed_t speed)：
```

该函数用于设置终端设备的输入波特率。
参数 termios_p 是指向 struct termios 结构体的指针， 包含了终端设备的属性信息。
参数 speed 是指定的输入波特率值。
通过调用 cfsetispeed() 函数可以将输入波特率设置为指定的值， 以指定串口设备接收数据的速率。

cfsetospeed()函数的作用如下：

```c
cfsetospeed(struct termios *termios_p, speed_t speed)：
```

该函数用于设置终端设备的输出波特率。
参数 termios_p 是指向 struct termios 结构体的指针， 包含了终端设备的属性信息。
参数 speed 是指定的输出波特率值。
通过调用 cfsetospeed() 函数可以将输出波特率设置为指定的值， 以指定串口设备发送数据的速率。
这两个函数通常与 struct termios 结构体一起使用， 通过设置输入和输出波特率来配置串口设备的通信速率。 正确地设置输入和输出波特率可以确保串口通信双方的数据传输速率匹配， 从而实现稳定的数据交换。

#### 3.1.2.5 tcflush()和 tcflow()函数

tcflush() 和 tcflow() 函数是用于控制终端设备输入输出数据流的函数， 常用于串口设备的操作。 以下是详细介绍：

```c
tcflush(int fd, int queue_selector)
```

该函数用于刷新终端设备的输入输出缓冲区。
参数 fd 是指向已打开的终端设备文件描述符的指针， 用于标识要操作的终端设备。
参数 queue_selector 是刷新缓冲区的方式， 可以是以下值之一：

* TCIFLUSH： 刷新输入缓冲区， 丢弃未读取的数据。

* TCOFLUSH： 刷新输出缓冲区， 丢弃未发送的数据。
* TCIOFLUSH： 同时刷新输入输出缓冲区。

通过 tcflush() 函数可以根据需求清空终端设备的输入缓冲区、 输出缓冲区或同时清空两者。

```c
tcflow(int fd, int action)
```

该函数用于控制数据流的暂停和恢复。
参数 fd 是指向已打开的终端设备文件描述符的指针， 用于标识要操作的终端设备。
参数 action 可以指定以下值之一：

* TCOOFF： 暂停数据的传输， 停止发送数据。
* TCOON： 恢复数据的传输， 继续发送数据。
* TCIOFF： 暂停数据的传输， 停止接收数据。
* TCION： 恢复数据的传输， 继续接收数据。

tcflush() 和 tcflow() 函数通常在串口通信中用于控制和管理数据的流动。 tcflush() 可以清空缓冲区中的数据， 而 tcflow() 可以控制数据的流动状态， 暂停或恢复数据的传输。 正确使用这两个函数有助于确保串口通信操作的稳定性和准确性。

#### 3.1.2.6 串口操作流程

**设置串口的波特率**

在编写串口应用程序时， 设置串口波特率是必须的步骤之一， 它决定了数据传输的速率。在 Linux 中， 设置波特率通常使用 cfsetspeed() 函数， cfsetspeed()函数所需头文件和函数原型如下所示：

```c
int cfsetspeed(struct termios *termios_p, speed_t speed);
```

它接受一个 struct termios 结构体作为输入参数， 同时返回一个整数值， 表示操作是否成功。 该函数实际上是对 c_cflag 字段中的波特率进行设置。 例如， 如果要将波特率设置为115200， 可以调用以下代码：

```c
struct termios options;
// 获取当前终端配置
tcgetattr(fd, &options);
// 设置波特率为 115200
cfsetspeed(&options, B115200);
// 将新的终端配置写入终端
tcsetattr(fd, TCSANOW, &options);
```

需要注意以下几点：
（ 1） 需要先打开串口设备文件并且获取串口的属性， 包括波特率在内的其他属性。 可以使用 tcgetattr() 函数获取属性值， 并存储在一个 termios 结构体变量中。
（ 2） 设置波特率时需要调用 cfsetspeed() 函数， 并传入一个波特率常量作为参数。 常用的波特率常量包括 B9600、 B115200 等。 这些常量可以在头文件 termios.h 中找到。
（ 3） 设置完成后， 需要使用 tcsetattr() 函数将属性值写回到串口设备中。

**设置数据位大小**

在串口通讯中， 数据位指的是每个字符（ byte） 中实际包含的数据位数。 通常情况下， 一个字符包含 8 个位（ 即 8 个 0 或 1） ， 但有时也可能为 7 个位或其他值。
在编写串口应用程序时， 需要使用 struct termios 结构体中的 c_cflag 成员变量来设置数据位大小。 具体来说， 需要将 c_cflag 成员变量中与数据位相关的位清零， 然后再根据需要设置相应的值。
清零操作通常使用按位与（ &） 运算符和位运算中的“非”运算符（ ~） ， 具体步骤如下：

```c
new_cfg.c_cflag &= ~CSIZE; // 将数据位相关的比特位清零
```

其中， CSIZE 是一个宏定义， 表示数据位的位掩码。 宏定义通常定义在 termios.h 头文件中， 其取值如下

```c
#define CSIZE 0x00000300 /* 字符长度掩码 */
```

通过清零操作， 将数据位相关的位全部置为 0。 接下来， 可以使用按位或（ |） 运算符和宏定义来设置具体的数据位数， 例如：

```c
new_cfg.c_cflag |= CS8; // 将数据位数设置为 8 位
```

此时， CS8 宏定义将会被解释为一个包含 8 位的位掩码， 通过按位或运算， 将其设置到c_cflag 成员变量中， 从而完成数据位的设置。

**设置奇偶校验位**

串口的奇偶校验位配置一共涉及到 struct termios 结构体中的两个成员变量： c_cflag 和c_iflag。 首先对于 c_cflag 成员， 需要添加 PARENB 标志以使能串口的奇偶校验功能， 只有使能奇偶校验功能之后才会对输出数据产生校验位， 从而对输入数据进行校验检查； 同时对于c_iflag 成员来说， 还需要添加 INPCK 标志， 这样才能对接收到的数据执行奇偶校验， 代码如下所示：
奇校验使能：

```c 
new_cfg.c_cflag |= (PARODD | PARENB); // 设置为奇校验
new_cfg.c_iflag |= INPCK; // 使能奇偶校验
```

偶校验使能：

```c
new_cfg.c_cflag &= ~PARODD; // 设置为偶校验
new_cfg.c_cflag |= PARENB; // 使能奇偶校验
new_cfg.c_iflag |= INPCK; // 对输入数据执行奇偶校验
```

无校验：

```c
new_cfg.c_cflag &= ~PARENB; // 禁用奇偶校验
new_cfg.c_iflag &= ~INPCK; // 不执行奇偶校验
```

**设置停止位**

在串口通信中， 停止位用于指定每个数据帧的结束位置。 在传输一个完整的数据字节后，通常需要一个或多个停止位， 以便接收端能够确定一个数据帧的结束。 停止位的数量通常为 1位或 2 位， 其中 1 位停止位被广泛使用， 而 2 位停止位则较少使用。
在 Linux 中， 通过在 struct termios 结构体中设置 c_cflag 成员变量的 CSTOPB 标志位来控制停止位的数量。 当 CSTOPB 为 0 时， 仅使用 1 位停止位； 当 CSTOPB 为 1 时， 则使用 2位停止位。
例如， 以下代码将串口的停止位设置为 1 位

```c
new_cfg.c_cflag &= ~CSTOPB; // 设置停止位为 1 位
```

#### 3.1.2.7 程序代码

```c
#include <stdio.h>
#include <termios.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <string.h>
#include <errno.h>

int fd;
char * str = "Hello, woniu!\n";

char buf[6] = {0};

/**
 * @brief 初始化串口
 * @param fd 串口文件描述符
 * @param baudrate 波特率
 * @param databits 数据位
 * @param stopbits 停止位 1-1位 2-2位
 * @param parity 校验位  0-无校验 1-奇校验 2-偶校验
 */
void serial_init(int fd, int baudrate, int databits, int stopbits, int parity){
    //termios结构变量中存储了所有串口的属性
    struct termios newtio;
    //清空termios结构变量
    memset(&newtio, 0, sizeof(newtio));
    //设置波特率
    switch(baudrate){
        case 9600:
            cfsetspeed(&newtio, B9600);
            break;
        case 19200:
            cfsetspeed(&newtio, B19200);
            break;
        case 38400:
            cfsetspeed(&newtio, B38400);
            break;
        case 57600:
            cfsetspeed(&newtio, B57600);
            break;
        case 115200:
            cfsetspeed(&newtio, B115200);
            break;
    }
    //设置数据位长度
    newtio.c_cflag &= ~CSIZE;
    switch(databits){
        case 5:
            newtio.c_cflag |= CS5;     //设置数据位长度为5
            break;
        case 6:
            newtio.c_cflag |= CS6;     //设置数据位长度为6
            break;
        case 7:
            newtio.c_cflag |= CS7;     //设置数据位长度为7          
            break;
        case 8:
            newtio.c_cflag |= CS8;     //设置数据位长度为8
            break;
    }
    //设置校验位
    switch(parity){
        case 0:
            newtio.c_cflag &= ~PARENB;    //无校验位
            break;
        case 1:
            newtio.c_cflag |= PARENB;     //奇校验位
            newtio.c_cflag |= PARODD;     //设置奇校验
            break;
        case 2:
            newtio.c_cflag |= PARENB;     //偶校验位
            newtio.c_cflag &= ~PARODD;    //设置偶校验
            break;
    }
    //设置停止位
    switch(stopbits){
        case 1:
            newtio.c_cflag &= ~CSTOPB;    //设置停止位为1
            break;
        case 2:
            newtio.c_cflag |= CSTOPB;     //设置停止位为2
            break;
    }
    newtio.c_cflag |= CREAD;    //设置接收使能
    newtio.c_cflag |= CLOCAL;   //设置本地模式

    //刷新缓冲区
    tcflush(fd, TCIOFLUSH);

    //设置串口属性
    tcsetattr(fd, TCSANOW, &newtio);
}

int main(int argc, char *argv[]){
    int ret;
    printf("Hello, world!\n");
    //打开串口
    fd = open("/dev/ttyS2", O_RDWR | O_NOCTTY | O_NDELAY);
    if (fd < 0) { perror("open serial"); return 1; }
    //配置串口
    serial_init(fd, 9600, 8, 1, 0);
    while(1){
        ret = read(fd, buf, sizeof(buf)-1);
        if(ret>0){
            buf[ret] = '\0';
            printf("read from serial: %s\n", buf);
        }
        if (ret < 0 && errno != EAGAIN && errno != EWOULDBLOCK && errno != EINTR) {
            perror("read serial");
            break;
        }
        if (ret <= 0) usleep(1000); /* 教学用轮询；正式程序可使用 poll/select */
    }
    //关闭串口
    close(fd);
    return 0;
}
```

普通用户没有串口通信的权限，如果需要使用普通用户来使串口，需要把这个用户加入到dialout用户 组中

```shell
# 给用户添加一个dialout组才有使用串口的权限，改了以后重新登录一下。
sudo usermod -aG dialout username
# 查看组
groups
```

<a id="part-37"></a>

## 3.2 接口类型

串口一般的接口电平有 TTL， RS232,RS485,RS422， 并且每种接口通常需要相应的电平转换芯片。 直接使用处理器引出的串口接口时， 通常是 TTL 电平。 然而， 处理器的不同型号或供应商可能存在电平差异， 这意味着在某些情况下不能直接连接设备。 因此， 为了确保正常通信，必须进行适当的电平转换。 一般的串口接口电平对比如下表所示：

| 电平             | 传输                             | 特点                                                         |
| ---------------- | -------------------------------- | ------------------------------------------------------------ |
| TTL              | 板间通信， 几米， 视电平特性而定 | (Transistor-Transistor Logic)电平标准，这是基于晶体管的电平标准， 其中 0表示低电平， 1 表示高电平， 低电平一般是 0V， 高电平可以是 3.3V， 5V， 2.5V或 1.8V， 具体值取决于设备的电源电压。 |
| RS232            | 约 50 米                         | (Recommended Standard 232) 电 平 标准。 这种电平标准中，-3\~-15V表示1，+3\~+15V表示0。 RS232 通常用于较长距离的通信和增加抗干扰能力。 |
| RS422<br />RS485 | 最大传输距离约 1219 米           | 采用差分信号进行数据传输（ 四根线） ， 俩线间的电压差为+2V 到+6V 表示逻辑 1， 俩线之间的电压差为-2V 到-6V 表示逻辑 0， 能够有效地减少噪声信号干扰， 延长通信距离 |

### 3.2.1 RS232 接口

RS232 协议是由美国电子工业协会在 1970 年制定的串行通信标准。 该标准统一了串口通信的连接器和引脚定义， 如下图所示， 并明确规定了每个连接器引脚的电平标准。

![image-20250412181855125](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412181855125.png)

DB9 是一种常见的串口连接器， 通常用于 RS-232 串口通信和其他串行通信应用。 它包含 9
个引脚， 每个引脚都有特定的功能。 下面是 DB9 连接器的引脚说明：
 Pin 1 - DCD (Data Carrier Detect):数据载波检测。 指示远程设备是否准备好进行通信。
 Pin 2 - RXD (Receive Data):接收数据。 从远程设备接收数据流。
 Pin 3 - TXD (Transmit Data):发送数据。 向远程设备发送数据流。
 Pin 4 - DTR (Data Terminal Ready):数据终端就绪。 指示数据终端设备（如计算机） 准备好进
行通信。
 Pin 5 - GND (Ground):地线。 电气接地， 用于电路的参考和屏蔽。
 Pin 6 - DSR (Data Set Ready):数据集准备好。 指示远程设备准备好接收和发送数据。
 Pin 7 - RTS (Request to Send):请求发送。 发送方使用此信号请求开始发送数据。
 Pin 8 - CTS (Clear to Send):清除发送。 接收方使用此信号表示准备好接收数据。
 Pin 9 - RI (Ring Indicator):铃信号指示器。 指示远程设备发送了铃响信号。

需要注意的是， RS232 本质上也是串口协议， 与我们之前讲解的其他串口协议相同。 它规定了串口的物理接口和电平特性， 因此在硬件层面有所不同， 但在软件编程和串口通信的实现上并无区别！
另外， 请注意不要将 RS232 接口与 VGA 接口混淆， 它们是完全不同的接口标准。

VGA 接口如下图所示：
![image-20250412181946359](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412181946359.png)

而 RS232 接口如下图所示：
![image-20250412182001250](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182001250.png)

**电平特性**

RS232（Recommended Standard 232） 是一种串行通信接口标准， 定义了数据通信设备之间的电气特性和信号传输规范。 以下是 RS232 的主要电平特性：

* RS232 接收-发送端的电信号是相对于公共地线（GND） 的电压信号。 在 RS232 标准中， 电压差值在+3V 至+15V 之间被定义为逻辑“0”， 而在-3V 至-15V 之间则表示逻辑“1”。 电压差值在-3V 至+3V 之间的情况未定义。 通常， 实际应用中希望电压差的绝对值在 5V 至 15V 之间， 以确保可靠的信号传输。 在数据发送时， 发送端驱动器输出+5V 至+15V 的正电压信号表示逻辑“0”， 而-5V 至-15V 的负电压信号表示逻辑“1”。 在数据接收时， 只要检测到大于3V 的电信号， 即视为有效信号。
* RS232 接口在发送和接收时具有相对较高的电流能力， 可以处理相对较大的电流负载， 这使得它适合于长距离通信和连接外部设备。

* RS232 信号具有较高的抗干扰能力， 能够在工业环境中稳定运行， 不易受到电磁干扰的影响。

* RS232 包括发送线（Tx） 、 接收线（Rx） 、 地线（Ground） 、 数据终端就绪（DTR） 、 数据
  就绪（DSR） 、 请求发送（RTS） 、 清除发送（CTS） 、 环路信号检测（DSR） 等信号线。
* RS232 支持各种波特率， 通常从低速率到较高速率， 最高可以达到数百千位每秒（kbps） 。

总体而言， RS232 的电平特性使其适用于需要可靠数据传输和抗干扰能力的应用场景， 例如计算机串口通信、 控制系统和各种工业设备之间的通信连接。 在迅为的 iTOP-RK3568 开发板上， 调试串口使用了 MAX3232 芯片将 TTL 电平转换成 232 电平， 调试串口的原理图如下图所示：

![image-20250412182149831](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182149831.png)

### 3.2.2 RS485 接口

接下来我们学习一下 RS485 接口。
RS485 标准是由电信行业协会（Telecommunications Industry Association, TIA） 和电子工业联盟（Electronic Industries Alliance, EIA） 共同制定的。 该标准的主要目的是解决长距离通信需求（最长达 1200 米） 以及提供优秀的抗干扰性能。
RS485 具有以下主要特点和优势：

* 长距离通信能力： RS485 能够在理想条件下实现长达 1200 米的通信距离， 适用于需要远距
  离数据传输的场合。
* 抗干扰能力强： 由于采用差分信号传输方式， RS485 能有效抵御电磁干扰（EMI） 和射频干
  扰（RFI） ， 保证数据传输的稳定性和可靠性。
* 多站能力： RS485 支持多个设备（最多 32 个） 在同一条总线上进行通信， 每个设备可以独
  立地发送和接收数据， 从而实现灵活的网络组网。
* 应用广泛： RS485 广泛应用于工业自动化控制系统、 建筑自动化、 智能家居系统、 电力系
  统监控等领域， 满足对长距离、 高速和可靠通信的要求。

RS485 因其长距离通信能力、 优异的抗干扰性能和多站能力， 成为许多工业和商业应用中首选的串行通信接口标准。 在迅为的 iTOP-RK3568 开发板上， 485 接口如下图所示：

![image-20250412182304035](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182304035.png)

**电平特性**

RS485 的电平特性如下：

* 差分信号传输： RS485 使用差分信号进行数据传输， 即数据信号是相对于两条信号线（通
  常标记为 A 和 B 线） 之间的电压差来表示的。 这种差分信号传输方式使得 RS485 具有良好
  的抗干扰能力和长距离传输能力。
* 电压与逻辑：RS485 使用 A/B 两线的差分电压，判决极性、阈值及共模范围应查所用收发器数据手册。A/B 不能直接连接 UART 的 TTL/CMOS TX/RX，必须使用 RS485 收发器转换。


* 电流能力： RS485 发送器具有较强的驱动能力， 能够推动较长的通信线路和多个接收器。
  接收器能够处理较大的输入电流， 以确保信号的可靠接收。
* 总线负载和距离：传统满单位负载预算常按 32 个接收器计算，使用分数单位负载收发器可支持更多节点。可达距离与速率、线缆、终端和干扰有关，不能把 1200 米当作任意速率下的保证。

总体而言， RS485 的电平特性使其非常适合于工业环境中的长距离和高抗干扰要求的数据通信应用。 在迅为的 iTOP-RK3568 开发板上使用 SIT3485E 芯片将 TTL 电平转换为 485 电平， 原理图如下图所示：

![image-20250412182421969](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182421969.png)

从上面的原理图中我们可以看到 RK3568 开发板的 RS485 接口实际上是通过 SIT3485E 芯片转接的串口 7。 我们尝试分析一下 SIT3485E 这个芯片。
首先我们打开 SIT3485E 的数据手册， 了解一下这个芯片的相关信息， 如下图所示：

![image-20250412182446868](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182446868.png)

![image-20250412182503323](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182503323.png)

![image-20250412182515515](https://woniumd.oss-cn-hangzhou.aliyuncs.com/aiot/luozhaoyong/image-20250412182515515.png)

由引脚定义图可知， RO 引脚为接收器输出端， 在原理图上连接到 UART7_RX_M1 引脚。 DI引脚为 DI 驱动器输入引脚， 在原理图上连接到 UART7_TX_M1 引脚。 原理图上的 A 引脚是接收器同向输入和驱动器同向输出端， 原理图上的 B 引脚是接收器反向输入和驱动器反向输出端，A 和 B 自然就是 RS485 的差分对了。 /RE 引脚是接收器输出使能控制引脚， 当/RE 接低电平时，接收器输出使能， RO 输出有效， 当/RE 接高电平时， 接收器输出禁能， RO 为高阻态。 DE 引脚是驱动器输出使能控制引脚， DE 接高电平时驱动器输出有效， DE 为低电平时输出为高阻态。 /RE 接高电平且 DE 接低电平时， 器件进入低功耗模式。
官方描述的相对晦涩， 简单来说：
/RE 为低电平时， RO 输出有效。 反之 RO 高阻态， 也就是无效。 RO 接的 UART7_RX_M1，UART7_RX_M1 是串口的接收引脚。 因此， /RE 低电平时， 串口可以接收数据， 反之串口无法接收数据。
DE 是高电平时， DI 有效， DI 接的是 UART7_TX_M1， UART7_TX_M1 是串口发送引脚， 因此， DE 是高电平时， DI 上的低电平使驱动器 同向端 A 输出为低电平， 驱动器反向端 B 输出为高电平， 串口可以发送数据， 反之串口无法发送数据。
本板把 /RE 与 DE 接到同一个方向控制 GPIO：低电平接收、高电平发送。这是常见的两线半双工实现，不是 RS485 要求两脚必须相连；收发器也可同时使能发送器和接收器来接收本机回显。总线上多个发送器同时驱动仍会冲突。
这样就很清晰了， 如果 GPIO0_C6 输出低电平， /RE 和 DE 是低电平， /RE 是低电平时，串口可以接收数据， DE 是低电平时， 串口不能发送数据。 如果 GPIO0_C6 输出高电平， /RE和 DE 是高电平， /RE 是高电平时， 串口不能接收数据， DE 是高电平时， 串口可以发送数据。
也就是说， 我们需要用 GPIO0_C6 这个引脚的高低电平来控制 RS485 是发送还是接收。 因此， 我们需要编写一个驱动来达到这个目的。 迅为提供的源码中默认配置了驱动来控制GPIO0_C6。

### 3.2.3 把调试串口设置为普通串口

> 先看一下ip地址
>
> rk3568-linux.dtsi

```c
	chosen: chosen {
		//bootargs = "earlycon=uart8250,mmio32,0xfe660000 console=ttyFIQ0 root=PARTUUID=614e0000-0000 rw rootwait";
		bootargs = "root=PARTUUID=614e0000-0000 rw rootwait";
	};

	// fiq-debugger {
	// 	compatible = "rockchip,fiq-debugger";
	// 	rockchip,serial-id = <2>;
	// 	rockchip,wake-irq = <0>;
	// 	/* If enable uart uses irq instead of fiq */
	// 	rockchip,irq-mode-enable = <1>;
	// 	rockchip,baudrate = <115200>;  /* Only 115200 and 1500000 */
	// 	interrupts = <GIC_SPI 252 IRQ_TYPE_LEVEL_LOW>;
	// 	pinctrl-names = "default";
	// 	pinctrl-0 = <&uart2m0_xfer>;
	// 	status = "okay";
	// };
```

---

[总目录](总目录.md) · [上一篇：CMake](2-CMake.md) · [下一篇：RK开发板入门与交叉编译及NFS](4-RK%E5%BC%80%E5%8F%91%E6%9D%BF%E5%85%A5%E9%97%A8%E4%B8%8E%E4%BA%A4%E5%8F%89%E7%BC%96%E8%AF%91%E5%8F%8ANFS.md)
