#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷水利監視器圖片顯示問題
檢查 API 資料結構和圖片 URL 有效性
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def diagnose_camera_images():
    """診斷水利監視器圖片問題"""
    print("=" * 60)
    print("診斷水利監視器圖片顯示問題")
    print("=" * 60)
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # 水利防災影像 API
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
            print("📡 正在獲取水利防災影像資料...")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"回應狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗: {response.status}")
                    return
                
                # 處理 UTF-8 BOM 問題
                text = await response.text()
                if text.startswith('\ufeff'):
                    text = text[1:]
                
                try:
                    data = json.loads(text)
                    print(f"✅ 成功獲取資料，共 {len(data)} 個監控點")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {e}")
                    return
                
                if not data:
                    print("❌ 無監控點資料")
                    return
                
                # 分析前5個監控點的詳細資料
                print("\n" + "=" * 50)
                print("前 5 個監控點詳細分析:")
                print("=" * 50)
                
                for i, camera in enumerate(data[:5], 1):
                    print(f"\n🏷️ 監控點 {i}:")
                    print("-" * 30)
                    
                    # 基本資訊
                    station_name = camera.get('VideoSurveillanceStationName', 'N/A')
                    camera_name = camera.get('CameraName', 'N/A')
                    location = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 'N/A')
                    district = camera.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', 'N/A')
                    image_url = camera.get('ImageURL', '')
                    status = camera.get('Status', '')
                    
                    print(f"監控站名稱: {station_name}")
                    print(f"攝影機名稱: {camera_name}")
                    print(f"縣市: {location}")
                    print(f"行政區: {district}")
                    print(f"狀態代碼: {status}")
                    print(f"影像 URL: {image_url}")
                    
                    # 檢查影像 URL 有效性
                    if image_url:
                        print(f"🔍 檢查影像 URL 有效性...")
                        try:
                            async with session.head(image_url, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                                if img_response.status == 200:
                                    content_type = img_response.headers.get('Content-Type', '')
                                    content_length = img_response.headers.get('Content-Length', 'Unknown')
                                    print(f"✅ 影像 URL 有效")
                                    print(f"   Content-Type: {content_type}")
                                    print(f"   Content-Length: {content_length}")
                                else:
                                    print(f"❌ 影像 URL 無效 (狀態碼: {img_response.status})")
                        except Exception as url_error:
                            print(f"❌ 影像 URL 檢查失敗: {str(url_error)}")
                    else:
                        print("❌ 無影像 URL")
                
                # 統計分析
                print("\n" + "=" * 50)
                print("整體統計分析:")
                print("=" * 50)
                
                total_cameras = len(data)
                cameras_with_urls = 0
                cameras_with_valid_urls = 0
                status_stats = {}
                location_stats = {}
                
                print(f"📊 正在分析 {total_cameras} 個監控點...")
                
                for i, camera in enumerate(data):
                    if i % 100 == 0:
                        print(f"   進度: {i}/{total_cameras}")
                    
                    # URL 統計
                    image_url = camera.get('ImageURL', '')
                    if image_url:
                        cameras_with_urls += 1
                        
                        # 快速檢查前50個URL的有效性
                        if i < 50:
                            try:
                                async with session.head(image_url, timeout=aiohttp.ClientTimeout(total=5)) as img_response:
                                    if img_response.status == 200:
                                        cameras_with_valid_urls += 1
                            except:
                                pass
                    
                    # 狀態統計
                    status = camera.get('Status', 'unknown')
                    status_stats[status] = status_stats.get(status, 0) + 1
                    
                    # 地區統計
                    location = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 'unknown')
                    location_stats[location] = location_stats.get(location, 0) + 1
                
                print(f"\n📊 統計結果:")
                print(f"總監控點數: {total_cameras}")
                print(f"有影像 URL 的監控點: {cameras_with_urls} ({cameras_with_urls/total_cameras*100:.1f}%)")
                print(f"有效影像 URL (前50個樣本): {cameras_with_valid_urls}/50 ({cameras_with_valid_urls/50*100:.1f}%)")
                
                print(f"\n📈 狀態分布:")
                for status, count in sorted(status_stats.items()):
                    status_name = "正常" if status == "1" else "異常" if status == "0" else f"未知({status})"
                    print(f"  {status_name}: {count} 個 ({count/total_cameras*100:.1f}%)")
                
                print(f"\n📍 地區分布 (前 10 名):")
                sorted_locations = sorted(location_stats.items(), key=lambda x: x[1], reverse=True)
                for location, count in sorted_locations[:10]:
                    print(f"  {location}: {count} 個")
                
                # 尋找台南地區的監控點作為測試樣本
                print(f"\n" + "=" * 50)
                print("台南地區監控點測試:")
                print("=" * 50)
                
                tainan_cameras = []
                for camera in data:
                    location = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                    if '台南' in location:
                        tainan_cameras.append(camera)
                
                print(f"找到 {len(tainan_cameras)} 個台南地區監控點")
                
                if tainan_cameras:
                    for i, camera in enumerate(tainan_cameras[:3], 1):
                        station_name = camera.get('VideoSurveillanceStationName', 'N/A')
                        image_url = camera.get('ImageURL', '')
                        status = camera.get('Status', '')
                        
                        print(f"\n🏷️ 台南監控點 {i}: {station_name}")
                        print(f"   狀態: {'正常' if status == '1' else '異常' if status == '0' else '未知'}")
                        print(f"   影像 URL: {image_url[:80]}{'...' if len(image_url) > 80 else ''}")
                        
                        if image_url:
                            try:
                                async with session.head(image_url, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                                    if img_response.status == 200:
                                        print(f"   ✅ 影像可用")
                                    else:
                                        print(f"   ❌ 影像不可用 ({img_response.status})")
                            except Exception as e:
                                print(f"   ❌ 影像檢查失敗: {str(e)}")
                        else:
                            print(f"   ❌ 無影像 URL")
                
    except Exception as e:
        print(f"❌ 診斷過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("診斷完成")
    print("=" * 60)

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(diagnose_camera_images())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
