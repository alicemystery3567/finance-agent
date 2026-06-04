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


def get_market_info(symbol):
    try:
        ticker = yf.Ticker(symbol)

        hist = ticker.history(period="3d")

        if len(hist) < 2:
            return None

        current = hist["Close"].iloc[-1]
        previous = hist["Close"].iloc[-2]

        change_pct = ((current - previous) / previous) * 100

        sign = "🔺" if change_pct > 0 else "🔻" if change_pct < 0 else "🔹"

        return {
            "price": current,
            "pct": change_pct,
            "sign": sign
        }

    except Exception as e:
        print(f"{symbol} error: {e}")
        return None


def format_item(name, symbol):

    data = get_market_info(symbol)

    if data is None:
        return f"• {name}: 取得失敗"

    if symbol == "TWD=X":
        return (
            f"• {name}: "
            f"{data['price']:.4f} "
            f"({data['sign']}{data['pct']:+.2f}%)"
        )

    return (
        f"• {name}: "
        f"{data['price']:,.2f} "
        f"({data['sign']}{data['pct']:+.2f}%)"
    )


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

    title = get_report_title()

    report = f"""
{title}

🇺🇸【美股大盤】

{format_item("標普500指數", "^GSPC")}
{format_item("那斯達克指數", "^IXIC")}
{format_item("道瓊工業指數", "^DJI")}

📈【ETF】

{format_item("VOO", "VOO")}
{format_item("QQQ", "QQQ")}
{format_item("VTI", "VTI")}

🏭【台積電ADR】

{format_item("TSM", "TSM")}

😱【市場情緒】

{format_item("VIX恐慌指數", "^VIX")}

💵【匯率】

{format_item("USD/TWD", "TWD=X")}

🕒 {datetime.now().strftime("%Y-%m-%d %H:%M")}
"""

    return report


if __name__ == "__main__":

    print("=== Finance Agent Start ===")

    report = build_report()

    send_line_message(report)

    print("=== Finance Agent Finished ===")
