"""
測試設施地圖按鈕實作
驗證按鈕組件是否正確建立
"""

import discord
from discord.ui import View, Button

# 模擬 API 資料
station_data = {
    'StationName': {'Zh_tw': '頂埔'},
    'FacilityMapURLs': [
        {
            'MapName': {'Zh_tw': '頂埔站資訊圖'},
            'MapURL': 'https://web.metro.taipei/img/ALL/INFOPDF/076.pdf'
        },
        {
            'MapName': {'Zh_tw': '頂埔站路線圖'},
            'MapURL': 'https://web.metro.taipei/img/ALL/INFOPDF/077.pdf'
        }
    ]
}

print("=== 測試設施地圖按鈕建立 ===\n")

# 建立 View
button_view = View(timeout=300)

# 新增設施地圖按鈕
facility_maps = station_data.get('FacilityMapURLs', [])
if facility_maps and len(facility_maps) > 0:
    print(f"找到 {len(facility_maps)} 個設施地圖")
    for i, map_item in enumerate(facility_maps[:5], 1):
        map_name = map_item.get('MapName', {}).get('Zh_tw', '車站資訊圖')
        map_url = map_item.get('MapURL', '')
        if map_url:
            button = Button(
                label=f"🗺️ {map_name}",
                url=map_url,
                style=discord.ButtonStyle.link
            )
            button_view.add_item(button)
            print(f"  按鈕 {i}:")
            print(f"    標籤: {button.label}")
            print(f"    URL: {button.url}")
            print(f"    樣式: {button.style}")
            print()

print(f"✅ 成功建立 {len(button_view.children)} 個按鈕")
print("\n=== 按鈕特性 ===")
print("- 類型: discord.ui.Button")
print("- 樣式: ButtonStyle.link (外部連結)")
print("- 行為: 點擊後在新分頁開啟 PDF")
print("- 顯示: 訊息下方的藍色按鈕")
