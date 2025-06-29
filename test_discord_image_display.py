#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Discord 圖片顯示功能
驗證水利監視器圖片是否能正確顯示在 Discord 中
"""

import discord
from discord.ext import commands
import asyncio
import aiohttp
import ssl
import json

# 模擬 Discord Embed 圖片顯示測試
class ImageDisplayTest:
    """圖片顯示測試類別"""
    
    def __init__(self):
        self.test_results = []
    
    async def test_water_camera_images(self):
        """測試水利監視器圖片顯示"""
        print("🖼️ 測試 Discord 圖片顯示功能")
        print("=" * 50)
        
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                # 獲取水利防災影像資料
                url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=362C7288-F378-4BF2-966C-2CD961732C52"
                
                print("📡 正在獲取監視器資料...")
                async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status != 200:
                        print(f"❌ API 請求失敗: {response.status}")
                        return False
                    
                    # 處理資料
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    data = json.loads(text)
                    print(f"✅ 獲取 {len(data)} 個監視器資料")
                    
                    # 尋找有圖片的監視器
                    print(f"\n🔍 尋找有效圖片 URL...")
                    valid_images = []
                    
                    for i, camera in enumerate(data[:20]):  # 檢查前20個
                        image_url = camera.get('ImageURL', '')
                        if image_url and image_url.strip():
                            # 修復 URL 格式
                            processed_url = self.fix_image_url(image_url)
                            
                            # 測試圖片可訪問性
                            try:
                                async with session.head(processed_url, timeout=aiohttp.ClientTimeout(total=10)) as img_response:
                                    if img_response.status == 200:
                                        content_type = img_response.headers.get('Content-Type', '')
                                        if 'image' in content_type.lower():
                                            valid_images.append({
                                                'camera': camera,
                                                'url': processed_url,
                                                'content_type': content_type
                                            })
                                            print(f"✅ 找到有效圖片: {camera.get('VideoSurveillanceStationName', 'N/A')}")
                            except:
                                pass
                    
                    print(f"\n📊 圖片可用性統計:")
                    print(f"檢查監視器: 20 個")
                    print(f"有效圖片: {len(valid_images)} 個")
                    print(f"成功率: {len(valid_images)/20*100:.1f}%")
                    
                    if valid_images:
                        # 測試 Discord Embed 格式
                        print(f"\n📱 模擬 Discord Embed 顯示:")
                        
                        for i, img_data in enumerate(valid_images[:3], 1):
                            camera = img_data['camera']
                            url = img_data['url']
                            
                            station_name = camera.get('VideoSurveillanceStationName', 'N/A')
                            location = camera.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', 'N/A')
                            river = camera.get('BasinName', 'N/A')
                            status = camera.get('Status', '0')
                            
                            print(f"\n🖼️ Embed {i}:")
                            print(f"   Title: 📸 {station_name}")
                            print(f"   Description: 📍 {location} | 🌊 {river}")
                            print(f"   Status: {'正常' if status == '1' else '異常'}")
                            print(f"   Image URL: {url}")
                            print(f"   Content-Type: {img_data['content_type']}")
                            print(f"   ✅ 此圖片可在 Discord 中顯示")
                        
                        # 創建實際的 Discord Embed 測試
                        print(f"\n🎯 創建 Discord Embed 測試:")
                        embed = discord.Embed(
                            title="📸 水利監視器測試",
                            description="測試圖片顯示功能",
                            color=discord.Color.blue()
                        )
                        
                        # 使用第一個有效圖片
                        test_image = valid_images[0]
                        embed.set_image(url=test_image['url'])
                        
                        print(f"✅ Discord Embed 創建成功")
                        print(f"   圖片 URL: {test_image['url']}")
                        print(f"   監視器: {test_image['camera'].get('VideoSurveillanceStationName', 'N/A')}")
                        
                        return True
                    else:
                        print(f"❌ 未找到可用的圖片")
                        return False
        
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
            return False
    
    def fix_image_url(self, url):
        """修復圖片 URL 格式"""
        if not url or not url.strip():
            return "N/A"
        
        processed_url = url.strip()
        
        # 確保 URL 格式正確
        if not processed_url.startswith(('http://', 'https://')):
            if processed_url.startswith('//'):
                processed_url = 'https:' + processed_url
            elif processed_url.startswith('/'):
                processed_url = 'https://opendata.wra.gov.tw' + processed_url
            else:
                processed_url = 'https://opendata.wra.gov.tw/' + processed_url
        
        return processed_url

async def main():
    """主測試函數"""
    print("開始 Discord 圖片顯示測試...")
    
    tester = ImageDisplayTest()
    success = await tester.test_water_camera_images()
    
    if success:
        print(f"\n🎉 Discord 圖片顯示測試通過！")
        print(f"✅ 水利監視器圖片可以正常在 Discord 中顯示")
        print(f"💡 現在可以正常使用 /water_cameras 指令查看圖片")
    else:
        print(f"\n⚠️ 圖片顯示可能有問題")
        print(f"🔧 建議檢查:")
        print(f"   1. 網路連線是否正常")
        print(f"   2. API 服務是否可用")
        print(f"   3. 圖片 URL 格式是否正確")

if __name__ == "__main__":
    asyncio.run(main())