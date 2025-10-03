# 捷運車站設施查詢功能說明

## 📋 功能概述
新增 `/metro_facility` 指令,可查詢台灣各捷運系統的車站設施資訊,包括電梯、電扶梯、廁所、哺集乳室等設施。

## 🚇 支援的捷運系統

| 系統代碼 | 系統名稱 | API 端點 |
|---------|---------|----------|
| **TRTC** | 臺北捷運 | Rail/Metro/StationFacility/TRTC |
| **TYMC** | 桃園捷運 | Rail/Metro/StationFacility/TYMC |
| **NTMC** | 新北捷運 | Rail/Metro/StationFacility/NTMC |
| **TMRT** | 臺中捷運 | Rail/Metro/StationFacility/TMRT |

## ✨ 功能特點

### 📊 顯示資訊
每個車站會顯示以下設施(如有):
- 🛗 **電梯** - Elevator
- 🚶 **電扶梯** - Escalator
- 🚻 **廁所** - Toilet
- 🍼 **哺集乳室** - NursingRoom
- 🏥 **AED** - 自動體外心臟去顫器
- 🔐 **置物櫃** - Locker
- 🅿️ **停車場** - Parking
- 🚲 **自行車停車** - BikeParking
- 📶 **WiFi** - 無線網路
- 🔌 **充電站** - ChargingStation
- 🎫 **售票機** - TicketMachine

### 📄 分頁顯示
- **每頁顯示**: 3 個車站
- **導航按鈕**: ◀️ 上一頁 | ▶️ 下一頁
- **智能按鈕**: 首頁/尾頁自動禁用按鈕
- **超時保護**: 5 分鐘後自動禁用

## 💻 使用方式

### 基本用法
```
/metro_facility metro_system:臺北捷運
```

### 選項說明
```
metro_system: 選擇要查詢的捷運系統
  - 臺北捷運 (TRTC)
  - 桃園捷運 (TYMC)
  - 新北捷運 (NTMC)
  - 臺中捷運 (TMRT)
```

## 📱 顯示範例

```
🚇 臺北捷運 車站設施

🚉 1. 台北車站 (R10)
🛗 電梯 | 🚶 電扶梯 | 🚻 廁所 | 🍼 哺集乳室 | 🏥 AED | 🔐 置物櫃 | 🅿️ 停車場 | 📶 WiFi | 🎫 售票機

🚉 2. 西門站 (G12)
🛗 電梯 | 🚶 電扶梯 | 🚻 廁所 | 🏥 AED | 📶 WiFi | 🎫 售票機

🚉 3. 中正紀念堂站 (R08)
🛗 電梯 | 🚶 電扶梯 | 🚻 廁所 | 🍼 哺集乳室 | 🏥 AED | 🔐 置物櫃 | 📶 WiFi | 🎫 售票機

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
第 1/25 頁 | 共 73 個車站 | TDX運輸資料流通服務
[◀️ 上一頁] [▶️ 下一頁]
```

## 🔧 技術實現

### API 資料來源
- **平台**: TDX運輸資料流通服務
- **版本**: v2 API
- **認證**: Bearer Token
- **格式**: JSON

### 資料結構
```python
{
    "StationID": "R10",
    "StationName": {
        "Zh_tw": "台北車站"
    },
    "Elevator": true,
    "Escalator": true,
    "Toilet": true,
    "NursingRoom": true,
    "AED": true,
    "Locker": true,
    "Parking": true,
    "BikeParking": false,
    "WiFi": true,
    "ChargingStation": false,
    "TicketMachine": true
}
```

### 核心函數
1. **fetch_metro_facility()** - 獲取設施資料
   ```python
   async def fetch_metro_facility(self, metro_system: str)
   ```
   - 參數: metro_system (TRTC/TYMC/NTMC/TMRT)
   - 回傳: List[Dict] 或 None

2. **MetroFacilityPaginationView** - 分頁視圖類
   ```python
   class MetroFacilityPaginationView(View)
   ```
   - 每頁 3 個車站
   - 自動計算總頁數
   - 動態更新按鈕狀態

