"""重绘课程专项图；仅输出图片与图源，不写笔记或 PDF。"""
from pathlib import Path
import json
import importlib.util
import xml.etree.ElementTree as ET
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np
ASSETS = Path(__file__).resolve().parents[1]
renderer_path = (Path.home() / '.codex' / 'skills' / 'diagramry' /
                 'scripts' / 'render_diagram.py')
spec = importlib.util.spec_from_file_location('diagram_renderer', renderer_path)
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)
plt.rcParams.update({'font.sans-serif': ['Microsoft YaHei'],
                     'axes.unicode_minus': False, 'font.size': 12,
                     'svg.fonttype': 'none', 'figure.facecolor': 'white'})
BLUE, ORANGE, GREEN, RED = '#2563a6', '#cd7516', '#25835b', '#c84848'
INK, PALE = '#25374b', '#edf5fd'
FIGURES = {}
DRAWIOS = {}


def save(cid, slug, fig, title, explanation):
    """保存双格式图片和每图解释。"""
    folder = ASSETS / cid
    folder.mkdir(parents=True, exist_ok=True)
    fig.suptitle(title, fontsize=17, color=INK, y=.99)
    fig.tight_layout(rect=(0, 0, 1, .94), pad=1.6)
    for ext in ('svg', 'png'):
        fig.savefig(folder / f'{slug}.{ext}', dpi=145,
                    bbox_inches='tight', facecolor='white')
    plt.close(fig)
    FIGURES.setdefault(cid, []).append((slug, title, explanation))

