# 38-以太网与WiFi移植

[总目录](总目录.md) · [上一篇：显示与触摸屏移植](37-显示与触摸屏移植.md) · [下一篇：摄像头移植与采集验证](39-摄像头移植与采集验证.md)

[TOC]

<a id="part-55"></a>

> 本次只扩充 38.2 的 RTL8723DU WiFi，使用迅为 RK3568 Android 11 原厂 SDK 实测记录。38.1 以太网和 38.3 通用 Linux 验证按你的要求保持原样；其中 Linux 6.1、构建脚本或网络管理命令属于原章节的环境，不自动作为 Android 11 的操作步骤。

## 38.1 以太网基础与移植

### 38.1.1 网络通信基础

#### 38.1.1.1 诞生与发展

早期计算机联网曾借助电话线路，让通信双方通过物理线缆连接。电话网络以建立通信连接为基础，计算机网络则逐渐发展出适合数字数据传输的分组交换机制。

**图 222.1　早期通信连接示意图**

![图 222.1 早期通信连接示意图](images/以太网移植/itop_fig222_01.png)

随着技术演进，计算机网络形成了以数据传输和信息交互为核心的通信系统。例如，两部手机之间的通信，需要网络把不同地点、不同设备的数据送到对方。网络的发展也不断提出新的要求：

- 提高通信的可靠性和稳定性。
- 让不同体系结构、不同操作系统的计算机互联。
- 让多个节点按照共同的规则访问网络。
- 通过冗余连接和路由提高网络的稳健性。

原书介绍的主要发展节点整理如下，其中跨大西洋连接和 TCP/IP 切换的年份已校正：

| 时间 | 事件 |
| --- | --- |
| 1969 年 | ARPANET 的首批四个节点建立连接，采用分组交换技术传输数据。 |
| 1972 年 | ARPANET 在国际计算机通信大会上进行公开演示，网络应用逐渐发展。 |
| 1973 年 | ARPANET 扩展到英国和挪威；Cerf、Kahn 等人开展后来形成 TCP/IP 的互联网络协议设计。 |
| 1983 年 1 月 1 日 | ARPANET 从 NCP 切换到 TCP/IP，是互联网发展中的重要节点。 |
| 1986 年前后 | NSFNET 骨干网开始推动更广泛的科研、教育网络互联。 |
| 1994 年 4 月 20 日 | NCFC 项目相关的国际专线开通，中国实现与国际互联网的全功能连接。 |

