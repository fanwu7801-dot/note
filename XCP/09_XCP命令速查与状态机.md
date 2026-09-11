# XCP 命令速查与状态机

本文用于把前面章节串成一条可执行的协议流程。命令的具体 PID、字段位置和可选能力以 XCP 版本、传输层和 A2L 为准。

## 命令按功能分类

| 类别 | 常见命令或动作 | 目的 |
| --- | --- | --- |
| 连接 | CONNECT、DISCONNECT | 建立或结束会话 |
| 状态 | GET_STATUS、SYNCH | 查询状态或恢复同步 |
| 识别 | GET_ID | 获取 ECU 标识或描述信息 |
| 内存 | SET_MTA、UPLOAD、SHORT_UPLOAD | 读取内存 |
| 内存 | DOWNLOAD、SHORT_DOWNLOAD | 写入内存 |
| DAQ | 分配 List/ODT、写 Entry、START_STOP_DAQ_LIST | 配置和启停测量 |
| STIM | 配置同步数据方向和 List | 向 ECU 注入数据 |
| 页面 | GET_CAL_PAGE、SET_CAL_PAGE、COPY_CAL_PAGE | 管理标定页 |
| 编程 | PROGRAM、PROGRAM_VERIFY、BUILD_CHECKSUM | 开发阶段编程和校验 |
| 安全 | GET_SEED、UNLOCK | 解锁受保护资源 |

## 最小读变量流程

```text
1. CONNECT
2. 读取 CONNECT 响应中的能力和长度
3. 按需要完成 GET_STATUS / GET_ID
4. SET_MTA(address, extension)
5. UPLOAD(length)
6. 按 A2L 解释原始字节
```

如果第 5 步失败，优先回看地址、长度、地址扩展、权限和内存段；不要先修改换算系数。

## 最小写 RAM 流程

```text
1. CONNECT
2. 获取并完成必要的解锁
3. SET_MTA(address, extension)
4. DOWNLOAD(raw_value)
5. 读取回读并比较
6. 观察应用行为
```

回读一致只能证明访问链路和内存值一致，仍需检查算法是否在正确时间点读取该参数。

## DAQ 配置流程

```text
查询 DAQ 资源
  -> 分配 DAQ List
  -> 分配 ODT
  -> 为 ODT Entry 设置地址和长度
  -> 绑定 Event Channel
  -> 设置模式
  -> 启动 DAQ
  -> 接收 DTO
```

配置完成前，事件线程不应使用半成品配置。停止时要清理运行状态和待发送队列。

## 从站状态检查

每个命令至少检查：

```text
连接状态 -> 资源状态 -> 保护状态 -> 参数范围 -> 资源忙状态
```

状态检查失败时返回错误响应，并保持上下文不变，避免“命令失败但 MTA 或 DAQ 状态已经被部分修改”。

## 练习：从工具动作反推报文

当用户在工具中点击“显示变量”时，可能触发一次 UPLOAD；点击“开始记录”时，可能先配置 DAQ，再出现周期 DTO。练习抓包时不要只找一条“读变量”报文，要把动作和完整命令序列对应起来。
