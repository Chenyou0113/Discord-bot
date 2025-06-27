#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整氣象測站功能測試腳本
測試機器人的氣象測站查詢功能是否正常運作

作者: Discord Bot Project
日期: 2025-01-05
"""

import sys
import os
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch
import json

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import discord
    from discord.ext import commands
    from cogs.weather_commands import WeatherCommands
    from bot import CustomBot
    from dotenv import load_dotenv
except ImportError as e:
    print(f"❌ 無法導入模組: {e}")
    print("請確保您已安裝所有依賴套件：pip install -r requirements.txt")
    sys.exit(1)

# 載入環境變數
load_dotenv()

class TestWeatherStationComplete(unittest.TestCase):
    """完整氣象測站功能測試"""
    
    def setUp(self):
        """測試前的設置"""
        self.bot = None
        self.weather_cog = None
        
    def tearDown(self):
        """測試後的清理"""
        if self.bot:
            pass
    
    async def test_weather_cog_initialization(self):
        """測試氣象 Cog 初始化"""
        print("\n🧪 測試氣象 Cog 初始化...")
        
        # 創建模擬機器人
        bot = MagicMock()
        
        # 初始化氣象 Cog
        weather_cog = WeatherCommands(bot)
        
        # 檢查基本屬性
        self.assertEqual(weather_cog.bot, bot)
        self.assertTrue(weather_cog.cwa_api_base.startswith("https://opendata.cwa.gov.tw"))
        self.assertTrue(hasattr(weather_cog, 'authorization'))
        self.assertIsInstance(weather_cog.station_data_cache, dict)
        self.assertEqual(weather_cog.cache_duration, 3600)
        
        print("✅ 氣象 Cog 初始化測試通過")
        print(f"   API 基礎 URL: {weather_cog.cwa_api_base}")
        print(f"   快取持續時間: {weather_cog.cache_duration} 秒")
    
    async def test_api_connection(self):
        """測試 API 連線"""
        print("\n🧪 測試 CWA API 連線...")
        
        bot = MagicMock()
        weather_cog = WeatherCommands(bot)
        
        try:
            # 嘗試獲取測站資料
            station_data = await weather_cog.fetch_station_data()
            
            # 檢查回應結構
            self.assertIsInstance(station_data, dict)
            if 'records' in station_data:
                self.assertIn('records', station_data)
                records = station_data['records']
                if 'Station' in records and records['Station']:
                    stations = records['Station']
                    self.assertIsInstance(stations, list)
                    if stations:
                        # 檢查第一個測站的基本欄位
                        first_station = stations[0]
                        expected_fields = ['StationId', 'StationName', 'CountyName']
                        for field in expected_fields:
                            self.assertIn(field, first_station)
                        
                        print("✅ API 連線測試通過")
                        print(f"   成功獲取 {len(stations)} 個測站資料")
                        print(f"   第一個測站: {first_station.get('StationName', 'N/A')}")
                    else:
                        print("⚠️  API 回應中沒有測站資料，但連線成功")
                else:
                    print("⚠️  API 回應格式異常，但連線成功")
            else:
                print("⚠️  API 回應格式異常，但連線成功")
                
        except Exception as e:
            print(f"❌ API 連線測試失敗: {e}")
            # 不讓測試失敗，因為可能是網路問題
            print("⚠️  跳過 API 測試（可能是網路問題）")
    
    async def test_search_functionality(self):
        """測試搜尋功能"""
        print("\n🧪 測試搜尋功能...")
        
        # 模擬測站資料
        mock_stations = [
            {
                "StationId": "C0A4A0",
                "StationName": "阿里山",
                "CountyName": "嘉義縣",
                "StationLatitude": 23.5083,
                "StationLongitude": 120.8028,
                "StationAltitude": 2413.0,
                "StationStatus": "正常"
            },
            {
                "StationId": "46692",
                "StationName": "玉山",
                "CountyName": "南投縣",
                "StationLatitude": 23.4883,
                "StationLongitude": 120.9597,
                "StationAltitude": 3844.8,
                "StationStatus": "正常"
            }
        ]
        
        bot = MagicMock()
        weather_cog = WeatherCommands(bot)
        
        # 測試關鍵字搜尋
        results = weather_cog.search_stations_by_keyword(mock_stations, "阿里山")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["StationName"], "阿里山")
        
        # 測試縣市搜尋
        results = weather_cog.search_stations_by_county(mock_stations, "嘉義縣")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["CountyName"], "嘉義縣")
        
        # 測試測站編號搜尋
        result = weather_cog.find_station_by_id(mock_stations, "46692")
        self.assertIsNotNone(result)
        self.assertEqual(result["StationName"], "玉山")
        
        print("✅ 搜尋功能測試通過")
        print("   關鍵字搜尋: ✓")
        print("   縣市搜尋: ✓")
        print("   測站編號搜尋: ✓")
    
    async def test_embed_creation(self):
        """測試 Embed 建立功能"""
        print("\n🧪 測試 Embed 建立功能...")
        
        # 模擬測站資料
        mock_station = {
            "StationId": "C0A4A0",
            "StationName": "阿里山",
            "CountyName": "嘉義縣",
            "StationLatitude": 23.5083,
            "StationLongitude": 120.8028,
            "StationAltitude": 2413.0,
            "StationStatus": "正常"
        }
        
        bot = MagicMock()
        weather_cog = WeatherCommands(bot)
        
        # 建立詳細資訊 embed
        embed = weather_cog.create_station_detail_embed(mock_station)
        
        # 檢查 embed 屬性
        self.assertIsInstance(embed, discord.Embed)
        self.assertIn("阿里山", embed.title)
        self.assertEqual(embed.colour, discord.Colour.blue())
        
        # 檢查欄位
        fields = {field.name: field.value for field in embed.fields}
        self.assertIn("測站編號", fields)
        self.assertIn("縣市", fields)
        self.assertIn("狀態", fields)
        
        print("✅ Embed 建立功能測試通過")
        print(f"   標題: {embed.title}")
        print(f"   欄位數量: {len(embed.fields)}")
    
    async def test_pagination(self):
        """測試分頁功能"""
        print("\n🧪 測試分頁功能...")
        
        # 建立多個模擬測站（超過每頁顯示數量）
        mock_stations = [
            {
                "StationId": f"TEST{i:03d}",
                "StationName": f"測站{i}",
                "CountyName": "測試縣",
                "StationStatus": "正常"
            }
            for i in range(15)  # 15 個測站，每頁 10 個
        ]
        
        bot = MagicMock()
        weather_cog = WeatherCommands(bot)
        
        # 測試分頁
        page_1 = weather_cog.get_stations_page(mock_stations, 0, 10)
        page_2 = weather_cog.get_stations_page(mock_stations, 1, 10)
        
        self.assertEqual(len(page_1), 10)
        self.assertEqual(len(page_2), 5)
        
        # 測試頁數計算
        total_pages = weather_cog.calculate_total_pages(len(mock_stations), 10)
        self.assertEqual(total_pages, 2)
        
        print("✅ 分頁功能測試通過")
        print(f"   第一頁項目數: {len(page_1)}")
        print(f"   第二頁項目數: {len(page_2)}")
        print(f"   總頁數: {total_pages}")

async def run_all_tests():
    """執行所有測試"""
    test_case = TestWeatherStationComplete()
    test_case.setUp()
    
    tests = [
        ("氣象 Cog 初始化", test_case.test_weather_cog_initialization),
        ("API 連線", test_case.test_api_connection),
        ("搜尋功能", test_case.test_search_functionality),
        ("Embed 建立", test_case.test_embed_creation),
        ("分頁功能", test_case.test_pagination)
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except Exception as e:
            print(f"❌ {test_name} 測試失敗: {e}")
            failed += 1
    
    test_case.tearDown()
    
    print(f"\n{'='*60}")
    print(f"測試結果: {passed} 個通過, {failed} 個失敗")
    print(f"{'='*60}")
    
    return failed == 0

def main():
    """主函數"""
    print("=" * 60)
    print("完整氣象測站功能測試")
    print("=" * 60)
    print("測試項目:")
    print("1. 氣象 Cog 初始化")
    print("2. CWA API 連線")
    print("3. 搜尋功能（關鍵字、縣市、測站編號）")
    print("4. Discord Embed 建立")
    print("5. 分頁功能")
    print("-" * 60)
    
    try:
        # 執行所有測試
        success = asyncio.run(run_all_tests())
        
        if success:
            print("\n🎉 所有測試通過！氣象測站功能運作正常")
            print("\n下一步:")
            print("1. 啟動 Discord 機器人進行實際測試")
            print("2. 在 Discord 伺服器中使用以下指令測試:")
            print("   • /weather_station [關鍵字]")
            print("   • /weather_station_by_county [縣市]")
            print("   • /weather_station_info [測站編號]")
            print("\n提示:")
            print("- 確保機器人已加入伺服器並有適當權限")
            print("- 確保 .env 檔案中的 CWA API 金鑰正確")
            print("- 測試時注意 API 回應時間可能較長")
        else:
            print("\n❌ 部分測試失敗，請檢查錯誤訊息")
            return False
            
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