这些时间点可对照 [Internet Society 的互联网简史](https://www.internetsociety.org/internet/history-internet/brief-history-internet/)、[UCL 对 1973 年跨国连接的记述](https://www.ucl.ac.uk/news/2025/jan/commentary-how-britain-got-its-first-internet-connection) 和 [中国科学院关于 NCFC 的记录](https://www.ecas.cas.cn/dtfb/ysdt/201802/t20180206_4934064.html)。

#### 38.1.1.2 网络协议

网络协议是设备之间进行通信时共同遵守的规则。它规定数据如何组织、如何寻址、何时发送，以及发生错误时如何处理。

**1. TCP/IP 协议族与 TCP**

TCP/IP 是互联网使用的一组协议，不能把整个协议族的特性都等同于 TCP。

- IP 负责主机之间的寻址和数据包转发。
- TCP 在 IP 之上提供面向连接、可靠、有序的字节流传输。

TCP 的主要特点如下：

- **面向连接**：通常先通过三次握手建立连接，再交换数据。
- **可靠、有序**：通过序号、确认、重传等机制处理丢失、重复和乱序；通过流量控制等机制协调发送与接收。遇到无法恢复的故障时，连接仍可能超时或报错。
- **基于字节流**：不保留应用程序每次发送的消息边界。例如，发送端两次 `send()` 的内容，接收端可能通过一次或多次 `recv()` 读出，应用协议需要自行规定消息长度或分隔方式。

TCP/IP 通过分层协作，为不同计算机和不同网络之间的数据交换提供基础。网页访问、文件传输、远程登录等应用都会使用这一协议体系。

**2. UDP 协议**

UDP（User Datagram Protocol，用户数据报协议）也属于 TCP/IP 协议族。它提供数据报传输服务：

- **无连接**：发送数据前不需要像 TCP 那样建立连接。
- **不提供可靠交付保证**：UDP 本身不负责确认重传，也不保证到达顺序。需要这些能力时，由应用层协议实现。
- **保留数据报边界**：应用数据以一个个数据报发送。UDP 首部包含源端口、目的端口、长度和校验和；源、目的 IP 地址属于外层 IP 首部。

UDP 常用于实时音视频、在线游戏等场景，因为应用可以自行决定是否等待或重传过期数据。它通常具有较小的协议开销，但不能简单理解成任何条件下都比 TCP 快。

**3. DNS 协议**

DNS（Domain Name System，域名系统）提供分布式的名称解析服务。例如，把 `www.example.com` 解析成对应的 IP 地址，使用户可以通过容易记忆的名称访问服务。DNS 解析成功与否，属于网络上层功能，不能直接用来判断 PHY 是否正常。

**4. DHCP 协议**

DHCP（Dynamic Host Configuration Protocol，动态主机配置协议）用于自动给客户端分配网络配置，常见内容包括 IP 地址、子网掩码、默认网关和 DNS 服务器地址。

开发板网口已经建立物理连接，却没有获得 IP 地址时，需要检查 DHCP 客户端、服务器和配置流程。

**5. FTP 协议**

FTP（File Transfer Protocol，文件传输协议）用于计算机之间的文件传输和共享。它属于应用层协议，依赖下层已经建立的网络连接。

**6. HTTP 与 HTTPS 协议**

HTTP（HyperText Transfer Protocol，超文本传输协议）是访问网页、图片、视频和网络接口等资源的应用层协议。

HTTPS 在 HTTP 通信中加入 TLS 保护，用于加密传输、校验数据完整性及认证服务器身份。原书提到的 SSL 是历史名称，实际开发应使用现代 TLS 实现。网上银行、支付和电子商务等应用普遍使用 HTTPS。

#### 38.1.1.3 传输介质

传输介质是数据传输的物理载体。原书讨论有线介质中的网线、电缆和光纤；本小节不展开无线传输介质。

**1. 双绞线网线**

常见以太网网线包含 8 根铜导线，两两绞合成 4 对双绞线，外部有绝缘材料和护套。双绞结构有助于降低串扰和外部电磁干扰；是否具有屏蔽层则取决于线缆类型，不能把护套本身理解成防止信息泄露的措施。

原书介绍的线缆类别如下：

| 类别 | 特点与用途 |
| --- | --- |
| 1 类、2 类 | 早期电话或低速数据线路，不用于现代以太网布线。 |
| Cat 3（3 类） | 常见于早期 10BASE-T 网络，支持 10 Mb/s 级以太网应用，现代布线中很少采用。 |
| Cat 4（4 类） | 早期网络线缆，后来被更高类别的线缆取代。 |
| Cat 5（5 类） | 早期百兆布线很常见；满足相应指标的四对 Cat 5 线缆也可承载 1000BASE-T，不能简单把 Cat 5 的上限写成 100 Mb/s。 |
| Cat 5e（超 5 类） | 改进了相关传输指标，是千兆铜缆以太网的常见选择，并向下兼容百兆。 |
| Cat 6（6 类） | 对串扰等指标提出更高要求，可用于千兆；是否支持更高速度还要结合距离和布线条件。 |
| Cat 6A（超 6 类） | 常用于 10GBASE-T 万兆布线。 |
| Cat 7（7 类） | 具有屏蔽结构和更高的传输指标，可用于相应的高速布线系统；连接器和整条链路也要匹配。 |

实际链路速率由 MAC、PHY、对端设备、线缆质量和连接情况共同决定，不能只根据线缆上的类别标识推断最终速率。

**2. T568A 与 T568B 线序**

制作网线时，常见端接方式为 T568A 和 T568B。按插头规定的引脚编号观察，线序如下：

| 引脚 | T568A | T568B |
| --- | --- | --- |
| 1 | 白绿 | 白橙 |
| 2 | 绿 | 橙 |
| 3 | 白橙 | 白绿 |
| 4 | 蓝 | 蓝 |
| 5 | 白蓝 | 白蓝 |
| 6 | 橙 | 绿 |
| 7 | 白棕 | 白棕 |
| 8 | 棕 | 棕 |

**图 222.2　T568A 与 T568B 网线线序**

![图 222.2 T568A 与 T568B 网线线序](images/以太网移植/itop_fig222_02.png)

- 两端使用同一种线序，为直通线。传统应用中常用于计算机与交换机等不同类型设备的连接。
- 一端使用 T568A、另一端使用 T568B，是传统百兆交叉线的常见做法，曾用于同类设备直连。
- 现代设备常支持 Auto-MDI/MDI-X，可自动适配收发线对；实际是否需要交叉线，应看设备能力，不能照搬传统规则到所有设备。

**3. 电缆**

电缆是传输电能或信号的线缆总称，通常由导体、绝缘层、护套等组成。双绞线网线本身也属于电缆，二者不是互斥的类别。选择电缆时要关注对应接口标准、阻抗、长度和抗干扰要求。

**4. 光纤**

光纤以光信号传输信息，利用玻璃或塑料纤维的导光特性传输数据，主要分为单模光纤和多模光纤。使用光纤时，需要匹配的光收发器、波长、纤芯类型和接口。

#### 38.1.1.4 网络模型

网络模型把复杂的通信过程划分成多个层次，每一层完成一组相对独立的工作。原书介绍 OSI 七层模型和 TCP/IP 四层模型。

**1. OSI 七层模型**

OSI（Open Systems Interconnection）模型由 ISO 提出，用于描述不同系统互联时的分层职责。

**图 222.3　OSI 七层网络模型**

![图 222.3 OSI 七层网络模型](images/以太网移植/itop_fig222_03.png)

| 层次（从底向上） | 主要职责 |
| --- | --- |
| 物理层 | 规定电气、光学等物理特性，把比特流转换成介质上的信号，并在接收端恢复比特。它不解释应用数据的含义。 |
| 数据链路层 | 把比特组织成帧，处理同一链路上的通信、帧边界、链路寻址及差错检测等；具体协议提供的控制能力有所不同。 |
| 网络层 | 处理跨网络的寻址与路由，把数据包从源主机送往目标主机。 |
| 传输层 | 提供端到端、进程之间的数据传输。是否提供可靠交付，要看 TCP、UDP 等具体协议。 |
| 会话层 | 管理应用之间的会话及对话过程，包括建立、维持和结束。 |
| 表示层 | 处理数据表示和格式转换等功能，可理解为不同数据表示之间的转换层。 |
| 应用层 | 为网络应用提供协议服务，通过应用之间的交互完成具体任务。 |

**2. TCP/IP 四层模型**

TCP/IP 模型把网络通信分成网络接口层、网际层、传输层和应用层。

**图 222.4　TCP/IP 四层网络模型**

![图 222.4 TCP/IP 四层网络模型](images/以太网移植/itop_fig222_04.png)

| 层次 | 主要职责及协议 |
| --- | --- |
| 应用层 | 与具体网络应用有关，常见协议有 HTTP、FTP、SMTP、DNS 等。例如，邮件应用使用 SMTP 发送邮件。 |
| 传输层 | 通过端口区分应用。TCP 提供可靠、有序的字节流，UDP 提供不保证可靠交付的数据报服务。 |
| 网际层 | 通过 IP 地址寻址，负责 IP 数据包的传输和路由。 |
| 网络接口层 | 对应具体链路和物理介质，包含以太网帧收发及底层信号传输等工作。 |

**3. 两种模型的区别与联系**

OSI 常用于分析和教学，TCP/IP 与互联网中的协议实现联系更紧密。可以把 OSI 的应用层、表示层、会话层，对应到 TCP/IP 的应用层；把 OSI 的数据链路层和物理层，对应到 TCP/IP 的网络接口层。

这种对应有助于理解职责，不能把两种模型的历史和实现关系简单理解成“先有 OSI，再把它删减成 TCP/IP”，也不能用层数多少判断传输效率。

**图 222.5　OSI 与 TCP/IP 模型的对应关系**

![图 222.5 OSI 与 TCP/IP 模型的对应关系](images/以太网移植/itop_fig222_05.png)

### 38.1.2 硬件连接

#### 38.1.2.1 RJ45 接口

以太网中常说的 RJ45 网口，通常指使用 8P8C 模块化插头、插座的接口。插头和插座通过网线连接，外形上的“8 个触点”不等于一定支持某个速率。

**图 223.1　RJ45 插头**

![图 223.1 RJ45 插头](images/以太网移植/itop_fig223_01.png)

插头通常有塑料外壳和 8 个金属触点。插入插座后，插头触点与插座中的弹性接触片接触，形成电气连接。

**图 223.2　RJ45 插座**

![图 223.2 RJ45 插座](images/以太网移植/itop_fig223_02.png)

插座一般安装在计算机网卡、交换机、路由器、开发板或墙壁面板上。iTOP-RK3568 开发板的网口如下，原书这套硬件支持千兆以太网。

**图 223.3　iTOP-RK3568 开发板网口**

![图 223.3 iTOP-RK3568 开发板网口](images/以太网移植/itop_fig223_03.png)

作为对照，iTOP-4412 开发板的原书示例网口最高支持百兆。

**图 223.4　iTOP-4412 开发板网口**

![图 223.4 iTOP-4412 开发板网口](images/以太网移植/itop_fig223_04.png)

百兆和千兆网口都可能使用同样外形的接口，内部收发电路及线对的使用方式却不同。

**表 223.1　10BASE-T / 100BASE-TX 常见 MDI 端口的引脚用途**

| 引脚编号 | 信号名称 | 功能说明 |
| --- | --- | --- |
| 1 | TX+ | 发送差分信号正端 |
| 2 | TX− | 发送差分信号负端 |
| 3 | RX+ | 接收差分信号正端 |
| 4 | 未用于本例数据传输 | 不参与上述两种模式的数据收发 |
| 5 | 未用于本例数据传输 | 不参与上述两种模式的数据收发 |
| 6 | RX− | 接收差分信号负端 |
| 7 | 未用于本例数据传输 | 不参与上述两种模式的数据收发 |
| 8 | 未用于本例数据传输 | 不参与上述两种模式的数据收发 |

MDI-X 或自动线对交换会影响收发对应关系；“未用于数据传输”也不代表在 PoE 等所有场景下都悬空。

**表 223.2　1000BASE-T 的四对线用途**

| 引脚编号 | 线对 | 功能说明 |
| --- | --- | --- |
| 1 | A+ | A 对差分信号正端，双向传输 |
| 2 | A− | A 对差分信号负端，双向传输 |
| 3 | B+ | B 对差分信号正端，双向传输 |
| 4 | C+ | C 对差分信号正端，双向传输 |
| 5 | C− | C 对差分信号负端，双向传输 |
| 6 | B− | B 对差分信号负端，双向传输 |
| 7 | D+ | D 对差分信号正端，双向传输 |
| 8 | D− | D 对差分信号负端，双向传输 |

1000BASE-T 同时使用四对线进行双向传输。原表把部分线对标成单独的 TX、RX，容易让人误以为千兆也固定由两对线分别负责单向发送和接收，这里统一按四对双向信号整理。

#### 38.1.2.2 处理器、MAC、PHY 与网络变压器

在嵌入式以太网硬件中，需要先分清下面几个部分。

**1. MAC 控制器**

MAC（Media Access Control，媒体访问控制）控制器负责以太网帧的收发和相关控制，与 PHY 通过数字接口交换数据，并通过 DMA、总线等机制与系统内存和 CPU 协作。RK3568 集成了两个以太网 MAC 控制器。

**2. PHY 芯片**

PHY（Physical Layer，物理层收发器）处理物理链路：把 MAC 侧的数据转换成适合介质传输的信号，并把接收到的介质信号恢复成数字数据。PHY 还参与链路检测、速率和双工模式的协商等工作。

常见芯片包括 Realtek RTL8211 系列、YT8531C 等，原书给出的外观示例如下。

**图 223.5　以太网 PHY 芯片示例**

![图 223.5 以太网 PHY 芯片示例](images/以太网移植/itop_fig223_05.png)

**3. 网络变压器**

在常见铜缆以太网设计中，PHY 的线缆侧与网口之间有网络变压器，用于信号耦合、电气隔离和匹配等。它可以是独立器件，也可以集成在带磁性器件的 RJ45 插座内。

原书 iTOP-RK3568 使用 HR911130A 这类内置网络变压器的插座，因此不能只根据板上是否看到独立变压器，判断电路有没有隔离器件。

**图 223.6　独立网络变压器示例**

![图 223.6 独立网络变压器示例](images/以太网移植/itop_fig223_06.png)

按 CPU、MAC、PHY 的集成情况，原书介绍了三种连接方式。

**方式一：CPU 内部集成 MAC 和 PHY**

外围器件可以减少，但接口能力和 PHY 规格受 SoC 集成方案限制，选型的灵活性相对较小。成本高低要结合具体芯片和外围电路判断。

**方式二：CPU 内部集成 MAC，PHY 使用独立芯片**

这类方式可以根据介质、速率、封装和工业温度等要求选择 PHY，是嵌入式系统中常见的方案。

**图 223.7　SoC 内置 MAC、外接 PHY 的连接框图**

![图 223.7 SoC 内置 MAC、外接 PHY 的连接框图](images/以太网移植/itop_fig223_07.png)

iTOP-RK3568 采用这一方式：RK3568 内部的 MAC，连接板上的 RTL8211 PHY，再经过磁性器件和网口连接网线。

**图 223.8　iTOP-RK3568 的 MAC、PHY 与网口**

![图 223.8 iTOP-RK3568 的 MAC、PHY 与网口](images/以太网移植/itop_fig223_08.png)

如果插座内没有集成网络变压器，就需要在电路中使用独立的磁性器件，不能省略相应功能。

**方式三：CPU 不集成可用的 MAC、PHY，通过其他总线扩展**

可以使用 USB、SPI、并行总线等连接外部网卡控制器，由外部器件提供 MAC、PHY 或它们的组合。原书以 USB 转以太网的结构为例。这会增加外部器件和一层总线适配，实际成本和性能取决于方案。

**图 223.9　通过外部接口扩展以太网的连接框图**

![图 223.9 通过外部接口扩展以太网的连接框图](images/以太网移植/itop_fig223_09.png)

iTOP-4412 的示例连接如下，板上使用独立的网络控制器，RJ45 插座内部包含网络变压器。

**图 223.10　iTOP-4412 的网络连接方案**

![图 223.10 iTOP-4412 的网络连接方案](images/以太网移植/itop_fig223_10.png)

#### 38.1.2.3 PHY 接口与原理图分析

在外接 PHY 的方案中，需要区分三类连接：

- **MAC ↔ PHY 的数据接口**：如 MII、RMII、GMII、RGMII。
- **MAC/MDIO 控制器 ↔ PHY 的管理接口**：MDIO、MDC，用于寄存器访问。
- **PHY ↔ 网络变压器、网线的介质接口**：MDI 差分线对。

MDIO 用于管理 PHY，不代替 RGMII 等数据接口；MDI 和 MDIO 也不是同一个接口。

**1. MII 接口**

MII（Media Independent Interface，介质独立接口）用于 MAC 和 PHY 之间的数据传输。数据总线宽度为 4 位：100 Mb/s 时使用 25 MHz 时钟，10 Mb/s 时使用 2.5 MHz 时钟。

**图 223.11　MII 接口连接**

![图 223.11 MII 接口连接](images/以太网移植/itop_fig223_11.png)

**表 223.3　MII 的 16 根数据接口信号线**

| 信号线 | 数量 | 方向 | 描述 |
| --- | --- | --- | --- |
| TX_ER | 1 | MAC → PHY | 发送错误指示 |
| TXD[3:0] | 4 | MAC → PHY | 发送数据 |
| TX_EN | 1 | MAC → PHY | 发送使能 |
| TX_CLK | 1 | PHY → MAC | PHY 提供的发送时钟 |
| COL | 1 | PHY → MAC | 冲突检测 |
| RXD[3:0] | 4 | PHY → MAC | 接收数据 |
| RX_ER | 1 | PHY → MAC | 接收错误指示 |
| RX_CLK | 1 | PHY → MAC | 接收时钟 |
| CRS | 1 | PHY → MAC | 载波侦听 |
| RX_DV | 1 | PHY → MAC | 接收数据有效 |

这里的 16 根不包含另外的 MDC、MDIO 管理信号。

**2. RMII 接口**

RMII（Reduced Media Independent Interface，简化介质独立接口）减少了数据位宽和控制信号，使用 2 位发送数据和 2 位接收数据，共用 50 MHz 参考时钟。

**图 223.12　RMII 接口连接**

![图 223.12 RMII 接口连接](images/以太网移植/itop_fig223_12.png)

**表 223.4　RMII 信号**

| 信号线 | 数量 | 描述 |
| --- | --- | --- |
| TXD[1:0] | 2 | MAC → PHY，发送数据 |
| TX_EN | 1 | MAC → PHY，发送使能 |
| CRS_DV | 1 | PHY → MAC，载波侦听与接收数据有效复用信号 |
| RXD[1:0] | 2 | PHY → MAC，接收数据 |
| REF_CLK | 1 | 50 MHz 参考时钟；由外部时钟或支持相应功能的器件提供，按具体时钟拓扑连接 |
| RX_ER | 可选 1 | PHY → MAC，接收错误指示 |

不计可选的 RX_ER 时为 7 根，计入 RX_ER 时为 8 根，另外还有管理接口。原表把 RX_ER 描述成“发送错误”，这里已改为接收错误。

**3. GMII 接口**

GMII（Gigabit Media Independent Interface，千兆介质独立接口）把千兆模式下的数据总线扩展到 8 位。1000 Mb/s 时的数据时钟为 125 MHz；10/100 Mb/s 的兼容模式使用对应的 MII 时序。

**图 223.13　GMII 接口连接**

![图 223.13 GMII 接口连接](images/以太网移植/itop_fig223_13.png)

**表 223.5　GMII 信号及方向**

| 信号线 | 数量 | 方向 | 描述 |
| --- | --- | --- | --- |
| GTX_CLK | 1 | MAC → PHY | 千兆发送时钟，125 MHz |
| TX_CLK | 1 | PHY → MAC | 10/100 Mb/s 兼容模式下由 PHY 提供的发送时钟；千兆发送使用 GTX_CLK |
| TXD[7:0] | 8 | MAC → PHY | 千兆发送数据 |
| TX_EN | 1 | MAC → PHY | 发送使能 |
| TX_ER | 1 | MAC → PHY | 发送错误 |
| RX_CLK | 1 | PHY → MAC | 接收时钟 |
| RXD[7:0] | 8 | PHY → MAC | 千兆接收数据 |
| RX_DV | 1 | PHY → MAC | 接收数据有效 |
| RX_ER | 1 | PHY → MAC | 接收错误 |
| CRS | 1 | PHY → MAC | 载波侦听，与半双工模式相关 |
| COL | 1 | PHY → MAC | 冲突检测，与半双工模式相关 |

按表中所有信号计算为 25 根，不包含管理接口。原表中 TX_CLK 的方向有误，已修正。

**4. RGMII 接口**

RGMII（Reduced Gigabit Media Independent Interface）通过 4 位数据线、双沿传输及控制信号复用，减少 GMII 的信号数量。它支持 10/100/1000 Mb/s，对应时钟为 2.5/25/125 MHz；千兆模式利用时钟上升沿和下降沿传输数据。

**图 223.14　RGMII 接口连接**

![图 223.14 RGMII 接口连接](images/以太网移植/itop_fig223_14.png)

**表 223.6　RGMII 数据接口信号**

| 信号线 | 数量 | 方向 | 描述 |
| --- | --- | --- | --- |
| TXC | 1 | MAC → PHY | 发送时钟；千兆时为 125 MHz |
| TX_CTL | 1 | MAC → PHY | 复用编码发送使能、发送错误等控制信息 |
| TXD[3:0] | 4 | MAC → PHY | 发送数据；千兆时双沿传输 |
| RXC | 1 | PHY → MAC | 接收时钟；千兆时为 125 MHz |
| RX_CTL | 1 | PHY → MAC | 复用编码接收有效、接收错误等控制信息 |
| RXD[3:0] | 4 | PHY → MAC | 接收数据；千兆时双沿传输 |

RGMII 数据接口为 **12 根信号线**；加上 MDC、MDIO 两根管理线，才是 14 根。原书把两种计数口径混用，这里已分开。Linux 6.1 的 [PHY 文档](https://www.kernel.org/doc/html/v6.1/networking/phy.html#rg-mii-electrical-interface-considerations) 也说明了 12 线接口和时钟、数据之间的延时要求。

RGMII 的时序与移植直接相关。MAC、PHY 或 PCB 走线需要共同满足采样要求，后面设备树中的 `phy-mode`、`tx_delay` 和 `rx_delay` 就与此有关。

**5. MDIO 管理接口**

MDIO（Management Data Input/Output）用于读写 PHY 的管理寄存器。通过它可以配置允许的速率和自动协商功能，读取链路状态等。

**表 223.7　MDIO 管理接口**

| 信号线 | 方向 | 描述 |
| --- | --- | --- |
| MDIO | 双向 | 管理数据线，读写 PHY 寄存器 |
| MDC | 管理控制器 → PHY | 管理时钟线，由管理控制器提供 |

传统 Clause 22 访问中，一次操作需要同时指定“访问哪颗 PHY”和“访问这颗 PHY 的哪个寄存器”。两个地址的区别在下一小节展开。

**6. iTOP-RK3568 硬件实践**

选择 MAC 与 PHY 的接口时，要同时检查 SoC 和 PHY 的能力，以及原理图的实际连线。原书 iTOP-RK3568 使用 RTL8211 系列 PHY，支持 10/100/1000 Mb/s 和自动协商。

数据手册中的连接关系如下：MAC 侧通过 RGMII 传输帧数据，通过 MDIO 管理 PHY；PHY 的 MDI 侧连接磁性器件和网口。

**图 223.15　RTL8211 的系统连接示意**

![图 223.15 RTL8211 的系统连接示意](images/以太网移植/itop_fig223_15.png)

把这套连接简化后，可以得到下面的框图。

**图 223.16　MAC、PHY、MDI 与网口的关系**

![图 223.16 MAC、PHY、MDI 与网口的关系](images/以太网移植/itop_fig223_16.png)

RK3568 核心板引出了 RGMII 相关引脚，原理图中的接口如下。

**图 223.17　RK3568 核心板的 RGMII 引脚**

![图 223.17 RK3568 核心板的 RGMII 引脚](images/以太网移植/itop_fig223_17.png)

底板将这些引脚连接到 RTL8211F，PHY 原理图如下。

**图 223.18　RTL8211F 原理图及 MAC 侧引脚**

![图 223.18 RTL8211F 原理图及 MAC 侧引脚](images/以太网移植/itop_fig223_18.png)

按图 223.18 中 RTL8211F-CG 的封装标注，相关引脚应整理为：

| 引脚编号 | 信号 | 方向或作用 |
| --- | --- | --- |
| 15、16、17、18 | TXD3、TXD2、TXD1、TXD0 | MAC → PHY 的发送数据 |
| 19 | TXCTL | MAC → PHY 的发送控制 |
| 20 | TXC | MAC → PHY 的发送时钟 |
| 22、23、24、25 | RXD3、RXD2、RXD1、RXD0 | PHY → MAC 的接收数据 |
| 26 | RXCTL / PHYAD2 | 接收控制，同时具有硬件配置复用功能 |
| 27 | RXC / PHYAD1 | 接收时钟，同时具有硬件配置复用功能 |
| 13 | MDC | 管理时钟 |
| 14 | MDIO | 双向管理数据 |
| 31 | INTB / PMEB | 中断或电源管理事件输出，按芯片配置选择 |

原文把“22、23、24、25、26”五个引脚对应到四根 RXD 线，还把 MDC、MDIO 都称为 MDIO 引脚，这里依据原理图修正。引脚号只适用于图中芯片和封装，换型号后要重新核对。

原书还介绍了 INTB/PMEB 的复用：通过芯片 Page `0xd40`、REG 22 的 bit5 选择功能，设置为 1 对应 PMEB，设置为 0 对应中断功能。是否连接到 SoC、是否需要上拉，以及未使用时如何处理，要按对应芯片数据手册和电路设计确定。

线缆侧的连接如下。

**图 223.19　RTL8211F 的 MDI、磁性器件和 RJ45 连接**

![图 223.19 RTL8211F 的 MDI、磁性器件和 RJ45 连接](images/以太网移植/itop_fig223_19.png)

PHY 的 MDI 差分线对是：

- 引脚 1、2：MDI[0]+、MDI[0]−。
- 引脚 4、5：MDI[1]+、MDI[1]−。
- 引脚 6、7：MDI[2]+、MDI[2]−。
- 引脚 9、10：MDI[3]+、MDI[3]−。

这些信号连接网络变压器和 RJ45 的四对线。原文说“第 1 到 10 脚对应 MDI”，需要扣除其中的电源等非 MDI 引脚，不能把 1–10 全部按信号脚连接。

### 38.1.3 PHY 寄存器

#### 38.1.3.1 PHY 寄存器与地址

原书通过 IEEE 802.3 的传统 Clause 22 寄存器空间介绍 PHY。这个空间通常使用 5 位寄存器编号，可以访问 0–31 号寄存器，标准定义的管理功能与厂商扩展功能共同组成芯片的管理接口。

**图 224.1　PHY 标准管理寄存器示意**

![图 224.1 PHY 标准管理寄存器示意](images/以太网移植/itop_fig224_01.png)

**1. 常用的控制寄存器与状态寄存器**

开发中经常接触 0 号和 1 号寄存器。

| 寄存器编号 | 名称 | 主要作用 |
| --- | --- | --- |
| 0 | BMCR，基本模式控制寄存器 | 配置复位、环回、自动协商、掉电、速率选择、双工模式等。 |
| 1 | BMSR，基本模式状态寄存器 | 报告链路状态、自动协商能力和完成状态，以及部分支持能力等。 |
| 2、3 | PHY ID 寄存器 | 用于识别 PHY，Linux PHY 驱动匹配时会使用。 |
| 4、5 | 本端通告、链路伙伴能力 | 与自动协商有关。 |
| 9、10 | 1000BASE-T 控制、状态 | 与千兆铜缆以太网协商和状态有关。 |
| 15 | 扩展状态 | 报告相应扩展能力。 |

不能仅凭 BMSR 中“支持某速率”的能力位，就认为当前链路运行在该速率。实际协商结果还要结合相应寄存器、PHY 驱动及 `ethtool` 输出判断。

原书用“0–15 号寄存器是标准部分，16–31 号是扩展部分”帮助入门。实际含义应理解为：标准规定了相关寄存器的用途和位语义，但不代表所有厂家的每一位、默认值和支持能力都完全一致；保留位和可选功能也不能随意读写。厂商还可能通过分页、间接访问或 MMD 等方式扩展寄存器空间。

Linux 的通用 PHY 支持可以处理标准功能，但具体芯片如果有复位、延时、时钟或勘误等特殊要求，仍需要对应厂商驱动。不是所有 PHY 都只靠通用驱动就能完整工作。

**2. 分清 MAC 地址、IP 地址、PHY 地址与寄存器编号**

原书特别区分了前三种地址，这里同时把容易混淆的寄存器编号列出来。

| 名称 | 所在位置与用途 | 示例 |
| --- | --- | --- |
| MAC 地址 | 数据链路层地址。以太网通常使用 48 位地址，用于帧的链路寻址；地址也可以由系统配置，需要避免同一网络中重复。 | `00:11:22:33:44:55` |
| IP 地址 | 网络层的逻辑地址，用于主机寻址和跨网络路由。IPv4 为 32 位，IPv6 为 128 位。 | `192.168.1.10`、IPv6 地址 |
| PHY 地址 | 标识同一条 MDIO 总线上的某颗 PHY。传统 Clause 22 地址为 5 位，范围 0–31；不同 MDIO 总线可以使用相同地址。 | 某条总线上的 PHY 地址 `1` |
| PHY 寄存器编号 | 指定所选 PHY 内部要访问的寄存器。它与 PHY 地址是两个不同字段。 | PHY 地址 `1` 的寄存器 `0` |

PHY 地址既不是网卡的 MAC 地址，也不是 IP 地址。对管理接口来说，通常先选中某条 MDIO 总线，再用 PHY 地址找到芯片，最后用寄存器编号找到芯片内部的寄存器。

**3. 根据原理图确定 PHY 地址**

RTL8211F 可以在复位释放时采样复用引脚的电平，确定 PHY 地址等硬件配置。原书给出的地址相关信号如下。

**图 224.2　PHY 地址配置引脚及外围电路**

![图 224.2 PHY 地址配置引脚及外围电路](images/以太网移植/itop_fig224_02.png)

芯片手册中，相关复用关系为：

| 引脚 | 配置功能 |
| --- | --- |
| 22，RXD3 / PHYAD0 | PHY 地址 bit0 |
| 27，RXC / PHYAD1 | PHY 地址 bit1 |
| 26，RXCTL / PHYAD2 | PHY 地址 bit2 |

**图 224.3　RTL8211F 硬件模式配置说明**

![图 224.3 RTL8211F 硬件模式配置说明](images/以太网移植/itop_fig224_03.png)

再对照底板上的上拉、下拉电阻，原书这张原理图给出的地址为 `PHYAD[2:0] = 001b`，即地址 1。

**图 224.4　底板 PHY 地址的上拉、下拉配置**

![图 224.4 底板 PHY 地址的上拉、下拉配置](images/以太网移植/itop_fig224_04.png)

硬件绑带、设备树 PHY 子节点的 `reg` 值，以及系统实际发现的 PHY 地址需要对应。后面实验截图出现的 `stmmac-0:00`，地址部分是十六进制 `00`，与这里图示的地址 `1` 不同；调试时应核对实际网口和板卡版本，不能把两处示例直接当成同一地址。

#### 38.1.3.2 PHY 寄存器操作实验

本实验保留原书通过 `phy_registers` 属性访问 PHY 的方法。这个属性属于原书所用 BSP 提供的调试入口，不能假定每个 Linux 6.1 SDK 都有同样的文件和写入格式。

**1. 找到实际 PHY 设备**

打开开发板调试串口，给开发板上电并进入终端，列出 MDIO 设备：

```bash
ls /sys/bus/mdio_bus/devices
```

原书使用的设备目录是 `stmmac-0:00`。下列变量要按实际输出修改，目录名中的空格不能照原文排版错误写入命令。

```bash
MDIO_DEV=stmmac-0:00
cd "/sys/bus/mdio_bus/devices/$MDIO_DEV"
ls
```

**图 224.5　进入原书示例的 PHY 设备目录**

![图 224.5 进入原书示例的 PHY 设备目录](images/以太网移植/itop_fig224_05.png)

如果没有 `phy_registers`，应先在当前 SDK 源码中查找相应实现，确认是否提供该入口；不要把文件不存在判断成 PHY 一定没有被识别。

```bash
# 在内核源码目录中查找原书使用的调试属性
rg -n 'phy_registers' drivers/net
```

**2. 读取寄存器**

在确实存在该属性的原书 BSP 中，执行：

```bash
cat phy_registers
```

**图 224.6　通过 phy_registers 查看 PHY 寄存器**

![图 224.6 通过 phy_registers 查看 PHY 寄存器](images/以太网移植/itop_fig224_06.png)

原书读出的 0 号寄存器为 `0x1040`，对应 BMCR。数据手册中的位定义如下。

**图 224.7　PHY 控制寄存器 BMCR 的位定义**

![图 224.7 PHY 控制寄存器 BMCR 的位定义](images/以太网移植/itop_fig224_07.png)

其数值分解为：

```text
0x1040 = 0x1000 | 0x0040
       = (1 << 12) | (1 << 6)
```

所以置位的是 **bit12 和 bit6**，不是原书文字所写的 bit13 和 bit6。相关含义为：

| 位 | 掩码 | 含义 |
| --- | --- | --- |
| bit12 | `0x1000` | 自动协商使能 |
| bit13 | `0x2000` | 速率选择位之一，在 `0x1040` 中未置位 |
| bit6 | `0x0040` | 速率选择位之一 |

当自动协商开启时，不能只看 BMCR 的速率选择位，就断言当前链路一定是千兆。原书图中的相关字段如下，位号解释以上面的数值分解为准。位定义也可对照 Linux 的 [MII 寄存器定义](https://github.com/torvalds/linux/blob/master/include/uapi/linux/mii.h)，实际开发时查看本机 Linux 6.1 源码中的同名文件。

**图 224.8　原书对控制寄存器数值的说明**

![图 224.8 原书对控制寄存器数值的说明](images/以太网移植/itop_fig224_08.png)

**3. 写入寄存器**

原书使用下面的命令向 0 号寄存器写入 `0x0040`。只有当前 BSP 的属性解析方式确实为“寄存器编号、寄存器值”时，这条命令才适用。

```bash
echo 0x00 0x40 > phy_registers
cat phy_registers
```

**图 224.9　原书写入 PHY 寄存器的实验**

![图 224.9 原书写入 PHY 寄存器的实验](images/以太网移植/itop_fig224_09.png)

从 `0x1040` 改为 `0x0040` 会清除自动协商使能位，因此这不是一条可以通用于所有板卡的“开启千兆”命令。复现实验时要记录原值、芯片型号、当前工作状态以及写入后的变化；日常配置速率和自动协商，应优先使用 PHY 驱动及 `ethtool` 提供的接口，避免直接写控制寄存器与驱动维护的状态不一致。

```bash
# 用实际网口名替换 eth0，查看驱动报告的链路状态
ethtool eth0
```

### 38.1.4 网络数据的封装和解封装

#### 38.1.4.1 基本概念

网络数据通常不会以应用程序中的原始形式直接出现在网线上，而是经过逐层封装后发送，再在接收端逐层解封装。

- **封装**：下层把上层数据作为自己的负载，按协议加入首部，必要时加入尾部，形成新的协议数据单元。
- **解封装**：接收端识别并处理本层协议字段，再把其中的上层数据交给对应的上层协议。

并不是每层都会同时添加“头和尾”，具体结构由对应协议决定。

#### 38.1.4.2 发送端的封装过程

**图 225.1　网络数据逐层封装**

![图 225.1 网络数据逐层封装](images/以太网移植/itop_fig225_01.png)

**1. 应用层**

应用程序生成具体业务数据，例如 HTTP 网页数据、SMTP 邮件数据。应用层协议按自身规则组织内容，例如 HTTP 请求头或响应头中包含请求方法、URL、响应状态码等信息。

**2. 传输层**

应用数据交给 TCP 或 UDP。

- TCP 添加首部，其中包括源端口、目的端口、序列号、确认号、控制位等，形成 TCP 段（Segment）。端口号用于区分通信的应用程序。
- UDP 添加较简单的首部，包括源端口、目的端口、长度和校验和，形成 UDP 数据报（Datagram）。

原书统一将两者称为“段”，这里区分 TCP 段和 UDP 数据报。

**3. 网际层**

IPv4 或 IPv6 在传输层数据外添加 IP 首部，其中包括源 IP、目的 IP 等信息，形成 IP 数据包。路由设备根据相应网络层信息，把数据包送往目标网络。

例如，访问网站时，本机发送的 TCP 段会被封装在目的地址为服务器 IP 的数据包中。

**4. 数据链路层与物理层**

以太网在 IP 数据包外增加帧头和帧尾，组成以太网帧。帧头包含源 MAC、目的 MAC、类型等信息，帧尾的 FCS 使用 CRC 检测传输错误。

随后，MAC、PHY 和介质共同完成帧的发送，PHY 把数据转换为网线上的电信号，或由相应物理接口转换为其他介质上的信号。

```text
应用数据
  ↓ TCP/UDP 封装
TCP 段 / UDP 数据报
  ↓ IP 封装
IP 数据包
  ↓ 以太网封装
以太网帧
  ↓ 物理层传输
介质上的信号
```

#### 38.1.4.3 接收端的解封装过程

**图 225.2　网络数据逐层解封装**

![图 225.2 网络数据逐层解封装](images/以太网移植/itop_fig225_02.png)

**1. 数据链路层解封装**

物理层恢复接收到的数据，链路层处理帧的地址、类型和校验等信息。检测到损坏的帧通常会被丢弃；通过检查的帧，其负载按协议类型交给上层。这里以以太网承载 IP 为例，把 IP 数据包交给网际层。

**2. 网际层解封装**

IP 协议处理首部，判断数据包的目的地址以及是否应交给本机。对于交给本机的数据，再根据上层协议类型，把负载交给 TCP、UDP 等传输层协议。需要转发的数据包则进入路由转发流程。

**3. 传输层解封装与交付应用**

TCP 或 UDP 根据端口等信息找到对应的应用。TCP 还处理序号、确认、重组等工作，再向应用提供有序字节流；UDP 向应用交付相应数据报。应用层协议解析收到的内容，完成网页访问、邮件收发等业务。

### 38.1.5 内核配置网卡

#### 38.1.5.1 使能 MAC 驱动和 PHY 支持

RK3568 的以太网 MAC 基于 Synopsys DesignWare IP。Linux 使用 stmmac 驱动框架，再由 Rockchip 平台适配代码处理时钟、复位和接口配置等。

PHY 的标准管理寄存器使 Linux 可以复用通用处理代码，但完成网口移植仍需要 MAC 驱动、平台适配、PHY 支持以及正确的板级配置共同配合。

在已经按板卡配置好的内核源码目录中，执行：

```bash
make ARCH=arm64 menuconfig
```

**图 227.1　进入内核 menuconfig**

![图 227.1 进入内核 menuconfig](images/以太网移植/itop_fig227_01.png)

原书使能 MAC 驱动的菜单路径如下：

```text
Device Drivers
  → Network device support
    → Ethernet driver support
      → STMicroelectronics devices
        → STMicroelectronics 10/100/1000/EQOS Ethernet driver
```

**图 227.2　stmmac 以太网驱动配置**

![图 227.2 stmmac 以太网驱动配置](images/以太网移植/itop_fig227_02.png)

接着检查 PHY 支持：

```text
Device Drivers
  → Network device support
    → PHY Device support and infrastructure
```

**图 227.3　PHY 驱动基础设施配置**

![图 227.3 PHY 驱动基础设施配置](images/以太网移植/itop_fig227_03.png)

原书截图来自其配套 SDK。对 Linux 6.1 SDK，还应核对下面这些相关配置项，不能只凭某一个菜单已经勾选，就认为整个网口驱动链已齐全。

| 配置项 | 作用 |
| --- | --- |
| `CONFIG_STMMAC_ETH` | Synopsys DesignWare / stmmac MAC 驱动框架 |
| `CONFIG_STMMAC_PLATFORM` | stmmac 平台设备支持 |
| `CONFIG_DWMAC_ROCKCHIP` | Rockchip SoC 的 GMAC 平台适配 |
| `CONFIG_PHYLIB` | PHY 管理和驱动基础设施 |
| `CONFIG_REALTEK_PHY` | 使用 RTL8211 等受支持的 Realtek PHY 时，检查对应 PHY 驱动 |

在内核源码目录中可以检查最终 `.config`，具体依赖由当前 SDK 的 Kconfig 决定：

```bash
rg -n 'CONFIG_(STMMAC_ETH|STMMAC_PLATFORM|DWMAC_ROCKCHIP|PHYLIB|REALTEK_PHY)' .config
```

配置为模块时，还要把对应当前内核版本的模块安装到根文件系统并正确加载。通用 PHY 驱动与专用 PHY 驱动的职责，可对照 [Linux 6.1 PHY 驱动说明](https://www.kernel.org/doc/html/v6.1/networking/phy.html#phy-device-drivers)。

#### 38.1.5.2 理解 SoC 层的 GMAC 节点

原书在下面的 SoC 设备树文件中查看 `gmac0`：

```text
kernel/arch/arm64/boot/dts/rockchip/rk3568.dtsi
```

这个路径从 SDK 顶层计算；如果已经位于内核源码目录，就从 `arch/arm64/boot/dts/rockchip/` 开始查找。不同 Linux 6.1 SDK 的内核目录名称、公共 `.dtsi` 拆分方式可能不同，应沿当前板卡 `.dts` 的包含关系定位。

```bash
# 在所用内核源码目录中定位节点及板级覆盖
rg -n 'gmac0:|ethernet@fe2a0000|&gmac0' arch/arm64/boot/dts/rockchip
```

**代码清单 227.1　原书 SoC 层的 gmac0 节点**

```dts
gmac0: ethernet@fe2a0000 {
    compatible = "rockchip,rk3568-gmac", "snps,dwmac-4.20a";
    reg = <0x0 0xfe2a0000 0x0 0x10000>;

    interrupts = <GIC_SPI 27 IRQ_TYPE_LEVEL_HIGH>,
                 <GIC_SPI 24 IRQ_TYPE_LEVEL_HIGH>;
    interrupt-names = "macirq", "eth_wake_irq";

    rockchip,grf = <&grf>;

    clocks = <&cru SCLK_GMAC0>,
             <&cru SCLK_GMAC0_RX_TX>,
             <&cru SCLK_GMAC0_RX_TX>,
             <&cru CLK_MAC0_REFOUT>,
             <&cru ACLK_GMAC0>,
             <&cru PCLK_GMAC0>,
             <&cru SCLK_GMAC0_RX_TX>,
             <&cru CLK_GMAC0_PTP_REF>,
             <&cru PCLK_XPCS>;
    clock-names = "stmmaceth", "mac_clk_rx", "mac_clk_tx",
                  "clk_mac_refout", "aclk_mac", "pclk_mac",
                  "clk_mac_speed", "ptp_ref", "pclk_xpcs";

    resets = <&cru SRST_A_GMAC0>;
    reset-names = "stmmaceth";

    snps,mixed-burst;
    snps,tso;
    snps,axi-config = <&gmac0_stmmac_axi_setup>;
    snps,mtl-rx-config = <&gmac0_mtl_rx_setup>;
    snps,mtl-tx-config = <&gmac0_mtl_tx_setup>;
    status = "disabled";

    mdio0: mdio {
        compatible = "snps,dwmac-mdio";
        #address-cells = <1>;
        #size-cells = <0>;
    };

    gmac0_stmmac_axi_setup: stmmac-axi-config {
        snps,wr_osr_lmt = <4>;
        snps,rd_osr_lmt = <8>;
        snps,blen = <0 0 0 0 16 8 4>;
    };

    gmac0_mtl_rx_setup: rx-queues-config {
        snps,rx-queues-to-use = <1>;

        queue0 {};
    };

    gmac0_mtl_tx_setup: tx-queues-config {
        snps,tx-queues-to-use = <1>;

        queue0 {};
    };
};
```

这个节点描述了控制器寄存器、中断、时钟、复位、MDIO 总线和收发队列等 SoC 资源。`status = "disabled"` 表示默认未启用，需要在使用该网口的板级设备树中完成配置并覆盖为 `"okay"`。

Linux 6.1 下保留所用 SDK 自带的 SoC 节点及资源定义，核对板级差异即可；不要用这份原书节选整体替换另一版本 SDK 的公共节点。

#### 38.1.5.3 配置板级设备树

原书使用的板级文件是：

```text
kernel/arch/arm64/boot/dts/rockchip/rk3568-evb1-ddr4-v10.dtsi
```

在相应板级节点中追加或修改 `&gmac0`，让软件配置符合实际 PHY 接口、时钟、GPIO、引脚组和布线。

**代码清单 227.2　原书板级 GMAC 配置**

```dts
&gmac0 {
    phy-mode = "rgmii";
    clock_in_out = "input";

    snps,reset-gpio = <&gpio3 RK_PB7 GPIO_ACTIVE_LOW>;
    snps,reset-active-low;
    /* Reset time is 20ms, 100ms for rtl8211f */
    snps,reset-delays-us = <0 20000 100000>;

    assigned-clocks = <&cru SCLK_GMAC0_RX_TX>,
                      <&cru SCLK_GMAC0>;
    assigned-clock-parents = <&cru SCLK_GMAC0_RGMII_SPEED>,
                            <&gmac0_clkin>;
    assigned-clock-rates = <0>, <125000000>;

    pinctrl-names = "default";
    pinctrl-0 = <&gmac0_miim
                 &gmac0_tx_bus2
                 &gmac0_rx_bus2
                 &gmac0_rgmii_clk
                 &gmac0_rgmii_bus
                 &gmac0_clkinout>;

    tx_delay = <0x3c>;
    rx_delay = <0x2f>;

    phy-handle = <&rgmii_phy0>;
    status = "okay";
};
```

该代码是原书硬件的配置示例，不是全部 Linux 6.1 板卡通用的参数。`cru`、`gpio3`、引脚组以及 `rgmii_phy0` 等标签，应由当前设备树包含的文件提供定义；对应的时钟编号和 GPIO 宏也要来自当前 SDK 的头文件。

尤其要注意：这里按 PDF 原文使用 `clock_in_out = "input"`，并选择 `gmac0_clkin`。如果另一块板采用由 MAC 输出参考时钟的方案，需要连同硬件时钟方向、时钟父节点及引脚配置一起调整。

#### 38.1.5.4 关键属性与 Linux 6.1 下的核对方法

**1. `phy-mode`：MAC 与 PHY 的接口和延时约定**

`phy-mode` 要与硬件连接一致，例如 RMII 或 RGMII。RGMII 的几种常见写法具有不同的 PHY 延时约定：

| 写法 | PHY 侧的延时约定 |
| --- | --- |
| `"rgmii"` | PHY 不负责插入内部 RGMII 延时，所需时序由 MAC 或 PCB 等其他位置满足。 |
| `"rgmii-id"` | PHY 负责接收和发送方向的内部延时。 |
| `"rgmii-rxid"` | PHY 负责接收方向的内部延时。 |
| `"rgmii-txid"` | PHY 负责发送方向的内部延时。 |

这些约定需与当前 MAC、PHY 驱动的实现以及实际电路一致，避免重复插入延时或缺少延时。定义可参照 [Linux 6.1 RGMII 延时说明](https://www.kernel.org/doc/html/v6.1/networking/phy.html#rg-mii-electrical-interface-considerations)。

**2. `pinctrl-0`：引脚复用**

RGMII 数据线、收发时钟、MDC、MDIO 以及本例的参考时钟引脚，要切换到相应的 GMAC 功能。引脚组还应与原理图实际采用的复用组匹配，例如代码中的 `tx_bus2`、`rx_bus2`。

**3. `snps,reset-gpio`：PHY 硬件复位**

原书用 `GPIO3_B7` 连接 PHY 复位脚，并使用低有效复位配置。移植时按实际连接修改 GPIO，核对电平和时序。Linux 6.1 SDK 如果采用 PHY 子节点上的 `reset-gpios` 等绑定写法，应遵循本 SDK 的绑定文档和驱动，避免同时配置互相冲突的复位描述。

**4. `snps,reset-delays-us`：复位各阶段的时间**

三个数值分别描述复位前、复位有效期间、复位释放后的延时，单位为微秒。本例为低有效：

```text
<0 20000 100000>
  │   │      └─ 复位释放后等待 100000 μs，即 100 ms
  │   └──────── 低电平有效复位持续 20000 μs，即 20 ms
  └──────────── 复位前等待 0 μs
```

低有效复位的电平过程为“高 → 低 → 高”，具体时长要满足所用 PHY 的数据手册要求。其他极性或其他绑定格式，以实际驱动的解析方式为准。

**5. `clock_in_out` 与 `assigned-clock-*`：时钟拓扑**

除了时钟频率，还必须确认时钟由谁产生、由谁接收。原书示例给出 `input`、`gmac0_clkin` 和 125 MHz 的配置组合，表示这套板级设计采用相应的外部参考时钟路径。不能只改 `input`/`output` 字符串，而忽略时钟父节点和引脚。

PHY 的晶振参考时钟、GMAC 的参考时钟，以及 RGMII 的 TXC/RXC 并不必然是同一个信号，应按原理图逐条核对。

**6. `tx_delay` 与 `rx_delay`：收发时序调整**

这两个属性用于 Rockchip MAC 侧的发送、接收延时配置。原书给出的 `0x3c`、`0x2f` 是示例值，不是纳秒数，也不是所有 PCB 都适用。

原书建议在相关硬件支持的范围内调整，本例常见扫描范围为 `0x00–0x7f`。若 SDK 提供 `dwmac-rk-tool` 一类工具，可按对应版本的方法扫描和测试，并结合长时间收发、错误计数、不同速率下的表现选择参数；具体范围和用法由当前驱动与 SoC 决定。

**7. `phy-handle` 与 PHY 地址**

`phy-handle` 指向实际使用的 PHY 子节点。本例引用 `rgmii_phy0`，需要在当前设备树中找到这个标签，检查其所在 MDIO 总线、`reg` 地址、复位和中断配置。它的 `reg` 要与实际硬件绑带或有效地址配置匹配。

```bash
# 在内核源码目录中核对 PHY 标签、节点和地址
rg -n 'rgmii_phy0|ethernet-phy@|&mdio0' arch/arm64/boot/dts/rockchip
```

**8. `status`：启用节点**

板级 `status = "okay"` 覆盖 SoC 层的 `"disabled"` 后，节点才具备被系统使用的条件；同时仍需满足驱动使能、资源和硬件配置等要求。

#### 38.1.5.5 编译、部署与验证

设备树和内核配置修改完成后，按当前 SDK 的板型选择和构建流程重新编译，并把实际启动所用的内核、DTB 或包含它们的启动镜像更新到板上。原书的 SDK 构建命令示例为：

```bash
# 在原书 SDK 顶层执行；其他 Linux 6.1 SDK 按其支持的构建流程操作
./build.sh kernel
```

板卡启动后，先检查驱动和物理链路：

```bash
dmesg | tail -n 100
ip -br link
ip -br addr

# 使用实际网口名；需要根文件系统中已经提供 ethtool
ethtool eth0
```

确认 MAC、MDIO、PHY 被识别，网线连接后链路能够建立，再检查 IP、路由和 DNS。原书用下面的命令测试外网连通性：

```bash
ping -c 4 www.baidu.com
```

域名 ping 同时依赖链路、地址、路由、DNS 和对端是否响应 ICMP，因此失败时需要按本讲义 38.3 节分层排查。完成同网段通信后，再检查跨网段和域名访问，最后用持续收发及错误统计确认稳定性。

<a id="part-57"></a>

## 38.2 Android 11 下移植 RTL8723DU WiFi

### 38.2.1 本节目标与实测基线

本节以你在迅为 RK3568 Android 11 原厂 SDK 中移植 RTL8723DU 的成功记录为主线。实测中的关键点是：引入驱动、接入 Kconfig/Makefile、调整驱动的 Android 配置，并在 Rockchip WiFi 适配层增加芯片识别与模块信息。

`wlan0` 只是常见接口名，不是所有板卡上都固定存在。WiFi 功能完成至少包含以下几层：

```text
USB 上发现 RTL8723DU
  → 内核驱动匹配、初始化、建立无线接口
  → 模块/固件安装到 Android 镜像需要的位置
  → Rockchip 适配层识别芯片并选择驱动
  → WiFi HAL、wificond、wpa_supplicant 与 Framework 协作
  → 扫描、认证、获取 IP、路由和 DNS 可用
```

原厂 Linux WiFi/BT 指南可用于理解总线、驱动、固件和排错，但其中 Buildroot 配置、`/usr/bin` 脚本和手动启动 supplicant 的方法不直接作为本 Android 11 产品的启动方案。

### 38.2.2 先分清 DU、DS、USB 和 SDIO

| 类型 | 典型连接与核对点 |
| --- | --- |
| 本次 RTL8723DU | USB 无线设备；原笔记识别表中的 VID:PID 为 `0bda:d723` |
| RTL8723DS | SDIO 无线设备；原表中的识别码为 `024c:d723` |
| 其他 SDIO 模块 | 需要相应 SDMMC/SDIO、供电、复位、host-wake 等配置 |
| PCIe 无线模块 | 需要对应 PCIe 控制器、复位/电源和 PCI 驱动匹配 |

DU 与 DS 名字很接近，但总线和驱动不能互换。同一后缀系列也可能存在硬件修订，实际以枚举 ID、模块规格和驱动支持为准。

本次是 USB WiFi，不应为了让它工作而随意打开某个 SDIO WiFi 节点。若板上有 USB 电源开关或 Hub，还要检查对应 USB Host、VBUS 及板级供电。组合模组中的蓝牙有自己的 HCI 传输和固件路径，WiFi 可用不代表蓝牙也已完成适配。

在 **主机终端**检查 Android 板：

```sh
adb shell ls /sys/bus/usb/devices
adb shell dmesg
```

如果系统没有 `lsusb`，可以在 **板端 shell**读取 USB 属性：

```sh
for dev in /sys/bus/usb/devices/*; do
    [ -f "$dev/idVendor" ] || continue
    echo "$dev"
    cat "$dev/idVendor" "$dev/idProduct"
done
```

能看到 USB ID 只证明总线枚举发生了；是否由正确驱动接管，继续看日志和接口。

### 38.2.3 把 Linux SDK 的驱动接入 Android 内核

原笔记中的“把 Linux SDK 驱动编译进 Android SDK”指的是移植**源码及其构建接入**，不是把 Linux SDK 中编好的 `.ko` 直接拷过去。

模块必须匹配 Android 产品实际使用的内核、配置、导出符号、架构与工具链。即使都是 RK3568，或者版本号看起来一致，也不能据此保证二进制模块兼容。

在 **Android SDK 顶层**查找已有路径和配置：

```bash
rg --files kernel/drivers/net/wireless | rg -i '8723du|Kconfig|Makefile'
rg -n '8723DU|8723du' kernel/drivers/net/wireless \
    kernel/arch/arm64/configs device/rockchip
```

接入过程分为四步：

1. 将驱动源码放进该 BSP 使用的无线驱动目录，保留来源和版本。
2. 在父目录 Kconfig 中接入子 Kconfig，在父 Makefile 中接入对应目录。
3. 在当前产品实际使用的 defconfig/配置片段中选择驱动，构建后核对最终 `.config`。
4. 使用第 36 篇的 Android 内核工具链构建，处理当前内核 API 差异，再按产品打包规则部署。

Kbuild 关系可以理解为下面的结构；其中配置符号和目录名必须使用真实驱动提供的名称：

```makefile
# 父目录 Kconfig 应 source 对应子目录的 Kconfig。
# 父 Makefile 示例：仅当该驱动确实定义 CONFIG_RTL8723DU 时使用。
obj-$(CONFIG_RTL8723DU) += rtl8723du/
```

`=y` 表示内建，`=m` 表示生成模块。后面的 HAL 模块加载表针对模块方案；如果实际选择内建，要检查该 BSP 的加载逻辑能否识别已经存在的接口，而不是再强行查找不存在的 `8723du.ko`。

### 38.2.4 原笔记中“Android 从 0 改为 11”的含义

你原来的实测步骤保留：驱动 Makefile 中有 Android 相关版本/平台开关，需要按该驱动版本调整为 Android 11。

不同 Realtek 驱动包的变量名和条件编译方式不同，不应把所有 Makefile 中的数字 `0` 都改成 `11`。先在实际驱动目录查找：

```bash
rg -n -i 'android|platform|cfg80211|cross_compile|ksrc|module_name' \
    kernel/drivers/net/wireless
```

看清变量在哪里参与条件判断、启用了哪些 Android 接口，以及它是否还影响编译路径或模块名称。这个修改本身不会替你完成 Kconfig、驱动 API 适配、HAL 识别、模块安装和固件部署。

如果编译报某个结构体成员或函数不存在，应对照 Android 内核中的真实头文件处理差异；先看第一个编译错误，不把后续连锁报错逐个当成独立问题。

### 38.2.5 Rockchip 识别表：把 USB ID 对应到 RTL8723DU

原笔记修改的位置是：

```text
frameworks/opt/net/wifi/libwifi_hal/rk_wifi_ctrl.cpp
```

保留你记录的识别内容，下面为节选后的完整数组形式；合并回 SDK 时保留原文件的其他条目，只添加缺少的 RTL8723DU 项：

```cpp
static wifi_device supported_wifi_devices[] = {
    {"RTL8188EU", "0bda:8179"},
    {"RTL8188EU", "0bda:0179"},
    {"RTL8723BU", "0bda:b720"},
    {"RTL8723BS", "024c:b723"},
    {"RTL8822BS", "024c:b822"},
    {"RTL8723CS", "024c:b703"},
    {"RTL8723DS", "024c:d723"},
    {"RTL8723DU", "0bda:d723"},
    /* 原 SDK 的其他条目继续保留。 */
};
```

该表帮助 Rockchip 用户态适配层选择芯片类型。它不会替代内核驱动里的 USB device ID 表：内核匹配和用户态识别是两件需要分别满足的事。

### 38.2.6 模块加载表：芯片名、模块名和路径要一致

原笔记的第二个修改位置是：

```text
frameworks/opt/net/wifi/libwifi_hal/wifi_hal_common.cpp
```

对应定义保留为：

```cpp
#define RTL8723DS_DRIVER_MODULE_PATH WIFI_MODULE_PATH "8723ds.ko"
#define RTL8723DU_DRIVER_MODULE_PATH WIFI_MODULE_PATH "8723du.ko"

#define RTL8723DS_DRIVER_MODULE_NAME "8723ds"
#define RTL8723DU_DRIVER_MODULE_NAME "8723du"
```

模块列表中的条目如下。这里只展示你原笔记涉及的部分，实际合并时保持原列表其余内容和顺序：

```cpp
wifi_ko_file_name module_list[] = {
    {"RTL8723BU", RTL8723BU_DRIVER_MODULE_NAME, RTL8723BU_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8188EU", RTL8188EU_DRIVER_MODULE_NAME, RTL8188EU_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8192DU", RTL8192DU_DRIVER_MODULE_NAME, RTL8192DU_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8822BU", RTL8822BU_DRIVER_MODULE_NAME, RTL8822BU_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8822BS", RTL8822BS_DRIVER_MODULE_NAME, RTL8822BS_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8188FU", RTL8188FU_DRIVER_MODULE_NAME, RTL8188FU_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8189ES", RTL8189ES_DRIVER_MODULE_NAME, RTL8189ES_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8723BS", RTL8723BS_DRIVER_MODULE_NAME, RTL8723BS_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8723CS", RTL8723CS_DRIVER_MODULE_NAME, RTL8723CS_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8723DS", RTL8723DS_DRIVER_MODULE_NAME, RTL8723DS_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    {"RTL8723DU", RTL8723DU_DRIVER_MODULE_NAME, RTL8723DU_DRIVER_MODULE_PATH, UNKKOWN_DRIVER_MODULE_ARG},
    /* 原 SDK 的其他条目继续保留。 */
};
```

这里故意保留本 BSP 原有宏的拼写 `UNKKOWN_DRIVER_MODULE_ARG`。它是代码符号，不能只因为英文看起来拼错，就单独改名导致编译失败。

在 **SDK 顶层**沿定义查找：

```bash
rg -n 'WIFI_MODULE_PATH|UNKKOWN_DRIVER_MODULE_ARG|module_list|RTL8723DU' \
    frameworks/opt/net/wifi/libwifi_hal
rg -n '8723du\.ko|BOARD_.*WIFI|WIFI_DRIVER|PRODUCT_COPY_FILES' \
    device/rockchip vendor/rockchip
```

检查 `WIFI_MODULE_PATH` 最终拼出的绝对路径、是否包含需要的 `/`、镜像中是否有该文件，以及模块内部名称是否与加载/卸载逻辑一致。只改宏而没有安装模块，开关 WiFi 时仍会失败。

这两个文件属于你这版 Rockchip Android 11 的扩展，不能推断新版本 AOSP 必然仍有相同文件。

### 38.2.7 模块、固件和 HAL 分别怎样进入镜像

| 修改对象 | 需要得到的结果 |
| --- | --- |
| 内核驱动源码/配置 | 更新内核，或生成与该内核配套的 `8723du.ko` |
| `.ko` 安装规则 | 模块被复制到 HAL 实际使用的目标路径 |
| 外部固件/配置文件 | 按驱动请求的名称、路径和格式安装 |
| `rk_wifi_ctrl.cpp` 等 C++ 文件 | 重新构建其所属用户态库并进入相应 Android 镜像 |
| 产品 Makefile / init / 权限策略 | 新配置进入最终产品，而不只存在于工作目录 |

固件是否单独请求、固件名称及位置由驱动决定。有的驱动将部分固件编进代码，不能因为指南列出某个 `/lib/firmware` 就机械创建同名目录；以 `request_firmware`、驱动配置及运行日志为证据。

`PRODUCT_COPY_FILES` 是一种复制文件进目标镜像的机制；`BOARD_VENDOR_KERNEL_MODULES` 等是否在当前 BSP 使用，要看产品构建规则。不要同时让多套规则安装不同版本的同名模块。

按原笔记，通过完整 Android 构建更新相关镜像最容易先形成可复现基线。之后再用 `m`、`mm` 或该 SDK 的模块目标缩短循环：先阅读相应 `Android.bp/Android.mk` 确认模块名，不能把 `libwifi_hal` 目录名直接当作所有版本都可用的构建目标。只更新 `boot.img` 不会更新 WiFi HAL 或 vendor 中的模块文件。

### 38.2.8 recovery.img 过大的实测处理及其边界

原笔记记录：当时构建提示 recovery.img 太大，修改：

```text
device/rockchip/rk356x/BoardConfig.mk
```

加入：

```makefile
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 125829120
```

`125829120` 字节等于 **120 MiB**。这里保留你的成功配置，但这个变量只是构建侧的镜像大小约束，**不会自动把设备上 recovery 分区扩成 120 MiB**。

再次使用这项修改前，核对最终生效的 BoardConfig、`parameter`/实际 GPT、烧录包中的分区布局，以及 recovery 镜像内容。构建放行而设备分区仍较小，并不构成一致的部署方案。

如果超限来自意外把大量无线驱动内建进内核，先确认产品是否确实需要这些驱动，以及 recovery 是否需要它们；不要只通过增加限制掩盖配置膨胀。该处是与你原实测记录相关的镜像一致性检查，分区工具原理见第 30 篇。

### 38.2.9 Android 11 的功能验证

以下在 **主机终端**执行；需要 root 的读取按第 36 篇进入 userdebug 调试环境：

```sh
adb shell uname -a
adb shell cat /proc/modules
adb shell ip link show
adb shell ip addr show
adb shell dmesg
adb shell cmd wifi help
adb shell dumpsys wifi
adb shell dumpsys connectivity
adb logcat -b all -d > android-wifi.log
```

Android 11 自带的 `ip` 可能不支持 Linux 发行版中的 `-br` 等选项，优先使用上面的基本形式。`cmd wifi` 的子命令以板端 help 为准，也可以通过系统设置操作 WiFi 开关、扫描和连接。

Framework 正在管理 WiFi 时，不再额外手工运行另一个 `wpa_supplicant` 或 DHCP 客户端。Android 的连接、地址和 DNS 管理由其网络服务协作完成；第 38.3 节保留的通用 Linux 环境示例中，`/etc/resolv.conf`、NetworkManager、systemd-networkd 等不是本 Android 11 SDK 的网络配置方法。

| 验证阶段 | 要取得的证据 |
| --- | --- |
| 总线 | 正确 USB VID/PID，设备未反复掉线 |
| 内核 | 正确驱动接管，模块加载成功，存在目标无线接口 |
| 用户态适配 | 识别为 RTL8723DU，实际模块路径和加载状态正确 |
| 扫描 | 系统设置中能看到附近 AP；仅看到 wlan0 还不够 |
| 认证/关联 | 能连接已知 AP，排除密码、加密方式及频段不匹配 |
| 获取地址 | 目标接口得到预期 IP；Android 网络服务未持续报 DHCP 失败 |
| 连通性 | 同网段访问、路由、域名解析和应用联网逐层验证 |
| 稳定性 | WiFi 开关、断线重连、重启、休眠恢复与持续传输 |

### 38.2.10 现象对应的排查位置

| 现象 | 优先检查 |
| --- | --- |
| 没有 USB 设备 | Host、Hub/VBUS、供电和硬件连接 |
| USB ID 正常但没有无线接口 | 内核 ID 表、Kconfig、模块装载、probe 和固件 |
| `invalid module format` / `Unknown symbol` | 内核与模块的构建配套、vermagic、导出符号及依赖 |
| 内核已有接口但 Android 开关失败 | 识别表、HAL、模块路径、服务和权限日志 |
| 能扫描但连接失败 | supplicant、加密认证、AP 配置和驱动能力 |
| 已关联但无 IP | Android DHCP/IpClient、AP 及网络服务日志 |
| 有 IP 但应用不联网 | 默认网络、策略路由、DNS、连通性检测和应用权限 |
| 负载后掉 USB / 固件重置 | 供电、USB 信号、驱动稳定性与日志时间线 |

`Permission denied` 还要分清普通文件权限与 SELinux 拒绝，查看实际进程和 `avc: denied`；不把全局关闭 SELinux 当作最终移植结果。


## 38.3 网络移植后的分层验证

驱动 probe 成功不代表网络已经可用。把问题分成驱动、物理链路、IP、路由、DNS 五层，每层都拿到证据后再往上查；以太网和 WiFi 的上层 IP 排查可以共用。

### 38.3.1 识别实际接口

```shell
ip -br link
ip -br addr
ip route
```

接口可能叫 eth0、end0、enp… 或 wlan0，不要把名称写死。下面 IFACE 要换成 `ip -br link` 查到的名字：

```shell
IFACE=eth0
ip -s link show dev "$IFACE"
cat "/sys/class/net/$IFACE/operstate"
cat "/sys/class/net/$IFACE/carrier"
```

operstate 与 carrier 用来辅助判断链路，计数器用来观察收发和错误；某些设备未启用时 carrier 读取会报错。以太网还要检查 PHY、MDIO、复位、时钟和 RGMII 延时；WiFi 则要看 SDIO/PCIe/USB 枚举、固件加载及 AP 关联。`ip` 的对象和子命令参见 [ip 手册](https://man7.org/linux/man-pages/man8/ip.8.html)。

### 38.3.2 区分地址、路由和 DNS 问题

| 检查 | 说明 |
| --- | --- |
| `ip addr` 没有预期 IP | 先查 DHCP 客户端或静态地址配置，不能直接归因于 PHY 驱动。 |
| 能访问同网段，跨网段失败 | 查默认网关和路由表。 |
| IP 地址能访问，域名失败 | 查 DNS 服务和解析器配置。 |
| 小流量正常、大流量异常 | 结合收发错误、丢包、MTU、供电、信号质量和持续负载观察。 |

```shell
# 将网关和目标地址替换为本网络实际值
ping -c 4 192.168.1.1
ip route get 192.168.1.100
cat /etc/resolv.conf
dmesg | tail -n 100
```

ping 不通也可能是对端禁用了 ICMP，需要结合实际应用连接判断。系统可能由 NetworkManager、systemd-networkd 或 BusyBox 脚本管理网络，应选当前正在使用的一套配置方式；不要让多个 DHCP 客户端同时管理同一接口。

### 38.3.3 交付一份可复现记录

记录板卡和内核版本、网口或无线模块型号、设备树修改、接口名、IP 获取方式、连接日志及收发统计。每次只修改一个影响因素，用同一网线/AP 和同一测试条件比较，便于区分软件配置与硬件链路问题。


## 38.4 WiFi 适配记录与参考资料

| 资料 | 用途 |
| --- | --- |
| 原始本篇 WiFi 笔记 | RTL8723DU 驱动引入、Android 开关、两处 HAL 修改和 recovery 大小记录 |
| [原厂 Linux WiFi/BT 指南 V6.0.2](../u盘资料/必须/15开发板原厂文档/docs/Linux/Wifibt/Rockchip_Developer_Guide_Linux_WIFI_BT_CN.pdf) | 总线/驱动/固件、功能验证和故障排查；该版以 Linux 4.4/4.19 为背景，Linux 启动脚本不直接套用到 Android |
| [AOSP WiFi 分层](https://source.android.com/docs/core/connect/wifi-overview) | Framework、HAL、wificond、supplicant 分工；Android 11 的实际接口以 BSP 为准 |
| [第 36 篇](36-Android系统构建与内核移植.md) | 构建、模块/用户态文件部署、日志和权限 |

本次未改动以太网章节及原通用 Linux 验证。WiFi 的实测 VID/PID、模块名、HAL 字段及 recovery 数值保留；新增步骤做了文档与语法检查，没有重新编译 SDK 或上板验证。

---

[总目录](总目录.md) · [上一篇：显示与触摸屏移植](37-显示与触摸屏移植.md) · [下一篇：摄像头移植与采集验证](39-摄像头移植与采集验证.md)
