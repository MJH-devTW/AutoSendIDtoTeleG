# 自動爬取周轉率和自動0903發送tg_main.py
# A : 爬取周轉率.py
# B : 即時發送到TG.py

import subprocess
import time
from datetime import datetime, time as dt_time

def run_script(script_name):
    """使用 subprocess 執行指定的 Python 腳本."""
    try:
        subprocess.run(['python', script_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"執行 {script_name} 發生錯誤，錯誤訊息: {e}")

if __name__ == '__main__':
    # 設定目標時間區間及標記變數
    target_time_A_start = "18:00:00"
    target_time_A_end = "19:00:00"
    target_time_B = "09:03:01"

    # 紀錄 A 和 B 是否已執行
    A_executed_today = False
    B_executed_today = False

    while True:
        # 取得當前日期與時間
        current_date = datetime.now().date()
        current_time = datetime.now().time()

        # 設定目標時間區間及標記變數，直接使用 datetime.time 格式
        target_time_A_start = dt_time(18, 0, 0)  # 18:00:00
        target_time_A_end = dt_time(19, 0, 0)  # 19:00:00
        target_time_B = dt_time(9, 3, 1)  # 09:03:01

        # 檢查是否到達新的一天，如果是則重置執行標記
        if current_time < target_time_A_start:
            A_executed_today = False
            B_executed_today = False

        # 檢查是否在 18:00 到 19:00 之間，並且 A 尚未執行過
        if target_time_A_start <= current_time <= target_time_A_end and not A_executed_today:
            print(f"{datetime.now()} - 正在執行爬蟲程序 爬取周轉率.py...")
            run_script('爬取周轉率.py')  # 執行 A 程式（爬取周轉率.py）
            A_executed_today = True  # 標記 A 已經執行過
            print(f"{datetime.now()} - 爬取周轉率.py 執行完成")

        # 檢查是否到達 09:03:01 且 B 尚未執行過
        if current_time.strftime('%H:%M:%S') == target_time_B.strftime('%H:%M:%S') and not B_executed_today:
            print(f"{datetime.now()} - 正在執行發送程序 即時發送到TG.py...")
            run_script('即時發送到TG.py')  # 執行 B 程式（即時發送到TG.py）
            B_executed_today = True  # 標記 B 已經執行過
            print(f"{datetime.now()} - 即時發送到TG.py 執行完成")

        # 每秒檢查一次
        time.sleep(1)

