---
AIGC:
  ContentProducer: '001191110102MAD55U9H0F10002'
  ContentPropagator: '001191110102MAD55U9H0F10002'
  Label: '1'
  ProduceID: '42bbfb71-b77e-4232-9a50-06f3dd2842e5'
  PropagateID: '42bbfb71-b77e-4232-9a50-06f3dd2842e5'
  ReservedCode1: '91123f3a-97cc-43cd-aa59-98bdccb4f31a'
  ReservedCode2: '91123f3a-97cc-43cd-aa59-98bdccb4f31a'
---

# 金融日报 SDD · 02-Spec 规格层

> 版本：v1.0 ｜ 生效日期：2026-08-24 ｜ 归属：finance-digest 技能
> 本文件定义**每个数据源的采集格式、表格结构、信号卡片与占位符规范**。冲突时以 01-Constitution 为准。

---

## 1. 11 项信号采集规格（每条信号一个数据块）

每条信号必须产出以下 **5 个字段**（缺一不可）：

| 字段 | 说明 | 示例 |
|------|------|------|
| 硬数据表 | 指标名+数值+时间口径，2-4行 | `上证指数 3,412.88 (+0.42%) 8/21收盘` |
| 大白话解读 | 1-2句非金融读者能懂的解释 | "今天A股小幅上涨，主要是新能源板块带动" |
| 机构观点 | 1条机构引用：机构名+分析师名 | "中金公司王xx：……" |
| 信源区 | 2-3个可点击URL+等级+发布时间(到分钟) | `S级 8/21 15:02 国家统计局` |
| 可信度标签 | ✅已验证 / ⚠️待确认 | 依据01-Constitution第3节判定 |

### 各信号数据要点（采集口径）

| # | 信号 | 必须采集的硬数据 | 备注 |
|---|------|-----------------|------|
| 1 | A股 | 上证/深成/创业板收盘+涨跌幅；两市成交额 | 非交易日用最近交易日 |
| 2 | 汇率 | 中间价/在岸/离岸 USDCNY；变动幅度 | 中国外汇交易中心为S级 |
| 3 | LPR | 1年期/5年期LPR；下次报价日 | 每月20日公布，头条级 |
| 4 | 国债收益率 | 10Y/30Y国债收益率；Shibor | 注意"收益率上行=价格下行" |
| 5 | 原油 | WTI/布伦特价格；涨跌幅 | 注意地缘事件驱动 |
| 6 | 黄金 | 现货金价；当日区间；催化剂 | 美联储预期是主变量 |
| 7 | 铜价 | LME铜价；涨跌幅 | 经济晴雨表 |
| 8 | 美联储 | 加息/降息概率（CME FedWatch）；CPI/非农 | 概率必须标"预测值" |
| 9 | 宏观数据 | CPI/PPI/PMI/社融/M2/贷款 | 必须标注发布日期+统计区间 |
| 10 | 资金面 | 两融余额；北向资金；主力资金 | 北向实时数据已暂停披露则以公告口径 |
| 11 | 央行操作 | 逆回购/MLF/买断式逆回购；净投放量 | S级：央行官网 |

---

## 2. 8 组搜索规格（关键词 + 时间过滤 + 优先级）

| # | 信号组 | 关键词模板（{{TODAY_DATE}}替换为当天日期） | 时间过滤 | 优先级 |
|---|--------|-------------------------------------------|---------|--------|
| 1 | A股核心组 | `A股 上证指数 深证成指 创业板 行情 收盘 {{TODAY_DATE}}` | week | 高 |
| 2 | 汇率组 | `人民币汇率 美元兑人民币 在岸 离岸 中间价 {{TODAY_DATE}}` | week | 高 |
| 3 | 利率组 | `LPR MLF 逆回购 国债收益率 央行 {{TODAY_DATE}}` | month | 高 |
| 4 | 大宗组 | `大宗商品 原油 WTI 黄金 铜价 期货 {{TODAY_DATE}}` | week | 中 |
| 5 | 海外组 | `美联储 议息 加息 降息 美债 美股 {{TODAY_DATE}}` | week | 中 |
| 6 | 宏观组 | `中国 CPI PPI PMI 社融 M2 进出口 {{TODAY_DATE}}` | month | 中 |
| 7 | 资金组 | `北向资金 两融余额 主力资金 成交量 {{TODAY_DATE}}` | week | 中 |
| 8 | 政策组 | `金融政策 监管 降准 降息 财政 部委 发布 {{TODAY_DATE}}` | month | 低 |

**搜索轮次铁律**：每轮最多并发 2 个搜索；R1-R4 按顺序跑完 8 组，R5 为头条交叉验证+事件日历补充。

