"""用同一布局生成 DMA 教学图的 draw.io、JSON、SVG 和 PNG。

默认读取本机 diagramry 技能；其他机器可用 --renderer 指定渲染器路径。
输出只写入脚本所在目录，不修改原有课程配图。
"""

import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

os.environ["MPLBACKEND"] = "Agg"
sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
FONT = "Microsoft YaHei,SimHei,DengXian,SimSun"
INK = "#243746"
BLUE = "#dceafa"
GREEN = "#dff2e5"
ORANGE = "#fff0d6"
GRAY = "#edf1f5"
SCALE = 70


class Figure:
    """以左上角为原点记录布局，预览与可编辑图共享节点和连线。"""

    def __init__(self, slug, title, height=9.2):
        self.slug = slug
        self.title = title
        self.height = height
        self.items = []
        self.nodes = {}
        self.edges = []
        self.text("title", 10, 0.45, title, 20)

    def text(self, key, x, y, text, size=12):
        """文本位置按中心坐标保存，保持两种输出的对齐方式一致。"""
        self.items.append(dict(
            kind="text", id=key, xy=[x, self.height - y],
            text=text, fontsize=size, color=INK,
            align=["center", "center"],
        ))

    def box(self, key, x, y, w, h, label, fill=GRAY, size=14):
        """记录数据、任务或状态节点，标签使用中文并允许换行。"""
        self.nodes[key] = (x, y, w, h)
        self.items.append(dict(
            kind="rect", id=key, xy=[x, self.height - y - h],
            w=w, h=h, label=label, fill=fill, color=INK,
            lw=1, fontsize=size, min_fontsize=11,
            cornerradius=0,
        ))

    def arrow(self, key, source, target, start, end, dashed=False):
        """连线区分地址引用和搬运路径；端点绑定可编辑节点。"""
        item = dict(
            kind="arrow", id=key,
            points=[[start[0], self.height - start[1]],
                    [end[0], self.height - end[1]]],
            color=INK, lw=1.5,
        )
        if dashed:
            item["ls"] = "--"
        self.items.append(item)
        self.edges.append((key, source, target, start, end, dashed))

    def spec(self):
        """输出 diagramry 的公开 shapes 格式，便于单张重绘。"""
        return dict(
            type="shapes", title=self.title,
            output=dict(
                dpi=160,
                theme=dict(bgcolor="white", color=INK, unit=3,
                           fontsize=14, font=FONT),
            ),
            items=self.items,
        )

    def drawio_page(self, parent, renderer):
        """生成原生节点，保持文本、框和连线可以分别编辑。"""
        page = ET.SubElement(
            parent, "diagram", id=self.slug, name=self.title,
        )
        model = ET.SubElement(page, "mxGraphModel", dict(
            adaptiveColors="auto", page="1", pageScale="1",
            pageWidth="1400", pageHeight=str(int(self.height * SCALE)),
        ))
        root = ET.SubElement(model, "root")
        ET.SubElement(root, "mxCell", id="0")
        ET.SubElement(root, "mxCell", id="1", parent="0")
        for item in self.items:
            kind = item["kind"]
            if kind not in {"rect", "text"}:
                continue
            key = item["id"]
            if kind == "rect":
                x, y, w, h = self.nodes[key]
                size = renderer.fit_fontsize(
                    item["label"], FONT, max(w - 0.22, 0.2),
                    max(h - 0.18, 0.2), item["fontsize"], 33,
                    min_fontsize=11,
                )
                label = item["label"]
                style = (
                    "rounded=1;arcSize=8;whiteSpace=wrap;html=0;"
                    f"fillColor={item['fill']};strokeColor={INK};"
                )
            else:
                cx, bottom_y = item["xy"]
                label = item["text"]
                size = item["fontsize"]
                w = max(4, min(20, max(map(len, label.splitlines()))))
                h = max(0.55, len(label.splitlines()) * 0.5)
                x = cx - w / 2
                y = self.height - bottom_y - h / 2
                style = (
                    "text;whiteSpace=wrap;html=0;align=center;"
                    "verticalAlign=middle;fillColor=none;strokeColor=none;"
                )
            style += (
                f"fontFamily=Microsoft YaHei;fontColor={INK};"
                f"fontSize={round(size * SCALE / 33, 1)};"
            )
            cell = ET.SubElement(root, "mxCell", dict(
                id=key, parent="1", vertex="1", value=label,
                style=style,
            ))
            ET.SubElement(cell, "mxGeometry", dict(
                x=str(x * SCALE), y=str(y * SCALE),
                width=str(w * SCALE), height=str(h * SCALE),
                **{"as": "geometry"},
            ))
        for key, source, target, start, end, dashed in self.edges:
            sx, sy, sw, sh = self.nodes[source]
            tx, ty, tw, th = self.nodes[target]
            style = (
                "endArrow=block;endFill=1;html=0;"
                f"strokeColor={INK};strokeWidth=1.5;"
                f"exitX={(start[0] - sx) / sw};"
                f"exitY={(start[1] - sy) / sh};exitPerimeter=0;"
                f"entryX={(end[0] - tx) / tw};"
                f"entryY={(end[1] - ty) / th};entryPerimeter=0;"
            )
            if dashed:
                style += "dashed=1;"
            cell = ET.SubElement(root, "mxCell", dict(
                id=key, parent="1", edge="1", source=source,
                target=target, style=style,
            ))
            ET.SubElement(cell, "mxGeometry", dict(
                relative="1", **{"as": "geometry"},
            ))


