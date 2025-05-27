#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
修正版的天氣資料格式化函數
用於替換 info_commands_fixed_v4.py 中的 format_weather_data 方法
"""

import discord
import datetime
import asyncio
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 天氣預報用表情符號對應 (簡化版)
WEATHER_EMOJI = {
    "晴天": "☀️",
    "晴時多雲": "🌤️",
    "多雲時晴": "⛅",
    "多雲": "☁️",
    "多雲時陰": "☁️",
    "陰時多雲": "🌥️",
    "陰天": "🌫️",
    "多雲陣雨": "🌦️"
}

async def format_weather_data(location, weather_data):
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
        logger.error(f"格式化天氣資料時發生錯誤: {str(e)}")
        return None

# 測試用的主程式
if __name__ == "__main__":
    # 模擬的天氣資料
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
    
    # 使用asyncio運行
    result = asyncio.run(format_weather_data("臺北市", mock_data))
    print("測試完成")
