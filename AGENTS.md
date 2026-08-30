---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '6a8653b3-5184-46e1-b6a0-3b7ecbfa0af8'
  PropagateID: '6a8653b3-5184-46e1-b6a0-3b7ecbfa0af8'
  ReservedCode1: 'b724d887-0e94-450b-866f-40946d0be997'
  ReservedCode2: 'b724d887-0e94-450b-866f-40946d0be997'
---

# AGENTS.md — 金融日报项目

> 项目入口目录。AI 接到金融日报任务时，先读本文件，再按需加载具体规格。
> 详细文档放 SDD/ 下，本文件只做索引（Lost in the Middle：重要规则在首尾）。

## 项目背景

面向中国白领的每日金融信号简报（商用标准）。核心原则：数据可追溯、解读大白话、预测有台账。每期覆盖 11 项信号，8 组联网搜索，双源交叉验证，输出 HTML+docx 双格式。

## 文件地图

| 需要什么 | 去哪找 |
|---------|--------|
| 最高约束（来源/验证/置信度/边界） | `SDD/01-Constitution.md` |
| 数据格式（11信号/8组关键词/占位符） | `SDD/02-Spec.md` |
| 执行流程（采集→验证→生成→校验+反馈循环） | `SDD/03-Plan.md` |
| 任务清单（T1-T10+Token预算） | `SDD/04-Tasks.md` |
| SDD 总索引 | `SDD/README.md` |
| 搜索关键词+来源评级（v2.0） | `../.config/TeleAgent/skills/finance-digest/references/search-config.md` |
| 预测台账规则 | `../.config/TeleAgent/skills/finance-digest/references/prediction-ledger.md` |
| 术语题库 | `../.config/TeleAgent/skills/finance-digest/references/terms-bank.md` |
| HTML 模板 | `../.config/TeleAgent/skills/finance-digest/assets/finance-template.html` |
| 卡片生成脚本 | `../.config/TeleAgent/skills/finance-digest/scripts/gen_cards.py` |
| 预测台账数据 | `台账/预测台账.md` |
| 历史日报 | `YYYY-MM-DD/` 目录 |

## 执行入口

1. 确认日期 → 创建 `YYYY-MM-DD/` 目录
2. 读 `SDD/03-Plan.md` 第1节，按 P1-P5 执行
3. 搜索关键词从 `SDD/02-Spec.md` 第2节取
4. 每条数值必须对照 `01-Constitution.md` 第2-3节验证
5. 生成 HTML（模板+gen_cards.py）→ docx（md_to_js.py→node）
6. 自检：对照 `03-Plan.md` 第5节清单，不通过则修复重跑（上限3次）

## 禁止事项（首尾位置高优）

- 禁止凭记忆输出数值（必须联网验证）
- 禁止编造来源/机构/分析师
- 禁止预测值混作实际值
- 禁止 B/C 级单源标 ✅已验证
- 禁止输出未登记台账的方向性断言
- 禁止跳过8组搜索中的任何一组

## 常用命令

```powershell
# docx 生成（两步）
$env:PYTHONUTF8 = "1"
python "...\skills\docx\scripts\md_to_js.py" --input <md> --output <js> --docx-output <docx>
node <js>
```

## Token 预算（速查）

系统10% / 用户15% / 检索40% / 历史25% / 工具10%
检索是最大投入，禁止冗余搜索；历史只取台账摘要+上期要点。

> AI生成