## 📈 使用情境

### 適用對象
- 🦽 **行動不便者** - 查詢電梯、無障礙設施
- 👶 **親子乘客** - 尋找哺集乳室
- 🚲 **單車族** - 確認自行車停車位
- 🅿️ **開車族** - 查詢停車場資訊
- 📱 **數位需求** - WiFi、充電站位置

### 查詢範例
1. **無障礙設施**: 查看哪些車站有電梯
2. **親子友善**: 尋找有哺集乳室的車站
3. **緊急需求**: 確認 AED 位置
4. **停車資訊**: 查詢停車場和單車停放處

## ⚙️ 指令統計

### 同步狀態
- ✅ 指令總數: **46 個** (新增 1 個)
- ✅ 新增指令: `metro_facility`
- ✅ 同步時間: 2025-10-03 01:10:21
- ✅ 所有系統: 運作正常

### 捷運相關指令列表
| 指令 | 說明 | 狀態 |
|------|------|------|
| `/metro_status` | 查詢捷運運行狀態 | ✅ |
| `/metro_liveboard` | 即時電子看板 | ✅ |
| `/metro_direction` | 按方向查詢 | ✅ |
| `/metro_news` | 最新消息 | ✅ |
| `/metro_facility` | 車站設施 | ✅ **NEW** |

## 🎨 UI/UX 設計

### 顏色配置
- **主色**: 綠色 (0x2ECC71) - 代表友善、可訪問性
- **按鈕**: Primary Style (藍色)
- **Emoji**: 豐富的圖示增強可讀性

### 使用者體驗
- ✅ 清晰的設施圖示
- ✅ 直覺的分頁導航
- ✅ 權限驗證(只有發起者可操作)
- ✅ 超時自動禁用按鈕
- ✅ 即時錯誤提示

## 🐛 錯誤處理

### 情境處理
1. **API 失敗**: 顯示友善錯誤訊息
2. **無資料**: 提示目前無設施資料
3. **權限錯誤**: 提示無操作權限
4. **超時**: 自動禁用所有按鈕

### 日誌記錄
```python
logger.info(f"使用者 {user} 查詢捷運車站設施: {system_name}")
logger.info(f"✅ 成功取得{system}車站設施資料，共{count}筆")
logger.error(f"metro_facility 指令執行時發生錯誤: {error}")
```

## 📝 更新記錄
- **2025-10-03 01:10**: 新增 metro_facility 指令
- **2025-10-03 01:10**: 支援 4 個捷運系統查詢
- **2025-10-03 01:10**: 實現分頁顯示(每頁3個車站)
- **2025-10-03 01:10**: 新增 11 種設施類型圖示

## 🔮 未來擴充
- [ ] 新增高雄捷運 (KRTC) 支援
- [ ] 新增高雄輕軌 (KLRT) 支援
- [ ] 提供設施篩選功能(只顯示有特定設施的車站)
- [ ] 地圖整合(顯示車站位置)
- [ ] 設施照片預覽

## 📞 維護說明

### 檔案位置
- **主檔案**: `cogs/info_commands_fixed_v4_clean.py`
- **指令定義**: 約 3748-3785 行
- **資料獲取**: 約 3854-3898 行
- **視圖類**: 約 6098-6242 行

### 修改建議
如需調整:
1. **修改每頁顯示數量**: 修改 `self.items_per_page = 3`
2. **新增設施類型**: 在 `create_embed()` 方法中添加判斷
3. **調整顏色**: 修改 `color=0x2ECC71`
4. **變更超時**: 修改 `timeout=300` (秒)

## 🎉 使用效果
- ✅ 快速查詢車站無障礙設施
- ✅ 友善的親子設施資訊
- ✅ 完整的便民服務一覽
- ✅ 直覺的操作介面
- ✅ 可靠的資料來源(官方 TDX 平台)

---
**資料來源**: TDX運輸資料流通服務平臺  
**API 版本**: v2  
**更新日期**: 2025-10-03
