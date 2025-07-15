#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試更新後的水利防災監控影像功能
驗證新 JSON API 的整合
"""

import asyncio
import aiohttp
import json
import ssl
import datetime

async def test_new_water_cameras_implementation():
    """測試新的水利防災監控影像實作"""
    
    print("🧪 測試新的水利防災監控影像實作")
    print("=" * 60)
    
    # 模擬 _get_water_cameras 方法的邏輯
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print(f"📡 請求 API: {api_url}")
            
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"📊 HTTP 狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return False
                
                content = await response.text()
                print(f"📄 回應長度: {len(content)} 字元")
                
                # 檢查回應是否為空
                if not content or len(content.strip()) == 0:
                    print("❌ API 回應為空")
                    return False
                
                # 處理可能的 BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                    print("✅ 移除 UTF-8 BOM")
                
                # 解析 JSON
                try:
                    data = json.loads(content)
                    print("✅ JSON 解析成功")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return False
                
                if not isinstance(data, list) or len(data) == 0:
                    print("❌ 資料格式錯誤或為空")
                    return False
                
                print(f"📋 總監視器數量: {len(data)}")
                
                # 處理資料
                cameras = []
                valid_count = 0
                
                for item in data:
                    try:
                        camera_info = {
                            'id': item.get('CameraID', ''),
                            'name': item.get('VideoSurveillanceStationName', item.get('CameraName', '未知監視器')),
                            'county': item.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知'),
                            'district': item.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', ''),
                            'image_url': item.get('VideoSurveillanceImageUrl', item.get('ImageUrl', item.get('Url', ''))),
                            'lat': item.get('TWD97Lat', item.get('Latitude', '')),
                            'lon': item.get('TWD97Lon', item.get('Longitude', ''))
                        }
                        
                        # 確保有基本資訊（即使沒有影像 URL 也顯示）
                        if camera_info['name'] and camera_info['name'] != '未知監視器':
                            cameras.append(camera_info)
                            valid_count += 1
                            
                    except Exception as e:
                        print(f"⚠️ 處理監視器資料時發生錯誤: {e}")
                        continue
                
                print(f"✅ 有效監視器數量: {valid_count}")
                
                if valid_count == 0:
                    print("❌ 無有效監視器資料")
                    return False
                
                # 顯示前 5 筆資料
                print("\n📊 前 5 筆監視器資料:")
                for i, camera in enumerate(cameras[:5], 1):
                    print(f"  {i}. [{camera['id']}] {camera['name']}")
                    print(f"     📍 {camera['county']} {camera['district']}")
                    print(f"     🔗 {camera['image_url'][:60]}...")
                    print()
                
                # 分析縣市分布
                counties = {}
                for camera in cameras:
                    county = camera['county']
                    counties[county] = counties.get(county, 0) + 1
                
                print(f"🏛️ 縣市分布 (共 {len(counties)} 個縣市):")
                for county, count in sorted(counties.items(), key=lambda x: x[1], reverse=True)[:10]:
                    print(f"  {county}: {count} 個監視器")
                
                # 測試縣市篩選功能
                print("\n🔍 測試縣市篩選功能:")
                test_counties = ['台北', '新北', '桃園', '台中', '台南', '高雄']
                
                for test_county in test_counties:
                    # 模擬篩選邏輯
                    normalized_county = test_county.replace('台', '臺')
                    if not normalized_county.endswith(('市', '縣')):
                        test_county_names = [f"{normalized_county}市", f"{normalized_county}縣"]
                    else:
                        test_county_names = [normalized_county]
                    
                    filtered_cameras = []
                    for cam in cameras:
                        cam_county = cam['county'].replace('台', '臺')
                        if any(test_name in cam_county or cam_county in test_name for test_name in test_county_names):
                            filtered_cameras.append(cam)
                    
                    print(f"  {test_county}: {len(filtered_cameras)} 個監視器")
                
                print("\n✅ 新 API 實作測試完成！")
                return True
                
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

async def main():
    """主測試函數"""
    success = await test_new_water_cameras_implementation()
    
    if success:
        print("\n🎉 所有測試通過！新的水利防災監控影像 API 已成功整合。")
    else:
        print("\n❌ 測試失敗，需要進一步檢查。")

if __name__ == "__main__":
    asyncio.run(main())
