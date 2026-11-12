# LIN 总线协议：从接线、波形到调度与软件

LIN（Local Interconnect Network，本地互连网络）是一种低成本的
单主多从串行通信网络。**主节点按调度表发送帧头，指定发布者发送数据，
订阅者校验后使用数据**，这是理解 LIN 的主线。

它常用于车窗、后视镜、座椅、空调执行器、开关和传感器等局部网络，
也常由网关连接到 CAN。LIN 可以独立组成网络，不要求必须搭配 CAN。

> 本文以 LIN 2.x / LIN 2.2A 为主要依据；所有节点名、ID、信号、周期
> 和抓包数据均为教学示例，不代表具体车型协议或硬件接线。

阅读顺序：

1. 先看接线与电平，区分 UART 逻辑侧和 LIN 总线侧。
2. 再看字节与完整帧，弄清 Header 和 Response 分别由谁发送。
3. 手算 PID 和 Checksum，再读调度表与 LDF。
4. 最后结合休眠、软件分层和抓包步骤定位问题。

全部 8 张图提供 [可编辑 draw.io 源文件](lin-assets/lin-bus-explained.drawio)，
每张图也有同名 SVG 和 JSON，见 [配图说明](lin-assets/README.md)。

## 1. 先记住这些基本参数

| 项目 | 正确理解 |
| --- | --- |
| 网络角色 | 一个主节点，多个从节点；普通通信由主任务发起 |
| 节点数量 | LIN 2.2A §6.5.5 建议一个网络总节点数不超过 16，即通常 1 主 + 最多 15 从；还受物理负载约束 |
| 信号线 | 一根 LIN 信号线，还需要节点间地参考及各自供电 |
| 典型物理电平 | 车载 VBAT 域；常见 12 V 系统，但不是固定精确的 12 V 逻辑输出 |
| 标准最高位速率 | 20 kbit/s；19.2 kbit/s 是常见配置之一 |
| 字节编码 | NRZ 异步串行，8 个数据位、无 UART 奇偶校验、1 个停止位，即 8N1 |
| 位顺序 | 每个字节先发最低位，LSB first |
| 数据段长度 | LIN 2.x 每帧 1～8 字节；诊断帧固定 8 字节 |
| 检错 | PID 的两个保护位 + 传统 / 增强 Checksum；不使用 CAN 的 CRC 机制 |
| 通信时机 | 由调度表决定，延迟取决于周期、帧长、位速率与应用处理 |
| 诊断 | 支持诊断与节点配置；诊断帧的 ID 不等于节点诊断地址 NAD |

LIN 的优势是成本低、布线简单、可预先安排通信时间。
它的带宽有限，适合低速局部控制；不能仅凭“支持调度”就认定满足任意实时性要求。

**几处容易记错的地方：**最高速率不是 1 Mbps；编码不是 Manchester；
不存在固定“约 1 ms 延迟”；显性是逻辑 0，而不是逻辑 1。

## 2. 硬件连接：UART 不等于 LIN 总线

![LIN 网络拓扑与电平关系](lin-assets/01-topology.png)

**如何读图：**每个 MCU 先通过 TXD / RXD 连接本节点的 LIN 收发器，
所有收发器的 LIN 端再接到同一根总线上。图中的箭头分别表示 MCU 发送
和接收的方向，不代表额外的两根车外通信线。

- MCU 的 TX 输出串行逻辑，经收发器 TXD 转成总线显性 / 隐性电平。
- 收发器监听 LIN，将接收结果从 RXD 送给 MCU 的 RX 输入。
- MCU 逻辑侧电压按芯片确定，可能是 3.3 V 或 5 V；LIN 侧属于 VBAT 域。
- 主节点通常具有电阻、二极管组成的较强上拉终端网络；从节点通常有较弱上拉。
  具体取值、是否集成、滤波与保护元件均以收发器手册和原理图为准。

因此，普通 USB-UART 的 TX / RX 不能直接连接车辆 LIN 线。
抓 LIN 应使用适配的 LIN 接口，或在收发器的逻辑侧用合适仪器观察。
LIN 也不采用 CAN 那种两端各一个 120 Ω 电阻的终端方式。

### 2.1 显性、隐性与“线与”

| 总线状态 | 逻辑值 | 直观含义 |
| --- | --- | --- |
| Dominant，显性 | 0 | 有节点将总线拉低 |
| Recessive，隐性 | 1 | 所有节点释放，总线由上拉回到高电平 |

只要有一个节点拉低，总线就是显性；所有节点都释放，总线才是隐性。
这就是“显性优先”，从逻辑角度可理解为线与。

空闲时通常为隐性高电平。实际接收阈值、波形斜率和允许电压范围应查
收发器数据手册，不能把理想图当成精确电压或边沿要求。

## 3. 字节、Break 与 Sync：从波形入门

![LIN 的 8N1 字节与 Break、Sync 波形](lin-assets/02-waveform.png)

**如何读图：**上半部分是普通字节 `0x55`；下半部分先是一段明显更长
的低电平 Break，再出现界定符和 `0x55`。上下两行分别用于观察字节格式
和帧起始，横向比例只用于教学。

### 3.1 普通字节：1 + 8 + 1 = 10 bit

除了 Break，每个字节都按以下格式发送：

```text
空闲 1 → 起始位 0 → D0 D1 D2 D3 D4 D5 D6 D7 → 停止位 1
                    8 个数据位，低位先发
```

`8N1` 中的 `N` 表示 UART 没有额外的奇偶校验位。
PID 内部的 P0 / P1 是它的 8 个数据位的一部分，不能把 UART 配成带校验
来代替 PID 的保护位。

以 `0x55 = 0101 0101b` 为例，数值通常按高位在左书写，但线上 D0 先发，
因此数据位的时间顺序是 `1 0 1 0 1 0 1 0`。

### 3.2 Break：告诉所有节点“新帧开始了”

Break 由主任务发送：

- 显性低电平持续至少 **13 个标称位时间**。
- 随后是隐性高电平的 Break delimiter，至少 **1 个标称位时间**。
- 它是特殊段，不遵循普通的 8N1 字节格式。

普通 `0x00` 只有起始位和 8 个数据位连续为低，共 9 bit，
随后停止位回到高电平，不能直接等同于合格的 LIN Break。
MCU 是否能自动生成或检测 LIN Break，要看具体 UART / LIN 外设能力。

### 3.3 Sync：固定为 0x55

Sync 的交替边沿为从节点测量主节点位时间、进行同步提供依据。
是否自动调整、怎样测量和允许多大误差，取决于外设及协议栈实现。
有同步机制也不代表可以忽略时钟精度和容差要求。

在 `19.2 kbit/s` 下：

```text
1 bit 时间        = 1 / 19200 ≈ 52.083 μs
普通 8N1 字节     = 10 bit    ≈ 520.833 μs
最短 Break 低电平 = 13 bit    ≈ 677.083 μs
最短界定符        = 1 bit     ≈ 52.083 μs
```

## 4. 完整帧：谁发帧头，谁发数据

![LIN 帧结构与发送职责](lin-assets/03-frame.png)

**如何读图：**沿时间方向从左往右看。左侧 Header 始终由主任务发送；
右侧 Response 由该帧配置的发布者发送，发布者可以位于主节点或某个从节点。
响应间隔属于响应时序的一部分，图中用 Header 与数据之间的空隙示意。

| 部分 | 字段 | 内容 / 作用 | 发送者 |
| --- | --- | --- | --- |
| Header | Break + delimiter | 标志新帧开始 | 主任务 |
| Header | Sync | 固定 0x55，用于同步 | 主任务 |
| Header | PID | 6 bit 帧 ID + P0 / P1 | 主任务 |
| Response | Data | 普通帧 1～8 字节 | 该帧唯一发布者 |
| Response | Checksum | 检查数据，增强模式还覆盖 PID | 同一个发布者 |

主节点包含“主任务”和“从任务”；从节点只有“从任务”。
这里的任务是协议角色，**不要求一定映射成两个 FreeRTOS 任务**。
主任务负责调度和帧头；从任务负责根据帧配置发布或订阅响应。

因此可以出现三种常见关系：

1. 主节点发 Header，从 A 发 Response，主节点订阅。
2. 主节点既发 Header 又发 Response，从 A / B 订阅。
3. 主节点发 Header，从 A 发 Response，从 B 订阅。

从节点不能自行发起普通帧头，但可以在主节点安排的时机向其他节点发布数据。
从节点发起休眠网络唤醒属于另一种机制，见第 9 节。

### 4.1 ID 是帧标识，不是简单的设备地址

例如 `A_Status` 的 ID 是 `0x01`，表示“这一类状态数据”。
谁发布、谁订阅、长几个字节，由网络配置约定。一个从节点可以发布多种 ID，
一种帧也可以有多个订阅者。

LIN 2.x 的 Header 不发送数据长度字段，接收方必须事先知道该 ID 的长度。
不能只看到 PID，就用统一公式从 ID 推出 LIN 2.x 帧长。
一些旧版资料按 ID 区间说明 2 / 4 / 8 字节的规则，不应套用到 LIN 2.x 配置。

### 4.2 没有独立的 ACK 字段

Response 是这帧的数据和校验和，不是额外的 ACK。
如果业务要求确认“命令已执行”，应定义执行状态反馈和超时机制。
发送 API 返回成功，只能证明相应软件层完成了它定义的操作，
不能直接证明从节点收到、执行成功或物理执行器已经动作。

## 5. PID：把 6 bit 的 ID 保护起来

![LIN PID 组成与手算示例](lin-assets/04-pid.png)

**如何读图：**上面按数值习惯排列 bit7 到 bit0，左侧两位是保护位，
右侧六位是帧 ID；实际串行发送仍从 bit0 开始。

```text
P0  = ID0 ⊕ ID1 ⊕ ID2 ⊕ ID4
P1  = NOT(ID1 ⊕ ID3 ⊕ ID4 ⊕ ID5)，结果仅保留 1 bit
PID = ID | (P0 << 6) | (P1 << 7)
```

`⊕` 是异或；`|` 是按位或。接收方先检查保护位，再从 `PID & 0x3F`
得到 6 bit 的 ID。仅掩码取 ID 而不检查 P0 / P1，会丢失这层检错能力。

| ID | P0 | P1 | 线上 PID | 示例用途 |
| --- | --- | --- | --- | --- |
| 0x01 | 1 | 1 | 0xC1 | A_Status |
| 0x02 | 1 | 0 | 0x42 | B_Command |
| 0x03 | 0 | 0 | 0x03 | B_Status |
| 0x3C | 0 | 0 | 0x3C | 主节点诊断请求 |
| 0x3D | 1 | 0 | 0x7D | 从节点诊断响应 |

帧 ID 的用途分区：

- `0x00～0x3B`：信号携带帧。
- `0x3C / 0x3D`：诊断及配置。
- `0x3E / 0x3F`：保留。

分析仪有的显示原始 ID，有的显示完整 PID。
因此日志中的 `0x3D` 和 `0x7D` 可能对应同一种诊断响应帧，先看工具字段定义。

## 6. Checksum：传统与增强校验如何计算

![LIN 传统和增强校验及回卷进位](lin-assets/05-checksum.png)

**如何读图：**中间一行是增强校验的逐步计算；黄色框专门说明发生进位
时怎样处理。核心是“**回卷进位求和，然后对最终的 8 bit 取反**”。

| 校验模型 | 参与求和的字节 | 典型适用情况 |
| --- | --- | --- |
| Classic，传统 / 标准校验 | 所有 Data | LIN 1.x 兼容通信，以及 ID 0x3C / 0x3D 的诊断帧 |
| Enhanced，增强校验 | 完整 PID + 所有 Data | 按配置使用增强校验的 LIN 2.x 信号帧 |

模型按帧配置，不能只看到“LIN 2.x”就对诊断帧也使用增强校验。
增强校验加入的是包含保护位的 **PID**，不是只有 6 bit 的 ID，
也不包含 Break 或 Sync。

### 6.1 回卷进位不等于直接丢掉高位

每次相加，如果和大于 `0xFF`，就减去 `0xFF`，等价于把溢出的进位加回低位。

```text
0xF0 + 0x30 = 0x120
回卷进位：    0x20 + 1 = 0x21
最终取反：    ~0x21 & 0xFF = 0xDE
```

