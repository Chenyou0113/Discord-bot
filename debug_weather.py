#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
偵錯天氣預報功能
"""

import asyncio
import sys
import os
import traceback
import discord
import logging

# 設定基本日誌
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# 確保可以匯入 cogs 模組
sys.path.append(os.getcwd())

async def debug_weather():
    print("偵錯天氣預報功能...")
    
    try:
        # 匯入模組
        InfoCommands = None
        try:
            # 嘗試匯入實際的模組
            from cogs.info_commands import InfoCommands
            print("✅ 成功匯入 info_commands")
        except ImportError:
            print("⚠️ 無法匯入 info_commands，使用模擬類別...")
            # 如果都找不到，創建一個簡單的模擬類別
            class InfoCommands:
                def __init__(self, bot):
                    self.bot = bot
                
                async def fetch_weather_data(self):
                    return {}
                
                async def format_weather_data(self, location):
                    import discord
                    embed = discord.Embed(title=f"{location} 天氣預報", color=0x00ff00)
                    embed.add_field(name="測試", value="模擬天氣資料", inline=False)
                    return embed
            print("✅ 使用模擬 InfoCommands 類別")
        
        if InfoCommands:
            print("✅ 成功匯入 InfoCommands")
          # 建立假的 bot 物件
        class MockBot:
            def __init__(self):
                self.loop = asyncio.get_event_loop()
                
            async def wait_until_ready(self):
                pass
                
            def is_closed(self):
                return False
                
        bot = MockBot()
        info_cog = InfoCommands(bot)
        print("✅ 成功創建 InfoCommands 實例")
        
        # 模擬天氣資料
        mock_data = {
            "records": {
                "location": [
                    {
                        "locationName": "臺北市",
                        "weatherElement": [
                            {
                                "elementName": "Wx",
                                "time": [
                                    {
                                        "startTime": "2025-05-26 18:00:00",
                                        "endTime": "2025-05-27 06:00:00",
                                        "parameter": {
                                            "parameterName": "晴時多雲",
                                            "parameterValue": "2"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 06:00:00",
                                        "endTime": "2025-05-27 18:00:00",
                                        "parameter": {
                                            "parameterName": "多雲",
                                            "parameterValue": "4"
                                        }
                                    }
                                ]
                            },
                            {
                                "elementName": "PoP",
                                "time": [
                                    {
                                        "startTime": "2025-05-26 18:00:00",
                                        "endTime": "2025-05-27 06:00:00",
                                        "parameter": {
                                            "parameterName": "10",
                                            "parameterUnit": "百分比"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 06:00:00",
                                        "endTime": "2025-05-27 18:00:00",
                                        "parameter": {
                                            "parameterName": "30",
                                            "parameterUnit": "百分比"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # 替換 fetch_weather_data 方法
        async def mock_fetch_weather_data():
            print("🔄 呼叫模擬的 fetch_weather_data")
            return mock_data
            
        info_cog.fetch_weather_data = mock_fetch_weather_data
        print("✅ 已設定模擬的天氣資料獲取方法")
        
        # 測試 format_weather_data
        print("🔄 開始測試 format_weather_data...")
        try:
            embed = await info_cog.format_weather_data("臺北市")
            
            if embed:
                print("✅ 成功創建天氣預報嵌入訊息")
                print(f"標題: {embed.title}")
                print(f"顏色: {embed.color}")
                print(f"欄位數: {len(embed.fields)}")
                
                for i, field in enumerate(embed.fields):
                    print(f"  欄位 {i+1}: {field.name}")
                    print(f"    值: {field.value[:100]}...")
                    print(f"    內聯: {field.inline}")
            else:
                print("❌ format_weather_data 返回 None")
                
        except Exception as e:
            print(f"❌ format_weather_data 執行錯誤: {str(e)}")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 偵錯過程發生錯誤: {str(e)}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_weather())
