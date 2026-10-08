# -*- coding: utf-8 -*-
"""
客户宝典 KYC 客户经营分析报告 - 通用PDF生成器
===============================================
用法：
  from kyc_pdf_generator import generate_kyc_pdf
  generate_kyc_pdf(client_data, output_path)

client_data 结构见下方 main() 中的示例。
"""

import os, json
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# ── 字体 ──
_fp = "/System/Library/Fonts/STHeiti Medium.ttc"
if not os.path.exists(_fp):
    _fp = "/System/Library/Fonts/PingFang.ttc"
pdfmetrics.registerFont(TTFont('ZH', _fp))

# ── 配色 ──
C_PRIMARY = colors.HexColor('#1a5276')
C_ACCENT  = colors.HexColor('#2980b9')
C_BLUE_BG = colors.HexColor('#ebf5fb')
C_GREEN_BG= colors.HexColor('#eafaf1')
C_RED_BG  = colors.HexColor('#fadbd8')
C_YELLOW_BG=colors.HexColor('#fcf3cf')
C_WHITE   = colors.white
C_GRAY    = colors.HexColor('#85929e')
C_DARK    = colors.HexColor('#2c3e50')
C_BORDER  = colors.HexColor('#d5d8dc')
C_STRIPE  = colors.HexColor('#fdfefe')

# ── 样式缓存 ──
_style_cache = {}
def _style(sz, bold=False, color=None, align=TA_LEFT):
    key = (sz, bold, color, align)
    if key not in _style_cache:
        _style_cache[key] = ParagraphStyle(
            f'z{len(_style_cache)}', fontName='ZH', fontSize=sz,
            textColor=color or C_DARK, alignment=align,
            leading=sz * 1.6, spaceAfter=3, spaceBefore=2,
        )
    return _style_cache[key]

def _P(text, sz=10, bold=False, color=None, align=TA_LEFT):
    """创建Paragraph"""
    return Paragraph(str(text), _style(sz, bold, color, align))

def _br(text):
    """换行符转<br/>"""
    return str(text).replace('\n', '<br/>')