def axis_clean(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.grid(axis='x', alpha=.15)

def wave(ax, times, levels, label, color=BLUE):
    ax.step(times, levels, where='post', color=color, lw=2.2)
    ax.set_ylim(-.25, 1.5)
    ax.set_yticks([0, 1], ['低', '高'])
    ax.set_ylabel(label, rotation=0, labelpad=32)
    axis_clean(ax)

def panel(cid, slug, title, rows, explanation, columns=None):
    """并列表格图，不用箭头误导概念之间的因果关系。"""
    fig, ax = plt.subplots(figsize=(11, max(3.6, len(rows)*.62+1.5)))
    ax.axis('off')
    tab = ax.table(cellText=rows, colLabels=columns,
                   loc='center', cellLoc='center')
    tab.auto_set_font_size(False)
    tab.set_fontsize(12)
    tab.scale(1, 2.35)
    for (r, c), cell in tab.get_celld().items():
        cell.set_edgecolor('white')
        cell.set_facecolor('#dceafa' if r == 0 else
                           ('#f0f5fa' if r % 2 else '#fafcff'))
    save(cid, slug, fig, title, explanation)

def memory_map(cid, slug, title, labels, explanation):
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.axis('off')
    for i, (head, body, color) in enumerate(labels):
        x = i * 3.5
        ax.add_patch(Rectangle((x, 0), 3.15, 2.2,
                     facecolor=color, edgecolor=BLUE, lw=1.4))
        ax.text(x+1.575, 1.7, head, ha='center', fontsize=14,
                fontweight='bold', color=INK)
        ax.text(x+1.575, .8, body, ha='center', va='center',
                fontsize=12, linespacing=1.6)
    ax.set(xlim=(-.2, len(labels)*3.5-.2), ylim=(-.2, 2.5))
    save(cid, slug, fig, title, explanation)

def make_specials():
    memory_map('01', 'memory', '同一个地址空间中，三类位置做不同的事', [
      ('Flash', '0x08000000 起\n程序、常量\n掉电保留', '#eaf3ff'),
      ('SRAM', '0x20000000 起\n变量、栈、堆\n普通 SRAM 掉电不保留', '#eaf7ef'),
      ('外设区域', '0x40000000 区域\n配置、状态、数据\n读写可能触发硬件动作', '#fff3df')],
      '三块并排表示地址空间中的不同区域，不是执行先后。先定位地址属于哪一区，再判断读写的含义；具体容量和边界按完整型号确认。')
    panel('01', 'boot', 'F103 启动选择：先选来源，再执行启动代码',
      [['0', '任意', '用户 Flash'], ['1', '0', '系统存储器'],
       ['1', '1', 'SRAM']],
      '先读 BOOT0，再在需要时读 BOOT1。选择启动源并不等于已经完成时钟和 C 运行环境初始化。此表针对课件 F1。',
      ['BOOT0', 'BOOT1', '启动来源'])
    panel('02', 'faults', '根据报错发生阶段，缩小排查范围',
      [['编译', '头文件找不到', 'Include Path / 文件名'],
       ['链接', '未定义符号', '实现 .c / 库 / 条件编译'],
       ['下载', '无法写入', '连接 / 算法 / 保护 / 地址'],
       ['运行', '进不了 main', '启动 / 时钟 / 异常 / 产物']],
      '从左往右看阶段、现象、检查项。先找到失败所在阶段，再检查该阶段的输入条件。',
      ['阶段', '例子', '优先检查'])
    memory_map('02', 'files', '文件名不同，是因为承担的工具链职责不同', [
      ('.h', '声明、类型、宏\n解决“如何调用”\n不自动提供实现', '#eaf3ff'),
      ('.c / .s', '函数与启动实现\n参与编译/汇编\n形成目标文件', '#eaf7ef'),
      ('.axf / .hex', '链接或导出产物\n用于调试/下载\n对应同一次构建', '#fff3df')],
      '头文件与实现文件各有责任。修改了源码后，旧 HEX 不会自动随之改变；应重新构建并核对下载产物。')
    fig, axs = plt.subplots(2, 1, figsize=(11, 5), sharex=True)
    t = [0, 10, 10.8, 11.5, 12.1, 12.8, 30, 31, 31.6, 32, 45]
    wave(axs[0], t, [1,0,1,0,1,0,0,1,0,1,1], '原始输入')
    wave(axs[1], [0,18,38,45], [1,0,1,1], '稳定状态', GREEN)
    axs[0].set_title('上拉按键接地的示例：一次按下可能有多个边沿')
    axs[1].set_xlabel('时间 / ms（示意，稳定确认策略依应用设定）')
    save('03', 'debounce', fig, '电平变化 → 消抖确认 → 一次按下事件',
      '先看上面的快速跳变，再看下面稳定后的状态。确认从松开变为按下时发布一次事件；不要每读到一次低电平就加一次按下计数。图中延时只是示意。')
    panel('03', 'drive', '同样写 0/1，推挽与开漏的物理动作不同',
      [['推挽', '主动拉低', '主动拉高'], ['开漏', '主动拉低', '释放，由上拉/外部电路决定高低']],
      '按“模式 → 写入值 → 物理动作”阅读。开漏释放时若没有合适上拉，不能保证读到高。输入电压容限仍需查器件数据手册。',
      ['模式', '输出控制写 0', '输出控制写 1'])
    fig, ax = plt.subplots(figsize=(11, 4))
    for y, spans, color, name in [(0,[(0,2),(7,3)],GREEN,'主程序'),
        (1,[(2,2),(6,1)],BLUE,'低优先级 ISR'),
        (2,[(4,2)],ORANGE,'更高抢占优先级 ISR')]:
        ax.broken_barh(spans,(y,.55),facecolors=color)
    ax.set(yticks=[.27,1.27,2.27],yticklabels=['主程序','低 ISR','高 ISR'],
           xlabel='执行时间（示意）',xlim=(0,10),ylim=(-.2,3))
    axis_clean(ax)
    save('04', 'preempt', fig, '抢占：高 ISR 完成后，先恢复被打断的低 ISR',
      '沿横轴看：主程序 → 低 ISR → 高 ISR → 低 ISR 剩余部分 → 主程'
          '序。只有抢占优先级满足条件才这样嵌套；子优先级不能单独实现这一效果。')
    panel('04','vectors','向量表：存入口地址的位置，与入口地址本身不同',
      [['基址 + 0', '初始 MSP 值', '初始化主栈'],
       ['基址 + 4', '复位处理地址', '进入 Reset_Handler'],
       ['基址 + 4 × 向量号', '相应处理地址', '异常响应时定位 ISR']],
      '第一列是表项地址，第二列是该地址中存的值，第三列是用途。外部 IRQ 的向量号一般为'
          ' IRQn + 16；VTOR 移动表的位置不会自动重装 MSP。',
      ['表项位置', '内容', '作用'])
    fig, axs=plt.subplots(1,2,figsize=(11,4))
    v=np.linspace(0,3.3,500)
    axs[0].plot(v,np.minimum(np.floor(v/3.3*4096),4095),color=BLUE)
    axs[0].set(xlabel='输入电压 / V',ylabel='12 位码值',title='全范围（理想示意）')
    v=np.linspace(1.648,1.654,400)
    axs[1].step(v,np.floor(v/3.3*4096),where='post',color=ORANGE)
    axs[1].set(xlabel='输入电压 / V',ylabel='码值',title='放大后看到量化台阶')
    for a in axs: axis_clean(a)
    save('05','quantize',fig,'ADC 把连续电压分成离散码值',
      '左图看全范围，右图看局部台阶。以 3.3 V、12 位为例，一步约 0.806 mV；图未包含噪声、偏移和增益误差，不能当作实测精度。')
    panel('05','dma-order','固定外设地址 + 递增内存地址，形成一轮数据',
      [['1','CH2','ADC_DR','samples[0]'], ['2','CH5','ADC_DR','samples[1]'],
       ['3','CH8','ADC_DR','samples[2]']],
      '按行看采样顺序：rank 是序列位置，CH 是物理通道号，数组下标按搬运顺序。三者不'
          '是天然相等；DMA 完整帧完成后才能按一致性策略交给消费者。',
      ['rank','示例通道','DMA 源','DMA 目的'])
    make_timer()
    fig,axs=plt.subplots(2,1,figsize=(11,5),sharex=True)
    t=np.arange(0,2401)
    wave(axs[0],t,((t%1000)<300).astype(int),'输入 PWM')
    axs[1].plot(t,t%1000,color=BLUE)
    axs[1].scatter([300,1000,1300,2000],[300,0,300,0],color=ORANGE,zorder=4)
    axs[1].set(ylabel='CNT',xlabel='时间 / μs',yticks=[0,300,1000])
    axis_clean(axs[1])
    save('07','pwmi',fig,'PWMI 示例：下降沿记录高电平，上升沿界定周期',
      '假设计数频率 1 MHz，周期 1000 μs、高电平 300 μs。复位从模式使 '
          'CNT 在上升沿复位；用于周期的捕获保存复位前的值。图中回零后的点不代表周期捕获等于'
          '零。')
    fig,axs=plt.subplots(2,1,figsize=(11,4.4),sharex=True)
    t=np.arange(0,9,.01)
    wave(axs[0],t,((t%4)<2).astype(int),'A')
    wave(axs[1],t,(((t-1)%4)<2).astype(int),'B',ORANGE)
    axs[1].set_xlabel('相位时间（示意）')
    save('07','encoder',fig,'编码器：两路相位次序帮助判断运动方向',
      '先看 A 的边沿，再看当时 B 的状态。反转时领先/滞后关系改变；实际正方向由接线和软件约定决定。不能只凭这张图就确定机械正转。')
    fig,ax=plt.subplots(figsize=(12,3.4))
    bits=[0]+[(0x41>>i)&1 for i in range(8)]+[1]
    times=[-1]+list(range(11))
    wave(ax,times,[1]+bits+[1],'TX')
    for i,b in enumerate(bits):
        ax.text(i+.5,1.23,('起始' if i==0 else '停止' if i==9
                else f'D{i-1}={b}'),ha='center',fontsize=11)
        ax.axvline(i,color='gray',alpha=.2)
    ax.set(xlabel='位时间（9600 bit/s 时每位约 104.17 μs）',xlim=(-1,11))
    save('08','uart-frame',fig,'0x41 的 8N1 波形：数据低位先发送',
      '从起始位向右数：0，然后 D0～D7 为 1、0、0、0、0、0、1、0，最后停止位为 1。数据只占八位，线上一帧共十位。')
    panel('08','bytes','字节、数值、字符和字符串的区别',
      [['单字节 0x41','41','可显示 A','1'],['字符串 "41"','34 31','字符 4 和 1','2'],
       ['数值 123 的文本','31 32 33','字符 1、2、3','3']],
      '先看线上实际 Hex 字节，再看显示解释。同一个数值可以用二进制字段或文本编码传输，接收端必须遵守约定。',
      ['输入含义','实际字节（Hex）','文本解释','字节数'])
    fig,ax=plt.subplots(figsize=(11,5))
    for s in range(16):
        for b in range(4):
            color='#fde5d7' if b==3 else '#eaf3ff'
            if s==0 and b==0: color='#d6e9db'
            ax.add_patch(Rectangle((b,15-s),.95,.88,facecolor=color,
                edgecolor='white'))
            ax.text(b+.475,15-s+.44,str(s*4+b),ha='center',va='center',
                fontsize=10)
    ax.set(xlim=(0,4),ylim=(0,16),xticks=[.475,1.475,2.475,3.475],
      xticklabels=['数据/厂商块','数据块','数据块','扇区控制块'],
      yticks=[15.44,10.44,5.44,.44],yticklabels=['扇区 0','扇区 5','扇区 10','扇区 15'])
    ax.tick_params(length=0)
    for spine in ax.spines.values():spine.set_visible(False)
    save('09','s50-map',fig,'S50：16 个扇区 × 4 块 × 16 字节',
      '格子里的数字是全局块号，右列是每个扇区的控制块；绿色块 0 是厂商相关块。按颜色先排除特殊用途块，再规划业务数据。')
    panel('09','transaction','扣款超时：必须区分“未执行”和“结果未知”',
      [['认证失败','尚未进入扣款','修正条件后重试'],
       ['发送前失败','确认没有请求到卡片','按状态恢复'],
       ['执行后应答丢失','结果未知','先读回/核对事务，再决定']],
      '同样是“没有成功应答”，处理可能不同。不要把结果未知统一转换成未执行，盲目重发可能重复扣减。',
      ['场景','当前证据','下一步'])
    panel('10','packet','课件广播帧：长度字段的计算范围需要读清楚',
      [['F1 DD','帧头','2'],['0A','后续十字节','1'],['00 05','源地址','2'],
       ['FF FF','广播目标','2'],['11 22 33 44','数据','4'],['0D 0A','帧尾','2']],
      '长度 0A 之后共有 2+2+4+2=10 字节，整帧共十三字节。这是课件模块协议示例，不是所有蓝牙的公共帧格式。',
      ['字节（Hex）','含义','该字段字节数'])
    memory_map('10','network','相同业务消息经过三个不同层次',[
      ('UART', '9600 等参数\n只约束本地串口\n先验证收发', '#eaf3ff'),
      ('无线网络', 'NETID / 节点地址\n模式与固件\n决定可达性', '#eaf7ef'),
      ('应用层', '命令与参数\n序号与应答\n决定业务结果', '#fff3df')],
      '三层都正确才有机会完成一次业务。模块串口回 OK，不能替代远端业务应答。')
    fig,ax=plt.subplots(figsize=(10,5));ax.axis('off')
    pts=[(0,0),(2,1),(2,-1),(4,1.7),(4,.3),(4,-1)]
    edges=[(0,1),(0,2),(1,3),(1,4),(2,5),(1,2)]
    for a,b in edges:ax.plot([pts[a][0],pts[b][0]],[pts[a][1],pts[b][1]],
        color='#9baec3',lw=2,zorder=1)
    for i,(x,y) in enumerate(pts):
        ax.scatter([x],[y],s=2800,
            color=('#d9eaff' if i==0 else
                   '#e4f3e9' if i<3 else '#fff0d8'),zorder=2)
        ax.text(x,y,'协调器' if i==0 else f'路由 {i}' if i<3 else f'终端 {i-2}',
            ha='center',va='center',zorder=3)
    ax.set(xlim=(-.8,4.8),ylim=(-1.8,2.5))
    save('11','topology',fig,'ZigBee 示意网络：转发节点与终端角色分开',
      '左侧协调器建立网络，中间路由器提供转发，右侧终端通过父节点接入。连接线仅示意可用关联/链路，不代表每条应用消息都沿固定路线传递。')
    panel('11','rate','250 kbit/s 是链路尺度，业务吞吐还需扣除开销',
      [['物理速率','250000 bit/s','约 31250 byte/s 的位换算上界'],
       ['协议与竞争','帧头、应答、退避','降低有效负载比例'],
       ['多跳与重试','占用额外空口时间','增加时延并降低吞吐']],
      '第一行只是单位换算，不是应用吞吐保证。多节点和无线干扰会进一步改变实际表现。',
      ['层次','内容','含义'])
    make_i2c_spi()
    panel('14','layout','C8 的 64 KiB Flash：地址计算与布局保留分开',
      [['0x08000000','Flash 起始','应用程序起点示例'],
       ['0x0800FC00','最后 1 KiB 页开始','候选数据页，必须链接保留'],
       ['0x0800FFFF','64 KiB 最后字节','标称范围末尾']],
      '这些是标称容量的地址计算。是否可以把末页拿来存参数，必须核对实际链接布局，图不构成已为当前工程保留空间的证据。',
      ['地址','含义','使用限制'])
    panel('14','bits','Flash 位变化：擦除与编程的方向不同',
      [['擦除后','FF = 11111111','整页恢复 1'],
       ['编程数据','F0 = 11110000','允许把选定位 1→0'],
       ['再想写 FF','不能直接恢复低四位','需要擦除相应页']],
      '从上向下看一次变化。一个变量要恢复成更大的数值，并不一定能直接再次编程；需按位判断并考虑整页其他数据。',
      ['步骤','示例字节','物理约束'])
    memory_map('15','clock','RTC 的三层表示：时钟、秒数、日历',[
      ('硬件节拍', '32768 Hz ÷ 32768\nPRL = 32767\n得到 1 Hz', '#eaf3ff'),
      ('计数基准', '每秒加一\n保存秒数\n初始化/校时可修改', '#eaf7ef'),
      ('日历显示', '软件转换年月日\n选择 UTC 或 UTC+8\n计数本身不重复偏移', '#fff3df')],
      '先由硬件得到秒，再由软件解释成日历。改变显示时区与校准硬件计数是两项不同操作。')
    panel('15','timezone','一个时刻可以有两种日历显示',
      [['0','1970-01-01 00:00:00','1970-01-01 08:00:00'],
       ['3600','1970-01-01 01:00:00','1970-01-01 09:00:00']],
      '每一行描述同一个时间点，第二、三列只是不同显示时区。先约定存储的是 UTC 秒数，再统一处理显示与输入转换。',
      ['Unix 秒数','UTC 显示','UTC+8 显示'])
    panel('16','modes','F103 低功耗：先比较保留内容与恢复路径',
      [['Sleep','保留','外设可运行','通常继续执行'],
       ['Stop','保留','主要高速时钟停止','先恢复所需时钟'],
       ['Standby','普通 SRAM 丢失','主域停止','复位路径重新启动']],
      '按列比较模式，不能只记功耗大小。RTC/BKP 是否继续取决于后备域供电和时钟；外设能否唤醒还需查对应模式的允许来源。',
      ['模式','普通 SRAM','时钟/供电特征','恢复重点'])
    panel('16','wake','睡前与醒后各有必须完成的工作',
      [['睡前','完成通信/存储事务','配置唤醒源并处理标志'],
       ['进入','设置 SLEEPDEEP/PWR 等','执行 WFI/WFE'],
       ['醒后','识别唤醒或复位原因','恢复时钟→外设→业务']],
      '从上向下看执行过程。WFI/WFE 是等待指令，模式取决于控制位；Stop 唤醒和 Standby 重启的恢复流程不同。',
      ['阶段','动作一','动作二'])
    make_rtos()

def structured(cid, slug, title, boxes, arrows, labels, explanation):
    """同一套节点/连线同时输出 SchemDraw 和 draw.io。"""
    items=[]
    page=ET.SubElement(DRAWIOS[cid],'diagram',id=slug,name=title)
    model=ET.SubElement(page,'mxGraphModel',page='1',
                        pageWidth='1400',pageHeight='850')
    root=ET.SubElement(model,'root')
    ET.SubElement(root,'mxCell',id='0')
    ET.SubElement(root,'mxCell',id='1',parent='0')
    def geo(cell,x,y,w,h):
        ET.SubElement(cell,'mxGeometry',x=str(50+x*90),
                      y=str(450-y*90-h*90),width=str(w*90),
                      height=str(h*90),attrib={'as':'geometry'})
    items.append({'kind':'text','xy':[5.5,4.3],'text':title,
                  'fontsize':17,'color':INK,'align':['center','center']})
    for i,(x,y,w,h,label) in enumerate(boxes):
        fill=['#eaf3ff','#eaf7ef','#fff3df'][i%3]
        items.append({'kind':'rect','xy':[x,y],'w':w,'h':h,
          'label':label,'fill':fill,'color':INK,'fontsize':14,
          'min_fontsize':8,'lw':1.3})
        cell=ET.SubElement(root,'mxCell',id=f'b{i}',vertex='1',parent='1',
           value=label,style='whiteSpace=wrap;html=0;fontFamily=Microsof'
               't YaHei;'
           f'fontSize=20;fillColor={fill};strokeColor={BLUE};')
        geo(cell,x,y,w,h)
    for i,pts in enumerate(arrows):
        items.append({'kind':'arrow','points':pts,'color':BLUE,'lw':1.4})
        cell=ET.SubElement(root,'mxCell',id=f'e{i}',edge='1',parent='1',
            style=f'endArrow=classic;strokeColor={BLUE};strokeWidth=2;')
        g=ET.SubElement(cell,'mxGeometry',relative='1',attrib={'as':'geometry'})
        ET.SubElement(g,'mxPoint',x=str(50+pts[0][0]*90),
                     y=str(450-pts[0][1]*90),attrib={'as':'sourcePoint'})
        ET.SubElement(g,'mxPoint',x=str(50+pts[-1][0]*90),
                     y=str(450-pts[-1][1]*90),attrib={'as':'targetPoint'})
        if len(pts)>2:
            array=ET.SubElement(g,'Array',attrib={'as':'points'})
            for x,y in pts[1:-1]:
                ET.SubElement(array,'mxPoint',x=str(50+x*90),y=str(450-y*90))
    for i,(x,y,text) in enumerate(labels):
        items.append({'kind':'text','xy':[x,y],'text':text,
            'fontsize':12,'color':INK,'align':['center','center']})
        cell=ET.SubElement(root,'mxCell',id=f't{i}',vertex='1',parent='1',
             value=text,style='text;html=0;align=center;verticalAlign=middle;'
                    'whiteSpace=wrap;fontSize=18;strokeColor=no'
                        'ne;fillColor=none;')
        geo(cell,x-1.5,y-.3,3,.6)
    data={'type':'shapes','output':{'canvas':'svg','dpi':165,'theme':
          {'bgcolor':'white','font':'Microsoft YaHei','color':INK}},
              'items':items}
    stem=ASSETS/cid/slug
    stem.with_suffix('.json').write_text(json.dumps(data,
        ensure_ascii=False,indent=2),'utf-8')
    for ext in ('svg','png'):
        path=stem.with_suffix('.'+ext)
        d=renderer.drawing_from_output(data,path)
        renderer.render_shapes(d,data);renderer.save_drawing(d,data,path)
        plt.close('all')
    FIGURES[cid].append((slug,title,explanation))

def make_connections():
    structured('01','mcu-chain','输入、程序与输出在 MCU 内怎样协作',[
      (0,0,2.4,1.3,'输入外设\nGPIO / ADC'),
      (4,0,2.4,1.3,'CPU\n执行程序'),
      (8,0,2.4,1.3,'输出外设\nGPIO / TIM'),
      (4,2.6,2.4,1.2,'Flash\n保存指令与常量'),
      (4,-2.5,2.4,1.2,'SRAM\n保存运行变量')],
      [[[2.4,.65],[4,.65]],[[6.4,.65],[8,.65]],
       [[5.2,2.6],[5.2,1.3]],[[4.7,0],[4.7,-1.3]],
       [[5.7,-1.3],[5.7,0]]],
      [(1.2,-.5,'外部电压/数据'),(9.2,-.5,'控制负载/发出数据')],
      '先横向看输入到输出，再看 Flash 提供程序、SRAM 保存现场。箭头表示概念上的数据/指令关系，省略了真实总线矩阵和仲裁。')
    structured('03','open-drain','开漏的“高”是释放：电压由外部电路建立',[
      (4,2.7,2.4,1,'VDD'),(4,.8,2.4,1,'上拉电阻 R'),
      (4,-1.1,2.4,1,'引脚节点\n接输入缓冲'),
      (0,-3.3,3,1.2,'输出低：开关闭合\n引脚可被拉向 GND'),
      (8,-3.3,3,1.2,'输出高：开关断开\n本设备释放引脚')],
      [[[5.2,2.7],[5.2,1.8]],[[5.2,.8],[5.2,-.1]],
       [[4,-.5],[1.5,-.5],[1.5,-2.1]],
       [[6.4,-.5],[9.5,-.5],[9.5,-2.1]]],[],
      '上方上拉提供变高的路径，下方两张框表示同一输出级的两种状态。释放后若别的设备仍拉低，节点仍为低；这是一幅开关等效图，不代表实际板卡接线。')
    structured('04','exti-map','同号引脚经过选择，映射到一条 EXTI 线',[
      (0,2.2,2.2,1,'PA0'),(0,.4,2.2,1,'PB0'),(0,-1.4,2.2,1,'其他端口的 0 号脚'),
      (4,.4,2.8,1.2,'AFIO 选择器\n只选一路来源'),
      (8,.4,2.6,1.2,'EXTI0\n边沿与挂起')],
      [[[2.2,2.7],[3.2,2.7],[3.2,1.3],[4,1.3]],
       [[2.2,.9],[4,.9]],[[2.2,-.9],[3.2,-.9],[3.2,.6],[4,.6]],
       [[6.8,1],[8,1]]],[(9.3,-.5,'再经 NVIC 到 CPU')],
      '三路箭头表示候选输入，不是同时启用的三路信号。同一条 EXTI0 由 AFIO 选择一个端口来源，再做触发和挂起判断。')
    structured('05','dma-ring','循环 DMA 与 CPU 读取必须划分一致的数据块',[
      (0,.3,2.3,1.4,'ADC_DR\n固定源地址'),
      (4,1.9,2.6,1.2,'缓冲前半区\nDMA 填写'),
      (4,-1.2,2.6,1.2,'缓冲后半区\nDMA 继续填写'),
      (8,.3,2.8,1.4,'CPU 消费\n读取已完成区')],
      [[[2.3,1],[3,1],[3,2.5],[4,2.5]],
       [[5.3,1.9],[5.3,0]],
       [[4,-.6],[3,-.6],[3,2],[4,2]],
       [[6.6,2.5],[7.3,2.5],[7.3,1.3],[8,1.3]],
       [[6.6,-.6],[7.3,-.6],[7.3,.6],[8,.6]]],
      [(5.3,-2.2,'半传输/全传输标记完成区；消费不能落后到被覆盖')],
      '沿左侧看固定地址的数据不断搬进内存，沿上下看两块轮换。CPU 读取已完成块时，DMA 应在另一块写；半/全完成机制并不自动防止消费者过慢。')
    structured('08','parser','串口状态机：正常路径与错误恢复路径都要有',[
      (0,1.6,2.3,1.3,'等待帧头'),(4,1.6,2.3,1.3,'检查长度'),
      (8,1.6,2.3,1.3,'接收负载'),(8,-1.1,2.3,1.3,'检查帧尾/校验'),
      (4,-1.1,2.3,1.3,'发布完整消息'),(0,-1.1,2.3,1.3,'错误或超时\n清理本帧状态')],
      [[[2.3,2.25],[4,2.25]],[[6.3,2.25],[8,2.25]],
       [[9.15,1.6],[9.15,.2]],[[8,-.45],[6.3,-.45]],
       [[5.15,-1.1],[5.15,-2.1],[1.15,-2.1],[1.15,1.6]],
       [[1.15,.2],[1.15,1.6]]],
      [(5.15,.65,'任一接收阶段出错/超时 → 左下恢复')],
      '从左上顺时针看正常接收路径。错误与半帧超时都要回到可接收新帧的状态；图中的发布表示交给业务层，不表示 ISR 中直接执行慢业务。')
    structured('10','unicast','单播与广播：收件范围不同，业务确认仍要设计',[
      (0,.6,2.5,1.4,'发送节点\n短地址 0005'),
      (4,2.2,2.6,1.2,'节点 0004'),(4,-1.1,2.6,1.2,'其他网络节点'),
      (8,.6,2.9,1.4,'单播：指定地址\n广播：FFFF\n课件模块示例')],
      [[[2.5,1.5],[3.2,1.5],[3.2,2.8],[4,2.8]],
       [[2.5,1],[3.2,1],[3.2,-.5],[4,-.5]]],
      [(1.3,-1,'同一网络内'),(5.3,.8,'单播只指定目标；\n广播面向规定范围')],
      '两路箭头用于比较收件范围：单播选择特定目标，广播可能面向多个节点。图不表示所有节点都已收到；无线可达性、睡眠和协议处理仍会影响结果。')
    structured('12','wired-and','I2C 的线与关系：任意一方拉低，总线就是低',[
      (4,2.6,2.6,1,'VDD → 上拉'),
      (4,.3,2.6,1.2,'SDA 总线节点'),
      (0,-2.2,2.8,1.3,'主机输出\n拉低或释放'),
      (8,-2.2,2.8,1.3,'从机输出\n拉低或释放')],
      [[[5.3,2.6],[5.3,1.5]],
       [[4,.9],[1.4,.9],[1.4,-.9]],
       [[6.6,.9],[9.4,.9],[9.4,-.9]]],
      [(5.4,-2,'双方都释放 → 高\n任何一方拉低 → 低')],
      '把节点看成共享的一根线。主机发完八位后释放 SDA，从机才可以在第九拍用拉低表示 ACK；不能用推挽强拉高与对方低电平对抗。')
    structured('14','flash-pages','独立参数页必须从链接布局中保留出来',[
      (2,2.5,7.3,1,'Flash 起始 0x08000000'),
      (2,.3,7.3,1.8,'程序 / 常量 / 其他已分配区域\n边界由实际链接布局决定'),
      (2,-1.7,7.3,1.2,'候选末页 0x0800FC00～0x0800FFFF\n只有明确独立保留后才能作为参数区')],
      [[[1,3],[1,-1.5]]],[(1,-2.1,'地址增大'),(5.65,-3,
          'F103C8 标称 64 KiB；示意图不是当前工程的链接证据')],
      '自上向下读地址。数据区需要链接器和程序共同约定，不能仅凭这张地址示意就执行擦除。参数更新影响整页，需保护同页内容与掉电恢复。')
    structured('15','backup-domain','RTC 保持：后备域电源与 LSE 时钟缺一不可',[
      (0,2,2.5,1.2,'主电源 VDD'),(0,-.5,2.5,1.2,'后备电源 VBAT'),
      (4,.7,2.8,1.5,'后备域\n电源切换与保持'),
      (8,2,2.7,1.2,'RTC / BKP'),(8,-.5,2.7,1.2,'LSE\n低速晶振路径')],
      [[[2.5,2.6],[3.2,2.6],[3.2,1.8],[4,1.8]],
       [[2.5,.1],[3.2,.1],[3.2,1],[4,1]],
       [[6.8,1.5],[7.4,1.5],[7.4,2.6],[8,2.6]],
       [[9.35,.7],[9.35,2]]],
      [(5.4,-1.4,'供电保留 + 有效时钟 + 不被重置 → 才能持续走时')],
      '左边看供电来源，右边看 RTC 还需要时钟。图表示功能依赖而非完整电路；备份域复位或无条件重新设置计数仍会破坏连续走时。')
    structured('16','stop-return','Stop 唤醒后：时钟恢复先于依赖它的业务',[
      (0,1.7,2.6,1.2,'确认通信/存储完成'),
      (4,1.7,2.6,1.2,'配置唤醒源\n进入 Stop'),
      (8,1.7,2.6,1.2,'有效事件唤醒\nF1 先使用 HSI'),
      (8,-1.3,2.6,1.3,'恢复 HSE / PLL\n等待就绪'),
      (4,-1.3,2.6,1.3,'恢复时钟配置\n检查接口参数'),
      (0,-1.3,2.6,1.3,'恢复业务\n发布有效状态')],
      [[[2.6,2.3],[4,2.3]],[[6.6,2.3],[8,2.3]],
       [[9.3,1.7],[9.3,0]],[[8,-.65],[6.6,-.65]],
       [[4,-.65],[2.6,-.65]]],[],
      '从左上沿箭头读一整次睡眠过程。唤醒后恢复哪些时钟由应用决定；等待就绪也必须有超时与降级处理，不能无期限停在恢复流程。')
    structured('17','task-states','任务状态：就绪只是获得运行资格',[
      (0,1.6,2.6,1.3,'就绪 Ready'),(4,1.6,2.6,1.3,'运行 Running'),
      (8,1.6,2.6,1.3,'阻塞 Blocked'),(4,-1.4,2.6,1.3,'挂起 Suspended')],
      [[[2.6,2.5],[4,2.5]],[[4,1.95],[2.6,1.95]],
       [[6.6,2.25],[8,2.25]],
       [[9.3,2.9],[9.3,3.6],[1.3,3.6],[1.3,2.9]],
       [[4.8,1.6],[4.8,-.1]],
       [[5.8,-.1],[5.8,.5],[1.3,.5],[1.3,1.6]]],
      [(3.3,3.1,'调度'),(3.3,1.35,'抢占/让出'),
       (7.3,1.35,'延时/等待'),(5.3,3.8,'时间到/事件满足 → 就绪'),
       (6.5,-2.2,'挂起后需恢复；图省略删除与部分转换')],
      '先看上排：运行任务等待资源或延时后阻塞，条件满足回到就绪，再由调度器决定何时运行。挂起是另一种受控状态，resume 不能代替可靠事件计数。')
    fig,axs=plt.subplots(2,1,figsize=(12,5.8),sharex=True)
    # 低任务已持锁，高任务在时刻 1 请求；中任务在时刻 2 就绪。
    for ax,spans in zip(axs,[[(0,1,GREEN),(1,1,GREEN),(2,4,BLUE),(6,1,
        GREEN),(7,1,ORANGE)],
                            [(0,1,GREEN),(1,2,GREEN),(3,1,ORANGE),(4,4,BLUE)]]):
        for x,w,c in spans:ax.broken_barh([(x,w)],(0,.65),facecolors=c)
        ax.set(ylim=(-.3,1.6),yticks=[],xlim=(0,8));axis_clean(ax)
        ax.axvline(1,color=RED,ls='--');ax.text(1,1.05,'高任务请求锁并阻塞',
            color=RED,fontsize=10)
    axs[0].set_title('无继承示意：中任务先运行，低任务更晚释放锁')
    axs[1].set_title('有继承示意：低任务临时提高优先级，完成后释放锁')
    axs[1].set_xlabel('时间（示意）；绿色=低任务持锁工作，蓝色=中任务，橙色=高任务')
    save('17','inheritance',fig,'优先级继承：让持锁者尽早完成并释放资源',
      '高任务在时刻 1 需要低任务持有的锁。无继承时，中任务可进一步推迟低任务；互斥锁继承'
          '高优先级后，低任务较早完成释放。图为简化单锁示例，继承不能消除持锁过久或所有死锁问题'
          '。')

def make_timer():
    fig,axs=plt.subplots(2,1,figsize=(11,4.7),sharex=True)
    t=np.arange(0,20.01,.02)
    wave(axs[0],t,((t%1)<.5).astype(int),'输入时钟')
    axs[1].step(range(21),[i//4 for i in range(21)],where='post',
        color=GREEN,lw=2.3)
    axs[1].set(ylabel='CNT',xlabel='输入时钟周期数',yticks=range(6));axis_clean(axs[1])
    save('06','divider',fig,'缩小示例：PSC = 3，每四个输入时钟 CNT 才加一',
      '先数上方四个完整时钟周期，再看下方 CNT 增加一步。真实 72 MHz 分频 72'
          ' 时，PSC 应为 71，得到 1 MHz，也就是每步 1 μs；仍需 ARR = '
          '999999 才能直接组成一秒，但它超出普通 16 位定时器范围，通常改用 PSC '
          '= 7199、ARR = 9999。')
    fig,ax=plt.subplots(figsize=(11,3.8));t=np.arange(21)
    ax.step(t,t%10,where='post',lw=2.6,color=BLUE)
    ax.set(xlabel='计数节拍序号',ylabel='CNT',yticks=range(10),xticks=range(0,21,2))
    for x in (10,20): ax.axvline(x,color=RED,ls='--')
    ax.text(10,.5,'  更新/回零',color=RED);axis_clean(ax)
    save('06','cnt',fig,'ARR = 9：0～9 共十格，每一格都保持一个节拍',
      '横向看台阶宽度：CNT = 9 也占一整格，下一拍回 0。周期是 (ARR + 1) / fCNT，不是 ARR / fCNT。')
    fig,axs=plt.subplots(2,1,figsize=(11,5.2),sharex=True);t=np.arange(0,2001)
    cnt=(t%1000)//100
    axs[0].step(t,cnt,where='post',color=BLUE,lw=2);axs[0].axhline(3,
        color=ORANGE,ls='--',label='CCR = 3')
    axs[0].set(ylabel='CNT',
        yticks=range(10));axs[0].legend(loc='upper right');axis_clean(axs[0])
    wave(axs[1],t,(cnt<3).astype(int),'输出 PWM',GREEN)
    axs[1].set_xlabel('时间 / μs（fCNT = 10 kHz，ARR = 9）')
    save('06','compare',fig,'PWM1、向上计数、有效高：CNT < CCR 时输出高',
      '两幅图共享横轴：0、1、2 三格输出高，CNT 到 3 时转低，走到周期边界才重新变'
          '高。CCR 不是让 CNT 清零的命令。此图周期 1 ms、高电平 0.3 ms，占'
          '空比 30%。')
    fig,axs=plt.subplots(5,1,figsize=(11,8),sharex=True);t=np.arange(0,2001)
    for ax,ccr in zip(axs,[0,3,5,7,10]):
        wave(ax,t,((t%1000)//100<ccr).astype(int),f'CCR={ccr}',BLUE)
        ax.text(2020,.6,f'{ccr*10}%',color=GREEN,fontsize=13)
    axs[-1].set_xlabel('时间 / μs；ARR=9、fCNT=10 kHz，五行周期相同')
    save('06','duty',fig,'只改 CCR，比较 0%、30%、50%、70%、100% 占空比',
      '纵向比较高电平宽度，再横向比较周期边界。100% 需要 CCR = ARR + 1 '
          '且该值能被 CCR 表示；当 ARR 已是寄存器最大值时不能直接写入最大值加一。')
    fig,axs=plt.subplots(3,1,figsize=(11,6),sharex=True);t=np.arange(0,301)
    pre=np.where(t<55,3,7);active=np.where(t<100,3,7)
    for ax,val,label in zip(axs[:2],[pre,active],['预装载 CCR','当前有效 CCR']):
        ax.step(t,val,where='post',color=BLUE,lw=2);ax.set(ylabel=label,
            yticks=[3,7],ylim=(0,9));axis_clean(ax)
    wave(axs[2],t,((t%100)//10<active).astype(int),'PWM',GREEN)
    for a in axs:
        a.axvline(55,color=ORANGE,ls=':');a.axvline(100,color=RED,ls='--')
    axs[0].set_title('55 时写入 7；100 的周期更新使新值生效（示意）')
    axs[2].set_xlabel('时间单位；本例每周期 100 单位')
    save('06','preload',fig,'开启 CCR 预装载：写入时刻与比较值生效时刻分开',
      '先看上两行：55 时只改变预装载值，100 时有效值才切换。下方 PWM 当前周期仍'
          '保持旧脉宽，下一周期使用新脉宽。前提是启用 OCxPE、正常更新，且没有中途强制 U'
          'G。')
    panel('06','gates','从定时器内部到引脚，每个开关控制不同环节',
      [['CR1.CEN','允许计数','决定 CNT 是否推进'],
       ['CR1.DIR/CMS','方向/对齐模式','改变计数方式与公式条件'],
       ['CR1.ARPE','ARR 预装载','决定 ARR 更新路径'],
       ['CCMR / CCER','模式、通道与极性','决定比较结果如何输出'],
       ['GPIO 复用 / TIM1 MOE','引脚路径 / 高级定时器主输出','满足后才到达实际引脚']],
      'CR1 是运行设置的总入口之一，不能替代通道和引脚配置。检查 PWM 无输出时，依次'
          '确认时钟、CEN、模式、CCxE、复用 GPIO，以及高级定时器 MOE/刹车条件。',
      ['设置','作用','观察重点'])
    panel('06','parameters','相同 72 MHz 输入，改变不同参数产生不同结果',
      [['7199','9999','—','1 s 更新周期'],
       ['71','999','300','1 kHz / 30% PWM'],
       ['71','999','700','1 kHz / 70% PWM'],
       ['71','1999','300','500 Hz / 15% PWM']],
      '逐行用 fCNT=fTIM/(PSC+1)、fPWM=fCNT/(ARR+1)、D='
          'CCR/(ARR+1) 复算。公式限常见向上计数、边沿对齐 PWM1、有效高等条件；'
          '变更 ARR 却不同比例调整 CCR，会同时改变占空比。',
      ['PSC','ARR','CCR','结果'])

def make_i2c_spi():
    fig,axs=plt.subplots(2,1,figsize=(12,5),sharex=True)
    t=np.arange(-1,11,.005)
    scl=np.ones_like(t)
    mask=(t>=0)&(t<9)
    scl[mask]=((t[mask]%1)>=.5).astype(int)
    bits=[1,1,0,1,0,0,0,0,0]
    sda=np.ones_like(t);sda[(t>=-.5)&(t<0)]=0
    for i,b in enumerate(bits):sda[(t>=i)&(t<i+1)]=b
    sda[(t>=9)&(t<9.5)]=0
    wave(axs[0],t,scl,'SCL');wave(axs[1],t,sda,'SDA',GREEN)
    for i,label in enumerate(['A6','A5','A4','A3','A2','A1','A0','W=0','ACK']):
        axs[0].text(i+.55,1.25,label,ha='center',fontsize=10)
    axs[1].text(-.5,1.2,'S',color=RED);axs[1].text(9.5,1.2,'P',color=RED)
    axs[1].set_xlabel('时钟槽（示意，地址 0x68 + 写方向 → D0）')
    save('12','i2c-wave',fig,'I2C：起始条件、地址八位、第九拍应答、停止条件',
      'SDA 在 SCL 高时下降构成 S；中间八个时钟传送 11010000，最后一位为'
          '写方向；第九拍由接收方拉低 ACK。P 是 SCL 高时 SDA 上升，真实边沿需满'
          '足建立保持时间。')
    panel('12','read-sequence','读寄存器：两次地址阶段，中间用重复起始连接',
      [['1','S → 地址+W → ACK','选择从机，准备给寄存器地址'],
       ['2','寄存器地址 → ACK','告诉从机从哪里读'],
       ['3','Sr → 地址+R → ACK','保持事务，切换读方向'],
       ['4','数据 → ACK（中间字节）','主机要求继续'],
       ['5','最后数据 → NACK → P','主机结束读取']],
      'S 为 START，Sr 为 repeated START，P 为 STOP。读数据'
          '时主机是接收方，因此 ACK/NACK 由主机控制；每处等待都要能超时退出。',
      ['顺序','总线动作','目的'])
    fig,axs=plt.subplots(3,1,figsize=(12,6),sharex=True)
    t=np.arange(-.5,8.6,.005);clk=np.zeros_like(t)
    m=(t>=0)&(t<8);clk[m]=((t[m]%1)>=.5).astype(int)
    data=np.zeros_like(t)
    bits=[0,0,0,0,0,0,1,1]
    for i,b in enumerate(bits):data[(t>=i)&(t<i+1)]=b
    wave(axs[0],t,np.where((t>=-.25)&(t<8.25),0,1),'CS')
    wave(axs[1],t,clk,'SCK',ORANGE);wave(axs[2],t,data,'MOSI',GREEN)
    for i,b in enumerate(bits):
        axs[2].text(i+.5,1.2,str(b),ha='center')
        axs[1].scatter([i+.5],[1],color=RED,s=25,zorder=5)
    axs[2].set_xlabel('位槽；本例 MSB 先发，模式 0：上升沿采样')
    save('13','spi-wave',fig,'SPI 模式 0 示例：CS 为低期间发送命令 0x03',
      '先看 CS 选择事务，再看红点标出的上升采样沿，最后读 MOSI 的 0000001'
          '1。此图只画命令阶段，读取 W25Q64 还要继续地址和数据时钟，不能发完 03 就'
          '结束 CS。')
    panel('13','page-split','起始地址 0x00F0，写入 40 字节应拆两页',
      [['第一次','0x00F0～0x00FF','16 字节','本页剩余空间'],
       ['第二次','0x0100～0x0117','24 字节','下一页继续']],
      '先算 256 - (地址 % 256)，得到本页还能写多少。每次页编程都需满足写使能，并等待完成；范围内需要擦除时，应先保护同扇区其他数据。',
      ['操作','目标地址','数量','边界原因'])

def make_rtos():
    fig,ax=plt.subplots(figsize=(12,4.5))
    ax.broken_barh([(0,1),(4,1),(8,1)],(2,.6),facecolors=ORANGE)
    ax.broken_barh([(1,2),(5,2),(9,2)],(1,.6),facecolors=BLUE)
    ax.broken_barh([(3,1),(7,1),(11,1)],(0,.6),facecolors=GREEN)
    ax.set(yticks=[.3,1.3,2.3],yticklabels=['Idle','处理任务','高优先级采样'],
           xlabel='时间（示意单位）',xlim=(0,12),ylim=(-.3,3))
    axis_clean(ax)
    save('17','schedule',fig,'单核调度：同一时刻只有一项占用 CPU',
      '沿横轴看采样任务周期性就绪并运行，随后阻塞，处理任务得到 CPU；都不就绪时才运行 '
          'Idle。每行空白代表未运行，不足以单独判断它处于阻塞还是就绪。')
    fig,ax=plt.subplots(figsize=(12,4))
    for y,starts,color in [(1,[0,12,24,36],BLUE),(0,[0,10,20,30],GREEN)]:
        ax.broken_barh([(s,2) for s in starts],(y,.5),facecolors=color)
    ax.set(yticks=[.25,1.25],yticklabels=['按计划时刻推进','工作后再延时 10'],
       xlabel='时间 / ms；每轮工作 2 ms，目标周期 10 ms',xlim=(0,40),ylim=(-.2,2))
    axis_clean(ax)
    save('17','period',fig,'相对延时会累积工作耗时，周期等待按计划推进',
      '上行每轮工作 2 ms 后再等待 10 ms，起点是 0、12、24、36；下行以 '
          '10 ms 计划间隔推进，起点是 0、10、20、30。图未考虑抢占和超期，实际仍需'
          '处理任务错过计划的情况。')
    panel('17','ownership','队列按元素复制：数据值和地址的生命周期不同',
      [['结构体值','消息字段内容','接收方持有独立副本'],
       ['缓冲区指针','指针地址','原缓冲必须继续有效'],
       ['局部变量地址','即将失效的栈地址','函数返回后不可继续使用']],
      '先确认 item size 与发送对象。指针队列需要约定分配、拥有、释放和复用时刻；排队成功不会自动使原对象延长寿命。',
      ['队列元素','实际复制什么','接收侧条件'])
    panel('17','choose','根据数据关系选择同步机制',
      [['传一条完整采样消息','队列','元素大小、容量、满处理'],
       ['保护同一设备','互斥锁','持有时间、优先级继承'],
       ['等待多个条件成立','事件组','位是条件，不是累计次数'],
       ['通知一个已知任务','任务通知','计数/覆盖/位语义'],
       ['硬件中断唤醒任务','FromISR 相关接口','中断优先级合法，不能阻塞']],
      '按“需求 → 机制 → 检查点”阅读。没有一种 API 同时替代所有通信、同步、保护和数据所有权责任。',
      ['需求','可选机制','关键限制'])

if __name__ == '__main__':
    for number in range(1, 18):
        cid = f'{number:02d}'
        (ASSETS / cid).mkdir(parents=True, exist_ok=True)
        DRAWIOS[cid] = ET.Element('mxfile', host='app.diagrams.net')
    make_specials()
    make_connections()
    for cid, root in DRAWIOS.items():
        if len(root):
            ET.ElementTree(root).write(
                ASSETS / cid / 'specials.drawio',
                encoding='utf-8', xml_declaration=True)
    print('专项图重绘完成。笔记与 PDF 未修改。')
