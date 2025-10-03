# 捷運車站設施查詢 - 修復前後對比

## 修復前 (Markdown 連結在 Field)

```
┌─────────────────────────────────────────┐
│  🚇 頂埔站設施資訊                      │
├─────────────────────────────────────────┤
│  🚉 車站名稱                            │
│  頂埔站                                 │
│                                         │
│  🏷️ 車站代碼                           │
│  BL01                                   │
│                                         │
│  🎯 車站設施                            │
│  無詳細設施資訊                         │
│                                         │
│  🗺️ 車站設施圖                         │
│  [頂埔站資訊圖](https://web.metro...)   │  ← 純文字,無法點擊 ❌
│                                         │
│  📍 位置                                │
│  [Google Maps](https://...)            │  ← 可以點擊 ✅
│                                         │
│  資料來源: TDX運輸資料流通服務          │
└─────────────────────────────────────────┘
```

**問題**: 
- Field value 中的 Markdown 連結不會渲染
- 使用者看到純文字,無法點擊開啟 PDF
- 與 Google Maps 連結的行為不一致 (description 可點擊)

---

## 修復後 (Button 組件)

```
┌─────────────────────────────────────────┐
│  🚇 頂埔站設施資訊                      │
├─────────────────────────────────────────┤
│  🚉 車站名稱                            │
│  頂埔站                                 │
│                                         │
│  🏷️ 車站代碼                           │
│  BL01                                   │
│                                         │
│  🎯 車站設施                            │
│  無詳細設施資訊                         │
│                                         │
│  📍 位置                                │
│  [Google Maps](https://...)            │
│                                         │
│  資料來源: TDX運輸資料流通服務          │
└─────────────────────────────────────────┘
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  🗺️ 頂埔站資訊圖                 │ │  ← 藍色按鈕,可點擊 ✅
│  └───────────────────────────────────┘ │
```

**改善**: 
- 按鈕顯示在訊息下方
- 清楚的視覺提示 (藍色按鈕)
- 點擊後在新分頁開啟 PDF
- 符合 Discord UI 設計規範

---

## 程式碼對比

### 舊版 (有問題)
```python
# 設施地圖 (PDF 連結)
facility_maps = station_data.get('FacilityMapURLs', [])
if facility_maps and len(facility_maps) > 0:
    map_links = []
    for map_item in facility_maps[:3]:
        map_name = map_item.get('MapName', {}).get('Zh_tw', '車站資訊圖')
        map_url = map_item.get('MapURL', '')
        if map_url:
            map_links.append(f"[{map_name}]({map_url})")  # Markdown 格式
    
    if map_links:
        embed.add_field(
            name="🗺️ 車站設施圖",
            value="\n".join(map_links),  # ❌ Field value 不支援 Markdown 連結
            inline=False
        )

await interaction.response.edit_message(embed=embed, view=None)
```

### 新版 (已修復)
```python
# 建立包含設施地圖按鈕的 View
button_view = View(timeout=300)

# 新增設施地圖按鈕
facility_maps = station_data.get('FacilityMapURLs', [])
if facility_maps and len(facility_maps) > 0:
    for map_item in facility_maps[:5]:  # 最多5個按鈕
        map_name = map_item.get('MapName', {}).get('Zh_tw', '車站資訊圖')
        map_url = map_item.get('MapURL', '')
        if map_url:
            button = Button(
                label=f"🗺️ {map_name}",
                url=map_url,
                style=discord.ButtonStyle.link  # ✅ 連結按鈕
            )
            button_view.add_item(button)

await interaction.response.edit_message(embed=embed, view=button_view)  # ✅ 傳入 button_view
```

---

## 支援多個連結

如果 API 回傳多個設施圖:

```python
facility_maps = [
    {'MapName': {'Zh_tw': '頂埔站資訊圖'}, 'MapURL': 'https://...076.pdf'},
    {'MapName': {'Zh_tw': '頂埔站路線圖'}, 'MapURL': 'https://...077.pdf'},
    {'MapName': {'Zh_tw': '頂埔站周邊圖'}, 'MapURL': 'https://...078.pdf'}
]
```

