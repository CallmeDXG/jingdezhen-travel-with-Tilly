#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 把每个地点的照片插进「每日行程」里对应的 event（POI）块。
# 匹配规则：地点的"行程文本 token"出现在某 .ev 行的 .act 中，即把该地点所有图插入该块。
import json, html

HTML = "景德镇亲子游攻略.html"
with open(HTML, encoding="utf-8") as f:
    src = f.read()
with open("photos_index.json", encoding="utf-8") as f:
    idx = json.load(f)

name2urls = {it["name"]: [fl["url"].replace("&", "&amp;") for fl in it["files"]]
             for it in idx if it["files"]}

# 行程里的称呼 token -> 正式地点名
TOKEN2NAME = {
    "景德镇陶瓷博物馆": "景德镇陶瓷博物馆",
    "陶阳里历史文化旅游区": "景德镇陶阳里历史文化旅游区",
    "陶阳新村夜市": "陶阳新村夜市",
    "小樱青花扎染店": "小樱青花扎染店",
    "绿西玻璃工作室": "绿西玻璃工作室",
    "胖师傅写真馆·妆造": "胖师傅写真馆·妆造",
    "三宝国际陶艺村": "陶源谷·三宝国际陶艺村",
    "雕塑瓷厂": "雕塑瓷厂",
    "陶溪川文创街区": "陶溪川文创街区",
    "今夕美术馆": "今夕美术馆",
    "古窑民俗博览区": "景德镇古窑民俗博览区",
    "浮梁新平村瓷宫": "浮梁县新平村瓷宫",
    "江西直升机科技馆": "江西直升机科技馆",
    "鄱阳湖国家湿地公园": "鄱阳湖国家湿地公园",
    "瑶里古镇风景区": "瑶里古镇风景区",
    "东埠古街古码头": "瑶里景区东埠古街古码头",
    "寒溪村": "寒溪村",
    "山闾村戏台": "山闾村戏台",
    "丙丁柴窑": "丙丁柴窑",
    "七四O厂": "景德镇市七四O厂",
    "东郊学堂": "东郊学堂",
}

# ---- 注入缩略图 CSS ----
CSS = """
  /* 行程 POI 缩略图 */
  .ev .poi-imgs { display:flex; gap:5px; margin-top:8px; flex-wrap:wrap; }
  .ev .poi-imgs img { width:92px; height:70px; object-fit:cover; border-radius:8px; border:1px solid var(--line); background:#f3efe8; }
"""
assert "</style>" in src
src = src.replace("</style>", CSS + "</style>", 1)

# ---- 逐行处理 event 块 ----
lines = src.split("\n")
total_imgs = 0
matched_places = set()
new_lines = []
for line in lines:
    if 'class="ev' in line and 'poi-imgs' not in line:
        found = [name for tok, name in TOKEN2NAME.items() if tok in line]
        if found:
            urls = []
            for name in found:
                matched_places.add(name)
                urls.extend(name2urls[name])
            if urls:
                imgs = "".join(
                    f'<img src="{html.escape(u, quote=True)}" alt="" loading="lazy">'
                    for u in urls
                )
                strip = f'<div class="poi-imgs">{imgs}</div>'
                pos = line.rfind("</div>")
                line = line[:pos] + strip + line[pos:]
                total_imgs += len(urls)
    new_lines.append(line)

src = "\n".join(new_lines)
with open(HTML, "w", encoding="utf-8") as f:
    f.write(src)

print("DONE. 插入缩略图事件数见上；共插入", total_imgs, "张图")
print("匹配到", len(matched_places), "个地点：", "、".join(sorted(matched_places)))
# 未匹配（有图但行程里没出现的）
unmatched = [n for n in name2urls if n not in matched_places]
print("有图但未放进行程的地点：", unmatched)