---

## 3. 采集数据格式（供 03-Plan 与 04-Tasks 使用）

采集到的数据按以下 JSON 结构组织（输出前转换为人话）：

```json
{
  "signal": 1,
  "name": "A股",
  "category": "股市",
  "data_rows": [
    {"metric": "上证指数", "value": "3,412.6", "change": "+0.42%", "period": "8/21收盘"}
  ],
  "plain_text": "……",
  "institution": {"org": "中金公司", "analyst": "王xx", "view": "……"},
  "sources": [
    {"url": "…", "grade": "S", "time": "8/21 15:02", "org": "国家统计局"}
  ],
  "credibility": "verified | pending"
}
```

---

## 3. 交付物格式规范

### 3.1 目录与命名

```
每日金融快讯/
├── YYYY-MM-DD/                    # 每期目录（ISO日期）
│   ├── 每日金融快讯_YYYYMMDD.html # 网页版（最终交付）
│   └── 每日金融快讯_YYYYMMDD.docx # Word存档版（最终交付）
├── SDD/                           # 本规格（4+1文件）
├── 台账/预测台账.md                # 预测台账
├── 知识库/                         # 搜索源配置、术语题库
└── 模板/                           # 模板存档
```

### 3.2 HTML 占位符（与 assets/finance-template.html 对应）

| 占位符 | 内容 |
|--------|------|
| `{{REPORT_DATE_CN}}` | 报告日期（2026年8月17日 周一） |
| `{{REPORT_DATE}}` | ISO日期（2026-08-17） |
| `{{DATA_DEADLINE}}` | 数据截至时间 |
| `{{NEXT_ISSUE}}` | 下一期日期 |
| `{{QUOTE_TEXT}}`/`{{QUOTE_SOURCE}}` | 每日金句 |
| `{{KEY_POINTS}}` | 今日要点（<li>列表） |
| `{{TRENDS}}` | 本周趋势标签 |
| `{{SIGNAL_CARDS}}` | 11张信号卡片 |
| `{{BACKTEST}}` | 历史预测回测块 |
| `{{SOURCE_SUMMARY}}` | 来源汇总表 |
| `{{RATE_ANCHORS}}` | 利率锚点表 |
| `{{TIPS_CARDS}}` | 每日术语 |
| `{{EVENTS}}` | 事件日历 |
| `{{POLICY_ITEMS}}` | 政策速递 |
| `{{STATS}}` | 数据源统计 |

### 3.3 信号卡片格式（gen_cards.py card()函数）

```python
from gen_cards import card, sources, inst_view
html = card(num, cat, title, lamp, lamp_text, table_rows, plain, cred_class, cred_text, inst_html, src_html)
```

| 参数 | 取值 |
|------|------|
| cat | 股市/汇率/利率/大宗/海外/宏观/资金面 |
| lamp | green（利好/走强）/ yellow（震荡/中性）/ red（偏热/风险） |
| cred_class | credibility-high / credibility-medium |

### 3.4 docx 存档版格式

1. 与 HTML 同内容（含机构观点、信源、免责声明）
2. 转换链路：Markdown源稿 → `md_to_js.py` → JS → `node` → docx
3. 命令模板：

```powershell
$env:PYTHONUTF8 = "1"
python "C:\Users\Administrator\.config\TeleAgent\skills\docx\scripts\md_to_js.py" --input <md> --output <js> --docx-output <docx>
node <js>
```

---

## 4. 来源汇总表（HTML页脚必带）

| 来源等级 | 来源机构 | 引用内容 | 发布时间 | 链接 |
|---------|---------|---------|---------|------|
| S | 国家统计局 | 7月CPI同比+2.1% | 8/09 09:30 | url |
| A | 财联社 | LPR维持不变 | 8/20 09:15 | url |

**页脚必须包含**：
1. 来源汇总表（全信源按等级分组）
2. 免责声明 5 条（报告性质/数据说明/预测说明/风险提示/来源等级说明）
3. 数据源统计行：如"8组关键词搜索 · 5轮交叉验证 · S级来源6个 · A级来源9个"

---

## 5. 预测台账格式（登记/回测）

预测登记三维度：**方向**（涨/跌/区间/不变）＋ **点位/时点**（如"上证挑战4150"）＋ **断言强度**（强/中/弱）。

回测判定：✅命中 / 🟡部分命中 / ❌未命中，回测时注明"原预测→实际→判定→偏差原因"。

> 台账文件：`每日金融快讯/台账/预测台账.md`（详细规则见 references/prediction-ledger.md）

> AI生成