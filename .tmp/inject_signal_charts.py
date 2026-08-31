# -*- coding: utf-8 -*-
"""
批量注入信号灯看板+Chart.js趋势图到9期正式版HTML
插入位置：summary-trends-box 闭合后、filter-bar/toc-nav 之前
"""
import json, re, os, glob

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARCHIVES = os.path.join(REPO, "archives")
DATA_FILE = os.path.join(os.path.dirname(__file__), "finance_data.json")

with open(DATA_FILE, "r", encoding="utf-8") as f:
    TS_DATA = json.load(f)

# 期次映射：日期 -> 文件名
DATE_FILE_MAP = {
    "2026-08-17": "每日金融快讯_20260817.html",
    "2026-08-20": "每日金融快讯_20260820.html",
    "2026-08-21": "每日金融快讯_20260821.html",
    "2026-08-23": "每日金融快讯_20260823.html",
    "2026-08-25": "每日金融快讯_20260825.html",
    "2026-08-26": "每日金融快讯_20260826.html",
    "2026-08-27": "每日金融快讯_20260827.html",
    "2026-08-28": "每日金融快讯_20260828.html",
    "2026-08-30": "每日金融快讯_20260830.html",
}

# 信号配置
SIGNALS = [
    {"name": "A股上证",   "key_val": "sse_close",    "key_chg": "sse_change",    "unit": "点",   "red_thr": 1.0,  "yellow_thr": 0.3},
    {"name": "创业板",   "key_val": "chinext_close", "key_chg": "chinext_change", "unit": "点",   "red_thr": 1.0,  "yellow_thr": 0.3},
    {"name": "人民币",   "key_val": "cny_midpoint",  "key_chg": None,             "unit": "",     "red_thr": 0.01, "yellow_thr": 0.003, "special": "fx"},
    {"name": "LPR利率",  "key_val": "lpr_1y",        "key_chg": None,             "unit": "%",    "red_thr": 0,    "yellow_thr": 0,    "special": "lpr"},
    {"name": "10年国债",  "key_val": "cn_10y_yield",  "key_chg": None,             "unit": "%",    "red_thr": 0.05, "yellow_thr": 0.02},
    {"name": "Shibor",   "key_val": "shibor_overnight","key_chg": None,           "unit": "%",    "red_thr": 0.1,  "yellow_thr": 0.05},
    {"name": "现货黄金",  "key_val": "gold_spot",     "key_chg": None,             "unit": "$/oz", "red_thr": 2.0,  "yellow_thr": 0.5},
    {"name": "布伦特油",  "key_val": "brent_oil",     "key_chg": None,             "unit": "$/bbl","red_thr": 2.0,  "yellow_thr": 0.5},
    {"name": "LME铜",    "key_val": "lme_copper",    "key_chg": None,             "unit": "$/t",  "red_thr": 1.0,  "yellow_thr": 0.3},
    {"name": "美元指数",  "key_val": "dollar_index",  "key_chg": None,             "unit": "",     "red_thr": 0.5,  "yellow_thr": 0.2},
    {"name": "美股道指",  "key_val": "dow_jones",     "key_chg": None,             "unit": "点",   "red_thr": 0.5,  "yellow_thr": 0.2},
]

def get_ts_index(date_str):
    """找到 date_str 在 TS_DATA 中的索引"""
    for i, d in enumerate(TS_DATA):
        if d["date"] == date_str:
            return i
    return -1

def format_value(val, unit):
    """格式化数值显示"""
    if val is None:
        return "—"
    if isinstance(val, float):
        if unit == "%":
            return f"{val:.3f}%"
        elif unit == "点":
            return f"{val:,.2f} 点"
        elif unit == "$/oz":
            return f"{val:,.2f} $/oz"
        elif unit == "$/bbl":
            return f"{val:.2f} $/bbl"
        elif unit == "$/t":
            return f"{val:,.1f} $/t"
        elif unit == "":
            return f"{val:.4f}"
        else:
            return f"{val}"
    return str(val)

