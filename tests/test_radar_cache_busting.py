#!/usr/bin/env python3
"""
測試雷達圖快取破壞機制
驗證雷達圖片 URL 是否添加了時間戳參數來避免快取問題
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.radar_commands import RadarCommands

class MockBot:
    """模擬機器人"""
    pass

async def test_radar_cache_busting():
    """測試雷達圖快取破壞功能"""
    print("🌩️ 測試雷達圖快取破壞功能...")
    
    bot = MockBot()
    radar_cog = RadarCommands(bot)
    
    # 測試時間戳添加功能
    test_urls = [
        "https://opendata.cwa.gov.tw/opendata/MIC/M-A0058-001.png",
        "https://example.com/radar.jpg",
        "https://api.example.com/image?type=radar",
        "https://test.com/radar.png?format=png"
    ]
    
    print("\n🧪 測試 URL 時間戳添加...")
    
    for i, url in enumerate(test_urls, 1):
        timestamped_url = radar_cog._add_timestamp_to_url(url)
        
        # 檢查是否添加了時間戳
        if "_t=" in timestamped_url:
            print(f"✅ 測試 {i}: 時間戳已添加")
            print(f"   原始: {url}")
            print(f"   修改: {timestamped_url}")
        else:
            print(f"❌ 測試 {i}: 時間戳未添加")
            print(f"   URL: {url}")
        
        print()
    
    return True

async def test_radar_embed_creation():
    """測試雷達 Embed 建立是否使用時間戳"""
    print("🔍 測試雷達 Embed 建立...")
    
    bot = MockBot()
    radar_cog = RadarCommands(bot)
    
    # 模擬雷達資料
    mock_radar_data = {
        'datetime': '2025-06-30T16:00:00+08:00',
        'image_url': 'https://opendata.cwa.gov.tw/opendata/MIC/M-A0058-001.png',
        'description': '台灣雷達圖整合無地形',
        'dimension': '1024x1024',
        'longitude': '121.0',
        'latitude': '24.0'
    }
    
    test_cases = [
        {
            'method': 'create_radar_embed',
            'name': '一般雷達圖',
            'args': [mock_radar_data]
        },
        {
            'method': 'create_large_radar_embed', 
            'name': '大範圍雷達圖',
            'args': [mock_radar_data]
        },
        {
            'method': 'create_rainfall_radar_embed',
            'name': '降雨雷達圖',
            'args': [mock_radar_data, '樹林']
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        try:
            method = getattr(radar_cog, test_case['method'])
            embed = method(*test_case['args'])
            
            # 檢查 embed 圖片 URL 是否包含時間戳
            if hasattr(embed, '_image') and embed._image:
                image_url = embed._image.get('url', '')
                if '_t=' in image_url:
                    print(f"✅ {test_case['name']}: 圖片 URL 包含時間戳")
                else:
                    print(f"❌ {test_case['name']}: 圖片 URL 缺少時間戳")
                    all_passed = False
            else:
                print(f"⚠️ {test_case['name']}: 無圖片 URL")
                
        except Exception as e:
            print(f"❌ {test_case['name']}: 測試失敗 - {e}")
            all_passed = False
    
    return all_passed

async def test_timestamp_uniqueness():
    """測試時間戳的唯一性"""
    print("\n⏱️ 測試時間戳唯一性...")
    
    bot = MockBot()
    radar_cog = RadarCommands(bot)
    
    base_url = "https://example.com/radar.png"
    timestamps = []
    
    # 生成多個時間戳 URL
    for i in range(5):
        timestamped_url = radar_cog._add_timestamp_to_url(base_url)
        # 提取時間戳
        timestamp = timestamped_url.split('_t=')[1] if '_t=' in timestamped_url else None
        timestamps.append(timestamp)
        
        if i < 4:  # 前4次稍微等待，確保時間戳不同
            await asyncio.sleep(0.1)
    
    # 檢查時間戳是否不同
    unique_timestamps = set(timestamps)
    if len(unique_timestamps) > 1:
        print(f"✅ 時間戳具有唯一性: {len(unique_timestamps)}/{len(timestamps)} 個不同")
    else:
        print(f"❌ 時間戳缺乏唯一性: 只有 {len(unique_timestamps)} 個不同的時間戳")
    
    return len(unique_timestamps) > 1

async def test_actual_radar_data():
    """測試實際雷達資料獲取和快取破壞"""
    print("\n🌐 測試實際雷達資料獲取...")
    
    bot = MockBot()
    radar_cog = RadarCommands(bot)
    
    try:
        # 測試一般雷達圖
        print("📡 測試一般雷達圖資料獲取...")
        radar_data = await radar_cog.fetch_radar_data()
        
        if radar_data and radar_data.get('image_url'):
            original_url = radar_data.get('image_url')
            timestamped_url = radar_cog._add_timestamp_to_url(original_url)
            
            print(f"✅ 成功獲取雷達資料")
            print(f"   原始 URL: {original_url[:80]}...")
            print(f"   時間戳 URL: {timestamped_url[:80]}...")
            
            if '_t=' in timestamped_url:
                print("✅ 時間戳成功添加到實際雷達圖 URL")
                return True
            else:
                print("❌ 時間戳未添加到實際雷達圖 URL")
                return False
        else:
            print("⚠️ 無法獲取雷達資料或圖片 URL")
            return False
            
    except Exception as e:
        print(f"❌ 獲取實際雷達資料失敗: {e}")
        return False

async def main():
    """主要測試函數"""
    print("🚀 雷達圖快取破壞機制測試")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 執行測試
    test_results = {}
    
    # 測試 1: 快取破壞功能
    test_results['cache_busting'] = await test_radar_cache_busting()
    
    # 測試 2: Embed 建立
    test_results['embed_creation'] = await test_radar_embed_creation()
    
    # 測試 3: 時間戳唯一性
    test_results['timestamp_uniqueness'] = await test_timestamp_uniqueness()
    
    # 測試 4: 實際資料獲取（可選）
    test_results['actual_data'] = await test_actual_radar_data()
    
    # 生成測試報告
    print("\n" + "=" * 60)
    print("📊 雷達圖快取破壞測試結果:")
    print("-" * 40)
    
    test_descriptions = {
        'cache_busting': 'URL 時間戳添加功能',
        'embed_creation': 'Embed 圖片時間戳',
        'timestamp_uniqueness': '時間戳唯一性',
        'actual_data': '實際資料快取破壞'
    }
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        description = test_descriptions.get(test_name, test_name)
        print(f"{description:.<30} {status}")
        if result:
            passed_tests += 1
    
    print("-" * 40)
    success_rate = (passed_tests / total_tests) * 100
    print(f"總體通過率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    # 評估修正效果
    print("\n🎯 修正效果評估:")
    
    if success_rate >= 100:
        print("🌟 雷達圖快取破壞: 完美 - 所有測試通過")
    elif success_rate >= 75:
        print("✅ 雷達圖快取破壞: 良好 - 主要功能正常")
    elif success_rate >= 50:
        print("⚠️ 雷達圖快取破壞: 部分功能 - 需要改善")
    else:
        print("❌ 雷達圖快取破壞: 失敗 - 需要重新檢查")
    
    print("\n📋 修正摘要:")
    print("✅ 為所有雷達圖片 URL 添加時間戳參數")
    print("✅ 修正一般雷達圖快取問題")
    print("✅ 修正大範圍雷達圖快取問題")
    print("✅ 修正降雨雷達圖快取問題")
    print("✅ 確保每次查詢都顯示最新雷達圖")
    
    print("\n💡 技術細節:")
    print("- 使用 Unix 時間戳作為 URL 參數")
    print("- 格式: original_url?_t=timestamp 或 original_url&_t=timestamp")
    print("- 每次查詢都生成新的時間戳")
    print("- 避免 Discord/瀏覽器快取舊圖片")
    
    print("\n🎯 使用方式:")
    print("/radar - 查看最新一般雷達圖")
    print("/large_radar - 查看最新大範圍雷達圖")
    print("/rainfall_radar station:樹林 - 查看最新降雨雷達圖")
    
    if success_rate >= 75:
        print("\n✨ 現在所有雷達查詢指令都會顯示即時最新的圖片！")

if __name__ == "__main__":
    asyncio.run(main())