如果直接做 `sum & 0xFF`，会得到 `0x20`，进而算出错误的 `0xDF`。

### 6.2 同一组数据，两种校验结果不同

假设 `ID = 0x01`，因此 `PID = 0xC1`，数据是 `10 20`：

```text
Classic：
  0x10 + 0x20 = 0x30
  Checksum = ~0x30 & 0xFF = 0xCF

Enhanced：
  0xC1 + 0x10 + 0x20 = 0xF1
  Checksum = ~0xF1 & 0xFF = 0x0E
```

接收时，可以重新计算后比较，也可以把接收到的 Checksum 加入同样的
回卷求和，正确结果应为 `0xFF`。例如 `0xF1 + 0x0E = 0xFF`。
校验和只能帮助检错，不代表数据来源经过认证，也不证明业务值一定合理。

## 7. 调度表：为什么 LIN 的时序可以提前规划

![LIN 调度表与发布订阅示例](lin-assets/06-schedule.png)

**如何读图：**每个格子是一个 10 ms 时隙，四个时隙构成 40 ms 循环。
每个时隙开始都由主任务发送相应 Header，绿色表示从节点发布的数据，
蓝色表示主节点发布的数据。

| 循环内时刻 | 帧名 | ID / PID | 数据长度 | Response 发布者 | 订阅者 |
| --- | --- | --- | --- | --- | --- |
| 0 ms | A_Status | 0x01 / 0xC1 | 2 字节 | 从 A | 主节点、从 B |
| 10 ms | B_Command | 0x02 / 0x42 | 2 字节 | 主节点 | 从 B |
| 20 ms | A_Status | 0x01 / 0xC1 | 2 字节 | 从 A | 主节点、从 B |
| 30 ms | B_Status | 0x03 / 0x03 | 2 字节 | 从 B | 主节点 |

因此 `A_Status` 的周期是 20 ms，另外两帧的周期是 40 ms。
“主任务每 10 ms 启动一个时隙”不等于“所有帧都是 10 ms 周期”。

### 7.1 先计算一帧占多久

按最短 Break、最短界定符、无额外间隔计算，设数据长度为 `N`，波特率为 `B`：

```text
Header 位数       = 13 + 1 + 10 + 10 = 34 bit
Response 位数     = 10 × (N + 1)     = 数据 + 1 字节校验和
T_frame_nominal   = [34 + 10 × (N + 1)] / B
```

| 数据长度 | 标称总位数 | 19.2 kbit/s 标称帧时间 | 1.4 倍标称时间 |
| --- | --- | --- | --- |
| 1 字节 | 54 bit | 2.813 ms | 3.938 ms |
| 2 字节 | 64 bit | 3.333 ms | 4.667 ms |
| 8 字节 | 124 bit | 6.458 ms | 9.042 ms |

LIN 2.2A §2.3.2 分别给 Header 和 Response 定义了标称时间的 1.4 倍上限，
用于容纳允许的时序开销。时隙还需要满足主任务的抖动、时间基准等要求；
不能把标称帧时间直接当作可用时隙长度。
本例选择 10 ms 时隙只是教学配置，不是所有网络都必须如此。

这个上限也不是让接收节点在 `1.4 × T_nominal` 时就一律截断帧；
规范对分析工具和接收节点的行为有区别，接收处理还要能与后续 Break
重新同步，不能拿手算的最短时间代替协议栈时序设计。

### 7.2 帧时间、更新周期、业务延迟是三件事

以本例 `A_Status` 为例，数据刚好在轮询结束后变化，可能接近 20 ms 后
才迎来下一次发送机会，随后还要经过响应传输和业务处理。
所以端到端延迟应包含：

```text
输入采样等待 → 等待调度机会 → 总线传输 → 解析 / 快照 → 应用处理
```

不能写成固定 1 ms。若还要转发到 CAN 或 UART，应继续计入转发队列、
发送周期和接收端处理时间。

### 7.3 常见帧类型

| 类型 | 主任务做什么 | 谁提供响应 | 需要注意 |
| --- | --- | --- | --- |
| Unconditional，无条件帧 | 到时隙就发送该帧 Header | 配置的唯一发布者 | 最常见；发布者应提供响应 |
| Event-triggered，事件触发帧 | 在安排的时隙发送事件帧 Header | 有更新的关联从节点 | 可无人响应；多节点响应可能冲突，主节点切换到冲突解决调度表 |
| Sporadic，偶发帧 | 有更新时，按配置优先级选择关联帧发送；无更新可保持时隙静默 | 主节点 | 选择发生在主节点内部，不是总线上的 CAN 式位仲裁 |
| Diagnostic，诊断帧 | 安排 0x3C 请求、0x3D 响应机会 | 请求由主节点发布，响应由被寻址从节点发布 | 固定 8 字节、Classic 校验；未就绪时可能没有诊断响应 |

事件触发帧仍需要主节点先发 Header，不代表从节点可以随时抢发。
“LIN 不需要 CAN 式仲裁”也不等于“任何配置下绝不会出现碰撞”。

## 8. LDF：节点、帧、信号和调度的共同约定

LDF（LIN Description File）描述整个网络的通信关系，
可供配置生成器、协议栈和分析仪使用。它类似通信的“共同说明书”。

| 查找内容 | 需要回答的问题 |
| --- | --- |
| 协议 / 语言版本、位速率 | 用哪个版本、以多快的速度通信？ |
| Nodes | 谁是主节点，有哪些从节点？ |
| Signals | 信号多宽、初值是什么、谁发布、谁订阅？ |
| Frames | 帧 ID、长度、发布者是什么，信号放在哪些 bit？ |
| Schedule_tables | 哪些帧按什么次序、以什么时隙发送？ |
| 诊断与节点属性 | NAD、产品标识、诊断能力及相应时序是什么？ |

下面仅摘录与 `A_Status` 有关的教学片段，省略了 Nodes、其他帧等定义，
**不是可独立导入的完整 LDF**：

```text
LIN_speed = 19.2 kbps;

Signals {
    A_Keys:  8, 0, NodeA, Master, NodeB;
    A_Level: 8, 0, NodeA, Master, NodeB;
}

Frames {
    A_Status: 0x01, NodeA, 2 {
        A_Keys,  0;
        A_Level, 8;
    }
}

Schedule_tables {
    Normal {
        A_Status  delay 10 ms;
        B_Command delay 10 ms;
        A_Status  delay 10 ms;
        B_Status  delay 10 ms;
    }
}
```

逐项理解：

- `A_Keys: 8, 0, ...`：信号长 8 bit，初值是 0；由 NodeA 发布，Master / NodeB 订阅。
- `A_Status: 0x01, NodeA, 2`：帧 ID 是 0x01，发布者是 NodeA，数据长度为 2 字节。
- `A_Keys, 0`：最低有效位放在帧数据区 bit offset 0。
- `A_Level, 8`：最低有效位放在 bit offset 8，即第二个字节。
- 每项 `delay 10 ms` 表示对应调度项的时隙长度，包含发送和空闲余量；
  不是“完整发完帧以后再额外等 10 ms”。

LIN 2.x 标量信号低位先映射，多字节标量按小端传输。
例如一个从 offset 0 开始的 16 bit 标量，数据 `34 12` 对应原始值 `0x1234`。
字节数组、诊断载荷的具体语义仍应按相应定义解读，不要对所有载荷统一反转。
物理量换算、枚举值与无效值也必须查适用协议和信号定义。

**拿到一个 LIN 工程，先对照 LDF 查 ID、长度、发布者和调度，
再看驱动代码；不要从变量名或收到的几个字节反推业务语义。**

## 9. 休眠与唤醒：总线休眠和 MCU 低功耗分开看

![LIN 网络休眠和唤醒流程](lin-assets/07-sleep-wake.png)

**如何读图：**上半部分从正常通信进入低功耗等待，下半部分从唤醒检测
恢复资源，再回到调度。它表示工程处理顺序，不是某一款芯片 EN / SLP 引脚的时序图。

### 9.1 进入休眠

标准 go-to-sleep 命令是主节点请求帧：

```text
ID       = 0x3C，PID = 0x3C
Data     = 00 FF FF FF FF FF FF FF
Checksum = Classic，结果为 0x00
```

规范要求接收方按第一个数据字节解释该休眠请求，忽略其余七字节的值；
发送方应按上面的标准格式发送。
LIN 2.2A 还规定了总线不活动 4～10 s 后的从节点总线休眠转换，
判定条件按协议栈和规范执行，不能直接拿普通业务报文超时代替。

**收到总线休眠请求不等于 MCU 必须立刻进入 STOP。**
节点应用可能还有收尾工作。工程上还要处理未完成事务、输出安全状态、
收发器模式和唤醒源，满足整机需求后才进入相应低功耗状态。

### 9.2 唤醒网络

休眠网络里的任意节点都可以发起唤醒请求。LIN 2.2A §2.6.2 的关键时序为：

| 项目 | 规范中的含义 |
| --- | --- |
| 发送唤醒脉冲 | 显性持续 250 μs～5 ms，并回到隐性 |
| 从节点检测与就绪 | 检测持续超过 150 μs 的显性脉冲及其上升沿；从结束边沿算起，100 ms 内准备好通信 |
| 主节点恢复时间 | 由网络设计者 / 应用决定；不能直接把从节点的 100 ms 规定套给主节点 |
| 请求无后续进展 | 按规范条件在 150～250 ms 后重发；连续三次失败后，第四次至少等待 1.5 s |

唤醒之后仍需要主节点重新发送 Header 才能恢复普通通信。
如果主节点直接用 Header 的 Break 唤醒网络，该第一帧可能在从节点尚未
就绪时被错过，不能默认它已经作为业务帧成功处理。

芯片的总线唤醒滤波、Standby / Sleep / Normal 模式、RXD 行为与控制引脚
极性必须查对应数据手册；不凭 `EN`、`SLP_N` 之类名字猜测实际硬件。

## 10. 软件如何组织：从原始字节到有效业务数据

![LIN 软件数据链与四元组边界](lin-assets/08-software-flow.png)

**如何读图：**先沿上排看数据如何从总线走到 APP，再看下排四个框如何
划分规则、内部过程、业务事实和外部行为。图中名称是职责示意，未规定具体 API。

建议按以下逻辑追踪接收链：

```text
LIN 线电平
  → 收发器 RXD
  → UART / LIN 外设及驱动
  → Break / Sync / PID 检查与帧配置匹配
  → 接收规定数量的数据和校验和
  → 校验成功、业务取值检查
  → 更新信号快照、时间戳与有效性
  → RTE / APP 读取快照，执行控制或降级
```

发送链反向体现业务意图：APP 请求控制 → 服务更新待发布信号 → 主任务
调度到相应帧 → 发布者从任务发送响应 → 收发器驱动 LIN。
不能让 APP 随意绕过调度直接往 UART 塞数据。

### 10.1 cfg / ctx / data / ops 对应什么

| 类别 | LIN 中的典型内容 | 所有权与边界 |
| --- | --- | --- |
| cfg | 位速率、ID、长度、校验模型、发布订阅关系、调度表、超时策略 | 静态配置或受控标定，业务不能随意改 |
| ctx | 当前收发状态、缓存索引、当前时隙、内部计时器、错误计数 | 所属模块私有维护 |
| data | 按键信号、执行器状态、时间戳、valid、quality | 所属服务发布，上层读取一致快照 |
| ops | 初始化、周期处理、命令请求、收帧处理、获取快照、休眠与恢复 | 外部通过有边界的行为接口交互 |

#### 10.1.1 示例范围：先把一帧数据管好

下面沿用前文 `A_Status`：ID 为 `0x01`，数据长度为 2 字节，采用增强校验。
代码只依赖 C 标准库，不需要尚未提供的 `drv_io.h`。
几个 `c` 代码块按顺序拼接，可以组成一个独立的 C11 主机程序。

本例接收的是底层已经组好的 `PID + Data + Checksum`，不是零散 UART 字节。
底层负责 Break / Sync 检查、按帧配置收齐数据以及响应接收超时；
本层负责校验、保存最近有效数据和检查业务数据是否过期。
UART 的起始位、停止位不会作为额外字节放进 `payload`。

本例所有接口由同一个执行上下文串行调用，不使用动态内存、忙等或阻塞延时。
实际项目若由 ISR 接收、任务消费，应将完整帧复制到队列，由所属任务调用接口；
多个任务直接访问时，还需在适配层保护整个快照和状态更新过程。
仅有 `const` 或 `volatile` 不能保证跨任务一致性。

