import asyncio
import json
import sys

# 添加專案路徑
sys.path.insert(0, '.')

async def test():
    import aiohttp
    import ssl
    import certifi
    from cogs.info_commands_fixed_v4_clean import InfoCommands
    
    # 創建假的 bot 物件
    class FakeBot:
        pass
    
    cog = InfoCommands(FakeBot())
    
    # 初始化 session
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    cog.session = aiohttp.ClientSession(connector=connector)
    
    print("正在獲取臺北捷運車站設施資料...")
    facility_data = await cog.fetch_metro_facility('TRTC')
    
    await cog.session.close()
    
    if facility_data:
        print(f"\n共獲取 {len(facility_data)} 個車站")
        print("\n第一個車站的完整資料:")
        print(json.dumps(facility_data[0], indent=2, ensure_ascii=False))
        
        # 檢查是否有圖片相關欄位
        print("\n\n=== 檢查圖片欄位 ===")
        station = facility_data[0]
        print(f"車站名稱: {station.get('StationName', {}).get('Zh_tw', 'N/A')}")
        print(f"車站代碼: {station.get('StationID', 'N/A')}")
        
        # 檢查各種可能的圖片欄位
        image_fields = ['StationImage', 'Picture', 'PictureUrl', 'PictureUrl1', 
                       'Image', 'ImageUrl', 'Photo', 'PhotoUrl']
        
        for field in image_fields:
            if field in station:
                print(f"✅ 找到欄位 '{field}': {station[field]}")
        
        # 顯示所有欄位
        print("\n\n=== 所有欄位列表 ===")
        for key in station.keys():
            print(f"- {key}")
    else:
        print("❌ 無法獲取資料")

if __name__ == "__main__":
    asyncio.run(test())
