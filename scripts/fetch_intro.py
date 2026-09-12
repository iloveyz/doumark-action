import json
import time
import random
import re
import requests
from pathlib import Path

# 读取 movie.json
json_path = Path("data/douban/movie.json")
data = json.loads(json_path.read_text(encoding="utf-8"))

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}

for item in data:
    subject = item.get("subject", {})
    url = subject.get("url")
    if not url:
        continue

    # 如果已经有 intro 就跳过
    if subject.get("intro"):
        continue

    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = "utf-8"
        html = resp.text

        # 豆瓣详情页的简介通常在 <span property="v:summary"> 或
        # <div class="indent" id="intro"> 里，这里做多重匹配兜底
        match = re.search(
            r'<span[^>]*property="v:summary"[^>]*>(.*?)</span>',
            html, re.S
        )
        if not match:
            match = re.search(
                r'<div[^>]*id="intro"[^>]*>(.*?)</div>',
                html, re.S
            )

        if match:
            intro = re.sub(r"<[^>]+>", "", match.group(1)).strip()
            subject["intro"] = intro
            print(f"OK: {subject.get('title')}")
        else:
            subject["intro"] = ""
            print(f"NO INTRO: {subject.get('title')}")

    except Exception as e:
        subject["intro"] = ""
        print(f"ERROR: {subject.get('title')} -> {e}")

    # 随机延时，避免触发反爬
    time.sleep(random.uniform(1.5, 3.5))

# 写回 movie.json
json_path.write_text(
    json.dumps(data, ensure_ascii=False, indent=2),
    encoding="utf-8"
)
print("Done.")
