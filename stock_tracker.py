import yfinance as yf
import requests
from datetime import datetime, timezone, timedelta

# ── 設定區 ──────────────────────────────────────
BOT_TOKEN = "8880925248:AAGFtxCPx-AYYU4oJmxkno6h6MutCIm96Zs"
CHAT_ID   = "8996994642"

STOCKS = [
    ("2330.TW", "台積電"),
    ("2317.TW", "鴻海"),
    ("2454.TW", "聯發科"),
]
# ────────────────────────────────────────────────

def send_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

def get_ma(hist, period):
    if len(hist) < period:
        return None
    return hist["Close"].rolling(period).mean().iloc[-1]

def analyze_stock(code, name):
    ticker = yf.Ticker(code)
    hist = ticker.history(period="30d")

    if hist.empty or len(hist) < 2:
        return f"\n❌ {name}({code}) 無法取得資料"

    today = hist["Close"].iloc[-1]
    prev  = hist["Close"].iloc[-2]
    change = today - prev
    pct    = change / prev * 100

    if change > 0:
        arrow = "🔴▲"
    elif change < 0:
        arrow = "🟢▼"
    else:
        arrow = "⬜─"

    ma5  = get_ma(hist, 5)
    ma10 = get_ma(hist, 10)
    ma20 = get_ma(hist, 20)

    lines = [
        f"\n━━━━━━━━━━━━━━━━",
        f"{arrow} {name}（{code.replace('.TW','')}）",
        f"收盤：{today:.1f} 元",
        f"漲跌：{change:+.1f} 元（{pct:+.2f}%）",
    ]

    if ma5:
        diff5 = (today - ma5) / ma5 * 100
        status = "⬆️ 站上" if today >= ma5 else "⬇️ 跌破"
        lines.append(f"{status} 五日線 {ma5:.1f}（偏離 {diff5:+.1f}%）")
    if ma10:
        status = "✅" if today >= ma10 else "❌"
        lines.append(f"{status} 十日線 {ma10:.1f}")
    if ma20:
        status = "✅" if today >= ma20 else "❌"
        lines.append(f"{status} 二十日線 {ma20:.1f}")

    return "\n".join(lines)

def main():
    # 台灣時區 (UTC+8)
    taiwan_tz = timezone(timedelta(hours=8))
    now = datetime.now(taiwan_tz).strftime("%Y/%m/%d %H:%M")
    
    msg = f"📊 每日股票報告\n🕐 {now}"

    for code, name in STOCKS:
        msg += analyze_stock(code, name)

    msg += "\n━━━━━━━━━━━━━━━━"

    send_telegram(msg)
    print("已發送到 Telegram！")
    print(msg)

if __name__ == "__main__":
    main()