#### 10.1.2 四个结构体：规则、过程、事实与行为

```c
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

/* 协议常量见第 4～6 节；0x3E、0x3F 不作为普通接收配置。 */
#define LIN_DATA_MIN_LENGTH      1U
#define LIN_DATA_MAX_LENGTH      8U
#define LIN_ID_MASK              0x3FU
#define LIN_DIAG_REQUEST_ID      0x3CU
#define LIN_DIAG_RESPONSE_ID     0x3DU
#define LIN_TIMEOUT_MAX_MS       (UINT32_MAX / 2U)

typedef enum
{
    LIN_SUCCESS = 0,              /* 操作成功 */
    LIN_ERROR_NULL_POINTER,        /* 输入或输出指针为空 */
    LIN_ERROR_OUT_OF_RANGE,        /* ID、长度或时间参数越界 */
    LIN_ERROR_INVALID_CONFIG,      /* 校验模式或配置组合不合法 */
    LIN_ERROR_NOT_INITIALIZED,     /* 模块尚未初始化 */
    LIN_ERROR_STATE_NOT_ALLOWED,   /* 当前状态不允许重复初始化 */
    LIN_ERROR_PID_PARITY,          /* PID 的保护位错误 */
    LIN_ERROR_UNEXPECTED_ID,       /* 非本例订阅的帧，调用方可忽略 */
    LIN_ERROR_LENGTH_MISMATCH,     /* 数据长度与配置不一致 */
    LIN_ERROR_CHECKSUM,            /* 接收校验和不正确 */
    LIN_ERROR_NO_DATA,             /* 初始化后尚无有效帧 */
    LIN_ERROR_TIMEOUT,             /* 最近有效数据已经过期 */
} Lin_ErrorCode_t;

typedef enum
{
    LIN_CHECKSUM_CLASSIC = 0,      /* 仅对 Data 求和 */
    LIN_CHECKSUM_ENHANCED,         /* 对完整 PID 和 Data 求和 */
} Lin_ChecksumMode_t;

typedef enum
{
    LIN_RX_WAITING = 0,           /* 等待第一帧有效数据 */
    LIN_RX_FRESH,                 /* 已收到有效数据 */
    LIN_RX_EXPIRED,               /* 已过期，仅新有效帧可以恢复 */
} Lin_RxState_t;

struct lin_cfg
{
    uint8_t id;                   /* 6 bit 帧 ID，不填写完整 PID */
    uint8_t length;               /* Data 字节数，不含 Checksum */
    Lin_ChecksumMode_t mode;      /* 本帧采用的校验模型 */
    uint32_t timeout_ms;          /* 业务新鲜度上限，不是帧接收时限 */
};

struct lin_ctx
{
    bool initialized;            /* 初始化完成后才允许处理数据 */
    Lin_RxState_t state;         /* 模块私有接收状态 */
    uint32_t rejected_frames;    /* 被拒绝的坏帧数，达到上限后饱和 */
};

struct lin_data
{
    uint8_t payload[LIN_DATA_MAX_LENGTH]; /* 最近一次有效帧的数据 */
    uint8_t length;               /* 有意义的数据字节数 */
    uint32_t rx_ms;               /* 最近有效帧的接收完成时间 */
    bool valid;                  /* 是否仍可作为新鲜数据使用 */
};

struct lin_ops
{
    Lin_ErrorCode_t (*init)(const struct lin_cfg *cfg);
    Lin_ErrorCode_t (*on_frame)(uint8_t pid, const uint8_t *payload,
                                uint8_t length, uint8_t checksum,
                                uint32_t rx_ms);
    Lin_ErrorCode_t (*poll)(uint32_t now_ms);
    Lin_ErrorCode_t (*get_snapshot)(uint32_t now_ms,
                                    struct lin_data *snapshot);
};

/* 三份对象均属于本模块；外部通过 ops 请求行为或复制快照。 */
static struct lin_cfg s_lin_cfg;
static struct lin_ctx s_lin_ctx;
static struct lin_data s_lin_data;
```

`s_lin_cfg` 仅在初始化成功时复制一次，运行期间不修改。
`s_lin_ctx` 中的状态和计数不向业务层暴露；`s_lin_data` 保存可消费的事实。
`struct lin_ops` 中是函数指针，后面会绑定到实际函数；它不保存实时数据。
这些结构体是内存中的软件对象，不能直接把结构体地址强转后发送到 LIN。

#### 10.1.3 协议运算：先检查参数，再计算

下面三个辅助函数对应第 5、6 节的公式。
生成 PID 时允许输入全部 6 bit ID；是否属于可用帧，由配置检查决定。
诊断帧则额外约束为 8 字节和 Classic 校验。

```c
/*
 * 根据 6 bit ID 生成 PID；pid 为输出指针。
 * 返回参数错误或成功，仅在成功时写入输出，不修改模块状态。
 */
static Lin_ErrorCode_t Lin_MakePid(uint8_t id, uint8_t *pid)
{
    uint8_t p0;
    uint8_t p1;

    /* 1. 检查输出地址和 ID。2. 按第 5 节生成两个保护位。 */
    if (NULL == pid)
    {
        return LIN_ERROR_NULL_POINTER;
    }
    if (LIN_ID_MASK < id)
    {
        return LIN_ERROR_OUT_OF_RANGE;
    }

    p0 = (uint8_t)((id ^ (id >> 1U) ^ (id >> 2U)
                    ^ (id >> 4U)) & 1U);
    p1 = (uint8_t)((~((id >> 1U) ^ (id >> 3U)
                     ^ (id >> 4U) ^ (id >> 5U))) & 1U);
    *pid = (uint8_t)(id | (p0 << 6U) | (p1 << 7U));
    return LIN_SUCCESS;
}

/*
 * 验证收到的 pid，并将 6 bit ID 写入 id。
 * 返回空指针、保护位错误或成功；失败时保留输出原值。
 */
static Lin_ErrorCode_t Lin_DecodePid(uint8_t pid, uint8_t *id)
{
    uint8_t raw_id;
    uint8_t expected_pid;
    Lin_ErrorCode_t result;

    /* 1. 检查输出指针。2. 重新生成保护位，完整比较 PID。 */
    if (NULL == id)
    {
        return LIN_ERROR_NULL_POINTER;
    }
    raw_id = (uint8_t)(pid & LIN_ID_MASK);
    result = Lin_MakePid(raw_id, &expected_pid);
    if (LIN_SUCCESS != result)
    {
        return result;
    }
    if (expected_pid != pid)
    {
        return LIN_ERROR_PID_PARITY;
    }
    *id = raw_id;
    return LIN_SUCCESS;
}

/*
 * 为 pid 对应的 length 个数据字节计算校验和，写入 checksum。
 * payload 必须实际可读 length 字节；调用方负责保证缓冲区大小。
 * 返回参数、PID 或配置错误；成功前不写输出，不修改模块状态。
 */
static Lin_ErrorCode_t Lin_CalculateChecksum(
    uint8_t pid, const uint8_t *payload, uint8_t length,
    Lin_ChecksumMode_t mode, uint8_t *checksum)
{
    uint8_t id;
    uint8_t index;
    uint16_t sum = 0U;
    Lin_ErrorCode_t result;

    /*
     * 1. 验证指针、长度、校验模型和诊断帧组合。
     * 2. 按配置加入 PID，逐字节回卷进位，再取反。
     */
    if ((NULL == payload) || (NULL == checksum))
    {
        return LIN_ERROR_NULL_POINTER;
    }
    if ((LIN_DATA_MIN_LENGTH > length)
        || (LIN_DATA_MAX_LENGTH < length))
    {
        return LIN_ERROR_OUT_OF_RANGE;
    }
    if ((LIN_CHECKSUM_CLASSIC != mode)
        && (LIN_CHECKSUM_ENHANCED != mode))
    {
        return LIN_ERROR_INVALID_CONFIG;
    }
    result = Lin_DecodePid(pid, &id);
    if (LIN_SUCCESS != result)
    {
        return result;
    }
    if (LIN_DIAG_RESPONSE_ID < id)
    {
        return LIN_ERROR_OUT_OF_RANGE;
    }
    if (((LIN_DIAG_REQUEST_ID == id) || (LIN_DIAG_RESPONSE_ID == id))
        && ((LIN_DATA_MAX_LENGTH != length)
            || (LIN_CHECKSUM_CLASSIC != mode)))
    {
        return LIN_ERROR_INVALID_CONFIG;
    }

    if (LIN_CHECKSUM_ENHANCED == mode)
    {
        sum = pid;
    }
    for (index = 0U; index < length; index++)
    {
        sum = (uint16_t)(sum + payload[index]);
        if (UINT8_MAX < sum)
        {
            sum = (uint16_t)(sum - UINT8_MAX);
        }
    }
    *checksum = (uint8_t)((~sum) & UINT8_MAX);
    return LIN_SUCCESS;
}
```

PID 校验使用“重新生成后比较”，因此只做 `pid & 0x3F` 还不够。
校验和的中间值使用 `uint16_t`，保留进位；直接用 `uint8_t` 累加会先丢掉进位。

#### 10.1.4 行为接口：初始化、收帧、超时与快照

`init()` 只允许成功执行一次；修改配置应设计受控的停止、重配和恢复流程。
所有时间都使用同一来源的 `uint32_t` 单调毫秒计数，不使用日历时间。
配置的新鲜度时限不超过半个计数范围；调用按时间顺序进行，检查间隔也应小于
半个范围，避免计数跨越一整圈后失去时间信息。

