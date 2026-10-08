---
name: customer-archive-manager
description: 管理大海和小安的客户KYC档案。用户要求新增、保存、查询、调取、修改、更新、删除、筛选、统计、导出或备份客户档案时使用；支持自动编号、按编号或姓名查询、跟进状态维护及Markdown档案归档。
---

# 客户档案管理

## 数据边界

- 客户档案含身份、健康、收入、资产、负债和家庭关系等敏感信息。
- 只处理用户明确指定的客户与字段；展示列表时优先输出必要摘要。
- 修改或删除前先确认目标档案；不要凭模糊姓名覆盖已有档案。
- 保留原有编号、字段、状态和历史记录，不擅自补写未知事实。

## 操作流程

1. 读取 `references/full-guide.md` 中与请求对应的操作章节。
2. 使用 `references/cases/archived/档案索引.md` 定位档案；名称冲突时以编号为准。
3. 新增时按原编号规则创建Markdown档案，并同步索引。
4. 修改时记录原值、新值和修改时间；未授权字段保持不变。
5. 查询或统计时仅读取必要档案，按原模板输出。
6. 导出或备份时保留Markdown格式和档案结构。

## 资源

- 完整操作规范与档案模板：`references/full-guide.md`
- 档案索引：`references/cases/archived/档案索引.md`
- 已归档客户：`references/cases/archived/`

原指南中的 `cases/archived/` 与 `cases/backup/`，在优化版中分别对应 `references/cases/archived/` 与 `references/cases/backup/`，其余业务内容不变。