def get_lamp_and_change(curr_data, prev_data, signal):
    """计算信号灯颜色和变化值"""
    key = signal["key_val"]
    curr_val = curr_data.get(key)
    prev_val = prev_data.get(key) if prev_data else None
    
    if curr_val is None:
        return "gray", None, "数据缺失"
    
    # 特殊处理 LPR
    if signal.get("special") == "lpr":
        lpr1 = curr_data.get("lpr_1y")
        lpr5 = curr_data.get("lpr_5y")
        lpr1p = prev_data.get("lpr_1y") if prev_data else None
        lpr5p = prev_data.get("lpr_5y") if prev_data else None
        if lpr1 is not None and lpr5 is not None:
            val_str = f"{lpr1}/{lpr5}%"
            if lpr1p is not None and lpr5p is not None and lpr1 == lpr1p and lpr5 == lpr5p:
                return "gray", 0, "持平"
            elif lpr1p is not None and lpr5p is not None:
                if lpr1 != lpr1p or lpr5 != lpr5p:
                    return "red", None, "LPR调整"
            return "gray", 0, "持平"
        return "gray", None, "数据缺失"
    
    if prev_val is None or prev_val == curr_val:
        return "gray", 0, "持平"
    
    # 计算变化百分比
    if signal.get("special") == "fx":
        # 人民币：数值下降=升值
        diff = curr_val - prev_val
        pct = (diff / prev_val) * 100
        if abs(pct) < signal["yellow_thr"]:
            return "gray", 0, "持平"
        if abs(pct) >= signal["red_thr"]:
            return "red", pct, "↑升值" if diff < 0 else "↓贬值"
        return "yellow", pct, "↑升值" if diff < 0 else "↓贬值"
    
    # 通用处理
    pct = ((curr_val - prev_val) / prev_val) * 100
    if abs(pct) < signal["yellow_thr"]:
        return "gray", 0, "基本持平"
    if abs(pct) >= signal["red_thr"]:
        return "red", pct, "重大变化"
    return "yellow", pct, "小幅波动"

def build_signal_dashboard_html(curr_data, prev_data):
    """构建信号灯看板HTML"""
    rows_html = ""
    for s in SIGNALS:
        lamp, change, note = get_lamp_and_change(curr_data, prev_data, s)
        key = s["key_val"]
        
        # 数值显示
        if s.get("special") == "lpr":
            lpr1 = curr_data.get("lpr_1y")
            lpr5 = curr_data.get("lpr_5y")
            val_str = f"{lpr1}/{lpr5}%" if lpr1 is not None else "—"
        else:
            val_str = format_value(curr_data.get(key), s["unit"])
        
        # 变化显示
        if change is None:
            if note == "LPR调整":
                change_str = '<span class="sig-change" style="color:var(--signal-red)">LPR调整</span>'
            elif note == "数据缺失":
                change_str = '<span class="sig-change flat">—</span>'
            else:
                change_str = '<span class="sig-change flat">持平</span>'
        elif change == 0:
            change_str = '<span class="sig-change flat">持平</span>'
        elif s.get("special") == "fx":
            color = "var(--signal-green)" if "升值" in note else "var(--signal-red)"
            change_str = f'<span class="sig-change" style="color:{color}">{note}</span>'
        else:
            sign = "+" if change > 0 else ""
            color = "var(--signal-red)" if change > 0 else "var(--signal-green)"
            change_str = f'<span class="sig-change" style="color:{color}">{sign}{change:.2f}%</span>'
        
        note_color = {"red": "var(--signal-red)", "yellow": "var(--signal-yellow)", "gray": "var(--text-tertiary)"}[lamp]
        rows_html += f'''      <div class="sig-row">
        <span class="sig-lamp {lamp}"></span>
        <span class="sig-name">{s["name"]}</span>
        <span class="sig-value">{val_str}</span>
        {change_str}
        <span class="sig-note" style="color:{note_color}">{note}</span>
      </div>
'''
    
    return f'''    <!-- 信号灯看板 -->
    <div class="signal-dashboard">
      <div class="sig-dashboard-header">
        <span>信号灯看板</span>
        <span class="sig-dashboard-hint">红=重大变化 黄=小幅波动 灰=基本持平</span>
      </div>
{rows_html}    </div>

'''