```c
/*
 * 校验并复制 cfg，建立空快照；不操作硬件。
 * 返回参数、配置、重复初始化错误或成功。
 */
static Lin_ErrorCode_t Lin_Init(const struct lin_cfg *cfg)
{
    /*
     * 1. 验证参数及诊断帧约束，拒绝运行中直接替换配置。
     * 2. 复制配置并清空快照，最后发布初始化完成状态。
     */
    if (NULL == cfg)
    {
        return LIN_ERROR_NULL_POINTER;
    }
    if (true == s_lin_ctx.initialized)
    {
        return LIN_ERROR_STATE_NOT_ALLOWED;
    }
    if ((LIN_DIAG_RESPONSE_ID < cfg->id)
        || (LIN_DATA_MIN_LENGTH > cfg->length)
        || (LIN_DATA_MAX_LENGTH < cfg->length)
        || (0U == cfg->timeout_ms)
        || (LIN_TIMEOUT_MAX_MS < cfg->timeout_ms))
    {
        return LIN_ERROR_OUT_OF_RANGE;
    }
    if ((LIN_CHECKSUM_CLASSIC != cfg->mode)
        && (LIN_CHECKSUM_ENHANCED != cfg->mode))
    {
        return LIN_ERROR_INVALID_CONFIG;
    }
    if (((LIN_DIAG_REQUEST_ID == cfg->id)
         || (LIN_DIAG_RESPONSE_ID == cfg->id))
        && ((LIN_DATA_MAX_LENGTH != cfg->length)
            || (LIN_CHECKSUM_CLASSIC != cfg->mode)))
    {
        return LIN_ERROR_INVALID_CONFIG;
    }

    s_lin_cfg = *cfg;
    s_lin_data = (struct lin_data){0};
    s_lin_ctx = (struct lin_ctx){0};
    s_lin_ctx.state = LIN_RX_WAITING;
    s_lin_ctx.initialized = true;
    return LIN_SUCCESS;
}

/*
 * 接收底层组好的帧；length 仅计 Data，checksum 单独传入。
 * rx_ms 为接收完成时间，payload 必须实际可读 length 字节。
 * 坏帧只计数，不刷新快照；其他 ID 返回可忽略状态，不计坏帧。
 */
static Lin_ErrorCode_t Lin_OnFrame(
    uint8_t pid, const uint8_t *payload, uint8_t length,
    uint8_t checksum, uint32_t rx_ms)
{
    uint8_t id;
    uint8_t expected_checksum;
    struct lin_data next = {0};
    Lin_ErrorCode_t result;

    /*
     * 1. 检查指针和初始化状态，确认 PID 及订阅关系。
     * 2. 检查长度和校验和，拒绝时保留最近有效数据。
     * 3. 在单线程上下文中整体替换快照，恢复新鲜状态。
     */
    if (NULL == payload)
    {
        return LIN_ERROR_NULL_POINTER;
    }
    if (false == s_lin_ctx.initialized)
    {
        return LIN_ERROR_NOT_INITIALIZED;
    }

    result = Lin_DecodePid(pid, &id);
    if ((LIN_SUCCESS == result) && (s_lin_cfg.id != id))
    {
        return LIN_ERROR_UNEXPECTED_ID;
    }
    if ((LIN_SUCCESS == result)
        && (s_lin_cfg.length != length))
    {
        result = LIN_ERROR_LENGTH_MISMATCH;
    }
    if (LIN_SUCCESS == result)
    {
        result = Lin_CalculateChecksum(pid, payload, length,
                                       s_lin_cfg.mode,
                                       &expected_checksum);
    }
    if ((LIN_SUCCESS == result) && (expected_checksum != checksum))
    {
        result = LIN_ERROR_CHECKSUM;
    }
    if (LIN_SUCCESS != result)
    {
        /* 坏帧不续期；计数饱和，避免溢出后看起来像没有错误。 */
        if (UINT32_MAX > s_lin_ctx.rejected_frames)
        {
            s_lin_ctx.rejected_frames++;
        }
        return result;
    }

    memcpy(next.payload, payload, length);
    next.length = length;
    next.rx_ms = rx_ms;
    next.valid = true;
    s_lin_data = next;
    s_lin_ctx.state = LIN_RX_FRESH;
    return LIN_SUCCESS;
}

/*
 * 根据 now_ms 检查新鲜度；调用方周期执行，也可由快照接口触发。
 * 返回未初始化、无数据、超时或成功；过期时保留数值并撤销 valid。
 */
static Lin_ErrorCode_t Lin_Poll(uint32_t now_ms)
{
    /*
     * 1. 区分尚无数据和已过期，过期状态只由新有效帧解除。
     * 2. 用无符号减法检查年龄，允许毫秒计数跨零回绕。
     */
    if (false == s_lin_ctx.initialized)
    {
        return LIN_ERROR_NOT_INITIALIZED;
    }
    if (LIN_RX_WAITING == s_lin_ctx.state)
    {
        return LIN_ERROR_NO_DATA;
    }
    if (LIN_RX_EXPIRED == s_lin_ctx.state)
    {
        return LIN_ERROR_TIMEOUT;
    }
    if (s_lin_cfg.timeout_ms <= (uint32_t)(now_ms - s_lin_data.rx_ms))
    {
        s_lin_data.valid = false;
        s_lin_ctx.state = LIN_RX_EXPIRED;
        return LIN_ERROR_TIMEOUT;
    }
    return LIN_SUCCESS;
}

/*
 * 用 now_ms 检查新鲜度，再将当前快照复制到 snapshot。
 * 无数据或超时时也复制无效快照；空指针、未初始化时不写输出。
 * 前提是所有接口串行调用；结构体赋值本身不保证跨任务原子性。
 */
static Lin_ErrorCode_t Lin_GetSnapshot(uint32_t now_ms,
                                       struct lin_data *snapshot)
{
    Lin_ErrorCode_t result;

    /* 1. 验证输出。2. 检查新鲜度后复制，避免遗漏周期检查而读到旧值。 */
    if (NULL == snapshot)
    {
        return LIN_ERROR_NULL_POINTER;
    }
    result = Lin_Poll(now_ms);
    if (LIN_ERROR_NOT_INITIALIZED == result)
    {
        return result;
    }
    *snapshot = s_lin_data;
    return result;
}

/* ops 是固定行为入口，调用方不需要接触私有 ctx 或直接改写 data。 */
static const struct lin_ops s_lin_ops =
{
    .init = Lin_Init,
    .on_frame = Lin_OnFrame,
    .poll = Lin_Poll,
    .get_snapshot = Lin_GetSnapshot,
};
```

这里的状态依次为：等待首帧 → 收到有效帧 → 超时过期 → 新有效帧恢复。
坏帧不会刷新 `rx_ms`，也不会让过期数据恢复有效。
`rejected_frames` 统计 PID、长度和 Checksum 拒绝，不把其他订阅 ID 当作坏帧。

快照中的旧数值可用于诊断；业务使用前必须同时检查返回值与 `valid`。
这个例子只校验原始帧，`A_Keys` 的按键映射、`A_Level` 的物理范围等业务规则
仍需由真实协议约束的上层服务校验，不能凭教学字节猜测。

#### 10.1.5 调用示例：收到、过期、再恢复

下面的 `main()` 仅用于在电脑上运行以上示例，不替换 MCU 工程入口。
`timeout_ms = 100` 是本例选择的 5 个 `A_Status` 周期，属于教学策略，
不是 LIN 规定的新鲜度时限；真实项目应使用经过确认的超时要求。
打印内容是传入测试数据后产生的主机结果，不是实际串口抓包。

```c
#include <stdio.h>

/* 在主机演示完整调用；任一步与预期不符即返回非零值。 */
int main(void)
{
    const struct lin_cfg cfg =
    {
        .id = 0x01U,
        .length = 2U,
        .mode = LIN_CHECKSUM_ENHANCED,
        .timeout_ms = 100U,
    };
    const uint8_t payload[] = {0x10U, 0x20U};
    const uint8_t checksum = 0x0EU; /* 第 6 节的增强校验结果。 */
    const uint32_t rx_ms = 1000U;  /* 人工设置的接收时间。 */
    struct lin_data snapshot;
    uint8_t pid;

    /*
     * 1. 建立配置，并验证本例 ID 对应的 PID。
     * 2. 模拟有效帧及超时，再用下一帧验证恢复。
     */
    if ((LIN_SUCCESS != s_lin_ops.init(&cfg))
        || (LIN_SUCCESS != Lin_MakePid(cfg.id, &pid)))
    {
        return 1;
    }
    if ((LIN_SUCCESS != s_lin_ops.on_frame(pid, payload, cfg.length,
                                          checksum, rx_ms))
        || (LIN_SUCCESS != s_lin_ops.get_snapshot(rx_ms, &snapshot))
        || (false == snapshot.valid))
    {
        return 1;
    }
    printf("PID=%02X Data=%02X %02X valid=%u\n", (unsigned int)pid,
           (unsigned int)snapshot.payload[0],
           (unsigned int)snapshot.payload[1],
           (unsigned int)snapshot.valid);

    if ((LIN_ERROR_TIMEOUT != s_lin_ops.poll(rx_ms + cfg.timeout_ms))
        || (LIN_ERROR_TIMEOUT != s_lin_ops.get_snapshot(
                rx_ms + cfg.timeout_ms, &snapshot))
        || (true == snapshot.valid))
    {
        return 1;
    }
    printf("timeout valid=%u\n", (unsigned int)snapshot.valid);

    if ((LIN_SUCCESS != s_lin_ops.on_frame(
            pid, payload, cfg.length, checksum,
            rx_ms + cfg.timeout_ms + 1U))
        || (LIN_SUCCESS != s_lin_ops.get_snapshot(
                rx_ms + cfg.timeout_ms + 1U, &snapshot))
        || (false == snapshot.valid))
    {
        return 1;
    }
    printf("recovered valid=%u\n", (unsigned int)snapshot.valid);
    return 0;
}
```

按顺序拼接本节所有 `c` 代码块后，预期输出：

```text
PID=C1 Data=10 20 valid=1
timeout valid=0
recovered valid=1
```

阅读时沿这条线追踪：`cfg` 确定接收规则 → `ops.on_frame()` 校验输入 →
`ctx` 维护执行状态 → `data` 保存快照 → `ops.get_snapshot()` 提供一致结果。
一致性的成立前提是本例的单线程调用约束，实际跨任务使用必须补足同步。

#### 10.1.6 主机验证与使用边界

将以上四个 `c` 代码块按顺序保存为 UTF-8 编码的 `lin_demo.c`，
可在安装了 GCC 的 PowerShell 中执行：

```powershell
gcc -std=c11 -O2 -Wall -Wextra -Werror -Wconversion `
    -Wshadow -Wpedantic -finput-charset=UTF-8 lin_demo.c `
    -o lin_demo.exe
.\lin_demo.exe
```

2026-11-11 对笔记中提取的同一份代码执行了主机验证：

- GCC 16.2.0 严格告警编译通过，示例输出与上文一致。
- 临时测试程序通过 16140 次断言检查，包括全部 64 个 ID、全部 256 个
  PID 候选值，以及两种校验模型下的 7680 组不同数据测试。
- 已覆盖空指针、非法枚举、长度和配置越界、诊断帧限制、未初始化、
  重复初始化、坏帧不续期、快照副本隔离、错误计数饱和、超时边界与恢复。
- 已检查 32 bit 毫秒计数回绕、最小和最大允许超时，以及代码和注释的
  80 列限制。

上述结果证明的是主机上的协议运算和状态处理；本例没有配置 MCU 外设，
未进行固件编译、烧录、真实 LIN 抓包、RTOS 并发或板上通信验证。

### 10.2 异常时怎么处理

- **PID 保护错误、长度不匹配、校验失败：**丢弃本次更新，记录错误；
  不把坏帧写入业务快照，也不刷新“最近一次有效数据”的时间戳。
- **未知 ID：**按本节点帧配置忽略；不能因为不知道长度就任意猜一个长度解析。
- **无响应或响应不完整：**区分帧类型并记录状态，按协议栈设计结束或重同步；
  事件触发帧和未就绪诊断响应允许无数据，不能统一报成断线。
- **持续没有有效数据：**按项目超时要求标为过期，执行明确的保持、撤销或安全默认策略。
  “保留最后数值”必须同时保留无效标记，不能伪装成新数据。
- **收到新的 Break / Sync 序列：**协议帧处理应能放弃未完成旧帧并重新同步。
- **并发访问：**任务 / 中断之间通过队列、临界区或快照机制交互，保证信号值、
  时间戳和有效性属于同一次更新。

注意 UART 空闲中断、DMA 搬运完成或“收到了几个字节”，都不等价于
“接收到一帧校验正确且业务有效的 LIN 数据”。

### 10.3 完整收发示例：发布、订阅与 UART 适配

这一节补齐第 10.1 节没有实现的发送路径。先分清三个动作：

- 主任务按调度发送 Header，选择本次通信的帧；PID 标识帧，不是节点地址。
- 发布者在当前 Header 后发送 Response；每个普通无条件帧只有一个发布者。
- 订阅者接收 Response，校验后交给应用；不因为订阅而返回 ACK。

**订阅关系来自提前配置的 LDF 或代码表，不需要先在总线上登记。**
第一次收到对应的合法 Header 就按配置处理；后续相同 PID 是再次调度，
不是第二阶段确认。一个节点可以发布某些帧，同时订阅另外一些帧。

本例继续使用第 7 节的帧与时隙，角色约定如下：

| 帧 | ID / PID | 发布者 | 订阅者 | 当前帧发生什么 |
| --- | --- | --- | --- | --- |
| A_Status | 01 / C1 | NodeA | Master、NodeB | 主机发 Header，NodeA 回状态 |
| B_Command | 02 / 42 | Master | NodeB | 主机发 Header 后继续发命令 |
| B_Status | 03 / 03 | NodeB | Master | 主机发 Header，NodeB 回状态 |

这里的 Master 是 LIN 主节点；“在电脑上运行的主机程序”则指 PC 测试程序。
二者不是同一个概念，电脑在本例中同时模拟三个独立 LIN 节点。

#### 10.3.1 发送逻辑在哪里，调用顺序是什么

| 入口 | 调用者和时机 | 下一步 |
| --- | --- | --- |
| Link_SetPayload | 发布者的业务代码准备数据 | 复制下一次要发布的数据，不直接发总线 |
| Link_MasterStart | 主节点调度器到达时隙 | 请求底层发送 Header |
| Link_OnTxDone | 平台确认最后一个停止位发完 | Header 后转接收或发送 Response |
| Link_OnHeader | 从节点底层确认合法 Header | 查表决定发布、订阅或忽略 |
| Link_SendResponse | 链路内部决定本节点需要发布 | 复制数据、算 Checksum，启动字节发送 |
| Link_OnResponse | 底层已经收到完整 Response | 校验并保存记录，不回复 ACK |
| Link_Poll | 节点所属任务周期执行 | 检查事务卡死，停止后才允许重试 |
| Link_OnIoError / Link_Recover | 底层报错 / 所属任务恢复 | 终止事务；停止失败则保持故障状态 |

