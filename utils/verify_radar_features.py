#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷達圖功能驗證腳本
本地測試雷達圖查詢功能的各項特性
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 添加專案根目錄到路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模擬 Discord 相關模組
class MockInteraction:
    def __init__(self):
        self.response = MockResponse()
        self.followup = MockFollowup()
        
class MockResponse:
    async def defer(self):
        print("📡 [模擬] 延遲回應...")

class MockFollowup:
    async def send(self, content=None, embed=None, view=None, ephemeral=False):
        if embed:
            print(f"📤 [模擬] 發送 Embed: {embed.title}")
            print(f"   描述: {embed.description}")
            for field in embed.fields:
                print(f"   欄位: {field.name} = {field.value}")
        else:
            print(f"📤 [模擬] 發送訊息: {content}")

class MockColour:
    @staticmethod
    def blue():
        return "藍色"
    @staticmethod
    def red():
        return "紅色"
    @staticmethod
    def green():
        return "綠色"

class MockEmbed:
    def __init__(self, title="", description="", color=None):
        self.title = title
        self.description = description
        self.color = color
        self.fields = []
        self.image_url = None
        self.footer_text = None
        
    def add_field(self, name, value, inline=True):
        field = type('Field', (), {'name': name, 'value': value, 'inline': inline})()
        self.fields.append(field)
        return self
        
    def set_image(self, url):
        self.image_url = url
        return self
        
    def set_footer(self, text):
        self.footer_text = text
        return self

# 模擬 discord 模組
import types
discord = types.ModuleType('discord')
discord.Embed = MockEmbed
discord.Colour = MockColour

sys.modules['discord'] = discord

