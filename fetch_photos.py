#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 外链版：只从 Wikimedia 搜索缩略图 URL，不下载（本环境数据中心 IP 被 upload 域 403 拦截）。
# 图片由用户端浏览器/微信加载，故用远程 URL 直接嵌入。
import urllib.request, urllib.parse, json, html

API = "https://commons.wikimedia.org/w/api.php"

PLACES = [
    ("景德镇陶瓷博物馆", "museum", ["Jingdezhen Ceramic Museum", "Jingdezhen porcelain museum"], 3),
    ("景德镇御窑博物馆", "museum", ["Jingdezhen Imperial Kiln Museum"], 3),
    ("景德镇民窑博物馆", "museum", ["Jingdezhen folk kiln", "Jingdezhen kiln"], 1),
    ("今夕美术馆", "museum", ["Jingdezhen art museum", "Taoxichuan art gallery"], 1),
    ("江西直升机科技馆", "museum", ["helicopter museum", "helicopter exhibition"], 2),
    ("陶溪川文创街区", "shop", ["Taoxichuan Jingdezhen", "Jingdezhen creative district"], 3),
    ("雕塑瓷厂", "shop", ["Jingdezhen sculpture ceramic factory", "Jingdezhen ceramic"], 2),
    ("陶阳新村夜市", "shop", ["Jingdezhen night market", "China night market"], 1),
    ("浮梁县新平村瓷宫", "shop", ["Jingdezhen Porcelain Palace", "Porcelain Palace Jingdezhen"], 3),
    ("景德镇古窑民俗博览区", "shop", ["Jingdezhen ancient kiln", "Jingdezhen kiln museum"], 3),
    ("景德镇陶阳里历史文化旅游区", "shop", ["陶阳里", "Jingdezhen Taoyangli", "Jingdezhen old town street", "Jingdezhen ancient street"], 2),
    ("景德镇市七四O厂", "shop", ["abandoned factory China", "industrial ruin"], 1),
    ("东郊学堂", "shop", ["old school building China", "abandoned school"], 1),
    ("丙丁柴窑", "shop", ["Jingdezhen wood fired kiln", "wood fired kiln China"], 2),
    ("山闾村戏台", "shop", ["Chinese opera stage", "ancient opera stage"], 1),
    ("小樱青花扎染店", "kids", ["Chinese tie dye", "indigo tie dye"], 2),
    ("绿西玻璃工作室", "kids", ["glass fusing art", "glass art studio"], 2),
    ("胖师傅写真馆·妆造", "kids", ["Hanfu photography", "Chinese traditional costume"], 2),
    ("前程漂流", "kids", ["river tubing China", "white water rafting"], 2),
    ("陶源谷·三宝国际陶艺村", "nature", ["Sanbao Jingdezhen", "Jingdezhen art village"], 3),
    ("瑶里古镇风景区", "nature", ["Yaoli ancient town", "Jiangxi ancient town"], 3),
    ("瑶里景区东埠古街古码头", "nature", ["ancient dock China", "old street Jiangxi"], 1),
    ("寒溪村", "nature", ["tea plantation village", "tea terrace China"], 1),
    ("饶州古镇", "nature", ["Chinese ancient town", "Jiangxi old town"], 1),
    ("鄱阳湖国家湿地公园", "nature", ["Poyang Lake", "Poyang Lake wetland"], 3),
]

UA = {"User-Agent": "JingdezhenTripPlanner/1.0 (educational; contact: traveler@example.com)"}


def search(query, limit):
    params = {
        "action": "query", "generator": "search",
        "gsrsearch": query, "gsrnamespace": 6, "gsrlimit": limit,
        "prop": "imageinfo", "iiprop": "url", "iiurlwidth": 960, "format": "json",
    }
    url = API + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    out = []
    for page in data.get("query", {}).get("pages", {}).values():
        ii = page.get("imageinfo")
        if ii and "thumburl" in ii[0]:
            out.append({"title": page.get("title"), "thumb": ii[0]["thumburl"],
                        "desc": page.get("descriptionurl", "")})
    return out


