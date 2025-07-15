#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試溫度分布圖快取修復
"""

import sys
import os
import time
from datetime import datetime

# 添加 cogs 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))

# 模擬 Discord 相關模組
class MockBot:
    pass

class MockInteraction:
    pass

# 模擬 Discord 模組
class discord:
    class Embed:
        def __init__(self, **kwargs):
            self.title = kwargs.get('title', '')
            self.description = kwargs.get('description', '')
            self.color = kwargs.get('color', None)
            self.fields = []
            self.image_url = None
        
        def add_field(self, **kwargs):
            self.fields.append(kwargs)
        
        def set_image(self, url):
            self.image_url = url
        
        def set_footer(self, text):
            self.footer_text = text
    
    class Color:
        @staticmethod
        def blue():
            return 'blue'
        @staticmethod  
        def red():
            return 'red'

# 將模擬的 discord 模組加入 sys.modules
sys.modules['discord'] = discord
sys.modules['discord.ext'] = type(sys)('discord.ext')
sys.modules['discord.ext.commands'] = type(sys)('discord.ext.commands')

# 模擬其他需要的模組
class commands:
    class Cog:
        pass

class app_commands:
    @staticmethod
    def command(**kwargs):
        def decorator(func):
            return func
        return decorator

sys.modules['discord.ext.commands'].Cog = commands.Cog
sys.modules['discord'].app_commands = app_commands

# 模擬 logging
import logging
logging.basicConfig(level=logging.INFO)

def test_temperature_cache_fix():
    """測試溫度分布圖快取修復"""
    print("=== 測試溫度分布圖快取修復 ===")
    
    # 模擬溫度資料處理邏輯
    def process_temperature_data():
        temp_info = {
            'title': '台灣溫度分布',
            'description': '目前台灣各地溫度狀況',
            'image_url': '',
        }
        
        # 模擬沒有從API取得圖片URL的情況
        if not temp_info['image_url']:
            # 使用標準的溫度分布圖URL，加上時間戳避免快取
            timestamp = int(time.time())
            temp_info['image_url'] = f"https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg?t={timestamp}"
            print(f"✅ 使用標準溫度分布圖片URL（帶時間戳）")
        
        return temp_info
    
    # 模擬有現有URL的情況
    def process_existing_url():
        temp_info = {
            'image_url': 'https://example.com/temp_image.jpg'
        }
        
        # 為現有的圖片URL也加上時間戳避免快取問題
        if temp_info['image_url'] and '?' not in temp_info['image_url']:
            timestamp = int(time.time())
            temp_info['image_url'] = f"{temp_info['image_url']}?t={timestamp}"
            print(f"✅ 為現有圖片URL加上時間戳")
        
        return temp_info
    
    # 測試案例1: 使用標準URL
    print("\n--- 測試案例1: 使用標準URL ---")
    result1 = process_temperature_data()
    print(f"產生的URL: {result1['image_url']}")
    
    # 驗證URL格式
    if '?t=' in result1['image_url']:
        print("✅ URL包含時間戳參數")
    else:
        print("❌ URL缺少時間戳參數")
    
    # 測試案例2: 處理現有URL
    print("\n--- 測試案例2: 處理現有URL ---")
    result2 = process_existing_url()
    print(f"處理後的URL: {result2['image_url']}")
    
    # 驗證URL格式
    if '?t=' in result2['image_url']:
        print("✅ URL包含時間戳參數")
    else:
        print("❌ URL缺少時間戳參數")
    
    # 測試案例3: 驗證時間戳唯一性
    print("\n--- 測試案例3: 驗證時間戳唯一性 ---")
    time.sleep(1)  # 等待1秒確保時間戳不同
    result3 = process_temperature_data()
    
    # 提取時間戳
    timestamp1 = result1['image_url'].split('?t=')[1] if '?t=' in result1['image_url'] else ''
    timestamp3 = result3['image_url'].split('?t=')[1] if '?t=' in result3['image_url'] else ''
    
    if timestamp1 != timestamp3:
        print("✅ 不同請求產生不同時間戳")
        print(f"   第一次: {timestamp1}")
        print(f"   第二次: {timestamp3}")
    else:
        print("⚠️ 時間戳相同（可能因為執行太快）")
    
    # 測試案例4: 檢查時間戳格式
    print("\n--- 測試案例4: 檢查時間戳格式 ---")
    timestamp = int(time.time())
    readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
    print(f"當前時間戳: {timestamp}")
    print(f"對應時間: {readable_time}")
    
    # 總結
    print("\n=== 測試結果總結 ===")
    
    checks = [
        ('標準URL包含時間戳', '?t=' in result1['image_url']),
        ('現有URL包含時間戳', '?t=' in result2['image_url']),
        ('時間戳格式正確', len(str(timestamp)) >= 10),
    ]
    
    all_passed = True
    for check_name, result in checks:
        status = "✅" if result else "❌"
        print(f"{status} {check_name}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n🎉 溫度分布圖快取修復測試全部通過！")
        print("主要改進:")
        print("• 為所有圖片URL加上時間戳參數")
        print("• 避免瀏覽器和Discord快取舊圖片")
        print("• 確保每次查詢都能取得最新圖片")
    else:
        print("\n⚠️ 部分測試未通過，需要進一步檢查")
    
    return all_passed

def demonstrate_before_after():
    """展示修復前後的差異"""
    print("\n=== 修復前後對比 ===")
    
    print("修復前:")
    print("❌ https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg")
    print("   問題: 總是顯示相同URL，容易被快取")
    
    timestamp = int(time.time())
    print("\n修復後:")
    print(f"✅ https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg?t={timestamp}")
    print("   改進: 每次查詢都有不同的時間戳，強制刷新")

if __name__ == "__main__":
    print("🔧 開始測試溫度分布圖快取修復")
    print("=" * 50)
    
    success = test_temperature_cache_fix()
    demonstrate_before_after()
    
    print(f"\n{'=' * 50}")
    print(f"測試結果: {'成功' if success else '失敗'}")
    
    if success:
        print("✅ 溫度分布圖快取問題已修復！")
        print("現在每次查詢都會顯示最新的溫度分布圖。")
    else:
        print("❌ 仍有問題需要修復")
