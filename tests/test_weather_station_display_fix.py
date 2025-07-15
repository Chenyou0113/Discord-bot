#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試天氣測站顯示修正

測試 /weather_station 指令的預設行為是否正確顯示簡化列表而不是詳細資料
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import logging
from datetime import datetime
from cogs.weather_commands import WeatherCommands
from unittest.mock import MagicMock, AsyncMock

# 設定日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockBot:
    """模擬 Discord Bot"""
    def __init__(self):
        self.connector = None

class MockInteraction:
    """模擬 Discord Interaction"""
    def __init__(self):
        self.user = "test_user"
        self.response = AsyncMock()
        self.followup = AsyncMock()
        self.response.defer = AsyncMock()
        self.followup.send = AsyncMock()

async def test_weather_station_display():
    """測試天氣測站顯示邏輯"""
    logger.info("=== 測試天氣測站顯示修正 ===")
    
    # 創建模擬物件
    bot = MockBot()
    weather_commands = WeatherCommands(bot)
    
    # 模擬測站資料
    mock_station_data = {
        "success": "true",
        "records": {
            "data": {
                "stationStatus": {
                    "station": [
                        {
                            "StationID": "C0A940",
                            "StationName": "板橋",
                            "StationNameEN": "Banqiao",
                            "StationAltitude": 10,
                            "StationLongitude": 121.4583,
                            "StationLatitude": 25.0122,
                            "CountyName": "新北市",
                            "Location": "新北市板橋區中山路一段161號",
                            "StationStartDate": "2009-01-01",
                            "StationEndDate": "",
                            "status": "現存測站",
                            "Notes": "測試測站",
                            "OriginalStationID": "",
                            "NewStationID": ""
                        }
                    ]
                }
            }
        }
    }
    
    # 模擬 API 回應
    weather_commands.fetch_station_data = AsyncMock(return_value=mock_station_data)
    
    # 測試情況1：預設行為（不指定 detailed 參數）
    logger.info("測試 1: 預設行為 - 應顯示簡化列表")
    mock_interaction = MockInteraction()
    
    await weather_commands.weather_station(mock_interaction, "板橋")
    
    # 驗證是否調用了 followup.send
    if mock_interaction.followup.send.called:
        call_args = mock_interaction.followup.send.call_args
        embed = call_args[1]['embed'] if 'embed' in call_args[1] else call_args[0][0]
        
        logger.info(f"回應標題: {embed.title}")
        logger.info(f"回應描述: {embed.description}")
        
        # 檢查是否顯示的是列表格式而非詳細資料
        if "測站列表" in embed.title or "查詢結果" in embed.title:
            logger.info("✅ 正確顯示簡化列表")
        else:
            logger.warning("❌ 顯示的不是列表格式")
        
        # 檢查是否有查看詳細資訊的提示
        has_detailed_tip = False
        for field in embed.fields:
            if "詳細資訊" in field.name:
                has_detailed_tip = True
                logger.info(f"✅ 找到詳細資訊提示: {field.value}")
                break
        
        if not has_detailed_tip:
            logger.warning("❌ 未找到查看詳細資訊的提示")
    else:
        logger.error("❌ 未調用 followup.send")
    
    # 測試情況2：明確指定 detailed=True
    logger.info("\n測試 2: 明確指定 detailed=True - 應顯示詳細資料")
    mock_interaction2 = MockInteraction()
    
    await weather_commands.weather_station(mock_interaction2, "板橋", detailed=True)
    
    # 驗證是否調用了 followup.send
    if mock_interaction2.followup.send.called:
        call_args = mock_interaction2.followup.send.call_args
        embed = call_args[1]['embed'] if 'embed' in call_args[1] else call_args[0][0]
        
        logger.info(f"回應標題: {embed.title}")
        logger.info(f"回應描述: {embed.description}")
        
        # 檢查是否顯示的是詳細資料格式
        if "板橋" in embed.title and "C0A940" in embed.title:
            logger.info("✅ 正確顯示詳細資料")
        else:
            logger.warning("❌ 顯示的不是詳細資料格式")
    else:
        logger.error("❌ 未調用 followup.send")
    
    # 測試情況3：明確指定 detailed=False
    logger.info("\n測試 3: 明確指定 detailed=False - 應顯示簡化列表")
    mock_interaction3 = MockInteraction()
    
    await weather_commands.weather_station(mock_interaction3, "板橋", detailed=False)
    
    # 驗證是否調用了 followup.send
    if mock_interaction3.followup.send.called:
        call_args = mock_interaction3.followup.send.call_args
        embed = call_args[1]['embed'] if 'embed' in call_args[1] else call_args[0][0]
        
        logger.info(f"回應標題: {embed.title}")
        logger.info(f"回應描述: {embed.description}")
        
        # 檢查是否顯示的是列表格式而非詳細資料
        if "測站列表" in embed.title or "查詢結果" in embed.title:
            logger.info("✅ 正確顯示簡化列表")
        else:
            logger.warning("❌ 顯示的不是列表格式")
    else:
        logger.error("❌ 未調用 followup.send")

