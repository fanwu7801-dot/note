"""生成深入机制补图；保留基础图，只写 extended 子目录。"""
from pathlib import Path
import importlib.util
import json
import sys
import xml.etree.ElementTree as ET
from PIL import Image

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('base', HERE/'redraw.py')
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
plt, np = b.plt, b.np
BLUE, GREEN, RED, ORANGE = b.BLUE, b.GREEN, b.RED, b.ORANGE
b.ASSETS = HERE.parent/'extended'
MANIFEST = []


def record(cid, section, slug, title, explanation):
    """记录图与小节的对应关系，供插图和验收使用。"""
    MANIFEST.append(dict(id=cid, section=section, slug=slug,
                         title=title, explanation=explanation))


def save(cid, section, slug, title, fig, explanation):
    """曲线图提供双格式与可复算的 Python 图源。"""
    b.save(cid, slug, fig, title, explanation)
    record(cid, section, slug, title, explanation)


def flow(cid, section, slug, title, nodes, explanation):
    """画有明确先后或传递关系的流程，超过三节点时折行。"""
    coords = [(0, 2), (4, 2), (8, 2), (8, -1), (4, -1), (0, -1)]
    boxes = [(x, y, 3, 1.3, text)
             for (x, y), text in zip(coords, nodes)]
    arrows = []
    for i in range(len(nodes)-1):
        x, y = coords[i]
        xx, yy = coords[i+1]
        if y == yy:
            arrows.append([[x+3 if xx > x else x, y+.65],
                           [xx if xx > x else xx+3, yy+.65]])
        else:
            arrows.append([[x+1.5, y], [xx+1.5, yy+1.3]])
    b.structured(cid, slug, title, boxes, arrows, [], explanation)
    record(cid, section, slug, title, explanation)


def lanes(cid, section, slug, title, rows, end, xlabel, explanation):
    """共享横轴的时间区间图，区间表示占用或状态的持续。"""
    fig, ax = plt.subplots(figsize=(12, max(4.4, len(rows)*.8+1.8)))
    for i, (label, intervals) in enumerate(rows):
        y = len(rows)-1-i
        for start, length, text, color in intervals:
            ax.broken_barh([(start, length)], (y-.3, .6),
                          facecolors=color, alpha=.83)
            ax.text(start+length/2, y, text, ha='center', va='center',
                    fontsize=10, color='white')
    ax.set(yticks=range(len(rows)),
           yticklabels=[r[0] for r in rows][::-1], xlim=(0, end),
           ylim=(-.7, len(rows)-.3), xlabel=xlabel)
    b.axis_clean(ax)
    save(cid, section, slug, title, fig, explanation)


def branch(cid, section, slug, title, nodes, explanation):
    """成功和失败分开连线，避免将互斥动作误画成连续动作。"""
    boxes = [(0, .5, 3, 1.3, nodes[0]), (4, .5, 3, 1.3, nodes[1]),
             (8, 2, 3.4, 1.3, nodes[2]),
             (8, -1, 3.4, 1.3, nodes[3])]
    arrows = [[[3, 1.15], [4, 1.15]],
              [[7, 1.15], [7.5, 1.15], [7.5, 2.65], [8, 2.65]],
              [[7.5, 1.15], [7.5, -.35], [8, -.35]]]
    b.structured(cid, slug, title, boxes, arrows, [], explanation)
    record(cid, section, slug, title, explanation)


def blocks(cid, section, slug, title, names, explanation):
    """画地址、字节或容量布局；区块宽度按给定权重。"""
    fig, ax = plt.subplots(figsize=(12, 4.3))
    total = sum(x[0] for x in names)
    cursor = 0
    small = []
    for i, (width, label) in enumerate(names):
        color = [BLUE, GREEN, ORANGE, RED][i % 4]
        ax.barh(0, width, left=cursor, height=.8, color=color, alpha=.8)
        if width/total < .06:
            small.append((cursor+width/2, label))
        else:
            ax.text(cursor+width/2, 0, label, color='white', ha='center',
                    va='center', fontsize=11)
        cursor += width
    for i, (center, label) in enumerate(small):
        xtext = total*(.2 + .6*i/max(1, len(small)-1))
        ax.annotate(label, xy=(center, .4), xytext=(xtext, 1.8),
                    ha='center', va='center', fontsize=11,
                    arrowprops=dict(arrowstyle='->', color=BLUE))
    ax.set(xlim=(0, total), ylim=(-1, 2.8 if small else 1), yticks=[])
    unit = {
        'ram-budget': '容量 / KiB；合计20 KiB',
        'pa5-bits': '布局从bit31向bit0；横轴表示已展示的位数',
        'w1c': '从左往右为操作先后，每格表示一步',
        'idle-boundary': 'DMA交付块的组成示意，宽度不代表传输时间',
        'value-block': '字节偏移；每个区间左闭右开',
        's50-space': '容量 / B；合计1024 B',
        'fragment-200': '业务载荷累计字节数 / B',
        'burst-budget': '累计SCL周期数 / clk',
        'page-split': '本次写入数据的累计字节数 / B',
        'link-reserve': '距Flash基址的偏移 / KiB',
        'nvic-encoding': '从bit7向bit0；横轴表示已展示的位数',
    }[slug]
    ax.set_xlabel(unit)
    b.axis_clean(ax)
    save(cid, section, slug, title, fig, explanation)


