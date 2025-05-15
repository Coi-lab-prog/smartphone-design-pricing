import requests, json, time, random
import pandas as pd
from tqdm import trange
from pathlib import Path

# ========== 配置区 ==========
SKU_ID = "100123450368"       # 你要抓的商品 SKU ID（京东商品 URL 中的一串数字）
MAX_PAGES = 100               # 最多抓取多少页（每页10条）
SCORE = 0                     # 0=全部 1=差评 2=中评 3=好评
USE_NEW_API = True            # 推荐使用新接口（更稳定）
USE_COOKIES = True            # 启用 Cookie 模拟登录状态（强烈建议）

# 复制浏览器请求的 Cookie 粘贴进来（访问京东商品详情页 -> F12 -> 网络 -> 任一请求 -> Headers -> Cookie）
COOKIES = "__jdv=76161171|direct|-|none|-|1747289541630; __jdu=1747289540569852912597; areaId=15; PCSYCityID=CN_330000_330100_0; shshshfpa=f073456c-bb7a-b05a-0599-dc8dd68f116c-1747289543; shshshfpx=f073456c-bb7a-b05a-0599-dc8dd68f116c-1747289543; TrackID=1fVpq0nqZ4xhau7LX1r-fikZUye2OuOS5kaJzneB5Q5IJkeRihfwi9zZTXqOGXYVjKOdqcTYt8BWdrJumXOi5-vprzJCb_Q9XHuJq14761Tw; thor=71D8A7052A333BB2FF4FC3C4AE2B0B2C2DC99A5AD3E07958589CE3BADF7857F653D711C199F182901A332DD0E1B0D792391F5AB9DA19E81B59F2D299269C09B6F5E1BE0E068BA1AF42D416CD26B785E8AE81F7B4C16C16E8DBDE687E1F34D9B58B8927C54F3C6DFE2CCA109AB68647E76BA67B2B49ED30E7EAC77ED7EAE4940D039460CEBF15EA4BB8EFA915E47C4E23F17546FCAFF08E1E4F3761FA617B46A5; light_key=AASBKE7rOxgWQziEhC_QY6yaQSehW-CB0xt1WWlRihjx6heGrZS_EMEcdnFlKalxnp7TOegP; pinId=T7k5JMUnhbqHDuo_NdFp5n1E2T3GC3C4; pin=jd_tnTxjz9P5tPkouM; unick=jd_ol9kj48v6c7n88; _tp=ELb%2BYIbWL2WEAM%2Bljo8SiX0drh7klXckiQKRNHvipvo%3D; _pst=jd_tnTxjz9P5tPkouM; jsavif=1; ipLoc-djd=15-1213-3038-0; unpl=JF8EAJ5nNSttW0JTVU5XGRFFGQ1XW1RdSR9RbjICUg4LSlQGHAcfR0N7XlVdWRRKEx9vYxRUWFNIUg4fBCsSEHteVVxcDEsRA21uNWRVUCVXSBtsGHwQBhAZbl4IexcCX2cDUVtbQlwBHgMfFRhCWVdWXQtPHwVfZjVUW2h7ZAQrAysTIAAzVRNdDk4RAGZvAVFcXExcDB8BExITT1VSblw4SA; mail_times=2%2C2; 3AB9D23F7A4B3CSS=jdd03DL7Y7LUFK6L4CPHA7VZDH2XMYU2TKFYU5NRTNWSKSKBW7RRX5JHP72MWR3H4BHGC4IAZYCCY4JFZ2M7WJZGZXJ47QUAAAAMW2LMM5HYAAAAACOZQHFI7VQ7IO4X; _gia_d=1; 3AB9D23F7A4B3C9B=DL7Y7LUFK6L4CPHA7VZDH2XMYU2TKFYU5NRTNWSKSKBW7RRX5JHP72MWR3H4BHGC4IAZYCCY4JFZ2M7WJZGZXJ47QU; token=9bc19168ae57b9a829044d0319d483b5,3,970718; __jda=181111935.1747289540569852912597.1747289540.1747289542.1747294145.2; __jdc=181111935; flash=3_St20y7yqDvv3rDXnGgTph26s2Fad-2LZvYj60egTQum3TwB-djr-tALjSaG-NYjc3MqdvlmQTS4XXlQdV0t92rCJqrPQwbFt9kVDPti0YE77ecsr0LRD7GKsvaPbsZmh4rVUfDrcrdogiLHX24_OkW1cBrWjrQwE8ZmN1zS-hn_4TCW1F8c_uNN1; cn=0; __jdb=181111935.4.1747289540569852912597|2.1747294145; shshshfpb=BApXSbYrR0fNAhet8ST1e7rdQtfptSaC2BgVpkmxo9xJ1MnK-OI62; sdtoken=AAbEsBpEIOVjqTAKCQtvQu17DeOm3d8gFtu1bBdKehg7b0NLh5CvY5_7y5ac74Jagk93F6pSrJCuc-YhZFReydXmVEGv2-1Fy6YsIYLOJMBTb9ivFtZxapUIqQhwvQskYEqnL8UVdx6C"

