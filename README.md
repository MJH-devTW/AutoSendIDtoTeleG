# 即時發送到TG.py

本程式整合多種功能，實現即時從 Shioaji API 獲取股票數據並格式化後發送至 Telegram 群組。
該程式適合用於金融市場的實時監控與數據提醒，方便交易者快速接收重要資訊。

注意:需搭配另一篇git的文章進行自動爬取 附件有付

---

## 程式碼大綱

### 1. **初始化與基本設定**
- **功能**：
  - 初始化 Telegram Bot，並在完成啟動時發送初始化完成的消息。
  - 初始化 Shioaji API，實現股票數據的查詢功能。
- **用途**：
  - 保證程式運行時與 Telegram 和 API 正常連接。

### 2. **即時股票數據查詢**
- **功能**：
  - 通過 Shioaji API 獲取指定股票的即時 K 線數據。
  - 對數據進行清理與格式化，計算漲跌趨勢與漲跌幅度。

### 3. **數據格式化與發送**
- **功能**：
  - 將整理後的 K 線數據格式化為易於閱讀的消息格式。
  - 計算價格變動的 tick 數量，並附加至消息中。
  - 將消息發送到 Telegram 群組，同時顯示於終端。

### 4. **過濾數據與檔案管理**
- **功能**：
  - 從目錄中查找最接近目標日期的數據檔案。
  - 提取檔案中的股票代號列表，用於後續查詢與處理。

### 5. **目標時間檢查與通知發送**
- **功能**：
  - 持續監控系統時間，當達到設定的目標時間時自動執行數據查詢與發送程序。
  - 支援多支股票的批量處理，確保所有目標股票都能被查詢與通知。

### 6. **API 資源管理**
- **功能**：
  - 在程式結束時自動登出 Shioaji API，釋放系統資源。

---

## 注意事項

1. **Telegram Bot Token**：
   請將 `TOKEN` 替換為您自己的 Telegram Bot Token。

2. **Shioaji API 設定**：
   請根據需求填入有效的 API Key 與 Secret Key。

3. **檔案格式與路徑**：
   確保指定的數據目錄（例如 `過濾輸出`）存在，且檔案格式正確。

4. **定時執行**：
   確保設定正確的目標日期與時間，例如：
   ```python
   target_date = "2024-09-30"
   target_time = "09:03:01"
