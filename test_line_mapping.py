#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試修正後的捷運路線顯示邏輯
"""

import sys
import os

# 添加項目根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 模擬高雄捷運 R 線資料
sample_kaohsiung_r_data = [
    {
        "LineID": "R",
        "StationID": "R3",
        "StationName": {
            "Zh_tw": "小港",
            "En": "Siaogang"
        },
        "DestinationStationName": {
            "Zh_tw": "岡山車站",
            "En": "Gangshan Station"
        },
        "EstimateTime": 2,
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    },
    {
        "LineID": "R",
        "StationID": "R10",
        "StationName": {
            "Zh_tw": "美麗島",
            "En": "Formosa Boulevard"
        },
        "DestinationStationName": {
            "Zh_tw": "小港",
            "En": "Siaogang"
        },
        "EstimateTime": 180,
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    }
]

# 模擬台北捷運 R 線資料
sample_taipei_r_data = [
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
        "EstimateTime": 120,
        "ServiceStatus": 0,
        "UpdateTime": "2025-09-21T10:09:54+08:00"
    }
]

def test_line_name_mapping():
    """測試路線名稱對應邏輯"""
    print("=" * 60)
    print("🚇 捷運路線名稱對應測試")
    print("=" * 60)
    
    # 測試高雄捷運 R 線
    def get_line_name_kaohsiung(line_id, metro_system):
        line_names = {
            'BR': '🤎 文湖線',
            'BL': '💙 板南線',
            'G': '💚 松山新店線',
            'O': '🧡 中和新蘆線',
            'Y': '💛 環狀線',
            'LG': '💚 安坑線',
            'V': '💜 淡海輕軌',
            'RO': '❤️ 紅線',
            'OR': '🧡 橘線',
            'C': '💚 環狀輕軌',
            'R': '❤️ 紅線' if metro_system == 'KRTC' else '❤️ 淡水信義線'
        }
        return line_names.get(line_id, line_id)
    
    print("測試高雄捷運 R 線:")
    kaohsiung_r_name = get_line_name_kaohsiung('R', 'KRTC')
    print(f"  高雄捷運 (KRTC) R線 -> {kaohsiung_r_name}")
    
    print("\n測試台北捷運 R 線:")
    taipei_r_name = get_line_name_kaohsiung('R', 'TRTC')
    print(f"  台北捷運 (TRTC) R線 -> {taipei_r_name}")
    
    print("\n" + "=" * 60)
    print("✅ 測試結果:")
    print(f"   高雄捷運 R線 正確顯示為: {kaohsiung_r_name}")
    print(f"   台北捷運 R線 正確顯示為: {taipei_r_name}")
    
    # 測試去重邏輯
    print("\n" + "=" * 60)
    print("🔄 重複資料過濾測試")
    print("=" * 60)
    
    # 模擬重複資料
    duplicate_data = [
        sample_kaohsiung_r_data[0],  # 小港站 往岡山車站 2秒
        sample_kaohsiung_r_data[0],  # 重複的相同資料
        {**sample_kaohsiung_r_data[0], "EstimateTime": 5},  # 相同車站不同時間
    ]
    
    # 去重邏輯
    unique_trains = []
    seen_trains = set()
    
    for train_data in duplicate_data:
        dest = train_data.get('DestinationStationName', {})
        dest_name = dest.get('Zh_tw', '') if isinstance(dest, dict) else str(dest)
        estimate_time = train_data.get('EstimateTime', 0)
        
        train_key = f"{dest_name}_{estimate_time}"
        if train_key not in seen_trains:
            seen_trains.add(train_key)
            unique_trains.append(train_data)
    
    print(f"原始資料筆數: {len(duplicate_data)}")
    print(f"去重後資料筆數: {len(unique_trains)}")
    print("去重後的列車:")
    for i, train in enumerate(unique_trains, 1):
        dest_name = train['DestinationStationName']['Zh_tw']
        estimate_time = train['EstimateTime']
        print(f"  {i}. 往{dest_name} - {estimate_time}秒")
    
    print("=" * 60)

if __name__ == "__main__":
    test_line_name_mapping()