def _make_table(data, col_widths, header_bg=C_PRIMARY, stripe=True):
    """通用表格生成"""
    t = Table(data, colWidths=col_widths)
    cmds = [
        ('BACKGROUND', (0, 0), (-1, 0), header_bg),
        ('TEXTCOLOR', (0, 0), (-1, 0), C_WHITE),
        ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]
    if stripe and len(data) > 1:
        cmds.append(('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_STRIPE, C_BLUE_BG]))
    t.setStyle(TableStyle(cmds))
    return t


def generate_kyc_pdf(data: dict, output_path: str):
    """
    生成 KYC 客户经营分析报告 PDF。

    data 字段说明：
    ─────────────────
    基本信息：
      name          客户姓名
      id            档案编号 (如 "005")
      date          分析日期 (如 "2026-05-16")
      age           年龄 (如 "45岁")
      gender        性别 (如 "女性")
      occupation    职业 (如 "夜总会驻唱歌手")
      description   一句话描述 (如 "45岁，女性，显年轻")

    摘要卡片 (summary)：
      核心焦虑 / 生命周期 / 客户类型 / 风险等级 / 预计首年保费
      每项为 dict: {"label": "...", "value": "..."}

    KYC采集 (kyc_items)：
      list of {"label": "1. 称呼", "value": "丁丁（45岁...）"}

    客户类型与风险 (client_profile)：
      type_str      如 "单亲家庭 + 三明治家庭（双重特征）"
      lifecycle     如 "成熟期（40-55岁）- ..."
      risk_level    如 "保守型 - ..."
      chapters      如 "参考《客户宝典》第6章+第7章+第9章"

    刚性事件 (rigid_events)：
      list of {"priority": "5星", "event": "...", "status": "...", "gap": "...", "ref": "第7章"}

    风险诊断 (risk_diagnosis)：
      list of {"level": "高危风险（需立即处理）", "color": "red"/"orange"/"yellow",
               "items": "1. ...\n2. ..."}
      color映射: red → C_RED_BG, orange → C_YELLOW_BG, yellow → C_GREEN_BG

    反常识洞察 (insights)：
      list of {"myth": "...", "truth": "...", "advice": "...", "ref": "第X章"}

    保额建议 (coverage)：
      list of {"product": "...", "amount": "...", "basis": "...", "note": "..."}

    保费预算 (budget_plans)：
      list of {"tier": "基础版", "annual": "约8,200元", "ratio": "6.4%",
               "content": "...", "monthly": "约680元"}

    分步实施 (steps)：
      list of {"step": "第一步（立即）", "products": "...", "amounts": "...",
               "costs": "...", "logic": "...", "ref": "第7章"}

    面谈话术 (talk_scripts)：
      list of {"scene": "开场破冰", "script": "..."}

    核心结论 (core_conclusions)：
      list of str，每条为一个关键发现

    核保提示 (underwriting_notes)：
      str 或 list of str，核保相关的健康风险提示

    异议处理 (objection_handling)：
      list of {"objection": "客户可能说", "response": "应对思路"}

    预计成交 (deal_assessment)：
      dict with keys: probability, first_year_premium, obstacles, breakthroughs, strategy, next_action

    跟进计划 (follow_up)：
      list of {"time": "成交后1个月", "content": "...", "ref": "第7章"}
    """

    def _add_page_number(canvas, current_doc):
        canvas.saveState()
        canvas.setFont('ZH', 8)
        canvas.setFillColor(C_GRAY)
        canvas.drawCentredString(A4[0] / 2, 0.9 * cm, f'- {current_doc.page} -')
        canvas.restoreState()

    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2.2*cm, bottomMargin=2*cm,
        title=f'{data["name"]} KYC客户经营分析报告',
        author='客户宝典 KYC分析工具',
        subject='客户KYC采集、需求分析与配置思路'
    )
    elements = []
    WW = A4[0] - 4 * cm  # 可用宽度

    # ══════ 封面标题 ══════
    elements.append(Spacer(1, 1*cm))
    elements.append(_P('客户宝典 · KYC客户经营分析报告', 20, True, C_PRIMARY, TA_CENTER))
    elements.append(Spacer(1, 0.3*cm))
    elements.append(HRFlowable(width='100%', thickness=2, color=C_PRIMARY, spaceAfter=0.3*cm))

    subtitle = f'{data["name"]}  ·  {data["occupation"]}  ·  {data["age"]}'
    elements.append(_P(subtitle, 15, True, C_ACCENT, TA_CENTER))
    elements.append(Spacer(1, 0.15*cm))
    elements.append(_P(f'档案编号：{data["id"]}  |  分析日期：{data["date"]}', 10, color=C_GRAY, align=TA_CENTER))
    elements.append(Spacer(1, 0.5*cm))

    # ══════ 摘要卡片 ══════
    summary = data.get('summary', [])
    if summary:
        cells = [[_P(f'<b>{s["label"]}</b>', 10, True, C_PRIMARY), _P(s["value"], 10)] for s in summary]
        st = Table(cells, colWidths=[3.8*cm, WW - 3.8*cm])
        st.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), C_BLUE_BG),
            ('BACKGROUND', (1, 0), (1, -1), C_STRIPE),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(st)
        elements.append(Spacer(1, 0.5*cm))

    # ══════ 第一节：KYC采集摘要 ══════
    elements.append(_section_hr())
    elements.append(_P('一、KYC采集摘要', 14, True, C_PRIMARY))
    elements.append(Spacer(1, 0.15*cm))
    kyc_items = data.get('kyc_items', [])
    for item in kyc_items:
        elements.append(_P(f'<b>{item["label"]}：</b>{item["value"]}', 10))
        elements.append(Spacer(1, 0.05*cm))
    elements.append(Spacer(1, 0.2*cm))

    # ══════ 第二节：客户宝典·需求分析 ══════
    elements.append(_section_hr())
    elements.append(_P('二、客户宝典 · 需求分析', 14, True, C_PRIMARY))
    elements.append(Spacer(1, 0.15*cm))
    profile = data.get('client_profile', {})
    if profile:
        elements.append(_P(f'<b>【客户类型判断】</b>{profile.get("type_str", "")}', 11))
        elements.append(Spacer(1, 0.1*cm))
        elements.append(_P(f'<b>【生命周期阶段】</b>{profile.get("lifecycle", "")} {profile.get("chapters", "")}', 11))
        elements.append(Spacer(1, 0.1*cm))
        elements.append(_P(f'<b>【风险承受等级】</b>{profile.get("risk_level", "")}', 11))
        elements.append(Spacer(1, 0.2*cm))

    # 刚性事件
    rigid = data.get('rigid_events', [])
    if rigid:
        elements.append(_P('<b>刚性事件清单（按优先级）</b>', 12, True, C_PRIMARY))
        elements.append(Spacer(1, 0.1*cm))
        hdr = [_P(h, 10, True, C_WHITE) for h in ['优先级', '刚性事件', '准备情况', '缺口', '参考']]
        rows = [[_P(r[k], 10) for k in ['priority', 'event', 'status', 'gap', 'ref']] for r in rigid]
        elements.append(_make_table([hdr] + rows, [1.5*cm, 3.5*cm, 3.5*cm, 3.5*cm, 1.5*cm]))
        elements.append(Spacer(1, 0.3*cm))

    # 风险诊断
    risks = data.get('risk_diagnosis', [])
    if risks:
        elements.append(_P('<b>风险诊断报告</b>', 12, True, C_PRIMARY))
        elements.append(Spacer(1, 0.1*cm))
        color_map = {'red': C_RED_BG, 'orange': C_YELLOW_BG, 'yellow': C_GREEN_BG}
        for r in risks:
            bg = color_map.get(r.get('color', 'red'), C_RED_BG)
            rd = [[_P(r['level'], 10, True, C_DARK), _P(_br(r['items']), 10)]]
            rt = Table(rd, colWidths=[WW * 0.3, WW * 0.7])
            rt.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), bg),
                ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 8),
                ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            elements.append(rt)
            elements.append(Spacer(1, 0.1*cm))
        elements.append(Spacer(1, 0.2*cm))

    # ══════ 第三节：反常识洞察 ══════
    elements.append(_section_hr())
    elements.append(_P('三、客户宝典 · 反常识洞察', 14, True, C_PRIMARY))
    elements.append(Spacer(1, 0.15*cm))
    insights = data.get('insights', [])
    if insights:
        hdr = [_P(h, 10, True, C_WHITE) for h in ['客户的认知/行为', '客户宝典视角', '建议调整', '参考']]
        rows = [[_P(i[k], 10) for k in ['myth', 'truth', 'advice', 'ref']] for i in insights]
        elements.append(_make_table([hdr] + rows, [3.8*cm, 3.8*cm, 3.5*cm, 1.5*cm]))
        elements.append(Spacer(1, 0.3*cm))

    # ══════ 第四节：保险配置方案 ══════
    elements.append(_section_hr())
    elements.append(_P('四、保险配置方案（分步实施）', 14, True, C_PRIMARY))
    elements.append(Spacer(1, 0.15*cm))

    # 保额建议
    coverage = data.get('coverage', [])
    if coverage:
        elements.append(_P('<b>【自动计算：保额建议】</b>', 12, True, C_ACCENT))
        elements.append(Spacer(1, 0.1*cm))
        hdr = [_P(h, 10, True, C_WHITE) for h in ['险种', '建议保额', '计算依据', '注意事项']]
        rows = [[_P(c[k], 10) for k in ['product', 'amount', 'basis', 'note']] for c in coverage]
        elements.append(_make_table([hdr] + rows, [3.2*cm, 2.5*cm, 4.0*cm, 3.8*cm], header_bg=C_ACCENT))
        elements.append(Spacer(1, 0.2*cm))

    # 保费预算
    budgets = data.get('budget_plans', [])
    if budgets:
        elements.append(_P('<b>【保费预算方案】</b>', 12, True, C_ACCENT))
        elements.append(Spacer(1, 0.1*cm))
        hdr = [_P(h, 10, True, C_WHITE) for h in ['方案档次', '年缴保费', '占收入比', '包含内容', '月均']]
        rows = [[_P(b[k], 10) for k in ['tier', 'annual', 'ratio', 'content', 'monthly']] for b in budgets]
        elements.append(_make_table([hdr] + rows, [2.8*cm, 2.2*cm, 2*cm, 4.8*cm, 2*cm]))
        elements.append(Spacer(1, 0.2*cm))

    # 分步实施
    steps = data.get('steps', [])
    if steps:
        elements.append(_P('<b>【分步实施方案】</b>', 12, True, C_ACCENT))
        elements.append(Spacer(1, 0.1*cm))
        hdr = [_P(h, 9, True, C_WHITE, TA_CENTER) for h in ['步骤', '险种', '保额', '年保费', '核心逻辑', '参考']]
        step_rows = []
        for s in steps:
            step_rows.append([
                _P(s['step'], 9, align=TA_CENTER),
                _P(_br(s['products']), 9),
                _P(_br(s['amounts']), 9),
                _P(_br(s['costs']), 9),
                _P(_br(s['logic']), 9),
                _P(s['ref'], 9),
            ])
        t = Table([hdr] + step_rows, colWidths=[1.8*cm, 4*cm, 2*cm, 2*cm, 3.4*cm, 1.5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), C_WHITE),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('LEFTPADDING', (0, 0), (-1, -1), 5),
            ('RIGHTPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_RED_BG, C_YELLOW_BG, C_GREEN_BG]),
        ]))
        elements.append(t)
        elements.append(Spacer(1, 0.3*cm))

    # ══════ 第五节：面谈话术 ══════
    talks = data.get('talk_scripts', [])
    if talks:
        elements.append(_section_hr())
        elements.append(_P('五、客户宝典 · 面谈话术参考', 14, True, C_PRIMARY))
        elements.append(Spacer(1, 0.15*cm))
        hdr = [_P(h, 10, True, C_WHITE) for h in ['场景', '关键话术']]
        talk_colors = [C_BLUE_BG, C_GREEN_BG, C_YELLOW_BG, C_RED_BG]
        data_rows = [[_P(t['scene'], 10, True, C_PRIMARY), _P(t['script'], 10)] for t in talks]
        tt = Table([hdr] + data_rows, colWidths=[3*cm, WW - 3*cm])
        tt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), C_WHITE),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), talk_colors),
        ]))
        elements.append(tt)
        elements.append(Spacer(1, 0.3*cm))

    # ═════·六、需求分析核心结论 ══════
    core_conclusions = data.get('core_conclusions', [])
    if core_conclusions:
        elements.append(_section_hr())
        elements.append(_P('六、需求分析核心结论', 14, True, C_PRIMARY))
        elements.append(Spacer(1, 0.15*cm))
        for i, c in enumerate(core_conclusions, 1):
            elements.append(_P(f'<b>{i}.</b> {_br(c)}', 10))
            elements.append(Spacer(1, 0.05*cm))
        elements.append(Spacer(1, 0.2*cm))

    # ══════ 七、核保风险提示 ══════
    uw_notes = data.get('underwriting_notes', [])
    if uw_notes:
        elements.append(_section_hr())
        elements.append(_P('七、核保风险提示', 14, True, C_PRIMARY))
        elements.append(Spacer(1, 0.15*cm))
        uw_items = uw_notes if isinstance(uw_notes, list) else [uw_notes]
        for i, note in enumerate(uw_items, 1):
            elements.append(_P(f'<b>{i}.</b> {_br(note)}', 10))
            elements.append(Spacer(1, 0.05*cm))
        elements.append(Spacer(1, 0.1*cm))
        elements.append(_P('建议：投保前先通过智能核保或预核保确认结论，避免留下拒保记录。', 10, color=C_GRAY))
        elements.append(Spacer(1, 0.2*cm))

    # ══════ 八、常见异议处理参考 ══════
    objections = data.get('objection_handling', [])
    if objections:
        elements.append(_section_hr())
        elements.append(_P('八、常见异议处理参考', 14, True, C_PRIMARY))
        elements.append(Spacer(1, 0.15*cm))
        hdr = [_P(h, 10, True, C_WHITE) for h in ['客户可能说', '应对思路']]
        rows = [[_P(_br(o['objection']), 10), _P(_br(o['response']), 10)] for o in objections]
        ot = Table([hdr] + rows, colWidths=[WW * 0.4, WW * 0.6])
        ot.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), C_PRIMARY),
            ('TEXTCOLOR', (0, 0), (-1, 0), C_WHITE),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [C_BLUE_BG, C_STRIPE]),
        ]))
        elements.append(ot)
        elements.append(Spacer(1, 0.3*cm))

    # ══════ 九、预计成交评估 ══════
    deal = data.get('deal_assessment', {})
    if deal:
        elements.append(_section_hr())
        elements.append(_P('九、预计成交评估', 14, True, C_PRIMARY))
        elements.append(Spacer(1, 0.15*cm))
        deal_items = [
            ('成交概率', deal.get('probability', '')),
            ('预计首年保费', deal.get('first_year_premium', '')),
            ('主要障碍', deal.get('obstacles', '')),
            ('突破点', deal.get('breakthroughs', '')),
            ('推荐策略', deal.get('strategy', '')),
            ('下次行动', deal.get('next_action', '')),
        ]
        dc = [[_P(f'<b>{k}</b>', 10, True, C_PRIMARY), _P(_br(v), 10)] for k, v in deal_items if v]
        dt = Table(dc, colWidths=[3.5*cm, WW - 3.5*cm])
        dt.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), C_BLUE_BG),
            ('BACKGROUND', (1, 0), (1, -1), C_STRIPE),
            ('GRID', (0, 0), (-1, -1), 0.5, C_BORDER),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        elements.append(dt)
        elements.append(Spacer(1, 0.3*cm))

    # ══════ 十、长期跟进计划 ══════
    followup = data.get('follow_up', [])
    if followup:
        elements.append(_section_hr())
        elements.append(_P('十、长期跟进计划', 14, True, C_PRIMARY))
        elements.append(Spacer(1, 0.15*cm))
        hdr = [_P(h, 10, True, C_WHITE) for h in ['时间节点', '跟进内容', '参考']]
        rows = [[_P(f[k], 10) for k in ['time', 'content', 'ref']] for f in followup]
        elements.append(_make_table([hdr] + rows, [2.5*cm, 5*cm, 3.5*cm], header_bg=C_ACCENT))
        elements.append(Spacer(1, 0.5*cm))

    # ══════ 页脚 ══════
    elements.append(HRFlowable(width='100%', thickness=1, color=C_GRAY))
    elements.append(_P(f'本报告基于《客户宝典》KYC分析工具 v3.0 生成 | 档案编号：{data["id"]} | 生成日期：{data["date"]}',
                        9, color=C_GRAY, align=TA_CENTER))
    elements.append(_P('本报告为AI辅助分析，具体产品以保险公司官方条款及核保结论为准。', 9, color=C_GRAY, align=TA_CENTER))

    doc.build(elements, onFirstPage=_add_page_number, onLaterPages=_add_page_number)
    return output_path


