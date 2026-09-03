import os
import pandas as pd
import requests
import yfinance as yf

TELEGRAM_BOT_TOKEN = "8833681673:AAF60AenVN6ClVhmp7Sazaw5IZ28Z1diYXw"
TELEGRAM_CHAT_ID = "8042354704"


def send_telegram_message(message):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
  response = requests.post(url, json=payload)
  return response.json()


def check_price_and_alert():
  gold = yf.Ticker("GC=F")
  data = gold.history(period="2d", interval="15m")

  if data.empty:
    print("ไม่สามารถดึงข้อมูลราคาได้")
    return

  low_14 = data["Low"].rolling(window=14).min()
  high_14 = data["High"].rolling(window=14).max()
  data["Stoch_K"] = (
      (data["Close"] - low_14) / (high_14 - low_14)
  ) * 100
  data["Stoch_D"] = data["Stoch_K"].rolling(window=3).mean()

  current_close = data["Close"].iloc[-1]
  current_k = data["Stoch_K"].iloc[-1]
  current_d = data["Stoch_D"].iloc[-1]
  prev_k = data["Stoch_K"].iloc[-2]
  prev_d = data["Stoch_D"].iloc[-2]

  recent_high = data["High"].iloc[-5:-1].max()
  recent_low = data["Low"].iloc[-5:-1].min()

  is_bullish_cross = (prev_k < prev_d) and (current_k > current_d) and (current_k < 30)
  is_bearish_cross = (prev_k > prev_d) and (current_k < current_d) and (current_k > 70)

  if is_bullish_cross:
    entry_price = current_close
    sl_price = recent_low - 1.5
    tp_price = entry_price + ((entry_price - sl_price) * 2)

    message = (
        f"🟢 *สัญญาณ BUY (TL Apex Reversal)*\n\n"
        f"📍 **Entry Price:** `{entry_price:.2f}`\n"
        f"🛑 **Stop Loss (SL):** `{sl_price:.2f}`\n"
        f"🎯 **Take Profit (TP):** `{tp_price:.2f}`\n\n"
        f"📊 *Stoch %K ตัด %D ขึ้นในโซน Oversold*"
    )
    send_telegram_message(message)

  elif is_bearish_cross:
    entry_price = current_close
    sl_price = recent_high + 1.5
    tp_price = entry_price - ((sl_price - entry_price) * 2)

    message = (
        f"🔴 *สัญญาณ SELL (TL Apex Reversal)*\n\n"
        f"📍 **Entry Price:** `{entry_price:.2f}`\n"
        f"🛑 **Stop Loss (SL):** `{sl_price:.2f}`\n"
        f"🎯 **Take Profit (TP):** `{tp_price:.2f}`\n\n"
        f"📊 *Stoch %K ตัด %D ลงในโซน Overbought*"
    )
    send_telegram_message(message)


if __name__ == "__main__":
  check_price_and_alert()
