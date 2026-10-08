# -*- coding: utf-8 -*-
"""
客户保险规划档案 PDF 生成模板
版本：1.0 | 基于 reportlab

使用方法：
1. 复制本文件为 generate_{客户拼音}_pdf.py
2. 替换下方【客户数据区】中的变量
3. 填充 story 内容区（参考注释中的页面结构）
4. 运行：python3 generate_{客户拼音}_pdf.py
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ═══════════════════════════════════════════════════
# 【客户数据区 — 替换为实际客户数据】
# ═══════════════════════════════════════════════════

CLIENT = {
    'name': '{客户名}',
    'pinyin': '{客户名拼音}',
    'archive_no': '{档案编号}',
    'age': '{年龄}',
    'gender': '{性别}',
    'occupation': '{职业}',
    'annual_income': '{年收入}',
    'savings': '{存款}',
    'risk_level': '{风险等级}',
    'risk_tags': ['{风险标签1}', '{风险标签2}', '{风险标签3}'],
    'date': '{建档日期}',
    'output_dir': os.getcwd(),
}

# 封面信息卡片（每行一个字符串）
COVER_INFO_ROWS = [
    '{年龄}岁  |  {性别}  |  {职业}',
    '{年收入}  |  {存款}',
    '{其他核心信息行}',
]

# ═══════════════════════════════════════════════════
# 【以下为通用模板，通常无需修改】
# ═══════════════════════════════════════════════════

# ── 字体注册 ──
FONT_PATH = '/System/Library/Fonts/STHeiti Medium.ttc'
# 备选路径（如主字体不存在时取消注释替换）：
# FONT_PATH = '/System/Library/Fonts/Supplemental/STHeiti Light.ttc'

pdfmetrics.registerFont(TTFont('ZhFont', FONT_PATH, subfontIndex=0))

FONT = 'ZhFont'

# ── 颜色常量 ──
C_PRIMARY = HexColor('#1A73E8')
C_DARK = HexColor('#1F2937')
C_BODY = HexColor('#374151')
C_MUTED = HexColor('#6B7280')
C_LIGHT_BG = HexColor('#F3F4F6')
C_ACCENT = HexColor('#059669')
C_RED = HexColor('#DC2626')
C_ORANGE = HexColor('#EA580C')
C_PURPLE = HexColor('#7C3AED')

WIDTH, HEIGHT = A4
MARGIN = 20 * mm

# ── 样式库 ──
styles = {
    'title': ParagraphStyle('title', fontName=FONT, fontSize=22, leading=30,
                            textColor=C_PRIMARY, spaceAfter=4*mm, alignment=TA_CENTER),
    'subtitle': ParagraphStyle('subtitle', fontName=FONT, fontSize=10,
                               textColor=C_MUTED, alignment=TA_CENTER, spaceAfter=6*mm),
    'h1': ParagraphStyle('h1', fontName=FONT, fontSize=16, leading=22,
                          textColor=C_PRIMARY, spaceBefore=8*mm, spaceAfter=4*mm),
    'h2': ParagraphStyle('h2', fontName=FONT, fontSize=13, leading=18,
                          textColor=C_DARK, spaceBefore=5*mm, spaceAfter=3*mm),
    'body': ParagraphStyle('body', fontName=FONT, fontSize=10, leading=16,
                            textColor=C_BODY, spaceAfter=2*mm, alignment=TA_JUSTIFY),
    'body_indent': ParagraphStyle('body_indent', fontName=FONT, fontSize=10, leading=16,
                                   textColor=C_BODY, spaceAfter=2*mm, leftIndent=8*mm,
                                   alignment=TA_JUSTIFY),
    'bullet': ParagraphStyle('bullet', fontName=FONT, fontSize=10, leading=16,
                              textColor=C_BODY, spaceAfter=1.5*mm, leftIndent=8*mm,
                              bulletIndent=3*mm, alignment=TA_LEFT),
    'small': ParagraphStyle('small', fontName=FONT, fontSize=8.5, leading=13,
                             textColor=C_MUTED, spaceAfter=1*mm),
    'table_header': ParagraphStyle('th', fontName=FONT, fontSize=9.5, leading=13,
                                    textColor=white, alignment=TA_CENTER),
    'table_cell': ParagraphStyle('tc', fontName=FONT, fontSize=9, leading=13,
                                  textColor=C_BODY, alignment=TA_CENTER),
    'table_cell_left': ParagraphStyle('tcl', fontName=FONT, fontSize=9, leading=13,
                                       textColor=C_BODY, alignment=TA_LEFT),
    'highlight': ParagraphStyle('hl', fontName=FONT, fontSize=10.5, leading=16,
                                 textColor=C_RED, spaceAfter=2*mm),
    'footer': ParagraphStyle('footer', fontName=FONT, fontSize=8, leading=11,
                              textColor=C_MUTED, alignment=TA_CENTER),
}


# ── 可复用组件 ──

def make_table(headers, rows, col_widths=None):
    """创建带蓝色表头 + 斑马纹的数据表格"""
    header_cells = [Paragraph(h, styles['table_header']) for h in headers]
    data = [header_cells]
    for row in rows:
        data.append([
            Paragraph(str(c), styles['table_cell_left']) if i == 0
            else Paragraph(str(c), styles['table_cell'])
            for i, c in enumerate(row)
        ])

    if col_widths is None:
        usable = WIDTH - 2 * MARGIN
        col_widths = [usable / len(headers)] * len(headers)

    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
        ('TEXTCOLOR', (0, 0), (-1, 0), white),
        ('FONTNAME', (0, 0), (-1, -1), FONT),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [white, C_LIGHT_BG]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
    ]))
    return t


def make_table_with_highlight(headers, rows, col_widths=None, highlight_last=False):
    """创建表格，可选高亮最后一行（用于合计行）"""
    t = make_table(headers, rows, col_widths)
    if highlight_last:
        # 覆盖样式：给最后一行加蓝色背景，去掉斑马纹
        last_idx = len(rows)  # +1 因为有表头
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, last_idx), (-1, last_idx), HexColor('#EFF6FF')),
            ('ROWBACKGROUNDS', (0, 1), (-1, last_idx - 1), [white, C_LIGHT_BG]),
        ]))
    return t


def section_header(title):
    """章节标题 + 蓝色分隔线"""
    return [
        Paragraph(title, styles['h1']),
        HRFlowable(width='100%', thickness=1, color=C_PRIMARY, spaceAfter=3*mm),
    ]


def bullet_list(items):
    """创建圆点列表"""
    return [Paragraph(f'<bullet>&bull;</bullet> {item}', styles['bullet']) for item in items]


def info_table(rows, col_widths=None):
    """创建键值对信息表（4列：标签-值-标签-值）"""
    usable = WIDTH - 2 * MARGIN
    if col_widths is None:
        col_widths = [usable*0.12, usable*0.38, usable*0.12, usable*0.38]

    data = [
        [Paragraph(rows[i][j], styles['table_cell_left'] if j in [1, 3] else styles['table_cell'])
         for j in range(4)]
        for i in range(len(rows))
    ]
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), HexColor('#EFF6FF')),
        ('BACKGROUND', (2, 0), (2, -1), HexColor('#EFF6FF')),
        ('GRID', (0, 0), (-1, -1), 0.5, HexColor('#D1D5DB')),
        ('ROWBACKGROUNDS', (1, 0), (1, -1), [white, C_LIGHT_BG]),
        ('ROWBACKGROUNDS', (3, 0), (3, -1), [white, C_LIGHT_BG]),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
    ]))
    return t


# ── 页脚 ──
def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont(FONT, 8)
    canvas.setFillColor(C_MUTED)
    page_text = f'{CLIENT["name"]} 客户保险规划档案  |  第 {doc.page} 页'
    canvas.drawCentredString(WIDTH / 2, 12 * mm, page_text)
    canvas.setStrokeColor(HexColor('#E5E7EB'))
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN, HEIGHT - MARGIN + 5*mm, WIDTH - MARGIN, HEIGHT - MARGIN + 5*mm)
    canvas.restoreState()


# ── 封面生成函数 ──
def build_cover(story, usable_w):
    """生成标准封面页"""
    story.append(Spacer(1, 30*mm))
    story.append(Paragraph('客户保险规划档案', styles['title']))
    story.append(Spacer(1, 4*mm))

    # 客户名大字
    name_style = ParagraphStyle('name', fontName=FONT, fontSize=36, leading=44,
                                 textColor=C_DARK, alignment=TA_CENTER, spaceAfter=2*mm)
    story.append(Paragraph(CLIENT['name'], name_style))

    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(f'档案编号：{CLIENT["archive_no"]}', styles['subtitle']))

    # 核心信息卡片
    card_style = ParagraphStyle('card', fontName=FONT, fontSize=11, leading=16,
                                 textColor=C_BODY, alignment=TA_CENTER)
    card_table = Table(
        [[Paragraph(row, card_style)] for row in COVER_INFO_ROWS],
        colWidths=[usable_w * 0.75],
        rowHeights=[12*mm] * len(COVER_INFO_ROWS),
    )
    card_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), C_LIGHT_BG),
        ('BOX', (0, 0), (-1, -1), 0.5, HexColor('#D1D5DB')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, HexColor('#E5E7EB')),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
    ]))
    story.append(card_table)

    story.append(Spacer(1, 10*mm))

    # 风险等级
    risk_style = ParagraphStyle('risk', fontName=FONT, fontSize=13, leading=18,
                                 textColor=C_RED, alignment=TA_CENTER, spaceAfter=3*mm)
    story.append(Paragraph(f'风险等级：{CLIENT["risk_level"]}', risk_style))

    # 风险标签
    tag_text = '  |  '.join(CLIENT['risk_tags'])
    tag_style = ParagraphStyle('tags', fontName=FONT, fontSize=9,
                                textColor=C_MUTED, alignment=TA_CENTER)
    story.append(Paragraph(tag_text, tag_style))

    story.append(Spacer(1, 15*mm))
    story.append(HRFlowable(width='60%', thickness=0.5, color=C_MUTED, spaceAfter=3*mm))
    story.append(Paragraph('基于《客户宝典》框架  |  建档日期 ' + CLIENT['date'], styles['small']))
    story.append(Paragraph('本档案仅作保险规划参考使用，具体方案以实际投保为准', styles['small']))

    story.append(PageBreak())


# ── 构建并生成 PDF ──
output_path = os.path.join(CLIENT['output_dir'], f'{CLIENT["pinyin"]}_客户保险规划档案.pdf')

doc = SimpleDocTemplate(
    output_path,
    pagesize=A4,
    leftMargin=MARGIN, rightMargin=MARGIN,
    topMargin=MARGIN + 3*mm, bottomMargin=MARGIN + 3*mm,
)

story = []
usable_w = WIDTH - 2 * MARGIN

# ═══════════════════════════════════════════════════
# PAGE 1: 封面（自动生成）
# ═══════════════════════════════════════════════════
build_cover(story, usable_w)

# ═══════════════════════════════════════════════════
# PAGE 2: 客户画像（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('一、客户画像'))
#
# story.append(Paragraph('<b>1.1 基础信息</b>', styles['h2']))
# info_rows = [
#     ['姓名', '...', '年龄', '...岁'],
#     ['性别', '...', '职业', '...'],
#     # ... 按需添加行
# ]
# story.append(info_table(info_rows))
#
# story.append(Paragraph('<b>1.2 家庭结构</b>', styles['h2']))
# story.extend(bullet_list([
#     '<b>标签</b>：描述内容',
#     # ...
# ]))
#
# # ... 继续其他小节
#
# story.append(PageBreak())

# ═══════════════════════════════════════════════════
# PAGE 3: 需求分析（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('二、需求分析'))
# # ...
# story.append(PageBreak())

# ═══════════════════════════════════════════════════
# PAGE 4: 保障方案设计（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('三、保障方案设计'))
# # ...
# story.append(PageBreak())

# ═══════════════════════════════════════════════════
# PAGE 5: 各层级详细配置（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('四、各层级详细配置'))
# # ...
# story.append(PageBreak())

# ═══════════════════════════════════════════════════
# PAGE 6: 补充保障（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('五、补充保障配置'))
# # ...
# story.append(PageBreak())

# ═══════════════════════════════════════════════════
# PAGE 7: 客户宝典洞察 + 话术（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('六、客户宝典核心洞察'))
# # ...
# story.append(PageBreak())

# ═══════════════════════════════════════════════════
# PAGE 8: 实施路径 + 跟进计划（手动填充）
# ═══════════════════════════════════════════════════
# story.extend(section_header('七、实施路径与跟进计划'))
# # ...
# # 最后一页不需要 PageBreak

# ── 生成 ──
if __name__ == '__main__':
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)
    print(f'PDF generated: {output_path}')
    print(f'File size: {os.path.getsize(output_path) / 1024:.0f} KB')