def mcu_and_tools():
    """建立地址、启动、链接、调试之间的具体联系。"""
    flow('01', 2, 'address-decode', '一次写 GPIOA_ODR 的地址怎样形成',
         ['GPIOA 基地址\n0x40010800', 'ODR 偏移\n+0x0C',
          '有效地址\n0x4001080C', '总线地址译码\n选 GPIOA 的 ODR',
          '写入锁存值\n再受引脚模式约束'],
         '沿箭头把基地址与偏移相加。地址选中的是寄存器，写 ODR '
         '改变输出锁存值；引脚电压还受模式、外部负载等条件约束。')
    flow('01', 3, 'c-startup', '进入 main 之前，初值和零值从哪里来',
         ['Flash\n.data 的初值映像', '启动代码复制\nFlash → SRAM',
          'SRAM\n.data 取得初值', '启动代码\n将 .bss 清零',
          'C 运行环境就绪\n进入 main'],
         '带非零初值的普通全局变量既占 Flash 初值空间，又占 SRAM '
         '运行空间；.bss 通常只在镜像中记录范围，启动时在 RAM 清零。'
         '实际初始化可能由编译器运行库完成。')
    blocks('01', 6, 'ram-budget', '20 KiB SRAM 预算：先扣固定成本，再留余量',
           [(4, '.data/.bss\n4 KiB'), (2, 'DMA\n2 KiB'),
            (6, '任务栈\n6 KiB'), (4, '堆\n4 KiB'),
            (4, '余量\n4 KiB')],
           '示例总计20 KiB。这里“堆”不再包含已单列的任务栈；若 '
           'FreeRTOS 动态创建任务，栈可能来自内核堆，不能重复相加。'
           '真实占用需结合 map、分配方式和运行峰值。')
    flow('01', 4, 'reset-vector', '复位入口读取的是两个表项，不是两条普通指令',
         ['启动映射地址 +0\n读取初始 MSP', '启动映射地址 +4\n读取复位向量',
          '复位入口地址\nbit0 标识 Thumb', '执行启动代码\n初始化运行环境',
          '进入 main\n后续异常按向量表分派'],
         '复位先建立栈，再从复位向量进入程序。图省略芯片启动映射细节。'
         '以后改 VTOR 只是改变异常向量表位置，不会自动重新装载 MSP。')

    flow('02', 1, 'translation-units', '头文件被展开，目标文件才交给链接器',
         ['main.c + 头文件\n预处理展开', '独立编译/汇编\nmain.o',
          '链接器收集\nmain.o / driver.o / 库', '符号解析与布局\n按链接脚本放置',
          'AXF/ELF + map\n代码、地址与调试信息'],
         '这是 main.c 的一条分支；driver.c 等各自编译成目标文件，'
         '再汇入链接器。头文件中的函数声明不会自动生成对应实现。')
    flow('02', 2, 'lma-vma', '同一份 .data 同时有装载地址与运行地址',
         ['链接布局\n规定 LMA 与 VMA', 'Flash：LMA\n保存 .data 初值',
          '启动时复制\n按链接符号确定范围', 'SRAM：VMA\n程序在此访问变量'],
         'LMA 是镜像存放初值的位置，VMA 是程序访问变量的地址。'
         '链接器与启动代码必须对这段复制范围保持一致。')
    lanes('02', 5, 'debug-halt', '断点停住 CPU 后，外设是否继续必须单独确认',
          [('CPU', [(0, 2, '运行', BLUE), (2, 6, '断点暂停', RED),
                    (8, 2, '恢复', BLUE)]),
           ('外部 UART 输入', [(1, 2, '帧1', GREEN), (4, 2, '帧2', GREEN),
                              (7, 2, '帧3', GREEN)]),
           ('接收处理', [(1, 1, '读DR', BLUE),
                        (2, 6, '暂停期间可能发生 ORE', ORANGE)])],
          10, '时间（示意）；是否冻结取决于外设和调试配置',
          '沿同一横坐标看：CPU 没执行接收代码时，外部发送器仍可能发帧。'
          'DMA、定时器和看门狗的冻结行为需分别核对，断点现场可能改变故障。')
    flow('02', 6, 'fault-pc', '从 HardFault 现场定位到出错访存',
         ['保存现场\nEXC_RETURN / MSP / PSP', '判断异常前所用栈\n定位硬件异常帧',
          '读取 stacked PC\n同时保存故障状态', '同一构建的反汇编\n定位指令与寄存器',
          '核对访问地址\n边界/权限/生命周期'],
         '先保存现场，再解析。若故障发生在异常入栈阶段，栈帧可能不完整；'
         '某些不精确总线错误的 stacked PC 也未必指向肇事指令。'
         '不能只看到 HardFault_Handler 就断言栈溢出。')


