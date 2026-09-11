# XCP 协议学习笔记

XCP（Universal Measurement and Calibration Protocol）是 ECU 与测量、标定工具之间的通用协议，主要用于读取 ECU 内部变量、修改标定参数、同步采集数据、外部激励和开发阶段编程。

## 推荐阅读顺序

1. [[00_XCP学习导航]]：先建立整体心智模型。
2. [[01_XCP整体模型]]：理解 XCP、A2L、ECU 内存和标定工具的关系。
3. [[02_XCP报文与CAN传输]]：看清 CTO、DTO 和 CAN 帧。
4. [[03_连接与内存访问]]：掌握最小可用的连接、读写流程。
5. [[04_DAQ同步采集]]：学习工程中最常用的周期测量。
6. [[05_STIM标定与页面管理]]：理解激励、参数页和 Flash 保存。
7. [[06_A2L文件阅读]]：能够从 A2L 找到地址、类型、换算和事件。
8. [[07_XCP抓包实战]]：把理论落到 CAN 抓包。
9. [[08_练习题与检查清单]]：用问题检查是否真正掌握。
10. [[09_XCP命令速查与状态机]]：把常用命令串成可执行流程。
11. [[10_XCP从站实现框架]]：从 ECU 软件角度理解如何落地。

## 学习目标

- 能解释 XCP Master、Slave、CTO、DTO、DAQ、ODT、ODT Entry 和 A2L。
- 能看懂一组 XCP on CAN 的连接、内存读取和 DAQ 报文。
- 能判断一个变量适合轮询读取还是 DAQ 采集。
- 能从 A2L 还原变量的地址、长度、数据类型和物理值换算。
- 能在 ECU 工程中定位 XCP 传输层、协议层、采样点和内存访问接口。
- 能从工具操作反推 XCP 从站的状态机、回调和资源边界。
- 能解释 DAQ 与 STIM 对任务实时性、缓存和总线带宽的影响。

## 重要边界

本文中的 CAN ID、内存地址和报文数据均为教学假设。实际项目必须以当前版本的 A2L、XCP 配置、通信矩阵和 ECU 源码为准。

## 参考资料

- [ASAM MCD-1 XCP 官方页面](https://www.asam.net/standards/detail/mcd-1-xcp/)
- [ASAM XCP Wiki](https://www.asam.net/standards/detail/mcd-1-xcp/wiki/)
- [ASAM MCD-2 MC（A2L/ASAP2）相关资料](https://www.asam.net/standards/detail/mcd-2-mc/)
