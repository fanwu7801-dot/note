# XCP 报文与 CAN 传输

## CTO 和 DTO

XCP 包大致分为两类：

- **CTO（Command Transfer Object）**：命令、正响应、错误响应和事件。
- **DTO（Data Transfer Object）**：DAQ/STIM 的同步数据。

命令通常是 Master -> Slave，正响应通常是 Slave -> Master；DAQ DTO 则由 Slave 按事件主动发送。

## 请求、响应和事件的关系

一个普通命令通常有一个请求和一个响应：

```text
Master                         Slave
  │                              │
  │──── Command Transfer ───────>│
  │                              │ 检查状态、参数、权限
  │<─── Positive Response ───────│
```

如果命令不允许、参数非法或资源不足，Slave 返回错误响应。异步事件不一定对应一个正在等待的命令，例如 DAQ 启停状态变化、编程完成或 ECU 状态变化。

## XCP on CAN 的思路

CAN 只负责传输一帧数据，XCP 负责解释数据中的 PID 和 payload。CAN ID、最大数据长度和是否需要 CAN-FD，不由 XCP 基础命令本身决定，而由 XCP on CAN 配置和 A2L 描述。

## CAN 帧与 XCP 包的边界

```text
CAN ID + CAN 控制字段 + CAN Data[0..7]
                         └── XCP 包的承载区域
```

CAN ID 属于传输层配置；Data 区中的 PID 和参数属于 XCP。CAN 仲裁、位填充、ACK 和错误帧属于 CAN 协议，不能在 XCP 命令解析器中重复实现。

教学假设：

```text
Command Receive CAN ID：0x600
Response/DAQ CAN ID：  0x650
经典 CAN 数据长度：    8 字节
```

实际项目不能直接套用这些值。

## 常见 PID 类型

| PID 类型 | 含义 |
| --- | --- |
| CMD | 主站发出的命令码 |
| RES | 从站对命令的正响应 |
| ERR | 从站对命令的错误响应 |
| EV | 异步事件 |
| SERV | 服务类消息 |
| DAQ PID | 标识某个 DAQ ODT 的数据 |

不同版本和具体命令的字节布局要以 XCP 规范和 ECU 的实现为准。抓包时先确认 PID 类型，再解析后续字节。

## 经典 CAN 8 字节的布局意识

在经典 CAN 中，XCP 包最多占用 8 个数据字节。常见情况是：

```text
Byte 0：PID 或命令码
Byte 1...：长度、地址、计数器或数据
未使用字节：按实现填充
```

地址、长度和数据的具体字节位置随命令而变化。不能把 `Byte 1` 永远理解成长度，也不能把填充字节当成有效数据。

## CAN-FD 和大数据

CAN-FD 可以提供更长的单帧数据区，但是否启用、最大 CTO/DTO 长度、是否需要分段，仍由传输层实现和 A2L 配置决定。工具看到 CAN-FD 并不意味着所有 XCP 命令自动支持更大长度。

## 一个最小请求响应例子

下面只用于理解结构，数据并非通用标准报文：

```text
Master -> ECU：CONNECT 命令
CAN ID 0x600：FF 00 00 00 00 00 00 00

ECU -> Master：CONNECT 正响应
CAN ID 0x650：FF 08 00 00 00 00 00 00
```

不要仅凭一帧报文判断连接成功。应继续检查 Master 是否读取资源、CTO/DTO 长度、地址粒度和当前状态。

## CAN 抓包的四个检查点

1. **方向**：哪个 CAN ID 是命令接收，哪个是响应或 DAQ 发送。
2. **周期**：CTO 通常由请求触发；DAQ DTO 应与配置的事件周期相关。
3. **长度**：短帧、填充字节、CAN-FD 和多包传输不能混淆。
4. **顺序**：连接、权限、地址设置、读写和启动采集有先后关系。

## 错误响应的分析方法

看到错误响应时按以下顺序排查：

1. 命令是否在当前 CONNECT 状态允许执行？
2. 参数长度是否满足当前 CTO 长度？
3. MTA、地址扩展和地址粒度是否正确？
4. 资源是否已分配，DAQ/PGM 是否正在运行？
5. ECU 是否因安全保护、Flash 忙或队列满而拒绝？

错误码只说明协议层拒绝原因，还要结合 ECU 日志和内存访问回调确定根因。

## 与 ISO-TP 的区别

XCP on CAN 可以使用 CAN 传输层能力；某些实现还可能通过其他传输方式或多帧机制承载较大数据。不能把所有 XCP 报文都当成 UDS ISO-TP 报文解析。先确认 A2L 中的 XCP on CAN 配置和工具设置。

## 常见误区

- 把 `0x600/0x650` 当成所有 ECU 的固定 ID。
- 把 CTO 命令响应和 DAQ DTO 混为一类。
- 看到连续 CAN 帧就认为是 DAQ，没有核对 DAQ PID 和事件周期。
- 忽略端序、地址粒度和数据对齐。