def _section_hr():
    """章节分隔线"""
    return HRFlowable(width='100%', thickness=1.5, color=C_PRIMARY, spaceBefore=0.2*cm, spaceAfter=0.2*cm)


# ══════════════════════════════════════
# 命令行入口：python kyc_pdf_generator.py client_data.json output.pdf
# ══════════════════════════════════════
if __name__ == '__main__':
    import sys

    # 默认用丁丁数据做演示
    demo_data = {
        "name": "丁丁",
        "id": "005",
        "date": "2026-05-16",
        "age": "45岁",
        "occupation": "夜总会驻唱歌手",
        "description": "45岁，女性，显年轻",
        "summary": [
            {"label": "核心焦虑", "value": "最怕猝死，倒下后妈妈和女儿无人照料"},
            {"label": "生命周期", "value": "成熟期（40-55岁）- 父母赡养峰值 + 自身养老窗口期"},
            {"label": "客户类型", "value": "单亲家庭 + 三明治家庭（双重特征）"},
            {"label": "风险等级", "value": "保守型 - 保障完全空白，高危风险堆积"},
            {"label": "预计首年保费", "value": "约9,200元（不含社保），月均770元"},
        ],
        "kyc_items": [
            {"label": "1. 称呼", "value": "丁丁（45岁，女性，显年轻）"},
            {"label": "2. 职业", "value": "徐汇夜总会驻场歌手，约20年经验，偶尔直播（粉丝少，变现弱）"},
            {"label": "3. 认识方式", "value": "夜总会认识，代理人主动分析，丁丁尚未主动关注保险"},
            {"label": "4. 婚姻子女", "value": "离异两次；女儿跟第一任前夫，不在身边；与小奶狗男友交往中"},
            {"label": "5. 同住人员", "value": "与母亲同住（70多岁，安徽人，高血压+高血糖+晕眩症，原早餐店个体户，无退休金，约100万存款）"},
            {"label": "6. 收入", "value": "月入8K-13K，年入约10-15万（波动收入）"},
            {"label": "7. 月度支出", "value": "约5,900-8,400元/月（中值约7,000元）"},
            {"label": "8. 资产", "value": "田林三村老破小一套（贷购，剩15年房贷）；个人存款约50万（买基金）；母亲存款约100万"},
            {"label": "9. 社保医保", "value": "丁丁无社保、无医保；母亲无职工医保，安徽可能有新农合；两人皆无商业保险"},
            {"label": "10. 健康", "value": "长期夜班颠倒生物钟，未体检，自述身体可能有隐患；母亲慢病多发"},
            {"label": "11. 性格/态度", "value": "热情奔放但不挥霍，有攒钱意识，不排斥保险但还未行动"},
            {"label": "12. 核心焦虑", "value": "怕猝死倒了妈妈没人管；女儿不在身边怕她孤僻；身体长期透支；职业不稳定；母亲无医保"},
            {"label": "13. 人生规划", "value": "想继续驻唱；已开始考虑养老；考虑未来帮女儿"},
            {"label": "14. 决策模式", "value": "可自主决策，性格不排斥保险，认同该配但未行动"},
        ],
        "client_profile": {
            "type_str": "单亲家庭（女儿不在身边但牵挂）+ 三明治家庭（上有老下有小压力），双重特征叠加。",
            "lifecycle": "成熟期（40-55岁）。关键财务责任：母亲医疗与养老、自身养老储备、女儿未来帮扶、房贷剩余15年。",
            "risk_level": "保守型。年龄45岁；收入波动大；保险认知白板。",
            "chapters": "参考《客户宝典》第6章+第7章+第9章。",
        },
        "rigid_events": [
            {"priority": "5星", "event": "丁丁本人医疗费用", "status": "无社保、无医保、无商保", "gap": "一场大病=掏空50万", "ref": "第7章"},
            {"priority": "5星", "event": "母亲医疗费用", "status": "无职工医保，仅可能有新农合", "gap": "慢病+意外均无兜底", "ref": "第7章"},
            {"priority": "5星", "event": "房贷（剩余15年）", "status": "月供约抵租金", "gap": "若收入中断无法偿还", "ref": "第8章"},
            {"priority": "4星", "event": "丁丁养老金", "status": "无社保，50万存款放基金", "gap": "缺口极大", "ref": "第9章"},
            {"priority": "4星", "event": "母亲养老（100万）", "status": "有存款但无医保", "gap": "大病迅速消耗存款", "ref": "第9章"},
            {"priority": "3星", "event": "女儿未来帮扶", "status": "有意愿但能力有限", "gap": "无专门规划", "ref": "第10章"},
        ],
        "risk_diagnosis": [
            {"level": "高危风险（需立即处理）", "color": "red",
             "items": "1. 丁丁本人：无社保+无商保+长期熬夜=医疗财务风险极高。一场大病或意外，50万存款瞬间掏空。建议：立即配置百万医疗险+含猝死责任意外险。\n\n2. 丁丁本人：无寿险，猝死焦虑最直接的风险。身故后母亲无人照料、女儿失去经济支持。建议：定期寿险150万。\n\n3. 母亲：70多岁+高血压高血糖+无医保=极高医疗风险。一场住院全部自费，100万快速消耗。建议：防癌医疗险+老年意外险。"},
            {"level": "中度风险（本月内配置）", "color": "orange",
             "items": "1. 职业不稳定，收入中断风险。45岁在夜场竞争力下降。建议：建立6个月应急金（4-5万）。\n\n2. 养老储备严重不足。45岁无社保，仅靠50万存款。建议：补缴社保或配置年金险。"},
            {"level": "潜在风险（有余力时规划）", "color": "yellow",
             "items": "1. 女儿未来经济帮扶。建议：有余力时配置教育年金。\n\n2. 母亲100万存款保值问题。建议：部分配置稳健理财或年金。"},
        ],
        "insights": [
            {"myth": "想先帮女儿，自己养老还没规划", "truth": "养老是生存问题，女儿帮扶是发展问题，生存优先", "advice": "先确保自己养老储备，不成为女儿负担", "ref": "第10章"},
            {"myth": "50万存款买基金，没上社保", "truth": "社保是基础，商保是补充", "advice": "先补缴灵活就业社保，再谈其他投资", "ref": "第7章"},
            {"myth": "母亲100万全存银行防老", "truth": "通胀让购买力缩水；无医保兜底", "advice": "用防癌医疗险+意外险兜底", "ref": "第6章"},
            {"myth": "保险是亏本的，先不急", "truth": "保险买的是关键时刻的保障价值", "advice": "用意外险（含猝死）300元/年破冰", "ref": "第7章"},
        ],
        "coverage": [
            {"product": "意外险（含猝死）", "amount": "100万", "basis": "10倍年收入（保守值）", "note": "最高200万，选含猝死责任产品"},
            {"product": "百万医疗险", "amount": "基础档/约100万级", "basis": "覆盖大病医疗支出", "note": "优先核对续保、免赔、医院和用药责任"},
            {"product": "定期寿险", "amount": "150万", "basis": "房贷+母亲赡养+女儿帮扶", "note": "最高300万，保至60岁"},
            {"product": "防癌医疗险（母亲）", "amount": "200-300万", "basis": "70岁可投，三高可投", "note": "防癌专属，健告宽松"},
            {"product": "养老年金（丁丁）", "amount": "月领3,000-5,000", "basis": "月支出的50-70%", "note": "无社保情况下需更高"},
        ],
        "budget_plans": [
            {"tier": "基础版（立即）", "annual": "约8,200元", "ratio": "6.4%", "content": "意外险+医疗险+母亲防癌险+意外险", "monthly": "约680元"},
            {"tier": "标准版（+寿险）", "annual": "约12,200元", "ratio": "9.7%", "content": "基础版+定期寿险150万", "monthly": "约1,020元"},
            {"tier": "充足版（+社保+养老）", "annual": "约32,200元", "ratio": "25.7%", "content": "标准版+社保+养老储备", "monthly": "约2,680元"},
        ],
        "steps": [
            {"step": "第一步（立即）", "products": "丁丁：意外险（含猝死）\n丁丁：百万医疗险\n母亲：防癌医疗险\n母亲：老年意外险",
             "amounts": "100万\n约100万级\n300万\n20万", "costs": "约300元\n约2,000元\n约2,500元\n约400元",
             "logic": "猝死焦虑破冰\n大病不掏存款\n三高可投保\n骨折保障", "ref": "第7章"},
            {"step": "第二步（本月内）", "products": "丁丁：定期寿险\n丁丁：灵活就业社保",
             "amounts": "150万\n养老+医疗", "costs": "约4,000元\n约20,000元",
             "logic": "身故赔给妈妈和女儿\n社保是基础", "ref": "第7章"},
            {"step": "第三步（有余力）", "products": "丁丁：养老年金",
             "amounts": "月领3,000+", "costs": "约20,000元",
             "logic": "养老窗口期即将关闭", "ref": "第9章"},
        ],
        "talk_scripts": [
            {"scene": "开场破冰", "script": '"你觉得猝死是最怕的事，那我们就先把这件事兜住。一年300块，每天不到一块钱，万一有什么事，保险公司赔100万给妈妈和女儿。"'},
            {"scene": "痛点唤醒（母亲）", "script": '"你妈妈70多岁了，有高血压高血糖，如果突发脑中风，一场住院十几万，她那100万存款要花掉多少？防癌医疗险专门为三高人群设计，一年两千多，换300万报销。"'},
            {"scene": "养老唤醒", "script": '"客户宝典里说：一个人真正能攒钱的年份，只有30岁到45岁。你现在45岁，正好在边界线上。如果今年开始每年存2万，60岁每月领3000；再等5年，每年要交4万。"'},
            {"scene": "异议处理（太贵）", "script": '"医疗先选能覆盖大额支出的基础档，重点看续保、免赔和用药，不为了数字好看堆保额。长期资金再按养老和家庭责任分步安排。"'},
        ],
        "follow_up": [
            {"time": "成交后1个月", "content": "协助办理灵活就业社保；确认体检安排", "ref": "第7章"},
            {"time": "成交后3个月", "content": "推进定期寿险（150万）；检视母亲防癌险", "ref": "第7章"},
            {"time": "成交后6个月", "content": "启动养老年金规划；检视基金持仓", "ref": "第9章"},
            {"time": "每年续保时", "content": "保单检视；母亲身体状况更新", "ref": "全生命周期"},
            {"time": "丁丁50岁时", "content": "养老储备中期检视，必要时加大缴费", "ref": "第9章"},
        ],
    }

    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.getcwd(), '丁丁_KYC客户经营分析报告.pdf')
    result = generate_kyc_pdf(demo_data, out)
    print(f'PDF OK: {result}')