以 ID 01 的第一个时隙为例：

1. 调度器调用主节点的 `Link_MasterStart(..., 0x01, ...)`。
2. 主节点先预备响应接收，再调用 `start_header()`；底层产生 Break、
   界定符、Sync 55 和 PID C1。
3. Header 实际发送完成，底层调用 `Link_OnTxDone()`，主节点转入等待响应。
4. NodeA 收到当前 Header 后查表发现自己是发布者，直接启动 `10 20 0E`。
   NodeB 查表发现自己是订阅者，准备接收同一份响应。
5. 主节点和 NodeB 收齐响应并校验，各自保存一份快照。NodeA 发送完成后空闲。
6. 到 20 ms 再次调度 ID 01 时重复上述动作，无须重新登记订阅。

ID 02 的区别是：主节点自己就是发布者，Header 完成后由
`Link_OnTxDone()` 调用 `Link_SendResponse()`；NodeB 只接收命令。

`0x55`、PID、每个 Data 字节和 Checksum 都由 UART 按 8N1 发送，
软件不在字节数组里另外添加起始位或停止位。Break 和界定符由专用底层接口
产生，不能用“发一个 0x00 字节”代替。

#### 10.3.2 先约定底层接口和时序边界

以下实现是非阻塞的教学链路，所有入口和完成事件由一个执行上下文按实际
事件顺序串行处理。底层启动函数不得在返回前重入链路事件函数。
真实系统若经队列转交事件，必须保证响应时限；不能假定普通低优先级任务
一定能及时发出从机响应。

| 平台接口 | 必须履行的约定 |
| --- | --- |
| prepare_rx | 预备接收 Data + Checksum，排除 Header 与本机发送回显 |
| start_header | 生成至少 13 bit Break、至少 1 bit 界定符，再发送 55 和 PID |
| start_response | 借用模块的发送副本，按 8N1 异步发送 Data + Checksum |
| abort | 取消当前事务；成功必须保证硬件停止访问旧缓冲区、事件已被隔离 |

`LINK_OK` 只表示请求受理，完成需另行通知。UART DMA 完成只说明搬运结束；
只有确认最后一个停止位输出完毕，才能通知 `Link_OnTxDone()`。
每个节点使用自己的 `ticket` 拒绝迟到事件，底层必须原样带回对应编号。

主节点的 `prepare_rx()` 在发 Header 前执行，是为了防止从机紧跟 PID 响应时
漏收首字节。底层还必须在发送完最后停止位后，先处理 Header 完成事件，
再交付 Response 完成事件；示例不处理被适配器任意颠倒的事件顺序。

本例仅实现表中的普通无条件帧，不含事件触发帧、诊断传输层、自动波特率、
休眠唤醒、实时 UART 字节组帧或实际引脚配置。

#### 10.3.3 数据结构与通信配置表

保留第 10.1 节原有代码。运行本节时，先复制 10.1.2、10.1.3、
10.1.4 的三个 `c` 代码块，**不复制 10.1.5 的旧 main()**，再依次拼接
本节四个 `c` 代码块。这样既复用 PID / Checksum，也保留原接收服务。

```c
/* 本示例仅处理表中的普通无条件帧；复用 10.1 的 PID、校验算法。 */
#define LINK_FRAME_COUNT        3U
#define LINK_NODE_COUNT         3U
#define LINK_SYNC_BYTE          0x55U
#define LINK_SLOT_US            10000U
#define LINK_WATCHDOG_US        LINK_SLOT_US
#define LINK_TIME_MAX_US        (UINT32_MAX / 2U)

typedef enum
{
    LINK_MASTER = 0,             /* 只有主节点可以主动发帧头 */
    LINK_NODE_A,
    LINK_NODE_B,
} Link_NodeId_t;

#define LINK_SUB_MASTER         (1U << LINK_MASTER)
#define LINK_SUB_A              (1U << LINK_NODE_A)
#define LINK_SUB_B              (1U << LINK_NODE_B)

typedef enum
{
    LINK_OK = 0,
    LINK_IGNORED,               /* 未订阅且不发布该帧，无需响应 */
    LINK_ERROR_NULL,
    LINK_ERROR_PARAMETER,
    LINK_ERROR_NOT_INITIALIZED,
    LINK_ERROR_STATE,
    LINK_ERROR_ROLE,            /* 当前节点不是所需的主机或发布者 */
    LINK_ERROR_BUSY,
    LINK_ERROR_UNKNOWN_ID,
    LINK_ERROR_PID,
    LINK_ERROR_NO_DATA,
    LINK_ERROR_LENGTH,
    LINK_ERROR_CHECKSUM,
    LINK_ERROR_IO,              /* 底层启动失败或报告硬件错误 */
    LINK_ERROR_TIMEOUT,         /* 本地事务看门狗到期 */
    LINK_ERROR_ABORT,           /* 未确认底层停止，禁止复用缓冲区 */
    LINK_ERROR_STALE_EVENT,     /* 已结束事务的迟到通知 */
    LINK_ERROR_SEQUENCE,        /* 事务编号耗尽，需受控重建对象 */
} Link_Result_t;

typedef enum
{
    LINK_IDLE = 0,
    LINK_HEADER_TX,
    LINK_RESPONSE_TX,
    LINK_RESPONSE_RX,
    LINK_FAULT,                 /* 停止失败，等待恢复 */
} Link_State_t;

typedef enum
{
    LINK_TX_HEADER = 0,
    LINK_TX_RESPONSE,
} Link_TxKind_t;

struct link_frame_cfg
{
    uint8_t id;
    uint8_t length;             /* 仅 Data，不含 Checksum */
    Lin_ChecksumMode_t mode;
    Link_NodeId_t publisher;    /* 每帧恰有一个发布者 */
    uint8_t subscribers;        /* 按节点编号建立订阅位图 */
};

/* 三个节点使用相同的通信约定，不需要在总线上注册订阅。 */
static const struct link_frame_cfg s_link_frames[LINK_FRAME_COUNT] =
{
    {0x01U, 2U, LIN_CHECKSUM_ENHANCED, LINK_NODE_A,
     LINK_SUB_MASTER | LINK_SUB_B},
    {0x02U, 2U, LIN_CHECKSUM_ENHANCED, LINK_MASTER, LINK_SUB_B},
    {0x03U, 2U, LIN_CHECKSUM_ENHANCED, LINK_NODE_B, LINK_SUB_MASTER},
};

/* 所有函数立即返回；成功只代表受理，完成通过事件另外通知。 */
struct link_port
{
    Link_Result_t (*prepare_rx)(void *io, uint32_t ticket,
                                uint8_t wire_length);
    Link_Result_t (*start_header)(void *io, uint32_t ticket, uint8_t pid);
    Link_Result_t (*start_response)(void *io, uint32_t ticket,
                                    const uint8_t *wire, uint8_t length);
    Link_Result_t (*abort)(void *io, uint32_t ticket);
};

struct link_cfg
{
    Link_NodeId_t node;
    uint32_t watchdog_us;       /* 本地卡死保护，不是规范最大帧时间 */
    const struct link_port *port;
    void *io;                  /* 平台适配器私有对象 */
};

struct link_ctx
{
    bool initialized;
    Link_State_t state;
    uint8_t frame_index;
    uint8_t pid;
    uint32_t ticket;           /* 每个节点独立递增，用于拒绝迟到事件 */
    uint32_t started_us;
    uint8_t wire[LIN_DATA_MAX_LENGTH + 1U]; /* 独占发送缓冲区 */
    Link_Result_t last_result;
};

struct link_received
{
    uint8_t payload[LIN_DATA_MAX_LENGTH];
    uint8_t length;
    uint8_t checksum;
    uint32_t rx_us;
    bool received;            /* 收到过正确帧，不代表业务仍然新鲜 */
};

struct link_data
{
    uint8_t pending[LINK_FRAME_COUNT][LIN_DATA_MAX_LENGTH];
    bool prepared[LINK_FRAME_COUNT];
    struct link_received received[LINK_FRAME_COUNT];
};

struct link_node
{
    struct link_cfg cfg;       /* 初始化后只读 */
    struct link_ctx ctx;       /* 仅链路模块维护 */
    struct link_data data;     /* 发布数据和已收数据分别存放 */
};
```

#### 10.3.4 链路实现：按角色驱动状态

这里的 `struct link_node` 表示一个独立实例。它包含分开的配置、内部状态
和数据对象，三个节点不会共用接收状态或发送缓冲区。初始化时必须先清零；
后续业务代码只通过下面的行为接口读写，不能直接修改 `ctx`。

| 四元组 | 本节对应内容 | 修改权限 |
| --- | --- | --- |
| cfg | 固定帧表、节点角色、平台接口、本地看门狗 | 初始化时建立，运行期只读 |
| ctx | 当前帧、状态、ticket、事务起点、发送副本 | 仅链路模块维护 |
| data | 待发布数据、最近正确接收记录 | 通过发布更新和快照接口访问 |
| ops | Link_MasterStart、Link_OnHeader 等函数 | 描述请求行为，底层细节交给 port |

`ctx.wire` 是事务独占缓冲区。业务更新 `data.pending` 时，不会改动正在
发送的副本。即使发生超时，也必须等 `abort()` 确认停止后才能复用它。
`Link_Stop()`、`Link_Open()`、`Link_SendResponse()` 和
`Link_ArmResponse()` 仅供内部使用，由已验证的入口保证对象和表索引有效。

`received` 表示“历史上收到过正确数据”，不是新鲜度标志。
本节链路记录接收时间；业务有效期继续由第 10.1 节的服务或上层规则检查，
避免把 UART 事务结束与业务数据仍然有效混为一谈。