UA_POOL = [
    # 多个浏览器 UA，可轮换使用
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/112.0",
]
# ========== 配置区结束 ==========

# 接口 URL（新接口）
API_URL = "https://api.m.jd.com/" if USE_NEW_API else "https://club.jd.com/comment/productPageComments.action"

# 解析 Cookie 字符串为字典
def parse_cookies(cookie_str: str):
    return dict(item.split("=", 1) for item in cookie_str.split("; ") if "=" in item)

def fetch_page(page: int):
    headers = {
        "User-Agent": random.choice(UA_POOL),
        "Referer": f"https://item.jd.com/{SKU_ID}.html"
    }
    if USE_NEW_API:
        params = {
            "appid": "item-v3",
            "functionId": "pc_club_productPageComments",
            "productId": SKU_ID,
            "score": SCORE,
            "sortType": 5,
            "page": page,
            "pageSize": 10,
            "fold": 1,
        }
    else:
        params = {
            "productId": SKU_ID,
            "score": SCORE,
            "sortType": 5,
            "page": page,
            "pageSize": 10,
            "fold": 1,
        }

    cookies = parse_cookies(COOKIES) if (USE_COOKIES and COOKIES) else None

    try:
        r = requests.get(API_URL, params=params, headers=headers, cookies=cookies, timeout=10)
        r.raise_for_status()
        
        # 🔽 确保 r 在 try 内部再访问 r.url
        print(f"[DEBUG] 第 {page} 页状态码: {r.status_code}")
        print(f"[DEBUG] 请求 URL: {r.url}")
        print(f"[DEBUG] 返回内容预览: {r.text[:150]}")
        
        txt = r.text.strip()
        if txt.startswith(("fetchJSON", "jsonp")):
            txt = txt[txt.find("(")+1 : txt.rfind(")")]
        return json.loads(txt)
    except Exception as e:
        print(f"[错误] 第 {page} 页请求失败：{e}")
        return {}


def crawl():
    rows = []
    for p in trange(MAX_PAGES, desc="抓取评论"):
        data = fetch_page(p)
        comments = data.get("comments") or data.get("data", {}).get("comments", [])
        if not comments:
            print(f"⚠️ 第 {p} 页无评论，可能已到尽头或触发反爬。")
            break
        for c in comments:
            rows.append({
                "content":       c.get("content"),
                "score":         c.get("score"),
                "time":          c.get("creationTime"),
                "user_level":    c.get("userLevelName"),
                "thumb_up":      c.get("usefulVoteCount"),
                "product_color": c.get("productColor"),
                "product_size":  c.get("productSize"),
            })
        time.sleep(random.uniform(1.0, 2.2))  # 防反爬：延迟
    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = crawl()
    filename = Path(f"jd_{SKU_ID}_{len(df)}.csv")
    df.to_csv(filename, index=False, encoding="utf_8_sig")
    print(f"\n✅ 抓取完成！共 {len(df)} 条评论，已保存到文件：{filename.resolve()}")