def comparison():
    """比较单次软件接力和硬件装载，不把框宽画成实际耗时。"""
    f = Figure("single-vs-chain", "下一段参数，由 CPU 还是 DMA 装载？")
    f.text("top", 10, 1.25, "普通单次 DMA：段间由 CPU 重新配置", 14)
    nodes = [
        ("cpu-a", 0.7, 3.4, "CPU\n配置 A", ORANGE),
        ("dma-a", 5.4, 3.2, "DMA\n搬运 A", BLUE),
        ("cpu-b", 10, 3.6, "CPU\n配置 B", ORANGE),
        ("dma-b", 15, 3.5, "DMA\n搬运 B", BLUE),
    ]
    for key, x, w, text, fill in nodes:
        f.box(key, x, 2, w, 1.5, text, fill)
    for a, b in zip(nodes, nodes[1:]):
        f.arrow(a[0] + "-next", a[0], b[0],
                (a[1] + a[2], 2.75), (b[1], 2.75))
    f.text("bottom", 10, 4.35, "硬件链式 DMA：CPU 提前准备，DMA 自动接力", 14)
    nodes = [
        ("prepare", 0.7, 4, "CPU 准备\nA → B 的链", ORANGE),
        ("chain-a", 6, 3.2, "DMA\n搬运 A", BLUE),
        ("load-b", 10.5, 3.6, "DMA 硬件\n装载 B 参数", GREEN),
        ("chain-b", 15.4, 3.8, "DMA\n搬运 B", BLUE),
    ]
    for key, x, w, text, fill in nodes:
        f.box(key, x, 5.1, w, 1.5, text, fill)
    for a, b in zip(nodes, nodes[1:]):
        f.arrow(a[0] + "-next", a[0], b[0],
                (a[1] + a[2], 5.85), (b[1], 5.85))
    f.text("note", 10, 7.6, "两种方式的一段内部，都由 DMA 搬数据", 14)
    f.text("boundary", 10, 8.45,
           "箭头表示顺序，框宽不代表耗时；链式能力与更新字段以手册为准")
    return f