index = []
for i, (name, cat, queries, n) in enumerate(PLACES, 1):
    urls, seen = [], set()
    for q in queries:
        if len(urls) >= n:
            break
        try:
            res = search(q, n * 3)
        except Exception as e:
            print("  search fail:", name, q, e)
            continue
        for it in res:
            if len(urls) >= n:
                break
            if it["title"] in seen:
                continue
            seen.add(it["title"])
            urls.append({"url": it["thumb"], "src": it["desc"], "query": q})
    index.append({"idx": i, "name": name, "cat": cat, "files": urls, "queries": queries})
    print(f"{i:02d} {name}: {len(urls)}/{n}")

with open("photos_index.json", "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

cat_label = {"museum": "🏛 博物馆/展馆", "shop": "🛍 门店/市集/景区",
             "kids": "🎨 亲子手工", "nature": "🌿 自然/古镇"}
groups = {}
for it in index:
    groups.setdefault(it["cat"], []).append(it)

parts = ['<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
         '<meta name="viewport" content="width=device-width,initial-scale=1">'
         '<title>景德镇攻略 · 配图确认</title><style>'
         '*{margin:0;padding:0;box-sizing:border-box}'
         'body{font-family:-apple-system,"PingFang SC",sans-serif;background:#fdf6ee;color:#4a3526;padding:18px}'
         'h1{font-size:22px;text-align:center;margin:10px 0 4px}'
         '.tip{text-align:center;color:#9b8775;font-size:13px;margin-bottom:6px}'
         '.warn{text-align:center;color:#c0392b;font-size:12px;margin-bottom:18px}'
         '.grp{max-width:1000px;margin:0 auto 26px}'
         '.grp h2{font-size:17px;color:#e06a44;border-left:5px solid #ff8c69;padding-left:10px;margin:18px 0 10px}'
         '.place{background:#fff;border:1px solid #f0e6da;border-radius:14px;padding:14px;margin-bottom:14px}'
         '.place h3{font-size:15px;margin-bottom:10px}'
         '.imgs{display:flex;flex-wrap:wrap;gap:10px}'
         '.imgs img{width:220px;height:160px;object-fit:cover;border-radius:10px;border:1px solid #eee;background:#f3efe8}'
         '.none{color:#c0392b;font-size:13px}'
         '.meta{font-size:11px;color:#aaa;margin-top:6px;word-break:break-all}'
         '</style></head><body>'
         '<h1>📸 景德镇攻略 · 配图确认</h1>'
         '<div class="tip">以下为每个地点从 Wikimedia 找到的照片（外链，你的浏览器/手机加载显示）</div>'
         '<div class="warn">说明：图片为远程链接，需联网显示；若某张不满意或不想用，告诉我，我替换/删除</div>']

for cat in ["museum", "shop", "kids", "nature"]:
    parts.append(f'<div class="grp"><h2>{cat_label[cat]}</h2>')
    for it in groups.get(cat, []):
        parts.append(f'<div class="place"><h3>{html.escape(it["name"])} '
                     f'<span class="meta">（找到 {len(it["files"])} 张）</span></h3>')
        if it["files"]:
            parts.append('<div class="imgs">')
            for fl in it["files"]:
                parts.append(f'<img src="{html.escape(fl["url"])}" alt="{html.escape(it["name"])}" loading="lazy">')
            parts.append('</div>')
            parts.append('<div class="meta">搜索词：' + " / ".join(html.escape(q) for q in it["queries"]) + '</div>')
        else:
            parts.append('<div class="none">⚠️ 未找到合适照片（待补）</div>')
        parts.append('</div>')
    parts.append('</div>')

parts.append('</body></html>')
with open("配图确认.html", "w", encoding="utf-8") as f:
    f.write("".join(parts))
print("DONE. 确认页：配图确认.html")