def build_charts_html(curr_idx, curr_data):
    """构建4张Chart.js mini趋势图HTML"""
    # 准备时间序列数据（从开始到当前期）
    ts_subset = TS_DATA[:curr_idx + 1]
    labels = [d["date"][-5:] for d in ts_subset]  # MM-DD
    sse_data = [d.get("sse_close") for d in ts_subset]
    gold_data = [d.get("gold_spot") for d in ts_subset]
    fx_data = [d.get("cny_midpoint") for d in ts_subset]
    brent_data = [d.get("brent_oil") for d in ts_subset]
    
    curr_sse = curr_data.get("sse_close")
    curr_gold = curr_data.get("gold_spot")
    curr_fx = curr_data.get("cny_midpoint")
    curr_brent = curr_data.get("brent_oil")
    
    return f'''    <!-- 趋势图表 -->
    <div class="sig-charts-grid">
      <div class="sig-chart-card">
        <div class="sig-chart-header"><span>A股上证</span>
          <span><span class="sig-chart-value">{format_value(curr_sse, "点") if curr_sse else "—"}</span></span>
        </div>
        <div class="sig-chart-container"><canvas id="sseMiniChart"></canvas></div>
      </div>
      <div class="sig-chart-card">
        <div class="sig-chart-header"><span>现货黄金</span>
          <span><span class="sig-chart-value">{format_value(curr_gold, "$/oz") if curr_gold else "—"}</span></span>
        </div>
        <div class="sig-chart-container"><canvas id="goldMiniChart"></canvas></div>
      </div>
      <div class="sig-chart-card">
        <div class="sig-chart-header"><span>人民币中间价</span>
          <span><span class="sig-chart-value">{format_value(curr_fx, "") if curr_fx else "—"}</span></span>
        </div>
        <div class="sig-chart-container"><canvas id="fxMiniChart"></canvas></div>
      </div>
      <div class="sig-chart-card">
        <div class="sig-chart-header"><span>布伦特原油</span>
          <span><span class="sig-chart-value">{format_value(curr_brent, "$/bbl") if curr_brent else "—"}</span></span>
        </div>
        <div class="sig-chart-container"><canvas id="oilMiniChart"></canvas></div>
      </div>
    </div>
'''

def build_chart_js(curr_idx):
    """构建Chart.js初始化脚本"""
    ts_subset = TS_DATA[:curr_idx + 1]
    labels = json.dumps([d["date"][-5:] for d in ts_subset], ensure_ascii=False)
    sse_data = json.dumps([d.get("sse_close") for d in ts_subset])
    gold_data = json.dumps([d.get("gold_spot") for d in ts_subset])
    fx_data = json.dumps([d.get("cny_midpoint") for d in ts_subset])
    brent_data = json.dumps([d.get("brent_oil") for d in ts_subset])
    
    return f'''
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
(function(){{
  if(typeof Chart==='undefined'){{console.warn('Chart.js not loaded');return;}}
  var labels={labels};
  function mk(id,color,data){{
    var el=document.getElementById(id);if(!el)return;
    var isDark=document.documentElement.classList.contains('dark');
    var grid=isDark?'rgba(255,255,255,0.05)':'rgba(0,0,0,0.05)';
    var txt=isDark?'#9aa0a6':'#5f6368';
    new Chart(el.getContext('2d'),{{
      type:'line',
      data:{{labels:labels,datasets:[{{data:data,borderColor:color,backgroundColor:color+'15',borderWidth:2,fill:true,tension:0.3,pointRadius:2,pointHoverRadius:5,pointBackgroundColor:color,spanGaps:true}}]}},
      options:{{responsive:true,maintainAspectRatio:false,plugins:{{legend:{{display:false}}}},scales:{{x:{{display:false,grid:{{display:false}}}},y:{{display:true,grid:{{color:grid}},ticks:{{color:txt,font:{{size:9}},maxTicksLimit:3}},beginAtZero:false}}}},interaction:{{intersect:false,mode:'index'}}}}
    }});
  }}
  mk('sseMiniChart','#0d47a1',{sse_data});
  mk('goldMiniChart','#f9a825',{gold_data});
  mk('fxMiniChart','#2e7d32',{fx_data});
  mk('oilMiniChart','#e65100',{brent_data});
}})();
</script>
'''