def descriptors():
    """分开画控制信息、源地址引用与实际数据路径。"""
    f = Figure("descriptor-and-data", "描述符是搬运单，缓冲区是数据", 10.5)
    nodes = [("a", 0.7, "A", "B"),
             ("b", 6.4, "B", "C"),
             ("c", 12.1, "C", "结束")]
    for key, x, name, nxt in nodes:
        f.box("desc-" + key, x, 1.45, 4.5, 2.6,
              f"描述符 {name}\nsrc：缓冲区 {name}\n"
              f"dst：同一外设寄存器\ncount：256 个半字\nnext：{nxt}",
              ORANGE, 12)
        f.box("buf-" + key, x, 5, 4.5, 1.05,
              f"缓冲区 {name}：512 字节", BLUE, 13)
        f.arrow("src-" + key, "desc-" + key, "buf-" + key,
                (x + 2.25, 4.05), (x + 2.25, 5), True)
    f.arrow("next-ab", "desc-a", "desc-b", (5.2, 2.7), (6.4, 2.7))
    f.arrow("next-bc", "desc-b", "desc-c", (10.9, 2.7), (12.1, 2.7))
    f.box("end", 17.8, 2.2, 1.6, 1.1, "链结束", GRAY, 11)
    f.arrow("next-end", "desc-c", "end", (16.6, 2.75), (17.8, 2.75))
    f.text("ptr-label", 17.4, 4.5, "虚线：地址引用")
    f.box("engine", 6.4, 7.55, 4.5, 1.1,
          "DMA：按 A / B / C 顺序搬运", GREEN, 12)
    f.box("peripheral", 13.1, 7.55, 5, 1.1,
          "固定目的：外设数据寄存器", BLUE, 12)
    for key, x, _, _ in nodes:
        f.arrow("data-" + key, "buf-" + key, "engine",
                (x + 2.25, 6.05), (8.65, 7.55))
    f.arrow("data-out", "engine", "peripheral",
            (10.9, 8.1), (13.1, 8.1))
    f.text("path-label", 11.95, 7.17, "数据")
    f.text("summary", 10, 9.65,
           "next 指向描述符；src 指向数据。三路源按段使用，不是同时搬运。")
    return f


def requests():
    """把参数与触发分开，避免把链表当成数据请求源。"""
    f = Figure("request-and-transfer", "链表决定搬什么，请求推动什么时候搬", 10)
    f.box("descriptor", 0.7, 1.5, 4.6, 1.7,
          "当前描述符\n源 / 目的 / 数量 / next", ORANGE, 13)
    f.box("params", 7, 1.5, 4.7, 1.7,
          "当前段参数\n地址、宽度和剩余数量", GREEN, 13)
    f.arrow("load", "descriptor", "params", (5.3, 2.35), (7, 2.35))
    f.text("load-text", 6.15, 1.85, "装载")
    f.box("trigger", 0.7, 4.45, 4.6, 1.65,
          "外设 FIFO / 数据就绪\n产生 DMA 请求", ORANGE, 13)
    f.box("transfer", 7, 4.45, 4.7, 1.65,
          "DMA 按参数搬运\n请求粒度由配置决定", BLUE, 13)
    f.box("destination", 14, 4.45, 5.3, 1.65,
          "数据到达目的地址\n本例：外设数据寄存器", BLUE, 13)
    f.arrow("request", "trigger", "transfer", (5.3, 5.27), (7, 5.27))
    f.text("request-text", 6.15, 4.75, "请求")
    f.arrow("config", "params", "transfer", (9.35, 3.2), (9.35, 4.45))
    f.arrow("payload", "transfer", "destination", (11.7, 5.27), (14, 5.27))
    f.text("payload-text", 12.85, 4.75, "数据")
    f.box("next", 6.2, 7.5, 6.3, 1.1,
          "段完成且有下一节点 → 硬件准备下一段", GREEN, 12)
    f.arrow("complete", "transfer", "next", (9.35, 6.1), (9.35, 7.5))
    f.text("caution", 10, 9.3,
           "没有有效请求，链表正确也可能不搬；预取和装载时机以手册为准。")
    return f


