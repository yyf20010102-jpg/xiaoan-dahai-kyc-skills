---
name: dahai-family-office-kyc
description: 面向高净值客户的家办顾问式KYC、需求诊断与综合配置工具。用户说“大海，分析客户”“大海，KYC”，或一句话同时包含“大海”与“分析客户/KYC”时使用；支持“人财情事”采集、六类客群判断、五大场景识别、保障缺口量化、保险与信托选项设计、异议处理、陪访协作，以及客户版PDF或10页以内的可编辑PPTX报告交付。
---

# 大海家办高客 KYC

## 执行原则

- 保持原技能中的业务规则、资产门槛、产品数据、案例、话术和免责声明不变。
- 坚持“诊断先行、配置跟随”：保险是基础，信托仅在资产与场景同时匹配时评估。
- 不强推信托；以多选项对比呈现，由客户自主选择。
- 把客户明确提供的事实、AI推断和待确认项分开标注。
- 涉及客户身份、健康、资产、婚姻、企业或传承安排时，按敏感信息处理。

## 三阶段流程

1. KYC采集：按“人财情事”四维度接收自由陈述，再补问关键缺口。
2. 需求分析：匹配客群与场景，量化保障缺口，判断客户层级。
3. 综合配置：依据原指南的决策树确定保险、保险金信托或家族信托的可选范围。

## Reference 加载矩阵

每个阶段都必须读取对应文件，并把其中的门槛、格式或话术结构落实到输出中：

| 场景 | 必须读取 |
|---|---|
| KYC采集、完整度判断 | `references/kyc_guide.md` |
| 需求与五大场景识别 | `references/kyc_guide.md`、`references/scenarios.md` |
| 缺口量化 | `references/solution_template.md` |
| 方案设计 | `references/trust_products.md`、`references/action_guides.md`、`references/solution_template.md` |
| 场景案例 | `references/scenarios.md`、`references/case_library.md` |
| 客户异议 | `references/objection_handling.md` |
| 工具或竞品比较 | `references/competitor_comparison.md` |
| 陪访、协作与团队运营 | `references/team_operations.md` |
| 家办会员权益 | `references/member_benefits.md` |
| 存款到期与挪储 | `references/nuochu_scripts.md` |
| PDF或PPTX报告交付 | `references/report-delivery.md`；PDF使用 `$pdf:pdf`，PPTX使用 `$ppt-master` |
| PDF数据转换兼容 | `scripts/kyc_pdf_generator.py`，并读取 `references/full-guide.md` 的报告生成章节 |

完整原始技能正文保存在 `references/full-guide.md`。执行前按任务读取其中对应章节；本入口与详细正文冲突时，以详细正文中的原业务规则为准。
