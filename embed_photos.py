#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 把 photos_index.json 的照片嵌进主攻略 HTML：
#  1) 新增「📸 景点相册」板块（按类型分组，每地点1-3张图+名称+一句话简介）
#  2) 给地图 popup 加一张缩略图（photoMap）
import json, html

HTML = "景德镇亲子游攻略.html"
with open(HTML, encoding="utf-8") as f:
    src = f.read()
with open("photos_index.json", encoding="utf-8") as f:
    idx = json.load(f)

# 每个地点的一句话简介（相册用）
INTRO = {
    "景德镇陶瓷博物馆": "看青花、颜色釉与历代瓷器，闺女瓷器启蒙最好的地方",
    "景德镇御窑博物馆": "陶阳里内的红砖拱形建筑，极出片（暂未找到实景图）",
    "景德镇民窑博物馆": "了解民窑烧造历史，规模小、顺路可看",
    "今夕美术馆": "陶溪川内的当代艺术展，免费参观",
    "江西直升机科技馆": "直升机展示+科普，爱机械的闺女必去",
    "陶溪川文创街区": "美术馆+画廊+文创市集，周五六晚有夜市",
    "雕塑瓷厂": "巷子原创陶瓷，淘小物件给闺女、拍照好看",
    "陶阳新村夜市": "夜宵小摊，便宜手工小物件",
    "浮梁县新平村瓷宫": "童话城堡般的瓷制宫殿，门票25元",
    "景德镇古窑民俗博览区": "传统柴窑+非遗拉坯演示，门票95元",
    "景德镇陶阳里历史文化旅游区": "含御窑与明清老街的大片区",
    "景德镇市七四O厂": "老电子厂改造，文艺复古风、适合拍照",
    "东郊学堂": "老学校改造的文化/艺术空间，可顺路停留",
    "丙丁柴窑": "清水混凝土现代柴窑，摄影圣地",
    "山闾村戏台": "古戏台建筑，瑶里方向顺路",
    "小樱青花扎染店": "扎染DIY约105元/人，闺女最爱",
    "绿西玻璃工作室": "玻璃熔合做小挂件，火候艺术很神奇",
    "胖师傅写真馆·妆造": "古风妆造拍摄，闺女穿青花服超好看",
    "前程漂流": "夏季玩水好去处，带替换衣物+防水袋",
    "陶源谷·三宝国际陶艺村": "艺术工作室聚集地，免费慢逛拍照",
    "瑶里古镇风景区": "徽派老屋+小桥流水，闺女可写生捡石头",
    "瑶里景区东埠古街古码头": "古茶叶运输码头，古街保存完好",
    "寒溪村": "艺术茶园村，凉快安静、返程顺路",
    "饶州古镇": "鄱阳湖方向的仿古商业街",
    "鄱阳湖国家湿地公园": "湿地生态+夏候鸟，D6备选方案",
}
CAT_LABEL = {"museum": "🏛 博物馆/展馆", "shop": "🛍 门店/市集/景区",
             "kids": "🎨 亲子手工", "nature": "🌿 自然/古镇"}

def esc(s):
    return html.escape(s, quote=True).replace("&", "&amp;")

# ---- CSS 注入（插到 </style> 前）----
CSS = """
  /* Gallery */
  .gal-group { margin-bottom: 22px; }
  .gal-group h3 { font-size: 16px; color: var(--clay-d); margin: 14px 0 10px; }
  .gal-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px,1fr)); gap: 14px; }
  .gal-item { background:#fff; border:1px solid var(--line); border-radius:12px; overflow:hidden; display:flex; flex-direction:column; }
  .gal-imgs { display:flex; gap:3px; background:#f3efe8; }
  .gal-imgs img { flex:1; min-width:0; height:150px; object-fit:cover; }
  .gal-body { padding:10px 12px; }
  .gal-name { font-size:14px; font-weight:700; color:var(--ink); margin-bottom:3px; }
  .gal-desc { font-size:12.5px; color:var(--muted); line-height:1.6; }
  .gal-note { font-size:12px; color:var(--muted); margin-top:8px; }
"""
assert "</style>" in src
src = src.replace("</style>", CSS + "</style>", 1)

# ---- 相册板块 HTML ----
groups = {}
for it in idx:
    if it["files"]:  # 只放有图的
        groups.setdefault(it["cat"], []).append(it)

parts = ['<section>',
         '<h2><span class="ic">📸</span>景点相册（附图版）</h2>',
         '<div class="note-inline">🖼️ 以下照片来自 <b>Wikimedia 共享资源</b>（免费授权），由你的手机/电脑联网加载。'
         '部分为<b>同类题材示意图</b>（非该地点实景，如古镇/老街用了其他地区的相似画面、个别为文献封面），仅供闺女先有个印象；'
         '想换成实景图随时告诉我地点名。</div>']

for cat in ["museum", "shop", "kids", "nature"]:
    parts.append(f'<div class="gal-group"><h3>{CAT_LABEL[cat]}</h3><div class="gal-grid">')
    for it in groups.get(cat, []):
        imgs = "".join(
            f'<img src="{esc(fl["url"])}" alt="{esc(it["name"])}" loading="lazy">'
            for fl in it["files"]
        )
        parts.append(
            f'<div class="gal-item"><div class="gal-imgs">{imgs}</div>'
            f'<div class="gal-body"><div class="gal-name">{esc(it["name"])}'
            f'</div><div class="gal-desc">{esc(INTRO.get(it["name"],""))}</div></div></div>'
        )
    parts.append('</div></div>')
parts.append('</section>')

gallery_html = "\n".join(parts)
# 插在「注意事项」板块之前
anchor = "  <!-- 注意事项 -->"
assert anchor in src
src = src.replace(anchor, gallery_html + "\n\n" + anchor, 1)

# ---- 地图 popup 加缩略图：构造 photoMap ----
photoMap = {}
for it in idx:
    if it["files"]:
        photoMap[it["name"]] = it["files"][0]["url"].replace("&", "&amp;")

pm_json = json.dumps(photoMap, ensure_ascii=False)
inject = f'const photoMap = {pm_json};\n'
# 在 forEach 前注入
assert "places.forEach(p => {" in src
src = src.replace("places.forEach(p => {", inject + "places.forEach(p => {", 1)

# 修改 bindPopup 行，加入图片
old_popup = "m.bindPopup(`<b>${p.name}</b><br>${p.desc.replace(/\\n/g,'<br>')}`);"
new_popup = (
    "const pimg = photoMap[p.name];\n"
    "  const popHtml = `<b>${p.name}</b>`\n"
    "    + (pimg ? `<br><img src=\"${pimg}\" style=\"width:240px;max-width:100%;height:140px;object-fit:cover;border-radius:8px;margin:6px 0;display:block;\">` : '')\n"
    "    + `<br>${p.desc.replace(/\\n/g,'<br>')}`;\n"
    "  m.bindPopup(popHtml);"
)
assert old_popup in src
src = src.replace(old_popup, new_popup, 1)

with open(HTML, "w", encoding="utf-8") as f:
    f.write(src)
print("DONE. 相册板块已插入，popup 已加图。")
print("photoMap 共", len(photoMap), "个地点含图")
