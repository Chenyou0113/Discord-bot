# Google Search API 配置指南

## 1. 獲取 Google Custom Search API 金鑰

### 步驟一：創建 Google Cloud 專案
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 創建新專案或選擇現有專案
3. 啟用 "Custom Search API"

### 步驟二：獲取 API 金鑰
1. 在 Google Cloud Console 中，前往 "憑證" 頁面
2. 點擊 "建立憑證" > "API 金鑰"
3. 複製生成的 API 金鑰

### 步驟三：設定 Custom Search Engine
1. 前往 [Google Custom Search](https://cse.google.com/)
2. 點擊 "新增搜尋引擎"
3. 在「要搜尋的網站」中輸入 `*` (搜尋整個網路)
4. 設定搜尋引擎名稱
5. 建立後，複製「搜尋引擎 ID」

## 2. 環境變數設定

在您的 `.env` 檔案中添加以下設定：

```
# Google Search API 設定
GOOGLE_SEARCH_API_KEY=您的_Google_API_金鑰
GOOGLE_SEARCH_ENGINE_ID=您的_搜尋引擎_ID
```

## 3. API 使用限制

- 免費配額：每天 100 次搜尋請求
- 如需更多配額，需要付費升級
- 建議設定合理的用戶限制以避免超出配額

## 4. 搜尋功能特色

✅ **安全搜尋** - 自動過濾不當內容
✅ **多語言支援** - 支援中文和英文搜尋
✅ **速率限制** - 防止濫用
✅ **每日配額管理** - 控制API使用量
✅ **用戶冷卻機制** - 避免短時間大量請求
✅ **管理員設定** - 可調整限制參數
✅ **搜尋統計** - 追蹤使用情況

## 5. 指令說明

### `/search` - 網路搜尋
- **用途**: 在網路上搜尋資訊
- **參數**: 
  - `query`: 搜尋關鍵字 (必填)
  - `num_results`: 結果數量 1-5 (選填，預設3)
- **限制**: 10秒冷卻時間，每日50次

### `/search_settings` - 搜尋設定 (管理員專用)
- **用途**: 管理搜尋功能設定
- **動作**: 
  - `view`: 查看目前設定
  - `cooldown`: 調整冷卻時間 (1-300秒)
  - `daily_limit`: 調整每日限制 (1-1000次)
  - `reset_stats`: 重置用戶統計

### `/search_stats` - 搜尋統計
- **用途**: 查看個人搜尋使用統計
- **顯示**: 今日使用次數、剩餘次數、冷卻狀態

## 6. 管理員設定

在 `search_commands.py` 第 28 行添加管理員 Discord ID：

```python
self.admin_user_ids = [
    123456789012345678,  # 替換為實際的 Discord ID
    987654321098765432,  # 可以添加多個管理員
]
```

## 7. 故障排除

### 常見問題：

1. **「搜尋功能不可用」**
   - 檢查 `.env` 檔案中的 API 設定
   - 確認 API 金鑰和搜尋引擎 ID 正確

2. **「搜尋失敗」**
   - 檢查網路連線
   - 確認 API 配額未超出
   - 查看 bot.log 中的錯誤訊息

3. **權限錯誤**
   - 確認用戶為管理員或已添加到 admin_user_ids
   - 檢查伺服器管理員權限

## 8. 安全性考量

- API 金鑰應保密，不要提交到公開代碼庫
- 使用 `.env` 檔案存儲敏感資訊
- 定期檢查 API 使用量，避免意外超出配額
- 合理設定用戶限制，防止濫用

## 9. 費用管理

- 免費配額通常足夠小型 Discord 伺服器使用
- 如需更多配額，可在 Google Cloud Console 中設定計費
- 建議設定配額警告，避免意外產生費用
