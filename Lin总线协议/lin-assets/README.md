# LIN 教学配图

本目录的 8 张图配合上一级 [LIN 笔记](../Lin总线.md) 阅读。

| 序号 | 文件名前缀 | 内容 |
| --- | --- | --- |
| 01 | 01-topology | 主从节点、MCU / 收发器 / 总线、电平关系 |
| 02 | 02-waveform | 8N1、LSB first、Break / delimiter / Sync |
| 03 | 03-frame | Header / Response 字段及发布订阅职责 |
| 04 | 04-pid | PID 位组成、保护位公式和诊断帧 PID |
| 05 | 05-checksum | Classic / Enhanced 和回卷进位手算 |
| 06 | 06-schedule | 四时隙循环、帧周期和发布订阅示例 |
| 07 | 07-sleep-wake | 总线休眠、唤醒和资源恢复的区别 |
| 08 | 08-software-flow | 总线到业务的数据链、cfg / ctx / data / ops |

- [lin-bus-explained.drawio](lin-bus-explained.drawio)：8 页可编辑源图，
  可用 draw.io / diagrams.net 打开，文字、方框、线段均可编辑。
- `*.png`：嵌入 Markdown 的预览。
- `*.svg`：矢量预览，适合放大查看；它是预览文件，不含 draw.io 编辑数据。
- `*.json`：与上述源图使用同一布局的 diagramry 输入，可重新渲染。

JSON 可通过 diagramry 的 `scripts/render_diagram.py` 渲染；字体优先使用
Microsoft YaHei，也可改为其他可用中文字体。
Windows 无界面环境生成 PNG 时，设置 `MPLBACKEND=Agg`。

图为教学功能示意，波形除明确标出的位宽关系外不用于精确量测。
实际电压、引脚、收发器控制与业务映射应查当前硬件和协议文件。
上一级原有的 image*.png 保留，本次不删除历史图片。
