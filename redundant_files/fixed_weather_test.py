#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修復版天氣預報顯示功能測試腳本
直接使用單獨的 format_weather_data 方法實現
"""

import asyncio
import sys
import os
import json
import datetime
import traceback
import discord
import logging
from typing import Optional, Dict, Any, List

# 設定基本日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 確保可以匯入 cogs 模組
sys.path.append(os.getcwd())

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
    "多雲時陰短暫雨": "🌧️",
    "陰時多雲短暫雨": "🌧️",
    "陰天陣雨": "🌧️",
    "陰天短暫雨": "🌧️", 
    "短暫雨": "🌧️",
    "雨天": "🌧️",
    "陣雨": "🌧️",
    "午後雷陣雨": "⛈️",
    "雷雨": "⛈️",
    "多雲雷陣雨": "⛈️",
    "晴午後陣雨": "🌦️",
    "晴午後雷陣雨": "⛈️",
    "陰陣雨": "🌧️",
    "多雲時晴短暫陣雨": "🌦️",
    "多雲時晴短暫雨": "🌦️",
    "多雲短暫陣雨": "🌦️",
    "多雲時陰陣雨": "🌧️",
    "陰時多雲陣雨": "🌧️",
    "陰短暫陣雨": "🌧️",
    "雨或雪": "🌨️",
    "雨夾雪": "🌨️",
    "陰有雨或雪": "🌨️",
    "多雲時陰有雨或雪": "🌨️",
    "多雲時陰短暫雨或雪": "🌨️",
    "多雲時陰短暫雪": "🌨️",
    "短暫雨或雪": "🌨️",
    "短暫雪": "❄️",
    "下雪": "❄️",
    "積雪": "❄️",
    "暴雨": "🌊",
    "大雨": "💦",
    "豪雨": "🌊",
    "大豪雨": "🌊",
    "超大豪雨": "🌊",
    "焚風": "🔥",
    "乾燥": "🏜️",
    "寒冷": "❄️",
    "熱浪": "🔥",
    "鋒面": "🌡️",
    "雲系": "☁️",
    "有霧": "🌫️",
    "霧": "🌫️",
    "煙霧": "🌫️",
    "沙塵暴": "🏜️"
}

async def format_weather_data(location: str, weather_data: Dict) -> Optional[discord.Embed]:
    """將天氣預報資料格式化為Discord嵌入訊息，同一天的資訊顯示在一起"""
    try:
        if not weather_data or 'records' not in weather_data or 'location' not in weather_data['records']:
            return None
            
        # 尋找指定地區的天氣資料
        target_location = None
        for loc in weather_data['records']['location']:
            if loc['locationName'] == location:
                target_location = loc
                break
                
        if not target_location:
            return None
            
        # 建立嵌入訊息
        embed = discord.Embed(
            title=f"🌤️ {location}天氣預報",
            color=discord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        # 整理資料，按日期分組
        date_groups = {}
        time_periods = []
        
        # 先獲取所有時間段
        if target_location['weatherElement'] and len(target_location['weatherElement']) > 0:
            for period in target_location['weatherElement'][0]['time']:
                start_time = period['startTime']
                end_time = period['endTime']
                
                # 提取日期 (忽略時間)
                date = start_time.split(' ')[0]
                
                # 創建日期組
                if date not in date_groups:
                    date_groups[date] = []
                
                # 將時間段添加到對應的日期組
                date_groups[date].append({
                    'start': start_time,
                    'end': end_time,
                    'data': {}
                })
                
                # 保存時間段順序
                time_periods.append({
                    'date': date,
                    'start': start_time,
                    'end': end_time
                })
                
        # 填充每個時間段的天氣資料
        for element in target_location['weatherElement']:
            element_name = element['elementName']
            
            for i, period in enumerate(element['time']):
                if i < len(time_periods):
                    date = time_periods[i]['date']
                    start_time = time_periods[i]['start']
                    end_time = time_periods[i]['end']
                    
                    # 在對應的時間段中找到正確的條目
                    for entry in date_groups[date]:
                        if entry['start'] == start_time and entry['end'] == end_time:
                            entry['data'][element_name] = period['parameter']
                            break
        
        # 按日期顯示天氣資料
        for date, periods in date_groups.items():
            # 轉換日期格式為更友好的顯示
            display_date = date.replace('-', '/')
            
            # 添加日期標題
            embed.add_field(
                name=f"📅 {display_date}",
                value="天氣預報資訊",
                inline=False
            )
            
            # 添加每個時間段的詳細資訊
            for period in periods:
                # 提取時間部分
                start_hour = period['start'].split(' ')[1].split(':')[0]
                end_hour = period['end'].split(' ')[1].split(':')[0]
                time_range = f"{start_hour}:00 - {end_hour}:00"
                
                # 獲取天氣資料
                wx_data = period['data'].get('Wx', {})
                pop_data = period['data'].get('PoP', {})
                min_t_data = period['data'].get('MinT', {})
                max_t_data = period['data'].get('MaxT', {})
                ci_data = period['data'].get('CI', {})
                
                # 取得天氣描述和表情符號
                wx_desc = wx_data.get('parameterName', '未知')
                weather_emoji = WEATHER_EMOJI.get(wx_desc, "🌈")
                
                # 建立資訊字串
                info = []
                info.append(f"**天氣狀況:** {wx_desc}")
                
                if pop_data:
                    info.append(f"**降雨機率:** {pop_data.get('parameterName', '未知')}%")
                
                if min_t_data and max_t_data:
                    info.append(f"**溫度範圍:** {min_t_data.get('parameterName', '未知')}°C - {max_t_data.get('parameterName', '未知')}°C")
                
                if ci_data:
                    info.append(f"**舒適度:** {ci_data.get('parameterName', '未知')}")
                
                # 添加到嵌入訊息
                embed.add_field(
                    name=f"{weather_emoji} {time_range}",
                    value="\n".join(info),
                    inline=True
                )
        
        # 添加資料來源和更新時間
        embed.set_footer(text=f"資料來源: 中央氣象署 | 查詢時間: {datetime.datetime.now().strftime('%Y/%m/%d %H:%M')}")
        
        return embed
        
    except Exception as e:
        print(f"格式化天氣資料時發生錯誤: {str(e)}")
        traceback.print_exc()
        return None

async def main():
    print("Python 版本:", sys.version)
    print("測試修復版天氣預報顯示功能...\n")

    try:
        # 模擬天氣資料結構
        mock_weather_data = {
            "success": "true",
            "result": {
                "resource_id": "F-C0032-001",
                "fields": [
                    {"id": "locationName", "type": "String"},
                    {"id": "weatherElement", "type": "Array"}
                ],
                "records": {
                    "datasetDescription": "一般天氣預報-36小時天氣預報",
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
        }
        
        # 測試天氣預報格式化功能
        print("開始呼叫 format_weather_data 方法...")
        embed = await format_weather_data("臺北市", mock_weather_data)
        
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
        print(f"❌ 測試時發生錯誤: {str(e)}")
        print("\n詳細錯誤信息:")
        traceback.print_exc()
        
    print("\n測試完成")

if __name__ == "__main__":
    asyncio.run(main())
