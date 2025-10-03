"""
測試設施地圖連結生成
"""
import json

# 模擬 API 資料
station_data = {
  "StationID": "BL01",
  "StationName": {
    "Zh_tw": "頂埔",
    "En": "Dingpu"
  },
  "FacilityMapURLs": [
    {
      "MapName": {
        "Zh_tw": "頂埔站資訊圖",
        "En": "Dingpu Station Information Map"
      },
      "MapURL": "https://web.metro.taipei/img/ALL/INFOPDF/076.pdf",
      "FloorLevel": "參考車站資訊圖"
    }
  ],
  "Elevators": []
}

# 測試生成連結
facility_maps = station_data.get('FacilityMapURLs', [])
print(f"設施地圖數量: {len(facility_maps)}")

if facility_maps and len(facility_maps) > 0:
    map_links = []
    for map_item in facility_maps[:3]:
        map_name = map_item.get('MapName', {}).get('Zh_tw', '車站資訊圖')
        map_url = map_item.get('MapURL', '')
        if map_url:
            link = f"[{map_name}]({map_url})"
            map_links.append(link)
            print(f"\n生成的連結:")
            print(f"  名稱: {map_name}")
            print(f"  URL: {map_url}")
            print(f"  Markdown: {link}")
    
    if map_links:
        joined = "\n".join(map_links)
        print(f"\n最終 value:")
        print(joined)
        print(f"\n包含換行符: {repr(joined)}")
else:
    print("沒有設施地圖")
