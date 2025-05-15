import requests, json, re, time, random
import pandas as pd
from tqdm import trange
from pathlib import Path

# ========== 配置区 ==========
ITEM_ID = "782189145082"        # 商品 ID
SELLER_ID = "2219260524931"     # 卖家 ID（可从 Network 中抓）
MAX_PAGES = 200                  # 最多抓取多少页（每页20条）
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
SAVE_PATH = Path(f"tmall_{ITEM_ID}_comments.csv")
SLEEP = (1.2, 2.4)              # 每页之间的随机间隔，防止被限流
# ========== 配置区结束 ==========

def fetch_page(page: int):
    url = "https://rate.tmall.com/list_detail_rate.htm"
    params = {
        "itemId": ITEM_ID,
        "sellerId": SELLER_ID,
        "order": "3",
        "currentPage": page,
        "callback": "jsonp"
    }

    HEADERS = {
        "User-Agent": UA,
        "Referer": f"https://detail.tmall.com/item.htm?id={ITEM_ID}",
        "Cookie": "mtop_partitioned_detect=1; _m_h5_tk=cd93b532fe0d9fea726204e86f010c99_1747303987522; _m_h5_tk_enc=95e14b3eda69b5c50905a3928146f118; xlly_s=1; dnk=tb126605378; uc1=existShop=false&cookie21=V32FPkk%2FgPzW&pas=0&cookie14=UoYajLe1%2F54Uew%3D%3D&cookie15=VT5L2FSpMGV7TQ%3D%3D&cookie16=Vq8l%2BKCLySLZMFWHxqs8fwqnEw%3D%3D; uc3=nk2=F5REPEeOeqgHwnI%3D&lg2=U%2BGCWk%2F75gdr5Q%3D%3D&vt3=F8dD2EXQcW8V2itwpsA%3D&id2=UUpgRK%2FS%2F0HNpX5E7Q%3D%3D; tracknick=tb126605378; lid=tb126605378; _l_g_=Ug%3D%3D; havana_lgc_exp=1747327200296; uc4=nk4=0%40FY4PbhDrGKQ02tpq4OAx5tKmxYGldA%3D%3D&id4=0%40U2gqy16cWzu5RTYP4432pPcqCfzZuYx8; unb=2212214215325; lgc=tb126605378; cookie1=WqSTQXPH0O2FGUN24zfEbEAl3EZJP5VfwQk%2FUsOyWac%3D; login=true; wk_cookie2=144b4c37389311df902a3b8760168ac5; cookie17=UUpgRK%2FS%2F0HNpX5E7Q%3D%3D; cookie2=181fd8e9fc80f6929c769e3a8aee6101; _nk_=tb126605378; sgcookie=E100%2BAYyTISc2GMhjEd9CYvDTzACGSDyjS%2BFIo6waoPDI2RRG9bPhsqcnP5Z%2Bi9RWRx4kYAQEo42WyO5sDp1g3kfTLyOTXVPn38Un7PAccXgNrB8imG0UbP8jigKiWMOnrdm; cancelledSubSites=empty; sg=850; t=26341ff7ac75e2697e8da87f13a6c845; csg=9015c190; sn=; _tb_token_=7aeade3e4b63a; wk_unb=UUpgRK%2FS%2F0HNpX5E7Q%3D%3D; isg=BGFhXNzArRXwUgFhrKLFHAqrcC17DtUAWpv6_cM2XWjHKoH8C17l0I_pjF6s2W04; havana_sdkSilent=1747382526952; bxuab=0; tfstk=gG7sCbGfOAD1KpTxGhVeNp0ie3LbTWzzfjOAZs3ZMFL9Gq1lh18VMK7Xl9XpDN8N_9afZTtwDZJVlfbCFquaIlfxlE8YU8zzz1cwoEezYTM9NdAc9KFeXc8AN7LYU8zEYXKgQEBVXJZTA6pHGIntWtdLOIOvkVKxWDHpKpLvMCpxppdyMCnvHtCLOIvpHEKOHHFBivQjdIr6M1NMm3lwLz9P6pgxkwUDfL1t0q3ARCt1s1pIYD7B1h9JDFIHeNBFMN7Mx8MJo6S5hiB04DY1MGL9a14sRUCOYZOFuSoXBObC9wKIa48fXOsvqMaoqhKXCMQ9Aj3AtEsp2i6_CcvOb9tk9HhbrBWyp1bOASDd6TJ6WBKUy71pDM7MqNyK5UIl_FSAnuoH5sI9Rg-IzL_rAmGBqqOBUWNImmVBUWunDu_fjhdH6zPQOviDXBACYWNImsx9tBuUOWio5"
    }

    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=10, proxies={})
        r.raise_for_status()

        txt = r.text.strip()
        if page == 0:
            print(f"[DEBUG] 返回前200字符：\n{txt[:200]}")

        # 只有当返回是 jsonp(...) 格式时剥离
        if txt.startswith("jsonp(") and txt.endswith(")"):
            txt = txt[6:-1]

        data = json.loads(txt)
        return data.get("rateDetail", {}).get("rateList", [])

    except Exception as e:
        print(f"[❌] 第 {page} 页请求失败：{e}")
        return []


def crawl():
    rows = []
    for page in trange(MAX_PAGES, desc="抓取天猫评论"):
        comments = fetch_page(page)
        if not comments:
            print(f"⚠️ 第 {page} 页无评论，可能已到尽头或被限流")
            break

        for c in comments:
            rows.append({
                "user": c.get("displayUserNick"),
                "rate_date": c.get("rateDate"),
                "content": c.get("rateContent"),
                "append": c.get("appendComment", {}).get("content") if c.get("appendComment") else "",
                "sku": c.get("auctionSku"),
                "status": c.get("feedback"),
            })

        # 每页暂停，防反爬
        time.sleep(random.uniform(*SLEEP))

    return pd.DataFrame(rows)

if __name__ == "__main__":
    df = crawl()
    df.to_csv(SAVE_PATH, index=False, encoding="utf_8_sig")
    print(f"\n✅ 共抓取 {len(df)} 条评论，保存至：{SAVE_PATH.resolve()}")