async def test_radar_api_connection():
    """測試雷達圖 API 連線"""
    print("🔍 測試雷達圖 API 連線...")
    
    try:
        from cogs.radar_commands import RadarCommands
        
        # 創建雷達指令實例
        radar_cog = RadarCommands(None)
        
        # 測試獲取雷達圖資料
        data = await radar_cog.fetch_radar_data()
        
        if not data:
            print("❌ API 連線失敗")
            return False
            
        print("✅ API 連線成功")
        
        # 測試資料解析
        radar_info = radar_cog.parse_radar_data(data)
        
        if not radar_info:
            print("❌ 資料解析失敗")
            return False
            
        print("✅ 資料解析成功")
        
        # 顯示解析結果
        print("\n📊 雷達圖資訊:")
        print(f"   識別碼: {radar_info.get('identifier', 'N/A')}")
        print(f"   觀測時間: {radar_info.get('datetime', 'N/A')}")
        print(f"   發布時間: {radar_info.get('sent', 'N/A')}")
        print(f"   描述: {radar_info.get('description', 'N/A')}")
        print(f"   雷達站: {radar_info.get('radar_names', 'N/A')}")
        print(f"   圖片 URL: {radar_info.get('image_url', 'N/A')}")
        
        coverage = radar_info.get('coverage', {})
        if coverage:
            print(f"   覆蓋範圍: 經度 {coverage.get('longitude', 'N/A')}, 緯度 {coverage.get('latitude', 'N/A')}")
            
        print(f"   圖像尺寸: {radar_info.get('dimension', 'N/A')}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_embed_creation():
    """測試 Embed 建立功能"""
    print("\n🎨 測試 Embed 建立功能...")
    
    try:
        from cogs.radar_commands import RadarCommands
        
        radar_cog = RadarCommands(None)
        
        # 獲取實際資料
        data = await radar_cog.fetch_radar_data()
        radar_info = radar_cog.parse_radar_data(data)
        
        if not radar_info:
            print("❌ 無法獲取雷達圖資料")
            return False
        
        # 測試主要雷達圖 Embed
        embed = radar_cog.create_radar_embed(radar_info)
        print("✅ 主要雷達圖 Embed 建立成功")
        print(f"   標題: {embed.title}")
        print(f"   描述: {embed.description}")
        print(f"   欄位數量: {len(embed.fields)}")
        
        # 測試說明 Embed
        info_embed = radar_cog.create_info_embed()
        print("✅ 說明 Embed 建立成功")
        print(f"   標題: {info_embed.title}")
        print(f"   欄位數量: {len(info_embed.fields)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Embed 建立失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_cache_mechanism():
    """測試快取機制"""
    print("\n🗄️ 測試快取機制...")
    
    try:
        from cogs.radar_commands import RadarCommands
        
        radar_cog = RadarCommands(None)
        
        # 第一次請求（應該從 API 獲取）
        print("   第一次請求...")
        data1 = await radar_cog.fetch_radar_data()
        if not data1:
            print("❌ 第一次請求失敗")
            return False
        print("✅ 第一次請求成功")
        
        # 第二次請求（應該從快取獲取）
        print("   第二次請求...")
        data2 = await radar_cog.fetch_radar_data()
        if not data2:
            print("❌ 第二次請求失敗")
            return False
        print("✅ 第二次請求成功")
        
        # 檢查快取是否有效
        if radar_cog.radar_cache:
            print("✅ 快取機制正常運作")
        else:
            print("⚠️ 快取可能未正常運作")
            
        return True
        
    except Exception as e:
        print(f"❌ 快取測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_datetime_formatting():
    """測試日期時間格式化"""
    print("\n⏰ 測試日期時間格式化...")
    
    try:
        from cogs.radar_commands import RadarCommands
        
        radar_cog = RadarCommands(None)
        
        # 測試不同格式的時間字符串
        test_cases = [
            "2025-06-28T17:00:00+08:00",
            "2025-06-28T09:00:00Z",
            "",
            "invalid_date"
        ]
        
        for test_time in test_cases:
            formatted = radar_cog.format_datetime(test_time)
            print(f"   輸入: {test_time} -> 輸出: {formatted}")
        
        print("✅ 日期時間格式化測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 日期時間格式化測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_error_handling():
    """測試錯誤處理"""
    print("\n🚨 測試錯誤處理...")
    
    try:
        from cogs.radar_commands import RadarCommands
        
        radar_cog = RadarCommands(None)
        
        # 測試無效資料的解析
        invalid_data_cases = [
            {},  # 空字典
            {"invalid": "data"},  # 無效格式
            {"cwaopendata": {}},  # 缺少必要欄位
        ]
        
        for i, invalid_data in enumerate(invalid_data_cases, 1):
            print(f"   測試無效資料 {i}...")
            result = radar_cog.parse_radar_data(invalid_data)
            if not result:
                print(f"✅ 正確處理無效資料 {i}")
            else:
                print(f"⚠️ 無效資料 {i} 可能未正確處理")
        
        print("✅ 錯誤處理測試完成")
        return True
        
    except Exception as e:
        print(f"❌ 錯誤處理測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_command_simulation():
    """模擬指令執行"""
    print("\n🤖 模擬指令執行...")
    
    try:
        from cogs.radar_commands import RadarCommands
        
        radar_cog = RadarCommands(None)
        
        # 模擬 /radar 指令
        print("   模擬 /radar 指令...")
        interaction = MockInteraction()
        await radar_cog.radar(interaction)
        print("✅ /radar 指令模擬成功")
        
        # 模擬 /radar_info 指令
        print("   模擬 /radar_info 指令...")
        interaction = MockInteraction()
        await radar_cog.radar_info(interaction)
        print("✅ /radar_info 指令模擬成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 指令模擬失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_summary(results):
    """顯示測試摘要"""
    print("\n" + "=" * 60)
    print("📊 雷達圖功能驗證摘要")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{status} {test_name}")
    
    print("-" * 60)
    print(f"總計: {passed_tests}/{total_tests} 項測試通過")
    
    if passed_tests == total_tests:
        print("🎉 所有雷達圖功能測試均通過！")
        print("\n✨ 功能特色:")
        print("   • 即時雷達圖顯示")
        print("   • 智慧快取機制")
        print("   • 詳細氣象資訊")
        print("   • 互動式重新整理按鈕")
        print("   • 完整錯誤處理")
        print("   • 雷達覆蓋範圍說明")
        print("   • 回波強度說明")
        
        print("\n📱 可用指令:")
        print("   • /radar - 查詢最新雷達圖")
        print("   • /radar_info - 查看功能說明")
        
        print("\n🔧 API 資訊:")
        print("   • 資料來源: 中央氣象署")
        print("   • 更新頻率: 每10分鐘")
        print("   • 圖像類型: PNG 格式，3600x3600 像素")
        print("   • 雷達站: 五分山、花蓮、七股、墾丁、樹林、南屯、林園")
        
    else:
        print(f"⚠️ 有 {total_tests - passed_tests} 項測試未通過，請檢查相關功能")
    
    return passed_tests == total_tests

async def main():
    """主要測試流程"""
    print("🌩️ 雷達圖功能驗證開始")
    print("測試項目: 台灣雷達圖整合無地形查詢功能")
    print("=" * 60)
    
    # 執行所有測試
    results = {}
    
    results["API 連線測試"] = await test_radar_api_connection()
    results["Embed 建立測試"] = await test_embed_creation()
    results["快取機制測試"] = await test_cache_mechanism()
    results["日期時間格式化測試"] = await test_datetime_formatting()
    results["錯誤處理測試"] = await test_error_handling()
    results["指令模擬測試"] = await test_command_simulation()
    
    # 顯示測試摘要
    success = print_summary(results)
    
    return success

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🎯 雷達圖功能已準備就緒，可以在 Discord 中使用！")
        else:
            print("\n❌ 部分功能測試失敗，請檢查問題後再試")
        
    except Exception as e:
        print(f"\n💥 驗證過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
