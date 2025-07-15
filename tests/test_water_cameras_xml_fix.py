#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修改後的水利防災監控影像功能
"""

import asyncio
import aiohttp
import ssl
import xml.etree.ElementTree as ET

async def test_water_cameras_xml():
    """測試 XML API 的水利監視器功能"""
    
    # 使用正確的 XML API
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=xml&id=362C7288-F378-4BF2-966C-2CD961732C52"
    
    try:
        print("🔍 測試水利防災監控影像 XML API...")
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                content = await response.text()
                
                # 檢查回應是否為空
                if not content or len(content.strip()) == 0:
                    print("❌ API 回應為空")
                    return
                
                # 處理可能的 BOM
                if content.startswith('\ufeff'):
                    content = content[1:]
                
                print(f"✅ API 請求成功，回應長度: {len(content)} 字元")
                
                # 解析 XML
                try:
                    root = ET.fromstring(content)
                    print(f"✅ XML 解析成功，根元素: {root.tag}")
                    
                    # 查找所有的 Table 元素
                    items = root.findall('.//diffgr:diffgram//NewDataSet//Table', 
                                       {'diffgr': 'urn:schemas-microsoft-com:xml-diffgram-v1'})
                    if not items:
                        # 嘗試其他可能的路徑
                        items = root.findall('.//Table')
                    
                    print(f"📋 找到 {len(items)} 個監視器")
                    
                    if items:
                        # 定義輔助函數
                        def get_xml_text(element, tag_name, default=''):
                            elem = element.find(tag_name)
                            return elem.text if elem is not None and elem.text else default
                        
                        # 尋找宜蘭縣的監視器
                        yilan_cameras = []
                        for item in items:
                            county = get_xml_text(item, 'CountiesAndCitiesWhereTheMonitoringPointsAreLocated')
                            if '宜蘭' in county:
                                camera_info = {
                                    'id': get_xml_text(item, 'CameraID'),
                                    'name': get_xml_text(item, 'VideoSurveillanceStationName') or get_xml_text(item, 'CameraName', '未知監視器'),
                                    'county': county,
                                    'district': get_xml_text(item, 'AdministrativeDistrictWhereTheMonitoringPointIsLocated'),
                                    'image_url': get_xml_text(item, 'ImageURL'),
                                    'lat': get_xml_text(item, 'latitude_4326'),
                                    'lon': get_xml_text(item, 'Longitude_4326'),
                                    'status': get_xml_text(item, 'Status'),
                                    'basin': get_xml_text(item, 'BasinName'),
                                    'tributary': get_xml_text(item, 'TRIBUTARY'),
                                }
                                yilan_cameras.append(camera_info)
                        
                        print(f"\n🎯 找到 {len(yilan_cameras)} 個宜蘭縣監視器:")
                        
                        for i, camera in enumerate(yilan_cameras[:10], 1):  # 顯示前10個
                            print(f"\n--- 監視器 {i} ---")
                            print(f"ID: {camera['id']}")
                            print(f"名稱: {camera['name']}")
                            print(f"縣市: {camera['county']}")
                            print(f"行政區: {camera['district']}")
                            print(f"影像 URL: {camera['image_url']}")
                            print(f"狀態: {camera['status']}")
                            print(f"緯度: {camera['lat']}")
                            print(f"經度: {camera['lon']}")
                            print(f"流域: {camera['basin']}")
                            print(f"支流: {camera['tributary']}")
                            
                            if camera['image_url']:
                                print("✅ 影像 URL 可用!")
                            else:
                                print("❌ 影像 URL 不可用")
                        
                        # 統計有多少監視器有可用的影像 URL
                        with_url = sum(1 for cam in yilan_cameras if cam['image_url'])
                        without_url = len(yilan_cameras) - with_url
                        
                        print(f"\n📊 統計:")
                        print(f"  有影像 URL: {with_url} 個")
                        print(f"  無影像 URL: {without_url} 個")
                        print(f"  總計: {len(yilan_cameras)} 個")
                        
                        if with_url > 0:
                            print("\n🎉 修改成功！宜蘭縣監視器現在有可用的影像 URL了！")
                        else:
                            print("\n⚠️ 宜蘭縣監視器仍然沒有影像 URL，可能需要進一步調查 API 結構")
                    
                    else:
                        print("❌ 未找到任何監視器資料")
                
                except ET.ParseError as e:
                    print(f"❌ XML 解析失敗: {e}")
    
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_water_cameras_xml())
