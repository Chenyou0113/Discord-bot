# 氣象測站查詢功能說明

## 功能概述

這個功能為 Discord 機器人新增了查詢中央氣象署無人氣象測站基本資料的能力。使用者可以通過斜線指令查詢全台各地的無人氣象測站資訊。

## 可用指令

### 1. `/weather_station` - 測站搜尋
**功能：** 根據關鍵字搜尋氣象測站
**參數：**
- `query` (必填): 搜尋關鍵字（測站名稱、編號、縣市或位置）
- `page` (選填): 頁數，預設為第1頁

**使用範例：**
```
/weather_station query:台北
/weather_station query:板橋 page:2
/weather_station query:C0A940
/weather_station query:學校
```

### 2. `/weather_station_by_county` - 縣市查詢
**功能：** 按縣市查詢氣象測站
**參數：**
- `county` (必填): 縣市名稱
- `status` (選填): 測站狀態篩選（全部/現存測站/已撤銷）
- `page` (選填): 頁數，預設為第1頁

**使用範例：**
```
/weather_station_by_county county:新北市
/weather_station_by_county county:台北市 status:現存測站
/weather_station_by_county county:花蓮縣 status:已撤銷 page:2
```

### 3. `/weather_station_info` - 詳細資訊
**功能：** 查詢特定測站的詳細資訊
**參數：**
- `station_id` (必填): 測站編號

**使用範例：**
```
/weather_station_info station_id:C0A940
/weather_station_info station_id:C0U620
```

## 顯示資訊

### 測站列表顯示
- 測站狀態（🟢 現存測站 / 🔴 已撤銷 / 🟡 其他）
- 測站名稱和編號
- 所在縣市
- 位置簡述
- 分頁瀏覽（每頁10個測站）

### 測站詳細資訊顯示
- **基本資訊**：測站名稱（中英文）、編號、狀態
- **地理位置**：縣市、詳細位置、海拔高度、經緯度
- **運作時間**：啟用日期、結束日期
- **測站變更**：原測站編號、新測站編號（如有）
- **備註**：相關說明（如有）
- **地圖位置**：Google 地圖連結

## 搜尋技巧

### 1. 測站名稱搜尋
```
/weather_station query:板橋
/weather_station query:金山
/weather_station query:鯉魚潭
```

### 2. 測站編號搜尋
```
/weather_station query:C0A940
/weather_station query:C0U620
```

### 3. 縣市搜尋
```
/weather_station query:新北市
/weather_station query:台北市
/weather_station query:宜蘭縣
```

### 4. 位置關鍵字搜尋
```
/weather_station query:國小
/weather_station query:學校
/weather_station query:公園
/weather_station query:消防
```

## 測站狀態說明

- **🟢 現存測站**：目前正在運作的測站
- **🔴 已撤銷**：已停止運作或撤銷的測站
- **🟡 其他狀態**：特殊狀態的測站

## 資料來源

所有資料來源於中央氣象署開放資料平臺：
- 資料集：無人氣象測站基本資料 (C-B0074-002)
- 更新頻率：定期更新
- 快取時間：1小時（提升查詢速度）

## 注意事項

1. **網路延遲**：首次查詢可能需要較長時間載入資料
2. **快取機制**：資料會快取1小時，提升後續查詢速度
3. **分頁瀏覽**：搜尋結果超過10個時會自動分頁
4. **精確搜尋**：使用測站編號可直接獲得詳細資訊
5. **地圖連結**：點擊可在 Google 地圖中查看測站位置

## 錯誤處理

- **資料獲取失敗**：API 連線問題，請稍後再試
- **未找到結果**：請檢查搜尋關鍵字是否正確
- **頁數超出範圍**：請輸入有效的頁數範圍
- **系統錯誤**：內部錯誤，請聯繫管理員

## 使用範例流程

### 情境1：查詢特定地區的測站
1. 使用 `/weather_station_by_county county:新北市` 查看新北市所有測站
2. 從列表中找到感興趣的測站編號
3. 使用 `/weather_station_info station_id:C0A940` 查看詳細資訊

### 情境2：搜尋特定名稱的測站
1. 使用 `/weather_station query:板橋` 搜尋包含"板橋"的測站
2. 如果結果太多，可以更精確地搜尋 `/weather_station query:板橋國小`
3. 點擊地圖連結查看測站實際位置

### 情境3：瀏覽所有現存測站
1. 使用 `/weather_station_by_county county:台北市 status:現存測站` 查看台北市現存測站
2. 使用 `page` 參數瀏覽不同頁面
3. 對感興趣的測站使用 `/weather_station_info` 查看詳細資訊

## 技術細節

- **API 端點**：https://opendata.cwa.gov.tw/api/v1/rest/datastore/C-B0074-002
- **資料格式**：JSON
- **快取策略**：記憶體快取，1小時過期
- **錯誤處理**：完整的錯誤捕獲和使用者友好的錯誤訊息
- **分頁機制**：每頁顯示10個結果，支援無限分頁
