import os
import requests
import yfinance as yf
from datetime import datetime

LINE_CHANNEL_ACCESS_TOKEN = os.environ["LINE_TOKEN"]
LINE_USER_ID = os.environ["LINE_USER_ID"]


def send_line_message(msg):
    url = "https://api.line.me/v2/bot/message/push"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }

    payload = {
        "to": LINE_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": msg
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("LINE Status:", response.status_code)


def get_realtime_change(symbol):
    try:
        ticker = yf.Ticker(symbol)

        info = ticker.fast_info

        current = info.get("lastPrice")
        previous = info.get("previousClose")

        if current is None or previous is None:
            return "N/A"

        pct = ((current - previous) / previous) * 100

        sign = "🔺" if pct > 0 else "🔻" if pct < 0 else "🔹"

        return f"{sign}{pct:+.2f}%"

    except Exception as e:
        print(f"{symbol} error: {e}")
        return "N/A"


def get_current_price(symbol):
    try:
        ticker = yf.Ticker(symbol)

        info = ticker.fast_info

        price = info.get("lastPrice")

        if price is None:
            return "N/A"

        return f"{price:.2f}"

    except Exception as e:
        print(f"{symbol} error: {e}")
        return "N/A"


def get_report_title():

    utc_hour = datetime.utcnow().hour

    if utc_hour == 13:
        return "📈 美股開盤監控"

    elif utc_hour == 14:
        return "📈 美股開盤一小時監控"

    elif utc_hour == 20:
        return "📊 美股收盤報告"

    else:
        return "📊 市場監控報告"


def build_report():

    # 美股三大指數
    dow = get_realtime_change("^DJI")
    sp500 = get_realtime_change("^GSPC")
    nasdaq = get_realtime_change("^IXIC")

    # ETF
    voo = get_realtime_change("VOO")
    qqq = get_realtime_change("QQQ")
    vti = get_realtime_change("VTI")

    # 台積電ADR
    tsm = get_realtime_change("TSM")

    # VIX
    vix = get_realtime_change("^VIX")

    # 匯率
    usd_twd = get_current_price("TWD=X")

    title = get_report_title()

    report = f"""
{title}

🇺🇸 美股大盤
道瓊      {dow}
標普500   {sp500}
NASDAQ    {nasdaq}

📈 ETF
VOO       {voo}
QQQ       {qqq}
VTI       {vti}

🏭 台積電ADR
TSM       {tsm}

😱 市場情緒
VIX       {vix}

💵 匯率
USD/TWD   {usd_twd}

🕒 {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""

    return report


if __name__ == "__main__":

    print("=== Finance Agent Start ===")

    report = build_report()

    send_line_message(report)

    print("=== Finance Agent Finished ===")
