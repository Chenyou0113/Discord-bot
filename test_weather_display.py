#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 用於測試天氣資料預報功能
# 檔案路徑：C:\Users\xiaoy\Desktop\Discord bot\test_weather_display.py

import asyncio
import sys
import os
import json
from datetime import datetime
import traceback
import discord
import logging

# 設定基本日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 確保可以匯入 cogs 模組
sys.path.append(os.getcwd())

# 修正 info_commands_fixed_v4 中的問題
def patch_info_commands():
    try:
        import cogs.info_commands_fixed_v4 as module
        print("✅ 成功匯入 info_commands_fixed_v4 模組")
        
        # 儲存原始方法
        original_format_weather = module.InfoCommands.format_weather_data
        original_init = module.InfoCommands.__init__
        
        # 修補 __init__ 方法
        def patched_init(self, bot):
            self.bot = bot
            self.earthquake_cache = {}
            self.weather_cache = {}
            self.weather_alert_cache = {}
            self.reservoir_cache = {}
            self.water_info_cache = {}
            self.cache_time = 0
            self.weather_cache_time = 0
            self.weather_alert_cache_time = 0
            self.reservoir_cache_time = 0
            self.water_info_cache_time = 0
            self.api_auth = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
            self.notification_channels = {}
            self.last_eq_time = {}
            self.check_interval = 300
            self.session = None
            # 不要啟動任務
        
        # 應用修補
        module.InfoCommands.__init__ = patched_init
        
        return module
    except Exception as e:
        print(f"❌ 匯入或修補 info_commands_fixed_v4 時發生錯誤: {str(e)}")
        traceback.print_exc()
        return None

async def main():
    print("Python 版本:", sys.version)
    print("測試天氣預報顯示功能...\n")

    try:
        # 獲取修補後的模組
        module = patch_info_commands()
        InfoCommands = module.InfoCommands
          # 創建一個簡單的機器人實例用於測試
        class MockBot:
            def __init__(self):
                self.loop = asyncio.get_event_loop()
                
            async def wait_until_ready(self):
                pass
                
            def is_closed(self):
                return False
                
        bot = MockBot()
        
        # 初始化 InfoCommands
        info_cog = InfoCommands(bot)        # 模擬天氣資料結構
        mock_weather_data = {
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
                                    },
                                    {
                                        "startTime": "2025-05-27 18:00:00",
                                        "endTime": "2025-05-28 06:00:00",
                                        "parameter": {
                                            "parameterName": "陰短暫雨",
                                            "parameterValue": "10"
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
                                    },
                                    {
                                        "startTime": "2025-05-27 18:00:00",
                                        "endTime": "2025-05-28 06:00:00",
                                        "parameter": {
                                            "parameterName": "80",
                                            "parameterUnit": "百分比"
                                        }
                                    }
                                ]
                            },
                            {
                                "elementName": "MinT",
                                "time": [
                                    {
                                        "startTime": "2025-05-26 18:00:00",
                                        "endTime": "2025-05-27 06:00:00",
                                        "parameter": {
                                            "parameterName": "22",
                                            "parameterUnit": "攝氏度"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 06:00:00",
                                        "endTime": "2025-05-27 18:00:00",
                                        "parameter": {
                                            "parameterName": "20",
                                            "parameterUnit": "攝氏度"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 18:00:00",
                                        "endTime": "2025-05-28 06:00:00",
                                        "parameter": {
                                            "parameterName": "19",
                                            "parameterUnit": "攝氏度"
                                        }
                                    }
                                ]
                            },
                            {
                                "elementName": "MaxT",
                                "time": [
                                    {
                                        "startTime": "2025-05-26 18:00:00",
                                        "endTime": "2025-05-27 06:00:00",
                                        "parameter": {
                                            "parameterName": "28",
                                            "parameterUnit": "攝氏度"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 06:00:00",
                                        "endTime": "2025-05-27 18:00:00",
                                        "parameter": {
                                            "parameterName": "30",
                                            "parameterUnit": "攝氏度"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 18:00:00",
                                        "endTime": "2025-05-28 06:00:00",
                                        "parameter": {
                                            "parameterName": "25",
                                            "parameterUnit": "攝氏度"
                                        }
                                    }
                                ]
                            },
                            {
                                "elementName": "CI",
                                "time": [
                                    {
                                        "startTime": "2025-05-26 18:00:00",
                                        "endTime": "2025-05-27 06:00:00",
                                        "parameter": {
                                            "parameterName": "舒適"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 06:00:00",
                                        "endTime": "2025-05-27 18:00:00",
                                        "parameter": {
                                            "parameterName": "悶熱"
                                        }
                                    },
                                    {
                                        "startTime": "2025-05-27 18:00:00",
                                        "endTime": "2025-05-28 06:00:00",
                                        "parameter": {
                                            "parameterName": "舒適"
                                        }
                                    }
                                ]
                            }
                        ]
                    }
                ]
            }
        }
        
        # 修改 fetch_weather_data 方法以返回我們的模擬資料
        async def mock_fetch_weather_data():
            return mock_weather_data
            
        # 替換方法
        info_cog.fetch_weather_data = mock_fetch_weather_data        # 測試天氣預報格式化功能
        try:
            embed = await info_cog.format_weather_data("臺北市")
            
            if embed:
                print("✅ 成功創建天氣預報訊息嵌入")
                print(f"標題: {embed.title}")
                print(f"顏色: {embed.color}")
                print(f"欄位數: {len(embed.fields)}")
                
                print("\n嵌入欄位內容:")
                for i, field in enumerate(embed.fields):
                    print(f"欄位 {i+1}: {field.name}")
                    print(f"   值: {field.value}")
                    print(f"   內聯: {field.inline}")
                    print("")
            else:
                print("❌ 無法創建天氣預報訊息嵌入")
        except Exception as e:
            print(f"❌ format_weather_data 執行時發生錯誤: {str(e)}")
            print("\n詳細錯誤信息:")
            traceback.print_exc()
            
    except Exception as e:
        print(f"❌ 測試時發生錯誤: {str(e)}")
        print("\n詳細錯誤信息:")
        traceback.print_exc()
        
    print("\n測試完成")

if __name__ == "__main__":
    asyncio.run(main())
