#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
簡化版天氣預報顯示測試腳本
"""

import asyncio
import sys
import json
import discord
from datetime import datetime
import traceback

# 天氣預報用表情符號對應
WEATHER_EMOJI = {
    "晴天": "☀️",
    "晴時多雲": "🌤️",
    "多雲時晴": "⛅",
    "多雲": "☁️",
    "多雲時陰": "☁️",
    "陰時多雲": "🌥️",
    "陰天": "🌫️",
    "多雲陣雨": "🌦️",
    "多雲短暫雨": "🌦️",
    "陰短暫雨": "🌧️"
}

# 測試資料
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
                                    "parameterName": "晴時多雲"
                                }
                            },
                            {
                                "startTime": "2025-05-27 06:00:00",
                                "endTime": "2025-05-27 18:00:00",
                                "parameter": {
                                    "parameterName": "多雲"
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
                                    "parameterName": "10"
                                }
                            },
                            {
                                "startTime": "2025-05-27 06:00:00",
                                "endTime": "2025-05-27 18:00:00",
                                "parameter": {
                                    "parameterName": "30"
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

async def simple_test():
    print("簡單測試天氣分組功能")
    
    # 根據日期分組
    try:
        # 取得地區資料
        location_data = mock_data["records"]["location"][0]
        
        # 建立嵌入訊息
        embed = discord.Embed(
            title=f"🌤️ {location_data['locationName']}天氣預報",
            color=discord.Color.blue(),
            timestamp=datetime.now()
        )
        
        # 整理資料，按日期分組
        date_groups = {}
        
        # 獲取所有時間段
        for period in location_data["weatherElement"][0]["time"]:
            start_time = period["startTime"]
            date = start_time.split(" ")[0]
            
            if date not in date_groups:
                date_groups[date] = []
                
            date_groups[date].append(period)
        
        # 顯示分組結果
        print(f"找到 {len(date_groups)} 個日期群組:")
        
        for date, periods in date_groups.items():
            print(f"- 日期: {date}, 時段數: {len(periods)}")
            
            # 添加日期標題到嵌入訊息
            embed.add_field(
                name=f"📅 {date}",
                value=f"{len(periods)} 個時段",
                inline=False
            )
            
            # 添加時段詳情
            for period in periods:
                start = period["startTime"].split(" ")[1]
                end = period["endTime"].split(" ")[1]
                
                embed.add_field(
                    name=f"⏱️ {start} - {end}",
                    value="天氣資訊",
                    inline=True
                )
        
        # 顯示結果
        print("\n嵌入訊息欄位:")
        for i, field in enumerate(embed.fields):
            print(f"欄位 {i+1}: {field.name}")
            print(f"  值: {field.value}")
            print(f"  內聯: {field.inline}\n")
            
        print("✅ 測試成功")
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        traceback.print_exc()

# 主程式
if __name__ == "__main__":
    asyncio.run(simple_test())