```c
/* 检查对象；所有节点在首次初始化前必须静态清零或用 {0} 初始化。 */
static Link_Result_t Link_Check(const struct link_node *node)
{
    if (NULL == node)
    {
        return LINK_ERROR_NULL;
    }
    if (false == node->ctx.initialized)
    {
        return LINK_ERROR_NOT_INITIALIZED;
    }
    return LINK_OK;
}

/* 查固定帧表，成功时写 index；失败时不写输出。 */
static Link_Result_t Link_Find(uint8_t id, uint8_t *index)
{
    uint8_t item;

    if (NULL == index)
    {
        return LINK_ERROR_NULL;
    }
    for (item = 0U; item < LINK_FRAME_COUNT; item++)
    {
        if (s_link_frames[item].id == id)
        {
            *index = item;
            return LINK_OK;
        }
    }
    return LINK_ERROR_UNKNOWN_ID;
}

/*
 * 复制 cfg 并清空数据；port、io 的生命周期必须覆盖 node 的使用期。
 * 返回指针、配置或重复初始化错误，不配置实际引脚。
 */
static Link_Result_t Link_Init(struct link_node *node,
                               const struct link_cfg *cfg)
{
    /* 1. 验证对象及所有回调。2. 建立空闲状态，最后开放调用。 */
    if ((NULL == node) || (NULL == cfg) || (NULL == cfg->port)
        || (NULL == cfg->io))
    {
        return LINK_ERROR_NULL;
    }
    if (true == node->ctx.initialized)
    {
        return LINK_ERROR_STATE;
    }
    if (((LINK_MASTER != cfg->node) && (LINK_NODE_A != cfg->node)
         && (LINK_NODE_B != cfg->node))
        || (0U == cfg->watchdog_us)
        || (LINK_TIME_MAX_US < cfg->watchdog_us))
    {
        return LINK_ERROR_PARAMETER;
    }
    if ((NULL == cfg->port->prepare_rx)
        || (NULL == cfg->port->start_header)
        || (NULL == cfg->port->start_response)
        || (NULL == cfg->port->abort))
    {
        return LINK_ERROR_NULL;
    }
    *node = (struct link_node){0};
    node->cfg = *cfg;
    node->ctx.initialized = true;
    return LINK_OK;
}

/*
 * 发布者更新下一次发送的数据，length 必须匹配帧配置。
 * 允许发送期间准备下一份数据；正在发送的 wire 不受影响。
 */
static Link_Result_t Link_SetPayload(struct link_node *node, uint8_t id,
                                     const uint8_t *payload,
                                     uint8_t length)
{
    uint8_t index;
    Link_Result_t result = Link_Check(node);

    /* 1. 验证所有权与长度。2. 复制数据，发布准备完成标记。 */
    if (LINK_OK != result)
    {
        return result;
    }
    if (NULL == payload)
    {
        return LINK_ERROR_NULL;
    }
    result = Link_Find(id, &index);
    if (LINK_OK != result)
    {
        return result;
    }
    if (s_link_frames[index].publisher != node->cfg.node)
    {
        return LINK_ERROR_ROLE;
    }
    if (s_link_frames[index].length != length)
    {
        return LINK_ERROR_LENGTH;
    }
    memcpy(node->data.pending[index], payload, length);
    node->data.prepared[index] = true;
    return LINK_OK;
}

/*
 * 终止当前事务；abort 成功必须保证 UART/DMA 已停止访问缓冲区。
 * 停止失败时保持 FAULT，调用方不得释放 node 或适配器对象。
 */
static Link_Result_t Link_Stop(struct link_node *node,
                               Link_Result_t reason)
{
    if (LINK_OK != node->cfg.port->abort(node->cfg.io, node->ctx.ticket))
    {
        node->ctx.state = LINK_FAULT;
        node->ctx.last_result = LINK_ERROR_ABORT;
        return LINK_ERROR_ABORT;
    }
    node->ctx.state = LINK_IDLE;
    node->ctx.last_result = reason;
    return reason;
}

/* 内部打开一次新事务；只允许空闲时调用，编号不允许回绕复用。 */
static Link_Result_t Link_Open(struct link_node *node, uint8_t index,
                               uint8_t pid, uint32_t now_us)
{
    if (LINK_IDLE != node->ctx.state)
    {
        return LINK_ERROR_BUSY;
    }
    if (UINT32_MAX == node->ctx.ticket)
    {
        return LINK_ERROR_SEQUENCE;
    }
    node->ctx.ticket++;
    node->ctx.frame_index = index;
    node->ctx.pid = pid;
    node->ctx.started_us = now_us;
    node->ctx.last_result = LINK_OK;
    return LINK_OK;
}

/* 内部复制发布数据并生成响应；缓冲区由模块保留到完成或停止确认。 */
static Link_Result_t Link_SendResponse(struct link_node *node)
{
    uint8_t index = node->ctx.frame_index;
    uint8_t length = s_link_frames[index].length;
    Link_Result_t result;

    /* 1. 检查数据。2. 固化本帧副本及校验和。3. 启动异步发送。 */
    if (false == node->data.prepared[index])
    {
        return Link_Stop(node, LINK_ERROR_NO_DATA);
    }
    memcpy(node->ctx.wire, node->data.pending[index], length);
    if (LIN_SUCCESS != Lin_CalculateChecksum(
            node->ctx.pid, node->ctx.wire, length,
            s_link_frames[index].mode, &node->ctx.wire[length]))
    {
        return Link_Stop(node, LINK_ERROR_PARAMETER);
    }
    node->ctx.state = LINK_RESPONSE_TX;
    result = node->cfg.port->start_response(
        node->cfg.io, node->ctx.ticket, node->ctx.wire,
        (uint8_t)(length + 1U));
    if (LINK_OK != result)
    {
        return Link_Stop(node, result);
    }
    return LINK_OK;
}

/* 内部准备接收，wire_length 同时包括 Data 和最后一个 Checksum。 */
static Link_Result_t Link_ArmResponse(struct link_node *node)
{
    uint8_t index = node->ctx.frame_index;
    Link_Result_t result = node->cfg.port->prepare_rx(
        node->cfg.io, node->ctx.ticket,
        (uint8_t)(s_link_frames[index].length + 1U));

    if (LINK_OK != result)
    {
        return Link_Stop(node, result);
    }
    return LINK_OK;
}

/*
 * 主节点按调度表调用，发送 Break、界定符、Sync 和 PID。
 * 返回 OK 仅表示帧头请求已受理，禁止在这里直接开始下一个时隙。
 */
static Link_Result_t Link_MasterStart(struct link_node *node,
                                      uint8_t id, uint32_t now_us)
{
    uint8_t index;
    uint8_t pid;
    Link_Result_t result = Link_Check(node);

    /*
     * 1. 检查角色、帧配置和状态。
     * 2. 订阅响应时先预备接收，防止从机立即响应而漏掉首字节。
     * 3. 将特殊 Break 生成和字节发送交给平台，等待完成事件。
     */
    if (LINK_OK != result)
    {
        return result;
    }
    if (LINK_MASTER != node->cfg.node)
    {
        return LINK_ERROR_ROLE;
    }
    result = Link_Find(id, &index);
    if (LINK_OK != result)
    {
        return result;
    }
    if (LIN_SUCCESS != Lin_MakePid(id, &pid))
    {
        return LINK_ERROR_PID;
    }
    if ((LINK_MASTER == s_link_frames[index].publisher)
        && (false == node->data.prepared[index]))
    {
        return LINK_ERROR_NO_DATA;
    }
    result = Link_Open(node, index, pid, now_us);
    if (LINK_OK != result)
    {
        return result;
    }
    node->ctx.state = LINK_HEADER_TX;
    if (LINK_MASTER != s_link_frames[index].publisher)
    {
        result = Link_ArmResponse(node);
        if (LINK_OK != result)
        {
            return result;
        }
    }
    result = node->cfg.port->start_header(
        node->cfg.io, node->ctx.ticket, pid);
    if (LINK_OK != result)
    {
        return Link_Stop(node, result);
    }
    return LINK_OK;
}

/*
 * 从节点在底层确认 Break / Sync / PID 后调用；不登记订阅关系。
 * 新 Break 必须先走 Link_OnBreak；未知或无关帧不启动响应。
 */
static Link_Result_t Link_OnHeader(struct link_node *node, uint8_t pid,
                                   uint32_t now_us)
{
    uint8_t id;
    uint8_t index;
    Link_Result_t result = Link_Check(node);

    /* 1. 检查 PID。2. 查表决定发布、订阅或忽略。3. 立即启动本帧动作。 */
    if (LINK_OK != result)
    {
        return result;
    }
    if (LINK_MASTER == node->cfg.node)
    {
        return LINK_ERROR_ROLE;
    }
    if (LINK_IDLE != node->ctx.state)
    {
        return LINK_ERROR_BUSY;
    }
    if (LIN_SUCCESS != Lin_DecodePid(pid, &id))
    {
        return LINK_ERROR_PID;
    }
    result = Link_Find(id, &index);
    if (LINK_OK != result)
    {
        return result;
    }
    if ((s_link_frames[index].publisher != node->cfg.node)
        && (0U == (s_link_frames[index].subscribers
                   & (1U << node->cfg.node))))
    {
        return LINK_IGNORED;
    }
    result = Link_Open(node, index, pid, now_us);
    if (LINK_OK != result)
    {
        return result;
    }
    if (s_link_frames[index].publisher == node->cfg.node)
    {
        return Link_SendResponse(node);
    }
    node->ctx.state = LINK_RESPONSE_RX;
    return Link_ArmResponse(node);
}

/*
 * 处理真正的发送完成；kind 区分帧头与响应，ticket 区分事务。
 * 平台须在最后一个停止位发完后通知，不可直接用 DMA 搬运完成代替。
 */
static Link_Result_t Link_OnTxDone(struct link_node *node,
                                   uint32_t ticket, Link_TxKind_t kind)
{
    Link_Result_t result = Link_Check(node);

    /* 1. 检查通知归属。2. 帧头完成后转收或转发。3. 响应完成后归还空闲。 */
    if (LINK_OK != result)
    {
        return result;
    }
    if ((LINK_TX_HEADER != kind) && (LINK_TX_RESPONSE != kind))
    {
        return LINK_ERROR_PARAMETER;
    }
    if ((node->ctx.ticket != ticket)
        || ((LINK_TX_HEADER == kind)
            && (LINK_HEADER_TX != node->ctx.state))
        || ((LINK_TX_RESPONSE == kind)
            && (LINK_RESPONSE_TX != node->ctx.state)))
    {
        return LINK_ERROR_STALE_EVENT;
    }
    if (LINK_TX_HEADER == kind)
    {
        if (LINK_MASTER
            == s_link_frames[node->ctx.frame_index].publisher)
        {
            return Link_SendResponse(node);
        }
        node->ctx.state = LINK_RESPONSE_RX;
    }
    else
    {
        node->ctx.state = LINK_IDLE;
        node->ctx.last_result = LINK_OK;
    }
    return LINK_OK;
}

/*
 * 接收底层已经分离回显并组好的 Data + Checksum；不含 PID。
 * wire 须可读 length 字节；坏帧不覆盖最近正确的接收记录。
 */
static Link_Result_t Link_OnResponse(struct link_node *node,
                                     uint32_t ticket,
                                     const uint8_t *wire,
                                     uint8_t length, uint32_t now_us)
{
    uint8_t index;
    uint8_t expected;
    uint8_t data_length;
    struct link_received next = {0};
    Link_Result_t result = Link_Check(node);

    /* 1. 检查事件及长度。2. 验证校验和。3. 复制正确帧并结束接收。 */
    if (LINK_OK != result)
    {
        return result;
    }
    if (NULL == wire)
    {
        return LINK_ERROR_NULL;
    }
    if ((node->ctx.ticket != ticket)
        || (LINK_RESPONSE_RX != node->ctx.state))
    {
        return LINK_ERROR_STALE_EVENT;
    }
    index = node->ctx.frame_index;
    data_length = s_link_frames[index].length;
    if ((uint8_t)(data_length + 1U) != length)
    {
        return Link_Stop(node, LINK_ERROR_LENGTH);
    }
    if (LIN_SUCCESS != Lin_CalculateChecksum(
            node->ctx.pid, wire, data_length,
            s_link_frames[index].mode, &expected))
    {
        return Link_Stop(node, LINK_ERROR_PARAMETER);
    }
    if (expected != wire[data_length])
    {
        return Link_Stop(node, LINK_ERROR_CHECKSUM);
    }
    memcpy(next.payload, wire, data_length);
    next.length = data_length;
    next.checksum = wire[data_length];
    next.rx_us = now_us;
    next.received = true;
    node->data.received[index] = next;
    node->ctx.state = LINK_IDLE;
    node->ctx.last_result = LINK_OK;
    return LINK_OK;
}

/* 获取接收记录副本；received 仅表示历史正确接收，业务超时由上层处理。 */
static Link_Result_t Link_GetReceived(const struct link_node *node,
                                      uint8_t id,
                                      struct link_received *snapshot)
{
    uint8_t index;
    Link_Result_t result = Link_Check(node);

    if (LINK_OK != result)
    {
        return result;
    }
    if (NULL == snapshot)
    {
        return LINK_ERROR_NULL;
    }
    result = Link_Find(id, &index);
    if (LINK_OK != result)
    {
        return result;
    }
    *snapshot = node->data.received[index];
    return (true == snapshot->received) ? LINK_OK : LINK_ERROR_NO_DATA;
}

/* 从节点发现新 Break 时先终止旧事务，再等待 Sync/PID；忽略本机回显。 */
static Link_Result_t Link_OnBreak(struct link_node *node)
{
    Link_Result_t result = Link_Check(node);

    if (LINK_OK != result)
    {
        return result;
    }
    if (LINK_MASTER == node->cfg.node)
    {
        return LINK_ERROR_ROLE;
    }
    if (LINK_FAULT == node->ctx.state)
    {
        return LINK_ERROR_ABORT;
    }
    if (LINK_IDLE == node->ctx.state)
    {
        return LINK_OK;
    }
    return Link_Stop(node, LINK_OK);
}

/* 平台报告异步硬件错误；迟到错误不得停止当前新事务。 */
static Link_Result_t Link_OnIoError(struct link_node *node,
                                    uint32_t ticket)
{
    Link_Result_t result = Link_Check(node);

    if (LINK_OK != result)
    {
        return result;
    }
    if ((node->ctx.ticket != ticket) || (LINK_IDLE == node->ctx.state))
    {
        return LINK_ERROR_STALE_EVENT;
    }
    return Link_Stop(node, LINK_ERROR_IO);
}

/* 周期检查本地事务卡死；必须使用同一单调微秒时钟，按时序串行调用。 */
static Link_Result_t Link_Poll(struct link_node *node, uint32_t now_us)
{
    Link_Result_t result = Link_Check(node);

    if (LINK_OK != result)
    {
        return result;
    }
    if (LINK_FAULT == node->ctx.state)
    {
        return LINK_ERROR_ABORT;
    }
    if ((LINK_IDLE != node->ctx.state)
        && (node->cfg.watchdog_us
            <= (uint32_t)(now_us - node->ctx.started_us)))
    {
        return Link_Stop(node, LINK_ERROR_TIMEOUT);
    }
    return LINK_OK;
}

/* 停止失败后显式重试；只有底层确认静止，才能重新启动事务。 */
static Link_Result_t Link_Recover(struct link_node *node)
{
    Link_Result_t result = Link_Check(node);

    if (LINK_OK != result)
    {
        return result;
    }
    if (LINK_FAULT != node->ctx.state)
    {
        return LINK_ERROR_STATE;
    }
    return Link_Stop(node, LINK_OK);
}
```

