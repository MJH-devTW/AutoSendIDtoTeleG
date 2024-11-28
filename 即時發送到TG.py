# 即時發送到TG.py
import os
import time
import pandas as pd
import shioaji as sj
import telebot
from datetime import datetime
from typing import List, Tuple, Optional

# Telegram Bot 的 Token
TOKEN = '---Use Youself TOKEN---'
bot = telebot.TeleBot(TOKEN)

# 初始化完成後發送消息到群組
init_message = 'init--- 初始化完成'
bot.send_message("---Use Youself ID---", init_message)
print("訊息已發送！", init_message)

# 定義獲取K線資料的函數
# def get_kbars_with_trend(api, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
#     """從 API 獲取 Kbars 資料並處理漲跌趨勢."""
#     kbars = api.kbars(
#         contract=api.Contracts.Stocks[stock_code],
#         start=start_date,
#         end=end_date
#     )
#     df_kbars = pd.DataFrame({**kbars})
#     df_kbars.ts = pd.to_datetime(df_kbars.ts)  # 將 'ts' 欄位轉換為 datetime 格式
#     df_kbars['漲跌'] = df_kbars.apply(lambda row: '紅' if row['Close'] > row['Open'] else ('綠' if row['Close'] < row['Open'] else '白'), axis=1)
#     df_kbars['change_price'] = df_kbars['Close'] - df_kbars['Open']
#     return df_kbars[['ts', 'Open', 'High', 'Low', 'Close', '漲跌', 'Volume', 'Amount', 'change_price']]


def get_kbars_with_trend(api, stock_code: str, start_date: str, end_date: str) -> pd.DataFrame:
    """從 API 獲取 Kbars 資料並處理漲跌趨勢."""
    try:
        # 確認 API 物件不為 None
        if api is None:
            raise ValueError("API 物件未正確初始化，請檢查 API 初始化流程。")

        # 獲取 K 線資料
        kbars = api.kbars(
            contract=api.Contracts.Stocks[stock_code],
            start=start_date,
            end=end_date
        )

        # 檢查是否成功取得 K 線資料
        if kbars is None:
            raise ValueError("無法取得 K 線數據，請確認 API 是否正常工作。")

        # 將 kbars 資料轉換為 DataFrame
        df_kbars = pd.DataFrame({**kbars})

        # 檢查 DataFrame 是否為空
        if df_kbars.empty:
            raise ValueError("取得的 K 線數據為空，請確認股票代碼及日期範圍是否正確。")

        # 將 'ts' 欄位轉換為 datetime 格式
        df_kbars.ts = pd.to_datetime(df_kbars.ts)

        # 計算漲跌趨勢：紅（漲），綠（跌），白（平）
        df_kbars['漲跌'] = df_kbars.apply(lambda row: '紅' if row['Close'] > row['Open'] else ('綠' if row['Close'] < row['Open'] else '白'), axis=1)

        # 計算每筆資料的漲跌幅度
        df_kbars['change_price'] = df_kbars['Close'] - df_kbars['Open']

        # 返回指定欄位的資料
        return df_kbars[['ts', 'Open', 'High', 'Low', 'Close', '漲跌', 'Volume', 'Amount', 'change_price']]

    except Exception as e:
        print(f"取得 K 線數據時發生錯誤: {e}")
        return pd.DataFrame()  # 若發生錯誤則返回空的 DataFrame


def format_kbars_message(stock_code: str, kbars_df: pd.DataFrame) -> str:
    """格式化K線資料，生成發送的Telegram消息."""
    message = f"股票代號 {stock_code}\n"
    for index, row in kbars_df.iterrows():
        time_str = row['ts'].strftime('%H:%M:%S')  # 只取時間部分
        message += f"{time_str} {row['漲跌']} \n"
    return message

def send_message_to_terminal_and_telegram(bot: telebot.TeleBot, chat_id: str, message: str):
    """同時將訊息發送到終端和Telegram."""
    print(message)  # 終端機輸出
    bot.send_message(chat_id, message)  # 發送 Telegram 訊息

