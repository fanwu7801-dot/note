"""重绘深入学习配图；所有数据都是教学模型，不代表板级实测。"""
from pathlib import Path
import importlib.util
import sys
import xml.etree.ElementTree as ET

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('base_diagrams', HERE/'redraw.py')
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
plt, np = base.plt, base.np
BLUE, GREEN = base.BLUE, base.GREEN
ORANGE, RED = base.ORANGE, base.RED
base.ASSETS = HERE.parent/'deep'


def initialize():
    """为本批深入图创建独立目录与可编辑图页。"""
    for number in range(1, 18):
        cid = f'{number:02d}'
        (base.ASSETS/cid).mkdir(parents=True, exist_ok=True)
        base.DRAWIOS[cid] = ET.Element('mxfile', host='app.diagrams.net')
        base.FIGURES[cid] = []


def make_waveforms():
    """用确定的公式画出误差、竞争和时序边界。"""
    fig, axs = plt.subplots(2, 1, figsize=(11, 5.8), sharex=True)
    t = np.arange(17)
    edge = t % 5
    center = np.array([0, 1, 2, 3, 4, 3, 2, 1]*2 + [0])
    axs[0].step(t, edge, where='post', color=BLUE, lw=2)
    axs[1].plot(t, center, 'o-', color=GREEN, lw=2)
    for ax in axs:
        ax.set(yticks=range(5), ylabel='CNT', xlim=(0, 16))
        base.axis_clean(ax)
    axs[0].set_title('边沿对齐 ARR=4：一个周期 5 tick')
    axs[1].set_title('中心对齐 ARR=4：一个完整往返周期 8 tick')
    axs[1].set_xlabel('计数 tick 序号；点表示计数时刻')
    base.save('06', 'center-aligned', fig,
              '同一个 ARR，边沿对齐与中心对齐的周期公式不同', '')

    fig, axs = plt.subplots(3, 1, figsize=(11, 6), sharex=True)
    t = np.arange(0, 201)
    arr = np.where(t < 50, 999, 1999)
    ccr = np.where(t < 150, 300, 600)
    vals = [arr, ccr, ccr/(arr+1)*100]
    names = ['有效 ARR', '有效 CCR', '占空比 / %']
    for ax, val, label in zip(axs, vals, names):
        ax.step(t, val, where='post', color=BLUE, lw=2)
        ax.set_ylabel(label)
        ax.axvline(50, color=RED, ls='--')
        ax.axvline(150, color=RED, ls='--')
        base.axis_clean(ax)
    axs[-1].set_xlabel('时间（示意）；50与150为两个更新边界')
    axs[0].set_title('更新前先写了新 ARR，下一次更新前才写完新 CCR')
    base.save('06', 'mixed-preload', fig,
              '多参数预装载仍需要统一提交：30% → 15% → 30%', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    t = np.linspace(0, 12, 500)
    err = np.exp(-t)
    ax.semilogy(t, err, color=BLUE, lw=2)
    ax.axhline(1/8192, color=ORANGE, ls='--', label='12位半LSB尺度')
    ax.axvline(np.log(8192), color=GREEN, ls=':')
    ax.set(xlabel='采样建立时间 / RC', ylabel='归一化残余误差',
           ylim=(1e-6, 1), xlim=(0, 12))
    ax.legend()
    base.axis_clean(ax)
    base.save('05', 'settling', fig,
              '延长采样窗口，是为了先让输入电压建立', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    t = np.linspace(0, .012, 3000)
    ts = np.arange(0, .0121, .001)
    ax.plot(t*1000, np.cos(2*np.pi*700*t), color=ORANGE,
            alpha=.7, label='连续700 Hz')
    ax.plot(t*1000, np.cos(2*np.pi*300*t), color=BLUE,
            alpha=.7, label='连续300 Hz')
    ax.scatter(ts*1000, np.cos(2*np.pi*700*ts), color=RED,
               zorder=5, label='1 kHz采样得到同一组点')
    ax.set(xlabel='时间 / ms', ylabel='幅值（归一化）')
    ax.legend(loc='upper right')
    base.axis_clean(ax)
    base.save('05', 'aliasing', fig,
              '混叠：采样点相同，原始连续信号却不同', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    x = np.logspace(2, 5, 400)
    ax.loglog(x, x/1e6*100, color=BLUE,
              label='测一个周期：1tick / 周期tick数')
    ax.loglog(x, 1/(x*.1)*100, color=GREEN,
              label='固定100ms门宽：1事件 / 总事件数')
    ax.set(xlabel='输入频率 / Hz', ylabel='单刻度相对量级 / %')
    ax.legend()
    ax.grid(alpha=.2, which='both')
    base.save('07', 'measurement-error', fig,
              '测周与测频：量化误差和响应时间的取舍', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    t = np.linspace(0, 35, 351)
    ax.plot(t, t*11.52, lw=2, color=BLUE, label='115200、8N1持续接收')
    ax.axhline(255, ls='--', color=RED, label='可用255字节')
    ax.axvline(20, ls=':', color=GREEN)
    ax.set(xlabel='消费者未处理的时间 / ms', ylabel='新增积压 / byte',
           ylim=(0, 410))
    ax.text(20.3, 210, '20ms约新增230字节')
    ax.legend()
    base.axis_clean(ax)
    base.save('08', 'buffer-budget', fig,
              '缓存预算要覆盖最长处理停顿，而不只看平均速率', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    days = np.arange(31)
    ax.plot(days, days*86400*10e-6, color=BLUE, label='固定10 ppm')
    ax.plot(days, days*86400*20e-6, color=ORANGE, label='固定20 ppm')
    ax.set(xlabel='持续走时 / 天', ylabel='累计偏差量级 / s')
    ax.legend()
    base.axis_clean(ax)
    base.save('15', 'clock-drift', fig,
              '晶振的小频差，会累积成明显日历误差', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    duration = np.linspace(0, 100, 300)
    ax.plot(duration, duration*.2, color=BLUE,
            label='浅睡：0.2mA，无额外恢复开销')
    ax.plot(duration, 5+duration*.02, color=GREEN,
            label='深睡：0.02mA，额外5μC恢复电荷')
    ax.axvline(5/.18, color=ORANGE, ls='--')
    ax.set(xlabel='空闲时长 / ms', ylabel='消耗电荷 / μC')
    ax.legend()
    base.axis_clean(ax)
    base.save('16', 'sleep-break-even', fig,
              '更深睡眠何时划算：还要算恢复开销', '')

    fig, ax = plt.subplots(figsize=(11, 4.5))
    for y, spans, color in [(2, [(0, 1)], ORANGE),
                             (1, [(1, 2)], BLUE),
                             (0, [(0, 3)], GREEN)]:
        ax.broken_barh(spans, (y, .5), facecolors=color)
    ax.set(yticks=[.25, 1.25, 2.25],
           yticklabels=['低任务响应窗口', '低任务实际执行', '高任务执行'],
           xlim=(0, 4), ylim=(-.2, 3.2), xlabel='时间 / ms')
    ax.axvline(2.5, color=RED, ls='--')
    ax.text(2.55, 2.7, '截止时间2.5ms', color=RED)
    base.axis_clean(ax)
    base.save('17', 'response-time', fig,
              '低任务只计算2ms，响应仍可能需要3ms', '')


def make_structured():
    """用同一图结构提供带连线的PNG/SVG/JSON和draw.io图源。"""
    base.structured('03', 'odr-race', 'ODR 读改写竞争：旧快照覆盖了新的位', [
        (0, 2, 3, 1.2, '主循环读取\nODR = 0000'),
        (4, 2, 3, 1.2, '中断置 bit1\nODR = 0010'),
        (8, 2, 3, 1.2, '主循环基于旧值置 bit0\n写回 ODR = 0001'),
        (4, -1.2, 3, 1.3, 'bit1 被旧快照覆盖\n不是中断没有执行')],
        [[[3, 2.6], [4, 2.6]], [[7, 2.6], [8, 2.6]],
         [[9.5, 2], [9.5, -.55], [7, -.55]]], [], '')
    base.structured('04', 'exception-frame', '基本异常堆栈帧：内容与历史最深栈不同', [
        (0, 2.5, 3, 1, '较高地址：xPSR、PC'),
        (0, .8, 3, 1, 'LR、R12'),
        (0, -.9, 3, 1, 'R3、R2'),
        (0, -2.6, 3, 1, '较低地址：R1、R0'),
        (6, .5, 4.5, 1.8, '基本帧共8字，可能另有对齐\n编译器/嵌套还有额外栈需求\n不能仅用当前SP证明从未溢出')],
        [[[4, 3], [4, -2.2]]], [(5.2, -2.5, '栈向低地址增长')], '')
    base.structured('14', 'commit-record', '掉电恢复：新副本提交之前，保留旧有效记录', [
        (0, 2, 3, 1.2, '旧记录 A\n完整且已提交'),
        (4, 2, 3, 1.2, '新位置 B\n写负载、版本、CRC'),
        (8, 2, 3, 1.2, '新记录 B\n验证后提交'),
        (4, -1.2, 3, 1.2, '下次上电扫描\n选择最新完整记录')],
        [[[3, 2.6], [4, 2.6]], [[7, 2.6], [8, 2.6]],
         [[9.5, 2], [9.5, -.6], [7, -.6]],
         [[1.5, 2], [1.5, -.6], [4, -.6]]],
        [(5.5, .4, '提交前掉电：仍可恢复 A')], '')
    base.structured('06', 'hardware-pipeline', '硬件时间链：触发、搬运、计算、装载各有边界', [
        (0, 2, 3, 1.2, '定时器事件\n确定采样相位'),
        (4, 2, 3, 1.2, 'ADC采样与转换\n随后DMA形成数据块'),
        (8, 2, 3, 1.2, 'ISR通知任务\n等待调度与计算'),
        (8, -1.3, 3, 1.3, '写CCR预装载\n等待有效更新'),
        (4, -1.3, 3, 1.3, '输出引脚与驱动\n产生真实动作')],
        [[[3, 2.6], [4, 2.6]], [[7, 2.6], [8, 2.6]],
         [[9.5, 2], [9.5, 0]], [[8, -.65], [7, -.65]]],
        [(4.5, .4, '总响应包含各阶段和相位等待')], '')
    base.structured('09', 'unknown-result', '交易超时：未执行与结果未知必须分开', [
        (0, 2, 3, 1.2, '发送之前失败\n能够证明未执行'),
        (4, 2, 3, 1.2, '请求可能已到卡片\n但未收到应答'),
        (8, 2, 3, 1.2, '应答与读回匹配\n确认业务结果'),
        (4, -1.3, 3, 1.3, '结果未知\n先核对事务与卡状态')],
        [[[5.5, 2], [5.5, 0]]],
        [(5.5, .8, '不能直接变成“失败后再扣一次”')], '')


def main():
    initialize()
    make_waveforms()
    make_structured()
    for cid, root in base.DRAWIOS.items():
        if len(root):
            ET.ElementTree(root).write(
                base.ASSETS/cid/'deep.drawio', encoding='utf-8',
                xml_declaration=True)
    print('深入图已生成：', sum(map(len, base.FIGURES.values())))


if __name__ == '__main__':
    main()
