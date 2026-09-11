# XCP 整体模型

## Master、Slave 和 A2L

XCP 采用主从模型。Master 一般是 CANape、INCA 或自研标定工具；Slave 是运行在 ECU 中的协议栈。Master 不需要把每个变量名称硬编码到协议命令中，而是通过 A2L 获得访问信息。

```text
A2L
 ├── XCP 连接参数：CAN ID、长度、超时
 ├── 变量信息：地址、数据类型、长度
 ├── 换算信息：比例、偏移、单位
 └── DAQ 信息：事件、可采集对象
        │
        ▼
Master 生成 XCP 命令
        │
        ▼
Slave 按地址访问 ECU 内存
```

## 地址导向访问

XCP 的核心是地址导向访问。工具最终会把“读取 VehicleSpeed”转换为“从某个地址读取若干字节”。变量名、单位和物理含义由 A2L 维护。

例如，以下是教学假设：

```text
变量名：VehicleSpeed
地址：  0x20001000
类型：  uint16
原始值：1234
换算：  物理值 = 原始值 × 0.1
结果：  123.4 km/h
```

## ECU 中的模块边界

典型实现可以分成：

```text
CAN 驱动/Socket 接收
        ↓
XCP Transport Layer
        ↓
XCP Protocol Layer
        ├── CTO 命令处理
        ├── 会话和权限状态
        ├── 内存访问适配
        └── DAQ/ODT 管理
        ↓
应用变量和事件触发接口
```

工程分析时不要只找命令枚举，还要继续追踪：接收回调、任务调度、内存读写回调、DAQ 事件触发点和发送队列。

## cfg / ctx / data / ops 映射

| 分类 | XCP 中的典型内容 |
| --- | --- |
| `cfg` | CAN ID、最大 CTO/DTO 长度、地址粒度、DAQ 数量、超时 |
| `ctx` | 连接状态、保护解锁状态、MTA、DAQ 运行状态、ODT 配置 |
| `data` | 上传数据、DTO 快照、时间戳、ECU 状态、错误响应 |
| `ops` | Connect、Upload、Download、DAQ Start/Stop、内存访问回调 |

常见越界是把连接状态暴露给应用直接修改，或者让应用绕过 XCP 内存访问接口直接操作传输缓冲区。协议状态应由 XCP 模块维护，应用只提供变量和事件接口。

## 资源和安全

ECU 可以通过 CONNECT 响应声明 CAL/PAG、DAQ、STIM、PGM 等资源。资源可用不代表当前一定允许操作，还可能受会话状态、内存段属性和 Seed & Key 保护限制。

任何允许写 RAM 或 Flash 的实现，都应明确：地址范围、长度上限、可写段、对齐要求、校验方式、异常响应和掉电风险。