def calculate_ticks(price_start: float, price_end: float) -> int:
    """計算從 price_start 到 price_end 的變動 tick 數量."""
    tick_intervals = [
        (0, 10, 0.01), (10, 50, 0.05), (50, 100, 0.1),
        (100, 500, 0.5), (500, 1000, 1), (1000, float('inf'), 5)
    ]
    def ticks_in_range(p_start, p_end, tick_size):
        return (p_end - p_start) / tick_size

    total_ticks = 0
    current_price = price_start
    for lower_bound, upper_bound, tick_size in tick_intervals:
        if current_price < upper_bound:
            end_price = min(price_end, upper_bound)
            total_ticks += ticks_in_range(current_price, end_price, tick_size)
            current_price = end_price
            if current_price >= price_end:
                break
    return int(total_ticks)

def format_kbars_message_with_ticks(stock_code: str, kbars_df: pd.DataFrame) -> str:
    """格式化K線資料，加入tick計算結果並生成發送的Telegram消息."""
    message = f"股票代號 {stock_code}\n"
    for _, row in kbars_df.iterrows():
        time_str = row['ts'].strftime('%H:%M')  # 取當前時間部分
        trend = row['漲跌']
        price_start = row['Open']
        price_end = row['Close']
        change_price = row['change_price']
        tick_value = calculate_ticks(price_start, price_end)
        message += f"{time_str} {trend} {change_price:>6.2f} [{tick_value:>3} t] \n"
    return message

def find_closest_file(target_date: str, directory: str = "過濾輸出") -> Tuple[Optional[str], Optional[datetime]]:
    """在指定目錄中查找最接近目標日期的 CSV 檔案."""
    target_date = datetime.strptime(target_date, '%Y-%m-%d')
    files = os.listdir(directory)
    closest_file, closest_date, smallest_diff = None, None, None
    for file in files:
        if file.startswith('output_') and file.endswith('.csv'):
            file_date_str = file[len('output_'):-len('.csv')]
            try:
                file_date = datetime.strptime(file_date_str, '%Y-%m-%d')
                if file_date == target_date:
                    continue
                date_diff = abs((file_date - target_date).days)
                if smallest_diff is None or date_diff < smallest_diff:
                    smallest_diff, closest_file, closest_date = date_diff, file, file_date
            except ValueError:
                continue
    return (os.path.join(directory, closest_file), closest_date) if closest_file else (None, None)

def read_stock_ids(file_path: str) -> List[str]:
    """從指定 CSV 檔案中讀取商品代號列表."""
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    return df['商品代號'].tolist()

if __name__ == '__main__':
    # 初始化 API 物件並登入
    api = sj.Shioaji()
    api.login(
        api_key='---Use Youself api_key---',
        secret_key='---Use Youself secret_key---',
        contracts_cb=lambda security_type: print(f"{repr(security_type)} fetch done.")
    )
    if api is None:
        raise ValueError("API 初始化失敗，請檢查 API 資訊。")

    # 設定目標日期與時間

    today = datetime.today()
    target_date = today.strftime('%Y-%m-%d')


    #target_date = "2024-09-30"
    target_time = "09:03:01"

    # 讀取最近日期的過濾檔案
    closest_file, closest_date = find_closest_file(target_date)
    if closest_file:
        print(f"最接近的檔案是: {closest_file}, 日期: {closest_date.strftime('%Y-%m-%d')}")
    else:
        print("沒有找到符合條件的檔案")
        exit()

    # 讀取股票代號列表
    stock_ids = read_stock_ids(closest_file)
    print("擷取到的商品代號:", stock_ids)

    queried_stocks = set()  # 記錄已經查詢過的股票

    # 開始即時檢查時間並在目標時間執行發送程序
    while True:
        now_date = datetime.now().strftime('%Y-%m-%d')
        now_time = datetime.now().strftime('%H:%M:%S')

        if now_date >= target_date and now_time >= target_time and len(queried_stocks) < len(stock_ids):
            for stock_code in stock_ids:
                if stock_code not in queried_stocks:
                    kbars_df = get_kbars_with_trend(api, str(stock_code), target_date, target_date)
                    if not kbars_df.empty:
                        first_three_rows = kbars_df.head(3)
                        if '綠' in first_three_rows['漲跌'].values or all(first_three_rows['漲跌'] == '白'):
                            continue  # 如果前三筆有綠色，跳過此次股票處理
                        formatted_message = format_kbars_message_with_ticks(stock_code, kbars_df.head(5))
                        send_message_to_terminal_and_telegram(bot, "---Use Youself ID---", formatted_message)

                    queried_stocks.add(stock_code)

            if len(queried_stocks) == len(stock_ids):
                break

        time.sleep(1)

    # 登出 API
    api.logout()
    print("登出")