**顯示結果**:
```
┌─────────────────────────────────────────┐
│  🚇 頂埔站設施資訊                      │
│  (embed content...)                     │
└─────────────────────────────────────────┘
│                                         │
│  ┌───────────────────────────────────┐ │
│  │  🗺️ 頂埔站資訊圖                 │ │  ← 按鈕 1
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  🗺️ 頂埔站路線圖                 │ │  ← 按鈕 2
│  └───────────────────────────────────┘ │
│  ┌───────────────────────────────────┐ │
│  │  🗺️ 頂埔站周邊圖                 │ │  ← 按鈕 3
│  └───────────────────────────────────┘ │
```

最多可顯示 **5 個按鈕** (超過會自動截斷)

---

## 實際 API 資料範例

來自 TDX API 的真實回應 (頂埔站):

```json
{
  "StationID": "BL01",
  "StationName": {"Zh_tw": "頂埔"},
  "LineID": "BL",
  "FacilityMapURLs": [
    {
      "MapName": {"Zh_tw": "頂埔站資訊圖"},
      "MapURL": "https://web.metro.taipei/img/ALL/INFOPDF/076.pdf"
    }
  ],
  "Elevators": [],
  "Toilets": [],
  "Parkings": []
}
```

**說明**:
- `Elevators`, `Toilets` 等為空陣列 → 顯示「無詳細設施資訊」
- `FacilityMapURLs` 有資料 → 建立按鈕連結到 PDF

---

## Discord 限制參考

### Button 組件限制
- 每個 ActionRow 最多 5 個 button
- 每個訊息最多 5 個 ActionRow
- 總計: 25 個 button 上限

### 當前實作
- 設定為最多 5 個按鈕: `facility_maps[:5]`
- 單一 ActionRow (自動管理)
- 超時時間: 300 秒 (5 分鐘)

### Embed 限制
- Title: 256 字元
- Description: 4096 字元
- Field name: 256 字元
- Field value: 1024 字元
- Footer text: 2048 字元
- Total fields: 25 個
- Total characters: 6000 字元

---

## 測試案例

### 案例 1: 無設施地圖
```json
{
  "FacilityMapURLs": []
}
```
**結果**: 不顯示按鈕,只有 embed 內容

### 案例 2: 單一設施地圖
```json
{
  "FacilityMapURLs": [
    {"MapName": {"Zh_tw": "頂埔站資訊圖"}, "MapURL": "https://...076.pdf"}
  ]
}
```
**結果**: 顯示 1 個按鈕

### 案例 3: 多個設施地圖
```json
{
  "FacilityMapURLs": [
    {"MapName": {"Zh_tw": "站內圖"}, "MapURL": "https://...01.pdf"},
    {"MapName": {"Zh_tw": "出口圖"}, "MapURL": "https://...02.pdf"},
    {"MapName": {"Zh_tw": "路線圖"}, "MapURL": "https://...03.pdf"},
    {"MapName": {"Zh_tw": "周邊圖"}, "MapURL": "https://...04.pdf"},
    {"MapName": {"Zh_tw": "轉乘圖"}, "MapURL": "https://...05.pdf"},
    {"MapName": {"Zh_tw": "無障礙圖"}, "MapURL": "https://...06.pdf"}
  ]
}
```
**結果**: 顯示前 5 個按鈕 (第 6 個被截斷)

---

## 結論

✅ **修復完成**: 設施地圖連結現在可以正常點擊
✅ **使用者體驗**: 清楚的藍色按鈕,符合 Discord UI 規範
✅ **技術正確**: 使用 discord.ui.Button 組件,而非不支援的 Markdown
✅ **已測試驗證**: 語法檢查、程式碼驗證、Bot 部署皆通過