def gpio_irq_adc():
    """用位布局、模拟曲线和时间线解释外设与并发。"""
    blocks('03', 1, 'pa5-bits', 'GPIOA_CRL：PA5 独占 bits23:20 的四位',
           [(4, 'PA7\n31:28'), (4, 'PA6\n27:24'),
            (4, 'PA5\n23:20\n0010'), (4, 'PA4\n19:16'),
            (16, 'PA3…PA0\nbits15:0')],
           '按图从高位往低位看。PA5 的 0010 拆成 CNF=00、MODE=10，'
           '对应 F1 通用推挽输出、最大输出速度2 MHz；这不是 PWM 频率。'
           '只更改 PA5 时应掩码保护其余引脚。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.axhspan(0, .3, color=GREEN, alpha=.2)
    ax.axhspan(.3, .7, color=ORANGE, alpha=.2)
    ax.axhspan(.7, 1, color=BLUE, alpha=.2)
    for yy, label in [(.15, '保证识别为低'), (.5, '逻辑结果不保证'),
                      (.85, '保证识别为高')]:
        ax.text(.5, yy, label, ha='center', va='center', fontsize=16)
    ax.set(ylim=(0, 1), xlim=(0, 1), xticks=[],
           yticks=[0, .3, .7, 1],
           yticklabels=['0', 'VIL(max)', 'VIH(min)', 'VDD'])
    b.axis_clean(ax)
    save('03', 3, 'threshold-regions', '输入阈值存在不保证区，不能把中点当阈值',
         fig, '纵轴仅作阈值区域示意，0.3/0.7 的图上位置不是器件规格值。'
         '实际 VIL、VIH、耐压和注入电流限制应分别查对应引脚与供电条件。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    t = np.linspace(0, 5, 400)
    for r, color in [(1, BLUE), (4.7, GREEN), (10, ORANGE)]:
        ax.plot(t, 3.3*(1-np.exp(-t/(r*.1))), lw=2, color=color,
                label=f'{r:g} kΩ，C=100 pF')
    ax.set(xlabel='释放后的时间 / μs', ylabel='节点电压 / V', ylim=(0, 3.5))
    ax.legend(); b.axis_clean(ax)
    save('03', 5, 'pullup-rise', '开漏释放后，上升速度取决于 R×C', fig,
         '按 V=3.3×(1−exp(−t/RC)) 画理想集中电容模型。'
         '电阻减小会加快上升，但拉低时的电流约为3.3/R，'
         '仍要满足设备灌电流和低电平电压约束。')
    lanes('03', 7, 'startup-glitch', '先设输出锁存值，再切输出模式可避免部分启动毛刺',
          [('不利顺序', [(0, 2, '输入', BLUE), (2, 2, '输出默认低', RED),
                        (4, 4, '写期望高', GREEN)]),
           ('较稳顺序', [(0, 2, '输入', BLUE), (2, 2, '先写高锁存', ORANGE),
                        (4, 4, '切输出：高', GREEN)])],
          8, '初始化动作的先后（示意），假设负载期望高电平',
          '红段说明切到输出后、软件尚未写期望值的间隙。预写 ODR/BSRR '
          '只能控制软件接管后的过程；复位期间的安全电平仍依赖上拉、下拉'
          '及外部驱动使能设计。')

    blocks('04', 2, 'w1c', 'PR 读改写会把读到的其他 1 一起写回清除',
           [(1, '初始\nPR1:0\n11'), (1, '读 PR\n得到\n11'),
            (1, 'OR bit0\n仍为\n11'), (1, '写回\n清 bit1,0\n00')],
           '这里两位同时挂起。PR |= (1<<0) 会写回11，两个事件都被清掉。'
           '只清 bit0 应直接写01，硬件执行 W1C 后保留 bit1，结果为10。'
           '这是寄存器语义，不能套用普通 RAM 的读改写直觉。')
    lanes('04', 3, 'preemption', '抢占优先级决定能否打断，子优先级用于待处理仲裁',
          [('低优先级 ISR', [(0, 3, '执行', BLUE), (5, 3, '继续执行', BLUE)]),
           ('更高抢占级 ISR', [(3, 2, '打断并执行', RED)]),
           ('同抢占级 ISR', [(4, 1, '到达', ORANGE),
                            (8, 2, '等待后执行', GREEN)])],
          10, '时间（示意），中断未被屏蔽',
          '第三行在 t=4 到达，但即便子优先级更高，也不能打断同抢占级'
          '的在执行异常。只有出现多个可服务的待处理中断时，才体现同级仲裁。')
    lanes('04', 5, 'irq-latency', '响应延迟、ISR 耗时与业务完成时间是三段',
          [('外部边沿', [(0, 1, '发生', RED)]),
           ('等待阶段', [(0, 3, '屏蔽/更高优先级/入栈', ORANGE)]),
           ('ISR', [(3, 2, '入口→出口', BLUE)]),
           ('任务处理', [(6, 3, '业务计算', GREEN)])],
          10, '时间（示意）；ISR入口=3，退出=5，业务完成=9',
          '边沿到 ISR 入口为3单位，ISR服务为2单位，端到端业务延迟为9单位。'
          '只在 ISR 入口和出口翻转 GPIO，测得的脉宽不能代表完整响应延迟。')
    lanes('04', 7, 'snapshot-tear', 'volatile 无法保证两个字段来自同一轮更新',
          [('生产者', [(1, 2, '写 value=新', BLUE),
                      (6, 2, '写 timestamp=新', BLUE)]),
           ('消费者', [(3, 2, '读 value=新', RED),
                      (5, 1, '读 time=旧', ORANGE)])],
          9, '一次交错执行（示意）',
          '消费者取得“新数值+旧时间”。volatile 约束编译访问，'
          '不提供多字段快照。应按并发关系选择短临界区、双缓冲'
          '或带内存顺序保证的版本化快照。')

    fig, ax = plt.subplots(figsize=(11, 4.8))
    n = np.arange(32)
    ax.plot(n, 1.65+.004*np.sin(n*2.3), 'o-', label='较准但有噪声')
    ax.plot(n, 1.72+.001*np.sin(n*2.3), 'o-', label='较稳定但有偏差')
    ax.axhline(1.65, color=GREEN, ls='--', label='参考真实值1.65 V')
    ax.set(xlabel='采样编号', ylabel='转换后电压 / V')
    ax.legend(); b.axis_clean(ax)
    save('05', 2, 'accuracy-noise', '读数稳定与接近真实值，是两个不同维度', fig,
         '两组数据是人为构造的对照。多次平均可减小部分随机噪声，'
         '不会自动消除参考电压误差、增益误差或直流偏差。')
    lanes('05', 3, 'scan-timing', '三通道扫描的同一轮数据，也不是同一瞬间采样',
          [('通道1', [(0, 4.625, '采样', BLUE),
                     (4.625, 1.042, '转换', ORANGE)]),
           ('通道2', [(5.667, 4.625, '采样', BLUE),
                     (10.292, 1.042, '转换', ORANGE)]),
           ('通道3', [(11.334, 4.625, '采样', BLUE),
                     (15.959, 1.041, '转换', ORANGE)])],
          18, '时间 / μs；fADC=12 MHz，采样55.5周期，转换12.5周期',
          '一通道约5.667 μs，三通道约17 μs。扫描是依次进行；'
          '三相电流等强同步需求还要评估通道间的采样偏移。')
    lanes('05', 7, 'dma-ownership', '半缓冲交接给 CPU 的，是一个有限时间的读取窗口',
          [('DMA 前半区', [(0, 4, '填写A', BLUE), (8, 4, '重写A', RED)]),
           ('DMA 后半区', [(4, 4, '填写B', GREEN), (12, 4, '重写B', GREEN)]),
           ('CPU 读A', [(4, 4, '安全窗口：须读完', ORANGE)]),
           ('CPU 读B', [(8, 4, '安全窗口：须读完', ORANGE)])],
          16, '时间（示意）；4与12为半传输，8与16为全传输',
          't=4 时前半区完成，但 t=8 起又被 DMA 使用。若 CPU 读A延续到'
          't=8 之后，就可能混入下一轮。标志位不会自动锁住内存。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    count = np.array([1, 4, 8, 16, 32, 64])
    ax.plot(count, count, 'o-', color=BLUE)
    ax.set(xlabel='每半区容纳的扫描轮数 N',
           ylabel='半区交付间隔 / ms', xticks=count)
    b.axis_clean(ax)
    save('05', 9, 'batch-latency', '缓冲区越大，回调越少，但批量交付等待越长', fig,
         '假设每1 ms完成一轮三通道扫描。每半区N轮，则每N ms交付一次。'
         'N=32 时半区96个半字、整缓冲384 B；首轮等到第32轮才交付，'
         '约额外等待31 ms，还需计入转换和调度时间。')


def timers():
    """输出与捕获分别画图，保留各自时钟、事件和数据语义。"""
    b.structured('06', 'clock-branches', 'PSC 与 CKD 位于不同的时序分支',
                 [(0, .5, 3, 1.3, '定时器内部时钟\nfCK_INT'),
                  (4, 2, 3, 1.3, 'PSC+1 分频\n生成计数节拍'),
                  (8, 2, 3, 1.3, 'CNT\n计数/比较/周期'),
                  (4, -1, 3, 1.3, 'CR1.CKD\n决定 tDTS'),
                  (8, -1, 3, 1.3, '相关数字滤波\n与死区时序')],
                 [[[3, 1.15], [3.5, 1.15], [3.5, 2.65], [4, 2.65]],
                  [[7, 2.65], [8, 2.65]],
                  [[3.5, 1.15], [3.5, -.35], [4, -.35]],
                  [[7, -.35], [8, -.35]]], [], '')
    record('06', 1, 'clock-branches', 'PSC 与 CKD 位于不同的时序分支',
           '先沿上分支看计数速度，再看下分支的滤波/死区。CKD并不是'
           'CNT后面又加一个分频器。72 MHz只除72得到1 MHz、每步1 μs；'
           '要定时1 s还需继续累计。16位定时器可用PSC=7199、ARR=9999：'
           '72 MHz÷7200÷10000=1 Hz，不能直接把一百万写进16位ARR。')
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.8))
    p = np.array([1, 2, 4, 10, 20, 40, 100])
    arr1 = 3600/p
    axs[0].plot(p-1, arr1, 'o-', color=BLUE)
    axs[0].set(xlabel='PSC 寄存器值', ylabel='每周期格数 ARR+1')
    axs[1].plot(p-1, 100/arr1, 'o-', color=ORANGE)
    axs[1].set(xlabel='PSC 寄存器值', ylabel='占空比步进 / 百分点')
    for ax in axs:
        b.axis_clean(ax)
    save('06', 2, 'psc-resolution', '同为20 kHz，过大的 PSC 会损失占空比刻度',
         fig, 'fTIM=72 MHz，边沿向上计数，(PSC+1)(ARR+1)=3600。'
         'PSC=0 有3600格，步进约0.0278个百分点；PSC=99只有36格，'
         '步进约2.778个百分点。两者频率相同，分辨率差100倍。')
    flow('06', 4, 'update-gates', '内部更新动作与 CPU 中断请求是两条判断链',
         ['溢出/下溢 或 UG\n来源不同', '按 UDIS 判断\n能否产生 UEV/装载',
          '按 URS 与来源判断\n是否设置 UIF', 'UIF=1 且 UIE=1\n形成更新中断请求',
          'NVIC/CPU允许\n才进入 ISR'],
         '图表示分层检查，不是所有来源都会完整走到最后。普通配置下'
         'URS=1 的 UG 仍能初始化/装载，却不因此置 UIF；UDIS=1 '
         '阻止 UEV 装载，UG 的计数器/预分频器初始化仍有单独语义。'
         '关UIE只关请求，PWM硬件仍可运行。')
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    t = np.linspace(0, 12, 2401)
    raw = ((t % 6) < 3).astype(int)
    high = (((t % 6) >= .5) & ((t % 6) < 3)).astype(int)
    low = (((t % 6) >= 3.5) & ((t % 6) < 6)).astype(int)
    for ax, val, label, color in zip(
            axs, [raw, high, low], ['OCREF', 'CH主输出', 'CHN互补输出'],
            [BLUE, GREEN, ORANGE]):
        b.wave(ax, t, val, label, color)
        for start in [0, 3, 6, 9]:
            ax.axvspan(start, start+.5, color=RED, alpha=.14)
    axs[-1].set_xlabel('时间 / μs；简化有效高门极模型，死区0.5 μs')
    save('06', 8, 'deadtime', '死区将待导通一路的边沿推迟，形成双方关断区', fig,
         '三行在同一时刻垂直对照，红色带内两路都为低。'
         '这只是TIM1互补输出的有效高简化模型，忽略极性、空闲态、'
         '刹车与驱动传播延迟；实际功率级还需测量门极及上下管交叠。')
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    t = np.arange(0, 19)
    cnt = np.where(t < 12, t % 10, 2)
    b.wave(axs[0], t, (t < 12).astype(int), 'CEN', BLUE)
    axs[1].step(t, cnt, where='post', color=GREEN, lw=2)
    axs[1].set(ylabel='CNT', yticks=[0, 2, 5, 9])
    b.axis_clean(axs[1])
    b.wave(axs[2], t, (cnt < 5).astype(int), 'PWM引脚', ORANGE)
    for ax in axs:
        ax.axvline(12, ls='--', color=RED)
    axs[-1].set_xlabel('时间 / tick；ARR=9、CCR=5，t=12时清CEN')
    save('06', 9, 'cen-freeze', '清 CEN 可能把 PWM 冻结在高电平', fig,
         'PWM1、有效高、输出仍使能且未触发刹车等条件下，CNT停在2，'
         'CNT<CCR继续成立。停止计数与要求负载进入安全态应分开设计；'
         '不能把清CEN当成通用拉低命令。')
    fig, axs = plt.subplots(2, 1, figsize=(12, 5.2), sharex=True)
    t = np.arange(21)
    cnt = t % 10
    axs[0].step(t, cnt, where='post', lw=2)
    axs[0].axhline(3, color=RED, ls='--', label='CCR=3')
    axs[0].set(ylabel='CNT', yticks=range(10)); axs[0].legend()
    b.axis_clean(axs[0])
    b.wave(axs[1], t, (cnt < 3).astype(int), '输出', GREEN)
    axs[1].set_xlabel('计数 tick；ARR=9、PWM1、有效高、通道使能')
    save('06', 10, 'ccr-threshold', 'CCR 是比较阈值：CNT=0、1、2 时输出高', fig,
         '垂直对照上下图：到CCR=3时翻为低，CNT不会停下；到10个tick'
         '完成一轮。因此D=3/(9+1)=30%。CR1的CEN控制是否计数，'
         'DIR/CMS控制走法，ARPE控制ARR预装载；输出还需CCMR与CCER配置。')

    fig, ax = plt.subplots(figsize=(11, 4.8))
    t = np.arange(301)
    cnt = (900+t) % 1000
    ax.plot(t, cnt, color=BLUE, lw=2)
    ax.scatter([0, 200], [900, 100], color=RED, s=70, zorder=3)
    ax.annotate('捕获C1=900', (0, 900), (30, 850))
    ax.annotate('捕获C2=100', (200, 100), (200, 400),
                arrowprops=dict(arrowstyle='->'))
    ax.set(xlabel='经过的计数 tick', ylabel='CNT', ylim=(0, 1050))
    b.axis_clean(ax)
    save('07', 2, 'capture-wrap', '900 → 回绕 → 100：差值要按计数模数计算', fig,
         'ARR=999，模数M=1000；Δ=(100−900+1000)%1000=200。'
         '只有已知两次捕获间隔小于一个模周期时，才能唯一解读为200 tick；'
         '多绕一圈同样得到这个余数。')
    lanes('07', 6, 'overcapture', 'CCR 是锁存位置，未读前又来边沿就可能丢测量',
          [('输入边沿', [(1, .6, 'A', BLUE), (4, .6, 'B', RED)]),
           ('CCR状态', [(1, 3, '保存A', BLUE), (4, 4, '被B覆盖', RED)]),
           ('软件', [(6, 2, '读取只见B', ORANGE)])],
          9, '时间（示意）；假设期间未读CCR也未及时DMA搬运',
          '第二次捕获可能置CCxOF，表示数据流已不完整。处理时应记录丢失、'
          '按手册清标志，并重新建立周期配对；不能继续把B当作紧邻上次的A。')
    lanes('07', 5, 'pwmi-pair', '跨周期混读：两个正确寄存器值也能算出错误占空比',
          [('周期k', [(0, 10, 'T=10，高3，D=30%', BLUE)]),
           ('周期k+1', [(10, 8, 'T=8，高4，D=50%', GREEN)]),
           ('错误快照', [(10, 8, '旧周期10 + 新高宽4 → 40%', RED)])],
          19, '时间 / ms（示例信号）',
          '40%不属于任一完整周期。实际PWMI复位模式的CCR更新顺序取决于'
          '边沿和通道，应在选定完成事件后组装一致快照，遇过捕获或超时则丢弃。')
    flow('07', 8, 'measurement-validity', '测量结果需要随时间失效，不能永远沿用上一次频率',
         ['收到合法捕获\n校验周期/配对', '发布频率/占空比\n带时间戳与有效位',
          '持续监测年龄\nnow−timestamp', '超过业务超时\n标为失效并报原因',
          '重新捕获\n重新配对后恢复有效'],
         '超时阈值应覆盖最低允许输入频率及合理抖动。停波时，旧频率只是历史值；'
         '发布valid=false和超时原因比只把频率写0更能区分失效与真实零速。')


def uart_and_radio():
    """串口与无线链路用分块、吞吐和事务图联系。"""
    lanes('08', 2, 'tx-completion', 'DMA完成、TXE与TC分别对应发送流水线的不同位置',
          [('DMA', [(0, 3, '最后一字节搬入DR', BLUE)]),
           ('DR', [(3, 2, '等待移位器接走', ORANGE)]),
           ('移位器/引脚', [(3, 2, '前一字节尾段', GREEN),
                            (5, 4, '最后一字节含停止位', GREEN)]),
           ('标志时点', [(2.5, 1, 'DMA完', BLUE),
                        (4.5, 1, 'TXE', ORANGE), (8.5, 1, 'TC', RED)])],
          10, '时间（示意）；TXE与TC通常会在多字节发送中多次变化',
          'TXE表示DR空，TC表示最后一帧已发完且DR也空。DMA完成时，'
          '字节可能还在DR或移位器。RS-485释放DE等操作必须依据真正线路发送完成。')
    lanes('08', 3, 'rx-overrun', '软件不及时取走接收数据，下一字节可能造成 ORE',
          [('接收移位器', [(0, 3, '收A', BLUE), (3, 3, '收B', GREEN)]),
           ('DR未读', [(3, 3, 'A等待取走', ORANGE)]),
           ('软件响应', [(6, 3, '此时才处理：流已缺字节', RED)])],
          10, '时间（示意）；A在t=3收完，B在t=6收完',
          't=6 时DR仍未腾空，会出现过载接收错误。不能只清ORE后假装消息完整；'
          '要记录错误并重新同步协议。F1相关错误清除依手册规定读取SR再读DR。')
    blocks('08', 5, 'idle-boundary', '同一串口帧可以分两块，两帧也可能落在同一块',
           [(1, 'DMA块A\n帧1前半'), (1, 'DMA块B\n帧1后半'),
            (2, 'DMA块C\n完整帧2 + 完整帧3')],
           '方框表示软件收到的DMA数据块，不代表协议帧。IDLE反映串口线上'
           '一段空闲，解析器仍需依据长度、校验、帧头或转义规则持续消费字节。')
    flow('08', 7, 'request-ack-done', '接收请求、接受请求、动作完成应有不同语义',
         ['收到请求\n校验帧与序号', '检查业务状态\n接受或拒绝',
          '返回接受确认\n仅说明已受理', '执行硬件/业务动作\n可能失败或超时',
          '返回完成结果\n关联同一事务序号'],
         '发送方分别设置接收确认与完成超时。若模块手册只有一种应答，'
         '要按其实际语义处理，不能凭命名把“收到”解释成“已完成”。')

    blocks('09', 4, 'value-block', 'Classic 值块的16字节含数值冗余和地址冗余',
           [(4, '字节0–3\nV'), (4, '字节4–7\n~V'),
            (4, '字节8–11\nV'), (4, '字节12–15\nA,~A,A,~A')],
           'V是32位值，通常低字节在前；~表示逐位取反。后四字节是地址及其冗余。'
           '这是Classic兼容值块的格式说明，不保证特定模块暴露了相应操作命令，'
           '冗余一致性也不能替代业务权限与交易校验。')
    flow('09', 6, 'card-presence', '卡离场会打断一次交易，重新进场应重新建会话',
         ['寻卡/防冲突\n选定目标卡', '认证指定扇区\n建立访问条件',
          '读写/业务校验\n随时可能卡离场', '超时或链路丢失\n终止当前会话',
          '重新寻卡\n重新认证并核对结果'],
         '中途离场不意味着写入一定未发生。若在提交后丢应答，重新进场后应'
         '结合交易号与读回结果判断，不能自动重复扣款。图不规定模块具体命令。')
    blocks('09', 2, 's50-space', 'S50：物理1024 B与常规业务数据空间不同',
           [(16, '制造商块\n16 B'), (752, '47个普通数据块\n752 B'),
            (256, '16个扇区尾块\n256 B')],
           '横轴按字节比例，最左制造商块很窄。扇区尾块含密钥和访问条件，'
           '不能当普通数据随便覆盖；47块只是常规结构容量，实际可写性由卡型和权限决定。')
    flow('09', 7, 'transaction-id', '消费250分：交易号把重试与重复扣款区分开',
         ['读取余额B与记录\n核对卡/账户', '创建交易号Q\n目标余额B−250',
          '提交Q与结果\n采用支持的一致性方案', '应答丢失后重连\n查询Q的最终状态',
          'Q已完成则复用结果\n未确认则继续核实'],
         '这是业务设计模型，不能把“余额+交易号”写在不同块就当成原子事务。'
         '实际需要可恢复日志、模块支持或服务器账本；超时只表示结果未知。')

    flow('10', 1, 'ble-layers', 'BLE 的连接角色与 GATT 数据角色处在不同层',
         ['GAP层建立连接\nCentral / Peripheral',
          '连接上承载ATT\n协商可用MTU等能力',
          'GATT组织数据\n服务/特征/描述符',
          'Client 发起访问\nServer 提供属性',
          '业务协议\n定义含义与完成条件'],
         '角色应逐层判断：Central/Peripheral不能直接等同于Client/Server。'
         '一个连接中的设备可按实现承担GATT双向角色；BR/EDR的SPP又是另一套能力。')
    blocks('10', 3, 'fragment-200', '200字节业务载荷，在每片20字节时要分成10片',
           [(20, '1'), (20, '2'), (20, '3'), (20, '4'), (20, '5'),
            (20, '6'), (20, '7'), (20, '8'), (20, '9'), (20, '10')],
           '假设ATT_MTU=23、一次通知的值最大20 B，且尚未扣业务分片头。'
           '若每片还需要序号和校验，200 B就会超过10片。分片要有事务号、'
           '片序、总长和重组超时；MTU变大也不能省掉业务边界。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    baud = np.array([9600, 19200, 57600, 115200])
    ms = 512*10/baud*1000
    ax.bar([str(x) for x in baud], ms, color=[ORANGE, BLUE, GREEN, BLUE])
    for i, value in enumerate(ms):
        ax.text(i, value+8, f'{value:.1f} ms', ha='center')
    ax.set(xlabel='UART波特率 / bit/s（8N1）',
           ylabel='512 B 的理想串行发送时间 / ms', ylim=(0, 620))
    b.axis_clean(ax)
    save('10', 4, 'uart-bottleneck', '无线再快，9600波特UART发512字节也至少约533 ms',
         fig, '8N1每字节10 bit，t=512×10/baud。不含AT封装、缓存等待、'
         '无线连接间隔、重传和对端处理；这是串行线发送下限，不是端到端实测。')
    flow('10', 5, 'at-state', 'AT配置与业务传输需要受控切换',
         ['业务模式\n正常收发数据', '停止新业务\n等待当前事务收尾',
          '按模块手册\n进入命令模式', '发送AT并校验应答\n每步都有超时',
          '退出并核实模式\n恢复业务接收解析'],
         '不同模块的引脚、电平、进入时机、波特率规则并不统一。'
         '此图只规定软件状态边界；失败时记录当前模式并按手册恢复，'
         '避免把AT应答当业务帧或把业务数据当配置命令。')

    b.structured('11', 'zigbee-topology', '终端依赖父节点，路由器承担转发',
                 [(4, 2, 3, 1.3, '协调器C\n建网/路由能力'),
                  (0, -.6, 3, 1.3, '路由器R1\n常供电/转发'),
                  (8, -.6, 3, 1.3, '路由器R2\n常供电/转发'),
                  (0, -3.2, 3, 1.3, '终端E1\n父节点R1'),
                  (8, -3.2, 3, 1.3, '终端E2\n父节点R2')],
                 [[[4, 2], [1.5, .7]], [[7, 2], [9.5, .7]],
                  [[1.5, -.6], [1.5, -1.9]],
                  [[9.5, -.6], [9.5, -1.9]]], [], '')
    record('11', 2, 'zigbee-topology', '终端依赖父节点，路由器承担转发',
           '连线表示一组示例父子关系，省略反向数据与其他邻接链路。'
           '终端通常不转发其他节点的包；网络角色不能仅凭模块外观判断。')
    flow('11', 3, 'join-chain', '入网失败要沿过程定位，不能只检查PAN ID',
         ['扫描可用信道\n找到候选网络', '允许加入?\n信号/容量是否满足',
          '关联并分配身份\n父节点接纳', '安全认证/密钥\n完成所需交换',
          '应用端点就绪\n再验证业务互通'],
         '每个关口都可能拒绝或超时；具体入网流程随协议版本与安全配置变化。'
         '关联成功不能直接当成业务成功，短地址也不能替代长期设备身份。')
    lanes('11', 4, 'multihop-airtime', '同一干扰域内，三跳要多次占用共享无线介质',
          [('源→R1', [(0, 2, '发送/应答', BLUE)]),
           ('R1→R2', [(3, 2, '转发/应答', GREEN)]),
           ('R2→目的', [(6, 2, '转发/应答', ORANGE)]),
           ('其他节点', [(0, 8, '需要竞争或等待', RED)])],
          9, '时间（示意），假设这些链路共享同一干扰域',
          '一份业务数据占用多次空口时间，容量不能按路由器数量相乘。'
          '空间复用、退避、重传和不同链路质量会进一步改变吞吐与尾延迟。')
    lanes('11', 5, 'sleep-poll', '休眠终端的下行消息可能等到下一次轮询',
          [('父节点', [(2, 6, '缓存下行消息', ORANGE)]),
           ('终端', [(0, 1, '轮询', BLUE), (1, 7, '休眠', GREEN),
                    (8, 1, '轮询/接收', BLUE)])],
          10, '时间 / s（教学示例，轮询周期8 s）',
          '消息在t=2到达，终端在t=8才取走，等待约6 s。'
          '父节点缓存容量、超时和子节点老化都有限，不能保证任意长休眠仍能收到。')


def i2c_spi_flash():
    """用电气约束、总线波形和掉电窗口解释存储数据链。"""
    fig, ax = plt.subplots(figsize=(11, 4.8))
    cap = np.linspace(30, 400, 300)
    lower = (3.3-.4)/.003/1000
    upper = 300e-9/(.8473*cap*1e-12)/1000
    ax.plot(cap, upper, color=BLUE, label='Rp最大：上升时间≤300 ns')
    ax.axhline(lower, color=RED, label='Rp最小：灌电流≤3 mA')
    ax.fill_between(cap, lower, upper, where=upper >= lower,
                    color=GREEN, alpha=.2, label='同时满足两条件的区间')
    ax.set(xlabel='总线电容 Cb / pF', ylabel='上拉电阻 Rp / kΩ')
    ax.legend(); b.axis_clean(ax)
    save('12', 1, 'rp-window', '电容变大时，上拉电阻的可选窗口逐渐收窄', fig,
         '假设VDD=3.3 V、VOL(max)=0.4 V、IOL=3 mA、tr(max)=300 ns。'
         'Rp(min)约0.967 kΩ，Cb=100 pF时Rp(max)约3.54 kΩ。'
         '这些是计算条件，不是对所有板卡的固定推荐；还需核对器件及走线。')
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    times = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    b.wave(axs[0], times, [1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1],
           '主机释放意图', BLUE)
    b.wave(axs[1], times, [1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1],
           '从机释放状态', ORANGE)
    b.wave(axs[2], times, [1, 0, 1, 0, 0, 0, 0, 1, 0, 1, 1],
           '实际SCL', GREEN)
    for ax in axs:
        ax.axvspan(4, 7, color=RED, alpha=.12)
    axs[-1].set_xlabel('时间（示意）；1表示释放，0表示主动拉低')
    save('12', 2, 'clock-stretch', '主机释放 SCL 后，实际线仍可能被从机拉低', fig,
         '实际SCL是开漏参与者共同作用的结果。红段主机已经释放，'
         '但从机尚未释放；支持拉伸的主机应观察实际线电平并有超时。'
         '图不表示所有器件都支持拉伸，也省略RC上升沿。')
    blocks('12', 6, 'burst-budget', '14字节连续读：数据位之外还有地址和应答时钟',
           [(9, 'SLA+W\n9 clk'), (9, '寄存器\n9 clk'),
            (9, 'SLA+R\n9 clk'), (126, '14字节数据及ACK/NACK\n126 clk')],
           '典型“写寄存器地址+重复起始+读14字节”约153个SCL周期。'
           '400 kHz理想耗时382.5 μs，100 kHz为1.53 ms，'
           '还要加起停建立、拉伸、软件空隙等；末字节由主机NACK结束。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    t = np.linspace(0, 120, 300)
    ax.plot(t, .5*t, color=RED, lw=2, label='仅积分：偏置0.5 °/s')
    ax.plot(t, 2*(1-np.exp(-t/4)), color=BLUE, lw=2,
            label='有低频约束的简化误差模型')
    ax.set(xlabel='时间 / s', ylabel='角度误差 / °')
    ax.legend(); b.axis_clean(ax)
    save('12', 7, 'gyro-drift', '微小陀螺偏置持续积分，会变成明显角度漂移', fig,
         '红线按误差=b×t计算，120 s为60°。蓝线只是有界对照模型，'
         '不是某个滤波器实测。重力可约束部分倾角，但线加速度会干扰，'
         '单靠加速度计无法给偏航提供绝对航向参考。')

    fig, axs = plt.subplots(4, 1, figsize=(12, 8), sharex=True)
    x = np.arange(0, 9)
    for mode, ax in enumerate(axs):
        cpol, cpha = mode//2, mode % 2
        vals = [cpol] + [(1-cpol if i % 2 else cpol) for i in range(1, 9)]
        ax.step(x, vals, where='post', color=BLUE, lw=2)
        for edge in range(1, 9):
            sample = (edge % 2 == 1) if cpha == 0 else (edge % 2 == 0)
            color = GREEN if sample else ORANGE
            ax.axvline(edge, color=color, ls='--', alpha=.75)
        ax.set(yticks=[0, 1], ylim=(-.3, 1.4),
               ylabel=f'Mode{mode}\nCPOL={cpol}\nCPHA={cpha}')
        b.axis_clean(ax)
    axs[-1].set_xlabel('SCK边沿序号；绿色=采样，橙色=改变数据')
    save('13', 1, 'spi-four-modes', '先看空闲电平，再按第一个或第二个边沿确定采样', fig,
         'CPHA=0在第一个有效边沿采样，首位须在该边沿之前准备好；'
         'CPHA=1在第二个边沿采样。图只画SCK与采样/改变标记，'
         '真实数据还须满足从设备的建立、保持及CS时序要求。')
    lanes('13', 3, 'read-duplex', '03h读命令期间，主机发送dummy才能持续提供读时钟',
          [('CS低有效窗口', [(0, 10, '覆盖整个事务', BLUE)]),
           ('MOSI', [(0, 2, '03h', GREEN), (2, 3, '24位地址', GREEN),
                     (5, 5, '持续发dummy', ORANGE)]),
           ('MISO', [(0, 5, '忽略命令阶段接收值', ORANGE),
                     (5, 5, '有效读取数据', GREEN)])],
          11, '阶段示意，宽度不代表真实字节比例',
          '针对课件常见24位地址的03h普通读取，命令后3个地址字节，随后读数据。'
          'dummy指主机为产生时钟而发送的占位字节，不是03h要求的额外dummy周期；'
          '不同快速读命令的规则需另查手册。')
    blocks('13', 10, 'page-split', '256 B页：从页内偏移248写20 B，应拆成8 B与12 B',
           [(8, '当前页\n偏移248…255\n先写8 B'),
            (12, '下一页\n偏移0…11\n再写12 B')],
           '第一段结束后等待BUSY清除、检查结果，再按器件要求WREN启动下一段。'
           '不能假定跨页Page Program会自动进入下一页；常见器件会在页内回绕。')
    flow('13', 9, 'spi-lock', '共享总线的锁需要覆盖配置、CS与整段收发',
         ['取得总线互斥锁\n检查设备是否就绪', '配置本设备参数\nCPOL/CPHA/速度',
          '拉低本设备CS\n发送命令与数据', '等待传输真正结束\n检查BSY等条件',
          '释放CS再解锁\n错误路径也需收尾'],
         '只锁发送函数的一次调用，仍可能在“命令→地址→数据”之间被别的任务改模式。'
         'SPI总线锁和Flash内部BUSY是两层：芯片忙时可否释放总线给其他设备，'
         '应由设备级状态与驱动约束共同决定。')

    blocks('14', 1, 'link-reserve', 'F103C8示例：参数页必须同时从代码链接区中扣除',
           [(62, '应用代码/常量等\n0x08000000…0x0800F7FF\n62 KiB'),
            (1, '参数A\n0x0800F800\n1 KiB'),
            (1, '参数B\n0x0800FC00\n1 KiB')],
           '示例以64 KiB主Flash和1 KiB页为前提，末两页做参数存储。'
           '最右两页很窄是实际比例；写存储宏还不够，链接布局也必须排除它们。'
           '这只是规划示例，没有修改用户工程的链接配置。')
    lanes('14', 3, 'flash-stall', '单Bank Flash忙期间，代码取指等待可能扩大中断延迟',
          [('Flash', [(1, 5, '擦除/编程忙', RED)]),
           ('CPU Flash取指', [(0, 1, '执行', BLUE),
                             (1, 5, '取指请求可能等待', ORANGE),
                             (6, 3, '恢复执行', BLUE)]),
           ('外部事件', [(3, 1, 'IRQ到达', GREEN),
                         (6, 2, '可能此时才服务', GREEN)])],
          10, '时间（示意），不代表具体擦除耗时',
          '仅把入口函数放RAM不一定解决问题：调用链、常量、向量表或ISR仍可能访问'
          '忙Flash。应核对手册的访问限制，并实际评估最坏中断延迟。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    seconds = np.logspace(0, 5, 200)
    years = 10000*seconds/(365*24*3600)
    ax.loglog(seconds, years, color=BLUE, lw=2)
    ax.scatter([1, 60, 3600], 10000*np.array([1, 60, 3600])/31536000,
               color=RED, zorder=3)
    ax.set(xlabel='同一页平均擦除间隔 / s',
           ylabel='10000次擦除对应的理论时间 / 年')
    b.axis_clean(ax)
    save('14', 6, 'wear-budget', '寿命预算首先看擦除频率，而不是只看写入字节数', fig,
         '仅假设单页10000次擦除作为计算预算，不作为无条件寿命保证。'
         '每秒擦除约2.78小时用完预算；每分钟约6.94天；每小时约1.14年。'
         '合并保存、追加日志、跨页轮换可改变平均磨损，还需考虑温度和数据保持条件。')
    flow('14', 9, 'power-loss', '两页提交：新页未确认有效前，始终保留旧页',
         ['A页为有效旧版本\nB页待使用', '擦B并写新载荷\n此时掉电选A',
          '写CRC并读回验证\n此时掉电仍选A', '最后写提交标记\n启动校验后可选B',
          '确认B有效后\n才回收旧A页'],
         '启动扫描必须同时校验提交标记、版本、长度和CRC等条件。'
         '提交标记写入中途掉电时，只有完整有效的新记录才可获选；'
         '序号比较要定义回绕规则，测试应覆盖每一步及标记半写入状态。')


def rtc_power_rtos():
    """把时间一致性、能量和调度的隐含边界可视化。"""
    lanes('15', 5, 'rtc-torn-read', '分开读高低半字时，可能拼出从未存在的时间',
          [('真实计数', [(0, 4, '0x0000_FFFF', BLUE),
                        (4, 4, '0x0001_0000', GREEN)]),
           ('不利读取', [(1, 2, '读高=0000', ORANGE),
                        (5, 2, '读低=0000', RED)]),
           ('拼接结果', [(7, 2, '错误值0', RED)])],
          9, '读取先后（示意）',
          '高低交界时旧高位+新低位造成错误。常用一致读法是高1→低→高2，'
          '若高1≠高2就重读；还需按F1 RTC规定处理APB同步。')
    flow('15', 4, 'timezone', 'UTC存储只做一次时区转换，避免重复加8小时',
         ['UTC时间戳\n对应UTC 00:00', '显示层转UTC+8\n显示08:00',
          '用户输入本地08:00\n明确其时区', '转换回UTC 00:00\n再写入存储'],
         '这是同一时刻的表示转换。若先把时间戳加8小时，再交给已配置UTC+8的'
         'localtime，就会显示16:00。time_t宽度、时区库配置和夏令时规则需要明确。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    t = np.arange(0, 21)
    ax.plot(t, t, 'o-', label='单调计时', color=GREEN)
    ax.plot(t, np.where(t < 10, t, t-6), 'o-',
            label='墙上时间：t=10时回拨6 s', color=RED)
    ax.axvline(10, color=ORANGE, ls='--')
    ax.set(xlabel='真实经过时间 / s', ylabel='相对计时值 / s')
    ax.legend(); b.axis_clean(ax)
    save('15', 7, 'wall-monotonic', '日志时间可以校准，超时计时应避免随之倒退', fig,
         '图用相对秒数省略日期。墙上时间回拨后可能重复，若用它计算通信超时，'
         '等待会被延长。单调计时还要正确处理计数回绕和低功耗期间的补偿。')
    branch('15', 6, 'rtc-trust', '启动时先判断时间可信度，再决定是否初始化',
         ['启动读取备份状态\n电源/复位原因', '检查配置标记\nRTC运行与数值范围',
          '可信：保留计时\n不重复写默认日期', '不可信：标为待校时\n按受控路径设时间',
          ],
         '右上和右下是两种判断结果；校时成功后记录来源与可信状态。'
         '标记存在不代表晶振始终正常，业务可结合掉电原因、时间范围和外部校时验证。')

    fig, ax = plt.subplots(figsize=(11, 4.8))
    ax.fill_between([0, 10], [20, 20], color=BLUE, alpha=.5,
                    label='工作：20 mA × 10 ms')
    ax.fill_between([10, 1000], [.02, .02], color=GREEN, alpha=.8,
                    label='休眠：0.020 mA × 990 ms')
    ax.set(xlabel='一个周期内的时间 / ms', ylabel='电流 / mA',
           ylim=(0, 23), xlim=(0, 1000))
    ax.legend(); b.axis_clean(ax)
    save('16', 2, 'current-area', '平均电流看曲线下面积：短时大电流也可能占主导', fig,
         '平均电流=(20×10+0.020×990)/1000=0.2198 mA。'
         '图是理想两状态模型，工作只占1%时间却贡献大部分电荷；'
         '实际还要计入唤醒、无线发送、稳压器和板级静态电流。')
    lanes('16', 4, 'sleep-race', '检查完无任务之后，进入睡眠之前仍有事件窗口',
          [('主循环', [(0, 2, '检查无任务', BLUE),
                      (4, 4, '直接WFI可能错过处理时机', RED)]),
           ('ISR', [(2, 2, '处理IRQ并设置工作标志', ORANGE)]),
           ('待处理标志', [(3, 5, '已有工作，但主循环未重查', GREEN)])],
          9, '时间（示意）；ISR已返回，且没有其他待处理中断',
          '事件不一定丢失，可能是软件已经置标志却又入睡，直到下次唤醒才处理。'
          '应使用已验证的原子检查/睡眠序列或RTOS低功耗入口，不能盲目关中断后WFI。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    cap = np.linspace(10, 1000, 250)
    available = cap*1e-6*(3.3**2-2.7**2)/2/(.020*3.0)*1000
    ax.plot(cap, available, color=BLUE, lw=2)
    ax.axhline(8, color=RED, ls='--', label='假设保存动作需8 ms')
    ax.set(xlabel='保持电容 / μF', ylabel='理想可维持时间 / ms')
    ax.legend(); b.axis_clean(ax)
    save('16', 7, 'pvd-energy', '掉电后是否来得及保存，需要比较能量与执行时间', fig,
         '用E=½C(V高²−V低²)，假设3.3→2.7 V、负载功率60 mW，'
         '100 μF理想约3 ms，1000 μF约30 ms。忽略ESR、泄漏和电源转换损耗，'
         '仅作能量估算；PVD门限、最低编程电压和最坏擦写耗时还需逐项满足。')
    branch('16', 6, 'wake-fallback', '唤醒恢复时钟，也必须给失败分支一个出口',
         ['STOP唤醒\n当前先用HSI', '启动HSE/PLL\n带超时等待',
          '成功则切目标时钟\n重新校核外设时基', '失败则保持可用时钟\n记录故障/限制业务',
          ],
         '右上与右下分别代表成功和失败结果，之后发布恢复状态。'
         '降级时USART、PWM、SysTick等配置必须匹配实际时钟；'
         '无法满足时序的业务应拒绝启动或进入项目定义的安全状态。')

    flow('17', 2, 'psp-msp', '任务切换：硬件异常帧与软件保存寄存器分两段',
         ['任务在线程模式\n用自己的PSP栈', '异常进入\n硬件在原栈压8字现场',
          'Handler用MSP\nPendSV运行', '端口代码把R4–R11等\n补存到任务栈',
          '选择另一任务栈\n恢复后异常返回'],
         '以典型Cortex-M3 FreeRTOS端口为机制示意。硬件帧为R0–R3、R12、'
         'LR、PC、xPSR，可能另有对齐；端口保存内容应以实际源码为准。'
         'MSP用于异常处理，不是所有任务共用一个PSP栈。')
    fig, ax = plt.subplots(figsize=(11, 4.8))
    phase = np.linspace(0, .999, 200)
    ax.plot(phase, 5-phase, color=BLUE, lw=2)
    ax.set(xlabel='调用相对上次Tick的相位 / ms',
           ylabel='等待5个Tick至解除阻塞 / ms', ylim=(3.8, 5.2))
    b.axis_clean(ax)
    save('17', 4, 'tick-phase', '同样延时5个Tick，真实等待会随调用相位变化', fig,
         '假设Tick=1 ms，无挂起调度等额外因素，等待时间大致落在4到5 ms。'
         '这只是解除阻塞时刻，变为Ready后何时运行还取决于调度和更高优先级工作。'
         'pdMS_TO_TICKS的取整还会进一步影响短延时。')
    flow('17', 6, 'queue-pointer', '队列复制指针值，不会延长局部数组的生命周期',
         ['生产者函数局部buf\n在当前栈帧里', '把buf地址入队\n只复制地址数值',
          '函数返回/继续运行\nbuf失效或被改写', '消费者出队指针\n地址相同，内容不再可靠',
          '改用消息副本\n或显式缓冲所有权协议'],
         '即便入队成功也不保证指向内容安全。若队列项本身是结构体，'
         '结构体中的指针仍是浅拷贝；缓冲池应明确归还时机、超时和失败回收路径。')
    b.structured('17', 'abba-deadlock', 'ABBA死锁：两个任务各持有一个锁，再等待对方',
                 [(0, 2, 3, 1.3, '任务A\n持有锁1'),
                  (8, 2, 3, 1.3, '任务B\n持有锁2'),
                  (0, -1, 3, 1.3, '等待锁2\n由B持有'),
                  (8, -1, 3, 1.3, '等待锁1\n由A持有')],
                 [[[1.5, 2], [1.5, .3]], [[9.5, 2], [9.5, .3]],
                  [[3, -.35], [5.5, -.35], [5.5, 2.65], [8, 2.65]],
                  [[8, -.65], [6, -.65], [6, 3.7], [1.5, 3.7],
                   [1.5, 3.3]]], [], '')
    record('17', 8, 'abba-deadlock', 'ABBA死锁：两个任务各持有一个锁，再等待对方',
           '沿依赖箭头形成等待环。提高任务优先级或启用优先级继承不会解除环；'
           '应统一加锁顺序、减少嵌套或设计有回滚的超时策略。')
    blocks('17', 9, 'nvic-encoding', 'F103四位优先级：逻辑值5写入硬件高四位0x50',
           [(4, '寄存器 bits7:4\n实现的优先级\n0101'),
            (4, '寄存器 bits3:0\n未实现\n0000')],
           '假设__NVIC_PRIO_BITS=4，CMSIS NVIC_SetPriority传逻辑值5，'
           '硬件字节是5<<4=0x50。逻辑数字越小紧迫性越高。'
           'FreeRTOS屏蔽阈值宏有逻辑值与已左移值两类，不能互相直接替换。')
    lanes('17', 11, 'timer-service', '一个软件定时器回调耗时过长，会拖住同一服务任务的后续工作',
          [('Timer服务任务', [(0, 6, '回调A长时间占用', RED),
                             (6, 2, '回调B迟到', BLUE)]),
           ('到期/命令', [(2, 2, 'B到期', GREEN),
                         (4, 2, '新命令待处理', ORANGE)])],
          10, '时间（示意），A与B在同一Timer服务任务中执行',
          '回调A不会自动获得独立线程。长计算或阻塞会延迟其他回调和定时器命令处理；'
          '回调宜做短操作并通知业务任务，命令队列容量与失败返回也要检查。')


def main():
    """每课独立保存图源；清单只包含本脚本生成的图。"""
    for number in range(1, 18):
        cid = f'{number:02d}'
        (b.ASSETS/cid).mkdir(parents=True, exist_ok=True)
        b.DRAWIOS[cid] = ET.Element('mxfile', host='app.diagrams.net')
        b.FIGURES[cid] = []
    for fn in [mcu_and_tools, gpio_irq_adc, timers, uart_and_radio,
               i2c_spi_flash, rtc_power_rtos]:
        fn()
        print(f'已完成 {fn.__name__}，累计 {len(MANIFEST)} 幅', flush=True)
    for cid, root in b.DRAWIOS.items():
        if len(root):
            ET.ElementTree(root).write(b.ASSETS/cid/'extended.drawio',
                                      encoding='utf-8', xml_declaration=True)
    for item in MANIFEST:
        stem = b.ASSETS/item['id']/item['slug']
        if not stem.with_suffix('.json').exists():
            continue
        # 固定白底，避免透明PNG在深色阅读器中降低标题对比度。
        path = stem.with_suffix('.png')
        with Image.open(path) as source:
            rgba = source.convert('RGBA')
            white = Image.new('RGBA', rgba.size, 'white')
            white.alpha_composite(rgba)
            white.convert('RGB').save(path)
        path = stem.with_suffix('.svg')
        tree = ET.parse(path)
        root = tree.getroot()
        x, y, width, height = root.attrib['viewBox'].split()
        ns = '{http://www.w3.org/2000/svg}'
        background = ET.Element(ns+'rect', x=x, y=y, width=width,
                                height=height, fill='white')
        root.insert(0, background)
        tree.write(path, encoding='utf-8', xml_declaration=True)
    (b.ASSETS/'manifest.json').write_text(
        json.dumps(MANIFEST, ensure_ascii=False, indent=2), 'utf-8')
    print(f'共输出 {len(MANIFEST)} 幅图')


if __name__ == '__main__':
    main()