#### 10.3.5 模拟 UART：看清“启动”和“完成”

下面的适配器只记录请求，并保留发送缓冲区的借用地址；
`Mock_CompleteTx()` 才模拟发送完成，`Mock_DeliverRx()` 才模拟接收完成。
它不生成真实电压波形，不假装已经配置了某款 MCU。

`fail_start` 和 `fail_abort` 用于测试启动与停止失败。
真实平台应把对应 UART / DMA 错误转换为事件，不能照搬这些模拟字段。

```c
/* 模拟器记录请求并保留借用地址；没有 UART、引脚或真实时间。 */
#include <stdio.h>

struct mock_port
{
    const char *name;
    struct link_node *owner;
    bool verbose;
    bool busy;
    bool armed;
    uint8_t expected_length;
    Link_TxKind_t kind;
    uint32_t tx_ticket;
    uint32_t rx_ticket;
    const uint8_t *borrowed;     /* 模拟 DMA 尚在使用发送缓冲区 */
    uint8_t tx_length;
    bool fail_start;            /* 测试下一次发送启动失败 */
    bool fail_abort;            /* 测试无法确认硬件停止 */
};

/* 预备响应接收；实际适配器需要排除帧头和发送回显。 */
static Link_Result_t Mock_PrepareRx(void *io, uint32_t ticket,
                                    uint8_t length)
{
    struct mock_port *port = io;

    if (NULL == port)
    {
        return LINK_ERROR_NULL;
    }
    if ((LIN_DATA_MIN_LENGTH + 1U > length)
        || (LIN_DATA_MAX_LENGTH + 1U < length))
    {
        return LINK_ERROR_LENGTH;
    }
    if ((true == port->armed) || (true == port->busy))
    {
        return LINK_ERROR_BUSY;
    }
    port->armed = true;
    port->rx_ticket = ticket;
    port->expected_length = length;
    return LINK_OK;
}

/* 仅记录主机发帧头；真实平台需要产生特殊 Break 和界定符。 */
static Link_Result_t Mock_StartHeader(void *io, uint32_t ticket,
                                      uint8_t pid)
{
    struct mock_port *port = io;

    if (NULL == port)
    {
        return LINK_ERROR_NULL;
    }
    if (true == port->busy)
    {
        return LINK_ERROR_BUSY;
    }
    if (true == port->fail_start)
    {
        port->fail_start = false;
        return LINK_ERROR_IO;
    }
    port->busy = true;
    port->kind = LINK_TX_HEADER;
    port->tx_ticket = ticket;
    if (true == port->verbose)
    {
        printf("%s HEADER: Break delimiter | %02X %02X\n", port->name,
               (unsigned int)LINK_SYNC_BYTE, (unsigned int)pid);
    }
    return LINK_OK;
}

/* 借用 wire，直到完成通知或 abort 成功；绝不在这里伪造完成事件。 */
static Link_Result_t Mock_StartResponse(void *io, uint32_t ticket,
                                        const uint8_t *wire,
                                        uint8_t length)
{
    struct mock_port *port = io;
    uint8_t index;

    if ((NULL == port) || (NULL == wire))
    {
        return LINK_ERROR_NULL;
    }
    if ((LIN_DATA_MIN_LENGTH + 1U > length)
        || (LIN_DATA_MAX_LENGTH + 1U < length))
    {
        return LINK_ERROR_LENGTH;
    }
    if (true == port->busy)
    {
        return LINK_ERROR_BUSY;
    }
    if (true == port->fail_start)
    {
        port->fail_start = false;
        return LINK_ERROR_IO;
    }
    port->busy = true;
    port->kind = LINK_TX_RESPONSE;
    port->tx_ticket = ticket;
    port->borrowed = wire;
    port->tx_length = length;
    if (true == port->verbose)
    {
        printf("%s RESPONSE:", port->name);
        for (index = 0U; index < length; index++)
        {
            printf(" %02X", (unsigned int)wire[index]);
        }
        putchar('\n');
    }
    return LINK_OK;
}

/* 成功即确认停止；模拟停止失败时仍保留借用地址，禁止复用。 */
static Link_Result_t Mock_Abort(void *io, uint32_t ticket)
{
    struct mock_port *port = io;

    (void)ticket;               /* 模拟器每个端口仅允许一个活动事务。 */
    if (NULL == port)
    {
        return LINK_ERROR_NULL;
    }
    if (true == port->fail_abort)
    {
        return LINK_ERROR_ABORT;
    }
    port->busy = false;
    port->armed = false;
    port->borrowed = NULL;
    return LINK_OK;
}

static const struct link_port s_mock_ops =
{
    .prepare_rx = Mock_PrepareRx,
    .start_header = Mock_StartHeader,
    .start_response = Mock_StartResponse,
    .abort = Mock_Abort,
};

/* 由测试驱动推进事件，模拟最后停止位已经发完，而非函数刚返回。 */
static Link_Result_t Mock_CompleteTx(struct mock_port *port)
{
    uint32_t ticket;
    Link_TxKind_t kind;

    if (NULL == port)
    {
        return LINK_ERROR_NULL;
    }
    if (false == port->busy)
    {
        return LINK_ERROR_STATE;
    }
    ticket = port->tx_ticket;
    kind = port->kind;
    port->busy = false;
    port->borrowed = NULL;
    return Link_OnTxDone(port->owner, ticket, kind);
}

/* 模拟底层收到完整响应；不添加 ACK，也不包含 UART 起止位。 */
static Link_Result_t Mock_DeliverRx(struct mock_port *port,
                                    const uint8_t *wire,
                                    uint8_t length, uint32_t now_us)
{
    if ((NULL == port) || (NULL == wire))
    {
        return LINK_ERROR_NULL;
    }
    if (false == port->armed)
    {
        return LINK_ERROR_STATE;
    }
    port->armed = false;
    return Link_OnResponse(port->owner, port->rx_ticket,
                           wire, length, now_us);
}
```

#### 10.3.6 跑一轮调度：主机和从机都发送一次

下面按 0、10、20、30 ms 依次调度 01、02、01、03，与第 7 节一致。
教学数据为 A_Status = 10 20、B_Command = 01 02、B_Status = 30 40；
这些只是无业务映射的测试字节，增强校验分别为 0E、BA、8C。

`1800 us` 和 `3500 us` 是人工推进事件的测试时间，分别略晚于本例
19.2 kbit/s 的最短 Header 和两字节完整帧时间，不是实测值或响应延迟要求。
模拟器按确定顺序推进完成通知，不进行实时等待。

主机将收到的 A_Status 交给原来的 `s_lin_ops.on_frame()`，
展示“链路接收 → 业务新鲜度服务”的衔接；其余帧只展示收发与快照。
业务毫秒时间必须来自独立的单调毫秒时基或平台正确扩展的时基；
下例的除以 1000 仅适用于本轮短时、没有回绕的人工时间，不能把
32 bit 微秒计数直接除以 1000 后当成长期单调毫秒时钟。

```c
/* 主机程序：按前文四个 10 ms 时隙，人工推进 UART 完成事件。 */
int main(void)
{
    struct link_node nodes[LINK_NODE_COUNT] = {0};
    struct mock_port ports[LINK_NODE_COUNT] = {0};
    const char *names[] = {"Master", "NodeA", "NodeB"};
    const uint8_t schedule[] = {0x01U, 0x02U, 0x01U, 0x03U};
    const uint8_t status_a[] = {0x10U, 0x20U};
    const uint8_t command_b[] = {0x01U, 0x02U};
    const uint8_t status_b[] = {0x30U, 0x40U};
    const struct lin_cfg service_cfg =
        {0x01U, 2U, LIN_CHECKSUM_ENHANCED, 100U};
    struct lin_data service_snapshot;
    unsigned int item;
    unsigned int slot;

    /*
     * 1. 初始化三个独立节点，提前准备各发布者的数据。
     * 2. 每个时隙发送帧头，再模拟各节点在当前帧的发布或订阅。
     * 3. 将主机收到的 A_Status 交给 10.1 的业务新鲜度服务。
     */
    for (item = 0U; item < LINK_NODE_COUNT; item++)
    {
        const struct link_cfg cfg =
        {
            .node = (Link_NodeId_t)item,
            .watchdog_us = LINK_WATCHDOG_US,
            .port = &s_mock_ops,
            .io = &ports[item],
        };

        ports[item].name = names[item];
        ports[item].owner = &nodes[item];
        ports[item].verbose = true;
        if (LINK_OK != Link_Init(&nodes[item], &cfg))
        {
            return 1;
        }
    }
    if ((LINK_OK != Link_SetPayload(&nodes[LINK_NODE_A],
                                    0x01U, status_a, 2U))
        || (LINK_OK != Link_SetPayload(&nodes[LINK_MASTER],
                                       0x02U, command_b, 2U))
        || (LINK_OK != Link_SetPayload(&nodes[LINK_NODE_B],
                                       0x03U, status_b, 2U))
        || (LIN_SUCCESS != s_lin_ops.init(&service_cfg)))
    {
        return 1;
    }

    for (slot = 0U; slot < sizeof(schedule) / sizeof(schedule[0]); slot++)
    {
        uint8_t index;
        uint8_t pid;
        uint8_t wire[LIN_DATA_MAX_LENGTH + 1U];
        uint8_t wire_length;
        uint32_t start_us = slot * LINK_SLOT_US;
        struct mock_port *publisher;
        struct link_received received;

        if ((LINK_OK != Link_Find(schedule[slot], &index))
            || (LIN_SUCCESS != Lin_MakePid(schedule[slot], &pid))
            || (LINK_OK != Link_MasterStart(&nodes[LINK_MASTER],
                                             schedule[slot], start_us))
            || (LINK_OK != Mock_CompleteTx(&ports[LINK_MASTER])))
        {
            return 1;
        }
        for (item = LINK_NODE_A; item <= LINK_NODE_B; item++)
        {
            Link_Result_t result;

            if (LINK_OK != Link_OnBreak(&nodes[item]))
            {
                return 1;
            }
            result = Link_OnHeader(&nodes[item], pid, start_us + 1800U);
            if ((LINK_OK != result) && (LINK_IGNORED != result))
            {
                return 1;
            }
        }

        publisher = &ports[s_link_frames[index].publisher];
        wire_length = publisher->tx_length;
        memcpy(wire, publisher->borrowed, wire_length);
        if (LINK_OK != Mock_CompleteTx(publisher))
        {
            return 1;
        }
        for (item = 0U; item < LINK_NODE_COUNT; item++)
        {
            if (0U != (s_link_frames[index].subscribers & (1U << item)))
            {
                if (LINK_OK != Mock_DeliverRx(
                        &ports[item], wire, wire_length,
                        start_us + 3500U))
                {
                    return 1;
                }
                printf("%s received ID=%02X\n", names[item],
                       (unsigned int)schedule[slot]);
            }
        }
        if (0x01U == schedule[slot])
        {
            if ((LINK_OK != Link_GetReceived(&nodes[LINK_MASTER],
                                              0x01U, &received))
                || (LIN_SUCCESS != s_lin_ops.on_frame(
                        pid, received.payload,
                        received.length, received.checksum,
                        received.rx_us / 1000U)))
            {
                return 1;
            }
        }
    }
    if ((LIN_SUCCESS != s_lin_ops.get_snapshot(33U, &service_snapshot))
        || (false == service_snapshot.valid)
        || (LINK_OK != Link_Poll(&nodes[LINK_MASTER], 40000U)))
    {
        return 1;
    }
    /* 本次未发生故障；引用错误入口，供读者查找实际平台应接的位置。 */
    (void)Link_OnIoError;
    (void)Link_Recover;
    return 0;
}
```

