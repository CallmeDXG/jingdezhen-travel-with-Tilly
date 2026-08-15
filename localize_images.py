#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把攻略里的 Wikimedia 外链图，通过 wsrv.nl 代理下载到本地 images/ 目录（webp 480px），
并把 HTML 中所有外链替换成本地相对路径 images/xxx.webp。带去重、间隔与退避重试。"""
import json, os, urllib.parse, urllib.request, time

BASE = "/Users/sunhaixin7/WorkBuddy/景德镇"
IMG_DIR = os.path.join(BASE, "images")
HTML = os.path.join(BASE, "景德镇亲子游攻略.html")
os.makedirs(IMG_DIR, exist_ok=True)

data = json.load(open(os.path.join(BASE, "photos_index.json"), encoding="utf-8"))

def prox_url(url):
    base = url.split("?utm_source")[0]
    dec = urllib.parse.unquote(base)               # 还原 %28 -> (
    q = urllib.parse.quote(dec, safe="/:")          # 干净重编码
    return "https://wsrv.nl/?url=" + q + "&w=480&output=webp&q=80"

def fetch(url, dest, attempts=6):
    p = prox_url(url)
    last = None
    for a in range(attempts):
        try:
            req = urllib.request.Request(p, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=45) as r:
                buf = r.read()
            if len(buf) < 2000 or buf[:4] != b"RIFF":
                raise ValueError("not-image(%d)" % len(buf))
            open(dest, "wb").write(buf)
            return len(buf)
        except Exception as e:
            last = e
            time.sleep(2 + a * 3)
    raise last

# 去重：相同 URL 共用一个文件
seen = {}
plan = []
for e in data:
    for fi, f in enumerate(e["files"], 1):
        u = f["url"]
        if u in seen:
            plan.append((e, u, seen[u], True))
        else:
            fn = "%02d_%d.webp" % (e["idx"], fi)
            seen[u] = fn
            plan.append((e, u, fn, False))

mapping = {}
errors = []
for e, u, fn, dup in plan:
    dest = os.path.join(IMG_DIR, fn)
    if dup:
        mapping[u] = "images/" + fn
        continue
    if os.path.exists(dest) and os.path.getsize(dest) > 2000 and open(dest, "rb").read(4) == b"RIFF":
        mapping[u] = "images/" + fn
        continue
    try:
        n = fetch(u, dest)
        mapping[u] = "images/" + fn
        print("OK   %s  %s  (%dKB)" % (fn, e["name"], n // 1024))
    except Exception as ex:
        errors.append((e["name"], fn, str(ex)[:70]))
        print("FAIL %s  %s  %s" % (fn, e["name"], ex))
    time.sleep(1.5)

# 写回 HTML
html = open(HTML, encoding="utf-8").read()
cnt = 0
for url, local in mapping.items():
    for variant in (url, url.replace("&", "&amp;")):
        if variant in html:
            html = html.replace(variant, local)
            cnt += 1
open(HTML, "w", encoding="utf-8").write(html)

print("\n=== 完成 ===")
print("本地图:", len(mapping), "张；HTML 引用替换:", cnt, "处；失败:", len(errors))
for x in errors:
    print("  -", x)
