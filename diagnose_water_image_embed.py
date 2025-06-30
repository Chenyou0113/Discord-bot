#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷水利監視器圖片嵌入問題
檢查圖片 URL 的有效性和處理邏輯
"""

import asyncio
import aiohttp
import sys
from pathlib import Path

async def test_water_image_urls():
    """測試水利防災影像 URL"""
    
    print("🔍 診斷水利監視器圖片嵌入問題")
    print("=" * 60)
    
    try:
        # 導入必要模組
        from cogs.reservoir_commands import ReservoirCommands
        
        # 創建實例
        mock_bot = None
        reservoir_cog = ReservoirCommands(mock_bot)
        
        print("1️⃣ 獲取實際的水利防災影像資料...")
        try:
            image_data = await reservoir_cog.get_water_disaster_images()
            if image_data:
                print(f"✅ 成功獲取 {len(image_data)} 筆資料")
                
                # 檢查前5筆有影像URL的資料
                valid_images = []
                for i, data in enumerate(image_data[:50]):  # 檢查前50筆
                    image_url = data.get('ImageURL', '')
                    if image_url and image_url.strip():
                        valid_images.append(data)
                        if len(valid_images) >= 5:
                            break
                
                print(f"✅ 找到 {len(valid_images)} 筆有影像URL的資料")
                
                print("\n2️⃣ 檢查圖片URL處理...")
                for i, data in enumerate(valid_images):
                    station_name = data.get('VideoSurveillanceStationName', f'監控站{i+1}')
                    original_url = data.get('ImageURL', '')
                    
                    print(f"\n📸 監控站: {station_name}")
                    print(f"   原始URL: {original_url}")
                    
                    # 使用處理方法
                    processed_url = reservoir_cog._process_and_validate_image_url(original_url)
                    print(f"   處理後URL: {processed_url}")
                    
                    # 測試URL是否可以訪問
                    if processed_url and processed_url != 'N/A':
                        await test_url_accessibility(processed_url)
                
            else:
                print("❌ 無法獲取水利防災影像資料")
                return False
                
        except Exception as e:
            print(f"❌ 獲取資料失敗: {e}")
            return False
        
        print("\n3️⃣ 測試 WaterCameraView 圖片嵌入...")
        try:
            from cogs.reservoir_commands import WaterCameraView
            
            if valid_images:
                view = WaterCameraView(valid_images, 0, "測試")
                embed = await view._create_water_camera_embed(valid_images[0])
                
                print("✅ Embed 創建成功")
                print(f"   標題: {embed.title}")
                print(f"   描述: {embed.description}")
                
                if embed.image and embed.image.url:
                    print(f"   嵌入圖片URL: {embed.image.url}")
                    await test_url_accessibility(embed.image.url)
                else:
                    print("❌ 沒有嵌入圖片")
                    
                    # 檢查原始資料
                    info = view._format_water_image_info(valid_images[0])
                    print(f"   格式化後影像URL: {info['image_url']}")
                    
                    if info['image_url']:
                        processed = view._process_and_validate_image_url(info['image_url'])
                        print(f"   處理後URL: {processed}")
                        
                        if processed and processed != 'N/A':
                            print("🚨 URL 處理正常但沒有設定到 Embed 中")
                        else:
                            print("🚨 URL 處理失敗")
            else:
                print("❌ 沒有有效的圖片資料")
                
        except Exception as e:
            print(f"❌ WaterCameraView 測試失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ 診斷失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_url_accessibility(url):
    """測試 URL 是否可以訪問"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.head(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    print(f"   ✅ URL 可以訪問 (狀態: {response.status})")
                    content_type = response.headers.get('content-type', '')
                    if 'image' in content_type:
                        print(f"      圖片類型: {content_type}")
                    else:
                        print(f"      ⚠️ 非圖片類型: {content_type}")
                else:
                    print(f"   ❌ URL 無法訪問 (狀態: {response.status})")
    except asyncio.TimeoutError:
        print(f"   ⏰ URL 訪問超時")
    except Exception as e:
        print(f"   ❌ URL 訪問錯誤: {e}")

def test_url_processing():
    """測試 URL 處理邏輯"""
    
    print("\n4️⃣ 測試 URL 處理邏輯...")
    
    # 導入 WaterCameraView 進行測試
    from cogs.reservoir_commands import WaterCameraView
    
    # 創建測試實例
    view = WaterCameraView([], 0, "")
    
    # 測試各種 URL 格式
    test_urls = [
        "https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg",
        "https://fhy.wra.gov.tw/images/camera/123.jpg",
        "/images/camera/test.jpg",
        "//alerts.ncdr.nat.gov.tw/image.jpg",
        "images/test.jpg",
        "",
        None,
        "not_a_url",
        "ftp://example.com/image.jpg"
    ]
    
    print("   測試 URL 處理:")
    for i, url in enumerate(test_urls):
        try:
            processed = view._process_and_validate_image_url(url)
            print(f"   {i+1}. '{url}' -> '{processed}'")
        except Exception as e:
            print(f"   {i+1}. '{url}' -> ERROR: {e}")

async def main():
    """主函數"""
    
    print("🚀 水利監視器圖片嵌入診斷")
    print("=" * 80)
    
    # 測試 URL 處理邏輯
    test_url_processing()
    
    # 測試實際的圖片 URL
    url_test = await test_water_image_urls()
    
    # 結果報告
    print("\n" + "=" * 80)
    print("📊 診斷結果:")
    print(f"URL 測試: {'✅ 通過' if url_test else '❌ 失敗'}")
    
    if url_test:
        print("\n💡 建議:")
        print("1. 檢查實際的 Discord 訊息是否正確顯示圖片")
        print("2. 確認圖片 URL 是否被防火牆或網路限制")
        print("3. 測試不同的監控點是否有相同問題")
        print("4. 檢查 Discord 是否支援該圖片格式")
    else:
        print("\n❌ 發現問題，需要進一步調查")
        print("1. 檢查 API 回應格式是否有變化")
        print("2. 確認圖片 URL 處理邏輯是否正確")
        print("3. 測試網路連線是否正常")
    
    return url_test

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 診斷程序錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