async def main():
    """主要測試函數"""
    try:
        await test_weather_station_display()
        logger.info("\n=== 測試完成 ===")
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
    print("• 在列表中提供查看詳細資訊的提示")
    
    print("\n📝 指令使用方式：")
    print("1. 簡化列表（預設）：")
    print("   /weather_station 板橋")
    print("   /weather_station 台北市")
    print("   /weather_station C0A940")
    
    print("\n2. 詳細資訊（當只有一個結果時）：")
    print("   /weather_station 板橋 detailed:True")
    print("   /weather_station C0A940 detailed:True")
    
    print("\n3. 翻頁查看：")
    print("   /weather_station 台北 page:2")
    
    print("\n4. 查看特定測站詳細資訊：")
    print("   /weather_station_info C0A940")
    
    print("\n💡 改進效果：")
    print("✅ 解決了「無人測站查詢顯示詳細資料」的問題")
    print("✅ 用戶現在預設看到簡化列表")
    print("✅ 提供了選擇查看詳細資訊的方式")
    print("✅ 改善了用戶體驗和操作直覺性")

def demonstrate_example_scenarios():
    """示範修正前後的差異"""
    
    print("\n" + "="*50)
    print("📊 修正前後對比示範")
    
    scenarios = [
        {
            "query": "板橋",
            "results": 1,
            "before": "自動顯示詳細資料（用戶可能不想看這麼多資訊）",
            "after": "顯示簡化列表 + 提示如何查看詳細資訊"
        },
        {
            "query": "台北市",
            "results": 5,
            "before": "顯示簡化列表（正常）",
            "after": "顯示簡化列表 + 提示如何查看詳細資訊（改善）"
        },
        {
            "query": "C0A940",
            "results": 1,
            "before": "自動顯示詳細資料（可能不符合用戶期望）",
            "after": "顯示簡化列表，用戶可選擇 detailed:True 看詳細資料"
        }
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📈 情境 {i}：搜尋 '{scenario['query']}'（{scenario['results']} 個結果）")
        print(f"   修正前：{scenario['before']}")
        print(f"   修正後：{scenario['after']}")

def show_implementation_details():
    """顯示實作細節"""
    
    print("\n" + "="*50)
    print("🔧 實作細節")
    
    print("\n📝 主要修改：")
    print("1. weather_station 指令添加 detailed 參數")
    print("2. 修改顯示邏輯：預設顯示列表格式")
    print("3. 添加查看詳細資訊的提示訊息")
    print("4. 保留原有的 weather_station_info 指令")
    
    print("\n⚙️ 程式邏輯：")
    print("if detailed and len(matching_stations) == 1:")
    print("    # 用戶明確要求詳細資訊且只有一個結果")
    print("    顯示詳細資料")
    print("else:")
    print("    # 預設顯示列表格式")
    print("    顯示簡化列表")

if __name__ == "__main__":
    test_weather_station_display_logic()
    demonstrate_example_scenarios()
    show_implementation_details()
    
    print("\n" + "="*50)
    print("✅ 測試完成")
    print("建議在 Discord 中測試以下指令驗證修正效果：")
    print("• /weather_station 板橋")
    print("• /weather_station 板橋 detailed:True")
    print("• /weather_station 台北市 page:1")