# 信号灯看板+图表的CSS
SIGNAL_CSS = """
/* ── 信号灯看板 ── */
.signal-dashboard { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; margin-bottom: 16px; }
.sig-dashboard-header { padding: 14px 20px 10px; font-size: 15px; font-weight: 700; color: var(--primary); border-bottom: 1px solid var(--border-light); display: flex; align-items: center; gap: 6px; }
.sig-dashboard-hint { font-size: 11px; color: var(--text-tertiary); font-weight: 400; margin-left: auto; }
.sig-row { display: flex; align-items: center; padding: 7px 20px; border-bottom: 1px solid var(--border-light); gap: 8px; }
.sig-row:last-child { border-bottom: none; }
.sig-lamp { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.sig-lamp.red { background: var(--signal-red); box-shadow: 0 0 6px rgba(198,40,40,0.4); }
.sig-lamp.yellow { background: var(--signal-yellow); box-shadow: 0 0 6px rgba(249,168,37,0.4); }
.sig-lamp.gray { background: #bdbdbd; }
.sig-name { font-size: 13px; font-weight: 600; min-width: 70px; flex-shrink: 0; }
.sig-value { font-size: 13px; font-weight: 700; font-family: "SF Mono","Consolas",monospace; min-width: 90px; }
.sig-change { font-size: 12px; font-family: "SF Mono","Consolas",monospace; min-width: 70px; text-align: right; }
.sig-change.flat { color: var(--text-tertiary); }
.sig-note { font-size: 11px; margin-left: auto; text-align: right; }
/* ── 趋势图表 ── */
.sig-charts-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.sig-chart-card { background: var(--card-bg); border-radius: var(--radius); box-shadow: var(--shadow); overflow: hidden; }
.sig-chart-header { padding: 10px 16px 6px; font-size: 13px; font-weight: 700; color: var(--text-secondary); display: flex; align-items: center; justify-content: space-between; }
.sig-chart-value { font-size: 15px; font-weight: 700; color: var(--primary); font-family: "SF Mono","Consolas",monospace; }
.sig-chart-container { padding: 0 12px 12px; height: 120px; }
@media (max-width: 600px) { .sig-charts-grid { grid-template-columns: 1fr; } .sig-name { min-width: 60px; } .sig-value { min-width: 75px; } }
"""

def process_file(html_path, date_str):
    """处理单个HTML文件，注入信号灯+图表"""
    with open(html_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # 检查是否已注入
    if "signal-dashboard" in content:
        print(f"  [SKIP] {date_str}: already has signal-dashboard")
        return False
    
    curr_idx = get_ts_index(date_str)
    if curr_idx < 0:
        print(f"  [ERROR] {date_str}: not found in TS_DATA")
        return False
    
    curr_data = TS_DATA[curr_idx]
    prev_data = TS_DATA[curr_idx - 1] if curr_idx > 0 else None
    
    # 1. 注入CSS（在 </style> 前插入）
    if "</style>" not in content:
        print(f"  [ERROR] {date_str}: no </style> found")
        return False
    
    content = content.replace("</style>", SIGNAL_CSS + "\n</style>", 1)
    
    # 2. 注入信号灯看板+图表HTML（在 summary-trends-box 闭合后、filter-bar/toc-nav 前）
    dashboard_html = build_signal_dashboard_html(curr_data, prev_data)
    charts_html = build_charts_html(curr_idx, curr_data)
    inject_html = "\n" + dashboard_html + charts_html
    
    # 找到 summary-trends-box 的闭合 </div> 后的 filter-bar 或 toc-nav
    # 匹配模式：summary-trends-box ... </div> \n <div class="filter-bar" 或 <div class="toc-nav"
    pattern = r'(</div>\s*\n\s*)(<div class="(?:filter-bar|toc-nav)")'
    match = re.search(pattern, content)
    if not match:
        # 尝试找 section-title 在后面
        pattern2 = r'(</div>\s*\n\s*)(<div class="(?:section-title|signal-card)")'
        match = re.search(pattern2, content)
    
    if not match:
        print(f"  [ERROR] {date_str}: insertion point not found")
        return False
    
    # 在 match.group(2) 前插入
    insert_pos = match.start(2)
    content = content[:insert_pos] + inject_html + "\n    " + content[insert_pos:]
    
    # 3. 注入Chart.js脚本（在 </body> 前插入）
    chart_js = build_chart_js(curr_idx)
    content = content.replace("</body>", chart_js + "\n</body>", 1)
    
    # 写回文件
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    print(f"  [OK] {date_str}: signal dashboard + charts injected")
    return True

# 主流程
print("=" * 60)
print("批量注入信号灯看板+Chart.js趋势图")
print("=" * 60)

success_count = 0
skip_count = 0
error_count = 0

for date_str, filename in sorted(DATE_FILE_MAP.items()):
    dir_path = os.path.join(ARCHIVES, date_str)
    html_path = os.path.join(dir_path, filename)
    
    if not os.path.exists(html_path):
        print(f"  [ERROR] {date_str}: file not found: {html_path}")
        error_count += 1
        continue
    
    print(f"\nProcessing {date_str}...")
    result = process_file(html_path, date_str)
    if result:
        success_count += 1
    elif "SKIP" in str(result):
        skip_count += 1

print(f"\n{'=' * 60}")
print(f"Done: {success_count} injected, {skip_count} skipped, {error_count} errors")
print("=" * 60)
