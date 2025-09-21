#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試捷運電子看板功能
"""

import asyncio
import sys
import os
import json
from datetime import datetime

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模擬捷運 API 資料
sample_metro_data = [
    {
        "LineID": "BL",
        "StationID": "BL05",
        "StationName": {
            "Zh_tw": "亞東醫院",
            "En": "Far Eastern Hospital"
        },
        "DestinationStationName": {
            "Zh_tw": "頂埔",
            "En": "Dingpu"
        },
        "EstimateTime": 45,  # 45秒
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    },
    {
        "LineID": "BL",
        "StationID": "BL05",
        "StationName": {
            "Zh_tw": "亞東醫院",
            "En": "Far Eastern Hospital"
        },
        "DestinationStationName": {
            "Zh_tw": "南港展覽館",
            "En": "Nangang Exhibition Center"
        },
        "EstimateTime": 120,  # 2分鐘
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    },
    {
        "LineID": "R",
        "StationID": "R10",
        "StationName": {
            "Zh_tw": "台北車站",
            "En": "Taipei Main Station"
        },
        "DestinationStationName": {
            "Zh_tw": "淡水",
            "En": "Tamsui"
        },
        "EstimateTime": 0,  # 進站中
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    },
    {
        "LineID": "R",
        "StationID": "R10",
        "StationName": {
            "Zh_tw": "台北車站",
            "En": "Taipei Main Station"
        },
        "DestinationStationName": {
            "Zh_tw": "象山",
            "En": "Xiangshan"
        },
        "EstimateTime": 300,  # 5分鐘
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    }
]

def format_estimate_time_display(estimate_time):
    """格式化預估到站時間顯示"""
    if estimate_time == 0:
        return "🚆", "**進站中**"
    elif estimate_time <= 60:  # 1分鐘內
        return "🔥", f"**即將進站** ({estimate_time}秒)"
    elif estimate_time <= 180:  # 3分鐘內
        minutes = estimate_time // 60
        seconds = estimate_time % 60
        return "🟡", f"**{minutes}分{seconds}秒**"
    elif estimate_time <= 600:  # 10分鐘內
        minutes = estimate_time // 60
        return "🟢", f"**{minutes}分鐘**"
    else:
        minutes = estimate_time // 60
        return "⏱️", f"**{minutes}分鐘**"

def test_metro_liveboard_formatting():
    """測試捷運電子看板格式化"""
    print("=" * 60)
    print("🚇 捷運電子看板剩餘時間顯示測試")
    print("=" * 60)
    
    # 按路線和車站分組重新整理資料
    lines_data = {}
    for train_data in sample_metro_data:
        line_id = train_data.get('LineID', '未知路線')
        station_id = train_data.get('StationID', '未知車站')
        
        if line_id not in lines_data:
            lines_data[line_id] = {}
        
        if station_id not in lines_data[line_id]:
            lines_data[line_id][station_id] = {
                'StationName': train_data.get('StationName', {}),
                'trains': []
            }
        
        # 添加列車資訊
        lines_data[line_id][station_id]['trains'].append(train_data)
    
    # 路線名稱對照
    line_names = {
        'BL': '💙 板南線',
        'R': '❤️ 淡水信義線',
    }
    
    # 顯示結果
    for line_id, stations_dict in lines_data.items():
        if not stations_dict:
            continue
            
        line_name = line_names.get(line_id, line_id)
        print(f"\n🚇 {line_name}")
        print("-" * 40)
        
        for station_id, station_info in stations_dict.items():
            # 取得車站資訊
            station_name = station_info.get('StationName', {})
            if isinstance(station_name, dict):
                station_name_zh = station_name.get('Zh_tw', '未知車站')
            else:
                station_name_zh = str(station_name)
            
            print(f"\n🚉 **{station_name_zh}**")
            
            # 處理該車站的所有列車
            trains = station_info.get('trains', [])
            for train_data in trains[:2]:  # 最多顯示2班列車
                # 取得列車資訊
                destination = train_data.get('DestinationStationName', {})
                if isinstance(destination, dict):
                    dest_name = destination.get('Zh_tw', '未知目的地')
                else:
                    dest_name = str(destination)
                
                # 取得預估到站時間（秒）
                estimate_time = train_data.get('EstimateTime', 0)
                
                # 計算剩餘時間顯示
                status_emoji, time_info = format_estimate_time_display(estimate_time)
                
                # 組合列車資訊
                train_info = f"{status_emoji} 往**{dest_name}** - {time_info}"
                print(f"    {train_info}")
    
    print("\n" + "=" * 60)
    print("✅ 測試完成！新功能顯示：")
    print("   🚆 進站中 (0秒)")
    print("   🔥 即將進站 (1-60秒)")  
    print("   🟡 分秒顯示 (61-180秒)")
    print("   🟢 分鐘顯示 (181-600秒)")
    print("   ⏱️ 長時間 (>600秒)")
    print("=" * 60)

if __name__ == "__main__":
    test_metro_liveboard_formatting()