预期输出：

```text
Master HEADER: Break delimiter | 55 C1
NodeA RESPONSE: 10 20 0E
Master received ID=01
NodeB received ID=01
Master HEADER: Break delimiter | 55 42
Master RESPONSE: 01 02 BA
NodeB received ID=02
Master HEADER: Break delimiter | 55 C1
NodeA RESPONSE: 10 20 0E
Master received ID=01
NodeB received ID=01
Master HEADER: Break delimiter | 55 03
NodeB RESPONSE: 30 40 8C
Master received ID=03
```

注意第一条 C1 就有 NodeA 的响应，不需要等第二条 C1；
ID 02 由主机发布，NodeA 既不发布也不订阅，保持静默；
NodeB 订阅 01、02，发布 03。同一个节点可以拥有不同帧的不同职责。

#### 10.3.7 异常、时限与真正移植时要接的位置

| 事件或状态 | 处理方式 |
| --- | --- |
| 未初始化、空指针、长度不匹配 | 返回明确错误，拒绝访问或复制无效对象 |
| 未配置 ID、PID 保护位错误 | 拒绝本帧，不发送响应 |
| 已知但与本节点无关的帧 | 返回 LINK_IGNORED，不改变订阅配置 |
| 发布者尚未准备数据 | 返回 NO_DATA，不擅自发布全零；应在启用调度前准备好 |
| UART 忙、启动失败、硬件错误 | 尝试停止，记录结果，等待后续调度或上层处理 |
| 接收长度错误、Checksum 错误 | 丢弃当前更新，保留上一份接收记录及其原时间戳 |
| 事务看门狗到期 | 停止事务；停止成功才归还空闲，不自动在总线抢发重试 |
| 停止无法确认 | 进入 FAULT，禁止重新启动，恢复成功前保留发送缓冲区 |
| 旧事务完成或错误通知迟到 | 根据 ticket 和阶段拒绝，避免结束当前新事务 |
| 新 Break 到来 | 从节点先停止旧事务，再接收新 Header；故障态仍需显式恢复 |

本例的 10 ms 看门狗是 PC 演示用的本地卡死保护，并不是 LIN 规范规定的
响应超时阈值，也不是“允许延迟 10 ms 才回复”。真实接收状态机应按适用规范、
外设能力和网络配置完成组帧、时序检查与 Break 重同步。

实际平台必须及时启动从机响应。不能把完整 Header 排队到一个慢任务后，
仍默认不会错过响应机会；应使用外设、驱动状态机或满足时限的处理上下文。
发现新的 Break 时，也要及时终止旧响应，不等到慢任务才释放 TX。

事务时间使用同一来源的单调微秒计数。时间戳、事件按实际先后处理，
看门狗和检查间隔均不得超过半个 32 bit 计数范围，以正确处理跨零回绕。
调度器每个时隙先处理完成、错误和超时事件，再尝试启动新帧；
如果上帧仍忙或处于故障态，应按项目策略跳过或记录时隙，不能重叠发帧。
这些条件需要 RTOS 任务周期、优先级、ISR 延迟和总线抓包共同验证。

第 10.1 节的 `timeout_ms` 用于判断业务数据多久没有有效更新；
本节的 `watchdog_us` 用于防止一次链路事务永久卡住。
两者控制不同状态，业务数据过期不会授权从节点自行发送 Header。

要接到真实 MCU，需要在平台适配层补齐以下路径：

1. `start_header()`：LIN 外设或经确认的 UART Break 机制 →
   Break / delimiter → Sync / PID → 真正的 Header 完成通知。
2. `start_response()`：保持缓冲区生命周期 → UART 中断或 DMA 发送 →
   UART 最终发送完成 → `Link_OnTxDone()`。
3. 接收：Break / Sync / PID 识别 → 从节点 `Link_OnHeader()` →
   接收指定长度 → 分离本机回显 → `Link_OnResponse()`。
4. 错误与恢复：硬件错误 → `Link_OnIoError()`；定时检查 →
   `Link_Poll()`；确认停止失败后，修复底层条件再调用 `Link_Recover()`。

平台底层负责硬件，帧表负责通信约定，上层服务负责业务取值、有效期和动作。
接收命令不会自动执行硬件，也不会自动返回 ACK。若需要确认执行结果，
应由真实应用更新相应状态帧，不能把本例固定的 B_Status 当作执行完成证明。

#### 10.3.8 编译方法和本次验证结果

按 10.3.3 说明拼接代码，保存为 UTF-8 的 `lin_link_demo.c`：

```powershell
gcc -std=c11 -O2 -Wall -Wextra -Werror -Wconversion `
    -Wshadow -Wpedantic -finput-charset=UTF-8 lin_link_demo.c `
    -o lin_link_demo.exe
.\lin_link_demo.exe
```

2026-11-11 在电脑上使用 GCC 16.2.0 编译并运行本节示例：

- 严格告警编译通过，输出与上面的四个时隙一致。
- 临时主机测试通过 304 次断言，检查发布 / 订阅 / 忽略矩阵，
  参数和角色错误、首帧直接响应、发送期间的数据副本隔离。
- 覆盖 Header 启动失败、Response 启动失败、硬件报错、
  长度和校验错误、Header / TX / RX 看门狗、停止失败与恢复。
- 检查新 Break 重同步、重复及迟到事件、事务编号耗尽、
  微秒计数回绕，以及错误帧不覆盖上次正确接收记录。
- 已检查代码和注释 80 列，以及 Markdown 代码围栏和差异范围。

模拟器不证明实际 Break 位宽、响应时限、波形电平、收发器控制、
回显消除、UART/DMA 停止行为或 RTOS 并发正确；这些仍需目标编译、
示波器和 LIN 分析仪验证。

## 11. 完整走一遍抓包示例

使用前面的教学网络：主节点轮询 `A_Status`，NodeA 发布，长度 2 字节，
采用 Enhanced；假设 `A_Keys = 0x10`，`A_Level = 0x20`。

```text
主节点发送： Break | delimiter | 55 | C1
NodeA 发送：                               10 | 20 | 0E
```

逐步解读：

1. 长低电平和界定符表示新帧；测低电平宽度，确认 Break 符合要求。
2. `55` 是同步字节，从位时间确认是否接近配置的 19.2 kbit/s。
3. `C1` 是 PID，检查保护位后得到 `C1 & 3F = 01`。
4. 查 LDF：ID 01 对应 A_Status，发布者 NodeA，长度 2 字节。
5. 因此 `10 20` 是数据，后面的 `0E` 是 Checksum，不能把它当第三个数据字节。
6. 增强校验：`C1 + 10 + 20 + 0E = FF`，本例校验正确。
7. offset 0 的 A_Keys 为 `0x10`，offset 8 的 A_Level 为 `0x20`。
8. 服务完成取值检查，发布一致快照，主节点和 NodeB 的应用才使用它。

这里仅演示原始值：`0x10` 的 bit4 为 1，`0x20` 的无符号原始值为 32。
哪个按键对应 bit4、32 对应多少物理量，都需要真实协议说明，本文不作车辆映射。

## 12. 抓不到、收不全、校验错时怎么排查

先固定：适用协议 / LDF 版本、主从角色、位速率、ID 与 PID 显示方式、
长度、校验模型、发布者、周期。然后沿“电源 → 线 → 收发器 → UART → 协议 → 业务”检查。

| 观察到的现象 | 优先检查 | 可以据此证明什么 |
| --- | --- | --- |
| LIN 长期为高，无任何帧头 | 主任务是否运行、调度是否启用、TXD 与收发器模式 | 仅凭静态高电平不能区分正常空闲、休眠、断线或主节点未发 |
| LIN 长期为低 | 短地、TXD 长低、收发器状态、相关节点供电 | 示波器低电平是电气现象，需继续定位拉低来源 |
| 有 Break，后续看不到 0x55 | 位速率 / 时钟、UART 格式、波形阈值与 Break 检测配置 | 不能仅凭一个低脉冲认定 Header 完整 |
| Header 正常，无 Response | 是否轮询正确帧、发布者是否上电就绪、PID / 配置是否一致 | 主节点发出了 Header，不等于指定从节点已正常工作 |
| 只有部分数据 | 预期长度、DMA / 缓存边界、驱动状态、响应时序、下一个 Break | DMA 完成数不一定等于协议帧长 |
| PID 保护错误 | 位速率、噪声、停止位、ID 与 PID 混用 | 单纯 `PID & 0x3F` 无法证明 PID 正确 |
| Checksum 错 | Classic / Enhanced、是否加入完整 PID、回卷进位、长度和字节对齐 | 不应第一反应就认为从节点发错 |
| 主节点自己发帧却又收到数据 | 本机 RXD 回读 / 驱动回显处理 | 本机回读不代表从节点返回了 ACK |
| 抓包正确，应用值不更新 | 信号 offset、取值检查、有效性、超时、快照读取与并发 | 总线正确和业务链正确是两个验证层次 |
| 休眠后无法恢复 | 唤醒脉冲、唤醒源、时钟 / UART 恢复、收发器模式、主节点恢复调度 | 看到唤醒边沿不等于通信已恢复 |

建议同时观察 MCU TX、MCU RX 与 LIN 线，分清故障在哪一侧。
量测 LIN 侧应使用满足电压范围和接地条件的仪器；普通低压逻辑分析仪不能
直接按 MCU 电平范围接到 VBAT 域。

### 12.1 调试记录至少写这些

| 记录项 | 示例 / 作用 |
| --- | --- |
| 时间戳 | 相邻有效帧间隔，判断真实周期和抖动 |
| 帧 ID 和 PID | 同时记录，避免工具显示口径混淆 |
| 数据长度、原始字节 | 按 LDF 解释前保留原始证据 |
| 校验模型与结果 | Classic / Enhanced，以及是否通过 |
| 发布者和方向 | 区分主节点 Header、主节点响应、从节点响应 |
| 错误状态 | PID、帧格式、无响应、不完整、校验错误分别统计 |
| 最近有效接收时间 | 判断业务新鲜度，区别于“最近收到任意字节” |
| 台架条件 | 供电、唤醒条件、连接节点、LDF 和固件版本 |

驱动初始化成功、UART 有中断、主任务有心跳，都不能替代总线波形、
有效帧抓包以及业务动作的证明。

## 13. 自查：是否真正理解了 LIN

| 问题 | 应能说出的结论 |
| --- | --- |
| 主节点发完 Header 就一定接收吗？ | 不一定；如果它是发布者，还要发 Response |
| 从节点之间能交换数据吗？ | 可以，但通信时机仍由主节点 Header 安排 |
| ID 0x01 在线上一定看到 01 吗？ | 不一定，完整 PID 是 0xC1 |
| Header 里能看到长度吗？ | LIN 2.x 没有长度字段，查 LDF / 帧配置 |
| 诊断 ID 0x3D 的 PID 是什么？ | 0x7D，仍使用 Classic 校验 |
| 调度时隙 10 ms，所有信号都是 10 ms 更新吗？ | 不是，要看每个帧在调度表中的出现频次 |
| 收到 UART 数据就能刷新有效时间戳吗？ | 不能，要通过帧校验和业务检查 |
| 从节点可发唤醒请求，是否可随时发普通数据？ | 不可以，普通数据仍需要主任务的帧头 |

## 14. 资料与核对范围

1. [LIN Specification Package Revision 2.2A](https://www.cs-group.de/wp-content/uploads/2016/11/LIN_Specification_Package_2.2A.pdf)
   —— LIN 联盟规范原文，由 C&S 托管。重点章节：§2.3 帧传输、§2.4 调度、
   §2.6 休眠唤醒、§2.8.3 校验示例、§6.5.5 节点负载、§9 LDF。
2. [TI SLLA383A：LIN Protocol and Physical Layer Requirements](https://www.ti.com/lit/an/slla383a/slla383a.pdf)
   —— 辅助理解收发器、逻辑侧与总线侧、负载和唤醒。
   对节点数量等表述，本文采用上方原始 LIN 2.2A 规范的口径。

本次核对了规范关键条款、PID / 校验和数值、时间计算、配图和文档链接。
本文属于协议学习资料，未对具体工程进行固件编译、烧录、台架抓包或实车验证。
