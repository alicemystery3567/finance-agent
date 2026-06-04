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
        "messages": [{"type": "text", "text": msg}]
    }
    print("正在嘗試發送 LINE 訊息...")
    response = requests.post(url, headers=headers, json=payload)
    print(f"LINE 回應狀態碼: {response.status_code}")

def get_market_data():
    print("開始抓取台/美股大盤與關鍵商品數據...")
    
    # 按照市場分類定義要監控的代號（新增 0050）
    market_categories = {
        "🇹🇼 【台股市場】": {
            "^TWII": "台股加權指數",
            "0050.TW": "元大台灣50 (0050)",
            "2330.TW": "台積電 (2330)",
            "2454.TW": "聯發科 (2454)"
        },
        "🇺🇸 【美股大盤】": {
            "^GSPC": "標普 500 指數",
            "^IXIC": "那斯達克指數",
            "^DJI": "道瓊工業指數"
        },
        "👑 【關鍵商品與匯率】": {
            "GC=F": "黃金期貨 (Gold)",
            "SI=F": "白銀期貨 (Silver)",
            "HG=F": "高級銅期貨 (Copper)",
            "TWD=X": "美元 / 新台幣 (USD/TWD)",
            "CNY=X": "美元 / 人民幣 (USD/CNY)"
        }
    }
    
    report_lines = []
    
    for category, targets in market_categories.items():
        report_lines.append(f"\n{category}")
        for ticker_id, name in targets.items():
            try:
                ticker = yf.Ticker(ticker_id)
                # 抓取最近 3 天的數據確保扣除休市日也能對比昨日收盤
                hist = ticker.history(period="3d")
                if len(hist) >= 2:
                    close_today = hist['Close'].iloc[-1]
                    close_yesterday = hist['Close'].iloc[-2]
                    change_pct = ((close_today - close_yesterday) / close_yesterday) * 100
                    
                    # 根據漲跌加上紅色/綠色/藍色視覺符號
                    sign = "🔺" if change_pct > 0 else "🔻" if change_pct < 0 else "🔹"
                    
                    # 格式化輸出
                    if "2330" in name or "2454" in name or "0050" in name:
                        # 台股個股與 ETF 價格（0050 習慣看兩位，個股看整數或依檔位，這裡統一保留兩位符合 yfinance 特性）
                        report_lines.append(f"• {name}: {close_today:,.2f} 元 ({sign}{change_pct:+.2f}%)")
                    elif "USD/TWD" in name or "USD/CNY" in name:
                        # 匯率精準顯示到小數點後四位
                        report_lines.append(f"• {name}: {close_today:.4f} ({sign}{change_pct:+.2f}%)")
                    else:
                        # 大盤指數與商品
                        report_lines.append(f"• {name}: {close_today:,.2f} ({sign}{change_pct:+.2f}%)")
                elif not hist.empty:
                    close_today = hist['Close'].iloc[-1]
                    report_lines.append(f"• {name}: {close_today:,.2f} (無昨日對比)")
            except Exception as e:
                print(f"抓取 {name} 失敗: {e}")
                report_lines.append(f"• {name}: 獲取失敗")
                
    return "\n".join(report_lines)

if __name__ == "__main__":
    print("=== 財經綜合監控 Agent 啟動 ===")
    
    market_report = get_market_data()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
    final_msg = f"\n📊 【AI 特助】每日資產市場監控報告\n報告時間: {current_time}\n" + market_report
    
    send_line_message(final_msg)
    print("=== Agent 執行完畢 ===")