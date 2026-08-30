---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: 'fb6260ca-42c8-43ef-8359-642bb4b9e488'
  PropagateID: 'fb6260ca-42c8-43ef-8359-642bb4b9e488'
  ReservedCode1: '21164f09-568b-4d8a-8419-3ba47acb9d39'
  ReservedCode2: '21164f09-568b-4d8a-8419-3ba47acb9d39'
---

# 金融日报 SDD 四层规格 · 索引

> 生成日期：2026-08-24 ｜ 依据：方法论精华提取「最值得立刻做的5件事·第2件」
> 用途：把金融日报规范从"人看的文档"升级为"AI可执行的四层规格"，配合 Token 预算管理压缩搜索空间。

---

## 四层结构（自上而下约束）

| 层 | 文件 | 内容 | 作用 |
|----|------|------|------|
| 宪法 | [01-Constitution.md](01-Constitution.md) | 核心原则、来源优先级、交叉验证硬规则、置信度标准、数据边界、Token总纲 | 最高约束，冲突时以此为准 |
| 规格 | [02-Spec.md](02-Spec.md) | 11信号采集格式、8组搜索关键词、JSON结构、HTML占位符、交付格式 | 定义"每样东西长什么样" |
| 流程 | [03-Plan.md](03-Plan.md) | 采集→验证→格式化→生成→校验五阶段 + 反馈循环 | 定义"怎么一步步做" |
| 任务 | [04-Tasks.md](04-Tasks.md) | T1-T10具体采集任务、Token预算管理 | 定义"每个数据源具体采什么" |
| 预检 | [06-QuickStart-Checklist.md](06-QuickStart-Checklist.md) | 6问30秒预判、执行模式选择（全量/精简/事件/降级）、路由快捷表 | **搜索前必读**，判断跳哪些搜索 |
| 路由 | [05-Routing-Analysis.md](05-Routing-Analysis.md) | Anthropic路由模式分析、6类路由分类 | 优化参考文档 |

## 分层关系

```
01-Constitution（为什么/边界）
      ↓ 约束
02-Spec（什么格式）
      ↓ 依据
03-Plan（怎么做）
      ↓ 执行
04-Tasks（具体任务清单）
```

## 与现有体系的关系

- 现有 `skills/finance-digest/references/search-config.md`（v2.0）→ 被 **02-Spec** 吸收扩展（8组关键词、来源评级、降级策略）
- 现有 `skills/finance-digest/references/prediction-ledger.md` → 继续作为台账详细规则，**02-Spec §5** 引用之
- 现有 `assets/finance-template.html` + `scripts/gen_cards.py` → **02-Spec §3** 定义占位符与卡片格式
- 本 SDD 四层是**规格的总纲**，skill 的 SKILL.md 为**执行入口**

## 使用方式

1. **AI 生成日报时**：先读 06-QuickStart-Checklist 做6问预判 → 按需加载本 SDD 四层（Constitution/Spec 常驻，Plan/Tasks 按需）
2. **人工维护时**：改这里的规格即可，不用改 SKILL.md
3. **冲突处理**：SKILL.md 与 SDD 冲突时，**以 SDD 的 01-Constitution 为准**（宪法优先）

## Token 预算速查（Context Engineering）

| 环节 | 占比 | 内容 |
|------|------|------|
| 系统 | 10% | Constitution/Spec 常驻 |
| 用户 | 15% | 指令+日期 |
| 检索 | 40% | 8组搜索+交叉验证 |
| 历史 | 25% | 台账摘要+上一期要点 |
| 工具 | 10% | 文件读写+HTML |

## 文件清单

```
每日金融快讯/SDD/
├── README.md                    ← 本索引
├── 01-Constitution.md           ← 宪法层
├── 02-Spec.md                    ← 规格层
├── 03-Plan.md                    ← 流程层
├── 04-Tasks.md                   ← 任务层
├── 05-Routing-Analysis.md        ← 路由分析（Anthropic 5大模式）
└── 06-QuickStart-Checklist.md    ← 预检清单（搜索前必读）
```

> AI生成