def ownership():
    """展示 TX 双缓冲的有限更新窗口，不将事件画成自动互斥锁。"""
    f = Figure("double-buffer-ownership", "A/B 循环链：DMA 读一块，CPU 准备另一块", 10)
    f.box("a", 4.1, 1.35, 4.1, 1.3, "描述符 A\n源：缓冲区 A", ORANGE, 12)
    f.box("b", 11.8, 1.35, 4.1, 1.3, "描述符 B\n源：缓冲区 B", ORANGE, 12)
    f.arrow("a-b", "a", "b", (8.2, 1.7), (11.8, 1.7))
    f.arrow("b-a", "b", "a", (11.8, 2.3), (8.2, 2.3))
    f.text("a-b-label", 10, 1.3, "next → B", 11)
    f.text("b-a-label", 10, 2.7, "next → A", 11)
    f.text("phase1", 4.4, 3.55, "阶段 1：首次读 A", 13)
    f.text("phase2", 10.3, 3.55, "阶段 2：切换读 B", 13)
    f.text("phase3", 16.2, 3.55, "阶段 3：回到 A", 13)
    f.text("label-a", 0.8, 4.95, "A 块", 12)
    f.text("label-b", 0.8, 6.4, "B 块", 12)
    for key, x, a_text, b_text, a_fill, b_fill in [
        ("first", 2, "DMA 读取 A\nCPU 不得改写", "B 已预填\n可在切换前更新",
         BLUE, GREEN),
        ("second", 7.9, "CPU 更新 A\n须在回到 A 前完成", "DMA 读取 B\nCPU 不得改写",
         GREEN, BLUE),
        ("third", 13.8, "DMA 读取 A\n使用新一轮数据", "CPU 更新 B\n须在回到 B 前完成",
         BLUE, GREEN),
    ]:
        f.box(key + "-a", x, 4.35, 4.8, 1.2, a_text, a_fill, 12)
        f.box(key + "-b", x, 5.8, 4.8, 1.2, b_text, b_fill, 12)
    for left, right, lx, rx in [
        ("first", "second", 6.8, 7.9),
        ("second", "third", 12.7, 13.8),
    ]:
        f.arrow(left + "-handoff", left + "-a", right + "-a",
                (lx, 4.95), (rx, 4.95))
    f.text("window", 10, 7.85,
           "假设每段 256 个半字、消耗率 16000 半字/秒：理论窗口 16 ms", 13)
    f.text("margin", 10, 8.65,
           "CPU 准备 + 调度 + 必要缓存维护，必须在该窗口内完成并留余量。")
    f.text("rx", 10, 9.35,
           "接收 RX 方向反过来：DMA 写当前块，CPU 读已完成块；须赶在覆盖前读完。")
    return f


def main():
    """先写可编辑图，再输出预览，保持多个格式来自同一逻辑模型。"""
    parser = argparse.ArgumentParser(description=__doc__)
    default = (Path.home() / ".codex" / "skills" / "diagramry"
               / "scripts" / "render_diagram.py")
    parser.add_argument("--renderer", type=Path, default=default)
    args = parser.parse_args()
    if not args.renderer.is_file():
        parser.error("找不到 diagramry 渲染器，请用 --renderer 指定路径")
    module = importlib.util.spec_from_file_location("renderer", args.renderer)
    renderer = importlib.util.module_from_spec(module)
    module.loader.exec_module(renderer)
    figures = [comparison(), descriptors(), requests(), ownership()]
    mxfile = ET.Element("mxfile", host="app.diagrams.net")
    for figure in figures:
        figure.drawio_page(mxfile, renderer)
    tree = ET.ElementTree(mxfile)
    ET.indent(tree, space="  ")
    tree.write(HERE / "dma-chain-explained.drawio", encoding="utf-8",
               xml_declaration=True)
    for figure in figures:
        spec = figure.spec()
        source = HERE / (figure.slug + ".json")
        source.write_text(json.dumps(spec, ensure_ascii=False, indent=2)
                          + "\n", encoding="utf-8")
        for extension in ("svg", "png"):
            output = HERE / (figure.slug + "." + extension)
            drawing = renderer.drawing_from_output(spec, output)
            renderer.render_shapes(drawing, spec)
            renderer.save_drawing(drawing, spec, output)
            print(output.name)
            if extension == "png":
                import matplotlib.pyplot as plt
                plt.close("all")


if __name__ == "__main__":
    main()
