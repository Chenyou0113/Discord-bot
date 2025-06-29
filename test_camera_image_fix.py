#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利監視器圖片顯示修復
驗證圖片 URL 處理和 Discord embed 顯示
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

class MockReservoirCommands:
    """模擬 ReservoirCommands 類別進行測試"""
    
    def format_water_image_info(self, image_data):
        """格式化水利防災影像資訊 - 修復版本"""
        try:
            station_name = image_data.get('VideoSurveillanceStationName', 'N/A')
            camera_name = image_data.get('CameraName', 'N/A') 
            location = image_data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
            district = image_data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
            basin_name = image_data.get('BasinName', '')
            tributary = image_data.get('TRIBUTARY', '')
            image_url = image_data.get('ImageURL', '')
            status = image_data.get('Status', '')
            latitude = image_data.get('latitude_4326', '')
            longitude = image_data.get('Longitude_4326', '')
            
            # 組合完整地址
            full_location = f"{location}{district}" if location and district else (location or district or "N/A")
            
            # 組合河川資訊
            river_info = f"{basin_name}" if basin_name else "N/A"
            if tributary and tributary != basin_name:
                river_info += f" ({tributary})"
            
            # 處理影像 URL - 修復版本
            processed_image_url = "N/A"
            if image_url and image_url.strip():
                processed_image_url = image_url.strip()
                # 確保 URL 格式正確
                if not processed_image_url.startswith(('http://', 'https://')):
                    if processed_image_url.startswith('//'):
                        processed_image_url = 'https:' + processed_image_url
                    elif processed_image_url.startswith('/'):
                        processed_image_url = 'https://opendata.wra.gov.tw' + processed_image_url
                    else:
                        # 如果是相對路徑，加上基礎 URL
                        processed_image_url = 'https://opendata.wra.gov.tw/' + processed_image_url
            
            return {
                'station_name': station_name,
                'camera_name': camera_name,
                'location': full_location,
                'river': river_info,
                'image_url': processed_image_url,
                'status': "正常" if status == "1" else "異常" if status == "0" else "未知",
                'coordinates': f"{latitude}, {longitude}" if latitude and longitude else "N/A"
            }
            
        except Exception as e:
            print(f"格式化水利防災影像資訊時發生錯誤: {str(e)}")
            return None

async def test_camera_image_fix():
    """測試水利監視器圖片顯示修復"""
    print("=" * 60)
    print("測試水利監視器圖片顯示修復")
    print("=" * 60)
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        mock_cog = MockReservoirCommands()
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # 獲取水利防災影像資料
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
            
            print("📡 正在獲取水利防災影像資料...")
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status != 200:
                    print(f"❌ API 請求失敗: {response.status}")
                    return
                
                # 處理 UTF-8 BOM 問題
                text = await response.text()
                if text.startswith('\ufeff'):
                    text = text[1:]
                
                data = json.loads(text)
                print(f"✅ 成功獲取資料，共 {len(data)} 個監控點")
                
                # 尋找台南地區的監控點進行測試
                print("\n🔍 尋找台南地區監控點...")
                tainan_cameras = []
                for camera in data:
                    location = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                    if '台南' in location:
                        tainan_cameras.append(camera)
                
                print(f"找到 {len(tainan_cameras)} 個台南地區監控點")
                
                if not tainan_cameras:
                    print("❌ 未找到台南地區監控點，改用前3個監控點進行測試")
                    tainan_cameras = data[:3]
                
                # 測試前3個監控點的圖片處理
                print("\n" + "=" * 50)
                print("測試監控點圖片處理:")
                print("=" * 50)
                
                for i, camera in enumerate(tainan_cameras[:3], 1):
                    print(f"\n🏷️ 監控點 {i}:")
                    print("-" * 30)
                    
                    # 原始資料
                    station_name = camera.get('VideoSurveillanceStationName', 'N/A')
                    original_url = camera.get('ImageURL', '')
                    status = camera.get('Status', '')
                    
                    print(f"監控站名稱: {station_name}")
                    print(f"狀態代碼: {status}")
                    print(f"原始 URL: {original_url}")
                    
                    # 使用修復後的格式化函數
                    info = mock_cog.format_water_image_info(camera)
                    
                    if info:
                        print(f"處理後 URL: {info['image_url']}")
                        print(f"狀態顯示: {info['status']}")
                        print(f"位置資訊: {info['location']}")
                        print(f"河川資訊: {info['river']}")
                        
                        # 測試 URL 有效性
                        if info['image_url'] != 'N/A':
                            print(f"🔍 測試 URL 有效性...")
                            try:
                                async with session.head(info['image_url'], timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                                    if img_response.status == 200:
                                        content_type = img_response.headers.get('Content-Type', '')
                                        print(f"✅ URL 有效 (Content-Type: {content_type})")
                                        
                                        # 測試是否為有效圖片
                                        if 'image' in content_type.lower():
                                            print(f"✅ 確認為圖片格式")
                                        else:
                                            print(f"⚠️ 非標準圖片格式")
                                    else:
                                        print(f"❌ URL 無效 (狀態碼: {img_response.status})")
                            except Exception as url_error:
                                print(f"❌ URL 測試失敗: {str(url_error)}")
                        else:
                            print(f"⚠️ 無影像 URL")
                        
                        # 模擬 Discord embed 設定
                        print(f"📱 Discord Embed 資訊:")
                        print(f"   Title: 📸 {info['station_name']}")
                        print(f"   Description: 📍 {info['location']} | 🌊 {info['river']} | 📡 {info['status']}")
                        if info['image_url'] != 'N/A':
                            print(f"   Image URL: {info['image_url']}")
                            print(f"   ✅ 將顯示圖片")
                        else:
                            print(f"   ⚠️ 將顯示無圖片訊息")
                    else:
                        print(f"❌ 格式化失敗")
                
                # 統計有圖片 URL 的監控點
                print(f"\n" + "=" * 50)
                print("整體圖片可用性統計:")
                print("=" * 50)
                
                total_with_urls = 0
                valid_urls_count = 0
                
                for camera in data[:20]:  # 檢查前20個監控點
                    info = mock_cog.format_water_image_info(camera)
                    if info and info['image_url'] != 'N/A':
                        total_with_urls += 1
                        
                        # 測試 URL 是否可訪問
                        try:
                            async with session.head(info['image_url'], timeout=aiohttp.ClientTimeout(total=5)) as img_response:
                                if img_response.status == 200:
                                    valid_urls_count += 1
                        except:
                            pass
                
                print(f"前20個監控點中:")
                print(f"有影像 URL: {total_with_urls}/20 ({total_with_urls/20*100:.1f}%)")
                print(f"URL 可訪問: {valid_urls_count}/{total_with_urls} ({valid_urls_count/max(1,total_with_urls)*100:.1f}%)")
                
                if valid_urls_count > 0:
                    print(f"✅ 修復成功！找到 {valid_urls_count} 個可用的監控點圖片")
                else:
                    print(f"⚠️ 雖然處理了 URL 格式，但可能需要進一步檢查 API 資料品質")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("測試完成")
    print("=" * 60)

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(test_camera_image_fix())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
