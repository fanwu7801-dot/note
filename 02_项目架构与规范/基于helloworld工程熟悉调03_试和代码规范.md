### debug
![alt text](embedded-development-note-main/02_项目架构与规范/image-2.png)
进如debug模式可以观察变量的值，单步执行代码，观察代码的运行流程等
![alt text](embedded-development-note-main/02_项目架构与规范/image-3.png)
![alt text](embedded-development-note-main/02_项目架构与规范/image-4.png)
> 注意观察堆栈区和数据区的变化 使用J-*Link调试器可以实时观察内存的变化*
> 如果这里的a变量是错误的或者没有，就先加入static和volatile关键字，防止编译器优化掉这个变量
> ![alt text](embedded-development-note-main/02_项目架构与规范/image-5.png)

### SWV工作原理
SWV（Serial Wire Viewer）是一种通过单线调试接口传输调试信息的技术。它利用处理器的调试功能，将调试数据通过单线接口发送到调试器，从而实现实时监控和分析程序的运行状态。SWV可以传输多种类型的数据，包括变量值、函数调用信息、中断事件等，帮助开发人员更好地理解和调试嵌入式系统中的代码。
![alt text](embedded-development-note-main/02_项目架构与规范/image-6.png)
>swv是旁听式的调试方式，不会影响程序的运行它是由ITM和DWT和TPIU三个模块组成的
#### SWD调试接口
- 串行线调试接口（Serial Wire Debug，SWD）是一种用于嵌入式系统的调试协议。它通过两根线（时钟线和数据线）实现与目标设备的通信，允许开发人员进行代码下载、调试和监控。SWD相比传统的JTAG接口具有更少的引脚需求和更高的效率，适用于资源受限的嵌入式系统。
![alt text](embedded-development-note-main/02_项目架构与规范/image-7.png)

SWD接口包括以下主要信号线：
- SWDIO（Serial Wire Debug Input/Output）：双向数据线，用于传输调试命令和数据。
- SWCLK（Serial Wire Debug Clock）：时钟线，用于同步数据传输。

*ITM*：相当于一个高速缓存区，存储需要传输的数据
*DWT*：数据观察点，可以监控变量的变化，设置断点等
*TPIU*：将数据转换为串行格式，通过SWDIO线传输给调试器
*SWO*：串行线输出，是SWV数据传输的物理通道(格式化)

#### debug
##### 表达式和变量
- 了解如何在debug哦是模式下查看和修改变量的值
- 观察变量的变化，理解程序的运行流程
依旧是用watch窗口观察变量的值+单步执行代码

##### 定位问题
一般情况下，代码的错误是Hard Fault中断引起的，可以通过查看堆栈信息和寄存器状态来定位问题
一般一来说常见的错误有4种
![alt text](embedded-development-note-main/02_项目架构与规范/image-8.png)
造成这些错误的原因有很多，比如数组越界访问，空指针访问，栈溢出等
![alt text](embedded-development-note-main/02_项目架构与规范/image-9.png)
![alt text](embedded-development-note-main/02_项目架构与规范/image-10.png)
根据这些寄存器的信息，可以定位到具体的代码行，从而找出问题所在
- PC寄存器：程序计数器，指向当前执行的指令地址
- LR寄存器：链接寄存器，保存函数返回地址
- PSP和MSP寄存器：进程堆栈指针和主堆栈指针，指向当前堆栈的位置
- CFSR寄存器：配置和状态寄存器，包含了各种错误状态标志

*data watch pointer*
可以先把变量的地址拿到 例如 `&ptr` 然后在debug模式下使用data watch pointer功能，输入变量的地址，就可以监控这个地址的值的变化，从而定位问题，使用`breakpoint`断点配合使用效果更好
![alt text](embedded-development-note-main/02_项目架构与规范/image-11.png)
这里就可以看到ptr指针的值的变化，从而定位问题

### SFR寄存器
SFR（Special Function Register，特殊功能寄存器）是微控制器中的一类寄存器，用于控制和配置微控制器的各种外设和功能。SFR寄存器通常具有特定的地址和功能，可以通过编程方式访问和修改它们的值，以实现对硬件资源的管理和控制。
> 在keil里面点击peripherals->system viewer 可以查看所有的SFR寄存器，也就是MCU和外界交互的接口