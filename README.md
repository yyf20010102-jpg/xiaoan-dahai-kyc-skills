# Xiaoan & Dahai KYC Skills

一组面向保险顾问、家庭财务规划与家族办公室场景的 AI Skills。仓库采用标准 `SKILL.md` 目录结构，可在 Codex 中直接安装，也可供其他支持 Markdown 指令或 Agent Skills 的 AI 工具读取使用。

## 包含内容

| Skill | 用途 |
|---|---|
| `xiaoan-kyc` | 普通家庭 KYC、风险保障与长期现金流规划 |
| `dahai-family-office-kyc` | 高净值客户、家企风险、家办与家族信托规划 |
| `customer-archive-manager` | 本地 Markdown 客户档案的新增、查询、更新、筛选与导出 |
| `insurance-pdf-generator` | 保险规划 PDF 生成的版式和中文字体兼容指引 |

## Codex 安装

将 `skills/` 下需要的文件夹复制到：

```text
~/.codex/skills/
```

重启 Codex 或新建会话后，可以显式调用：

```text
$xiaoan-kyc
$dahai-family-office-kyc
$customer-archive-manager
$insurance-pdf-generator
```

## 其他 AI 工具

如果平台支持 Agent Skills，将对应 Skill 目录导入即可。如果不支持自动加载，先让 AI 完整读取该目录的 `SKILL.md`，再按其中的路由指引按需读取 `references/` 内容。

PDF 和 PPTX 是交付工具层能力：

- 默认 KYC 报告交付 PDF。
- 用户明确要求 PPT/PPTX 时，交付 10 页以内的可编辑演示文稿。
- 仓库中的 `$pdf:pdf` 和 `$ppt-master` 是 Codex 工具路由名；其他 AI 可替换为自身的 PDF/PPTX 生成工具，但应保留内容结构与校验规则。

## 规划原则摘要

- 根据客户家庭背景决定优先级，不使用固定套餐。
- 家庭中有孩子或老人时，重点评估年金、养老、分红与长期现金流。
- 医疗险额度需与实际风险、就医目标和预算匹配，避免不必要的过高配置。
- 长期储蓄可评估8年缴分红险和万能账户的组合，必须区分保证与非保证利益。
- 输出是教育与规划材料，不代替具体产品条款、法律、税务或医疗意见。

## 隐私

本公开版不包含真实客户档案。请勿将姓名、电话、证件号、完整住址、账户号、病历原文或企业机密提交到公开仓库。详见 [PRIVACY.md](PRIVACY.md)。

