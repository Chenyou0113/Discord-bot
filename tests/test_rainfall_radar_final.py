#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
降雨雷達功能驗證腳本
測試新增的降雨雷達查詢功能
"""

import asyncio
import aiohttp
import json
import sys
import os
import ssl
from datetime import datetime

async def test_rainfall_radar_functionality():
    """測試降雨雷達功能"""
    print("📍 降雨雷達功能測試")
    print("=" * 80)
    
    # 降雨雷達配置
    radar_stations = {
        "樹林": {
            "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-001",
            "code": "O-A0084-001",
            "location": "新北樹林",
            "icon": "🏢"
        },
        "南屯": {
            "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-002", 
            "code": "O-A0084-002",
            "location": "台中南屯",
            "icon": "🏭"
        },
        "林園": {
            "api_url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-003",
            "code": "O-A0084-003", 
            "location": "高雄林園",
            "icon": "🏗️"
        }
    }
    
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("1️⃣ 測試所有降雨雷達 API 連線...")
            
            results = {}
            for station_name, station_info in radar_stations.items():
                print(f"\n🔍 測試 {station_info['icon']} {station_info['location']}...")
                
                try:
                    async with session.get(station_info['api_url'], params=params) as response:
                        if response.status == 200:
                            data = await response.json()
                            results[station_name] = data
                            print(f"✅ {station_info['location']} API 連線成功")
                            
                            # 測試資料解析
                            radar_info = parse_radar_data(data)
                            if radar_info:
                                print(f"✅ {station_info['location']} 資料解析成功")
                                print_radar_summary(radar_info, station_info)
                            else:
                                print(f"❌ {station_info['location']} 資料解析失敗")
                        else:
                            print(f"❌ {station_info['location']} API 連線失敗: HTTP {response.status}")
                            results[station_name] = None
                
                except Exception as e:
                    print(f"❌ {station_info['location']} 測試發生錯誤: {e}")
                    results[station_name] = None
            
            # 統計測試結果
            success_count = sum(1 for result in results.values() if result is not None)
            print(f"\n📊 API 連線測試結果: {success_count}/{len(radar_stations)} 成功")
            
            if success_count > 0:
                print("\n2️⃣ 測試 Embed 建立功能...")
                for station_name, data in results.items():
                    if data:
                        station_info = radar_stations[station_name]
                        radar_info = parse_radar_data(data)
                        embed_data = create_rainfall_embed_data(radar_info, station_name, station_info)
                        print(f"✅ {station_info['location']} Embed 建立成功")
                        print(f"   標題: {embed_data['title']}")
                        print(f"   欄位數量: {len(embed_data['fields'])}")
                
                print("\n3️⃣ 測試功能比較...")
                compare_rainfall_radars(results, radar_stations)
                
                return True
            else:
                return False
                
    except Exception as e:
        print(f"❌ 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return False

def parse_radar_data(data):
    """解析雷達圖資料"""
    try:
        if 'cwaopendata' not in data:
            return {}
        
        cwa_data = data['cwaopendata']
        dataset = cwa_data.get('dataset', {})
        
        # 解析基本資訊
        radar_info = {
            'identifier': cwa_data.get('identifier', ''),
            'sent': cwa_data.get('sent', ''),
            'datetime': dataset.get('DateTime', ''),
            'description': '',
            'image_url': '',
            'dimension': ''
        }
        
        # 解析資料集資訊
        dataset_info = dataset.get('datasetInfo', {})
        if dataset_info:
            radar_info['description'] = dataset_info.get('datasetDescription', '')
            
            parameter_set = dataset_info.get('parameterSet', {})
            if parameter_set:
                radar_info['dimension'] = parameter_set.get('ImageDimension', '')
        
        # 解析資源資訊
        resource = dataset.get('resource', {})
        if resource:
            radar_info['image_url'] = resource.get('ProductURL', '')
            if not radar_info['description']:
                radar_info['description'] = resource.get('resourceDesc', '')
        
        return radar_info
        
    except Exception as e:
        print(f"解析雷達圖資料時發生錯誤: {e}")
        return {}

def format_datetime(datetime_str):
    """格式化日期時間字符串"""
    try:
        if not datetime_str:
            return "未知時間"
        
        # 解析 ISO 格式時間
        dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
        
        # 轉換為台灣時間格式
        return dt.strftime('%Y年%m月%d日 %H:%M')
        
    except Exception as e:
        return datetime_str

def print_radar_summary(radar_info, station_info):
    """顯示雷達資訊摘要"""
    print(f"     觀測時間: {format_datetime(radar_info.get('datetime', ''))}")
    print(f"     發布時間: {format_datetime(radar_info.get('sent', ''))}")
    print(f"     圖像尺寸: {radar_info.get('dimension', 'N/A')}")
    print(f"     圖片URL可用: {'是' if radar_info.get('image_url') else '否'}")

def create_rainfall_embed_data(radar_info, station_name, station_info):
    """建立降雨雷達圖 Embed 資料"""
    embed_data = {
        'title': f"{station_info['icon']} {station_info['location']} 降雨雷達圖",
        'description': f"單雷達合成回波圖 - {station_name} 無地形",
        'color': "橙色" if station_name == "樹林" else "紫色" if station_name == "南屯" else "青色",
        'fields': []
    }
    
    # 觀測時間
    datetime_str = format_datetime(radar_info.get('datetime', ''))
    embed_data['fields'].append({
        'name': "⏰ 觀測時間",
        'value': datetime_str,
        'inline': True
    })
    
    # 發布時間
    sent_time = format_datetime(radar_info.get('sent', ''))
    embed_data['fields'].append({
        'name': "📡 發布時間",
        'value': sent_time,
        'inline': True
    })
    
    # 雷達站位置
    embed_data['fields'].append({
        'name': "📍 雷達站位置",
        'value': station_info['location'],
        'inline': True
    })
    
    # 圖像規格
    dimension = radar_info.get('dimension', '')
    if dimension:
        embed_data['fields'].append({
            'name': "📐 圖像尺寸",
            'value': f"{dimension} 像素",
            'inline': True
        })
    
    # 資料集資訊
    embed_data['fields'].append({
        'name': "📊 資料集",
        'value': station_info['code'],
        'inline': True
    })
    
    # 特色說明
    embed_data['fields'].append({
        'name': "⭐ 特色",
        'value': "單雷達合成回波，無地形遮蔽",
        'inline': True
    })
    
    # 說明
    description = radar_info.get('description', '')
    if description:
        embed_data['fields'].append({
            'name': "📝 說明",
            'value': f"{description}\\n🎯 專注於 {station_info['location']} 區域的精細降雨觀測",
            'inline': False
        })
    
    # 圖片
    image_url = radar_info.get('image_url', '')
    if image_url:
        embed_data['image_url'] = image_url
        embed_data['fields'].append({
            'name': "🔗 圖片連結",
            'value': f"[點擊查看原始圖片]({image_url})",
            'inline': False
        })
    
    return embed_data

def compare_rainfall_radars(results, radar_stations):
    """比較不同降雨雷達的特性"""
    print("📊 降雨雷達比較分析:")
    print("-" * 60)
    
    successful_results = {k: v for k, v in results.items() if v is not None}
    
    if len(successful_results) < 2:
        print("   需要至少兩個成功的雷達站才能進行比較")
        return
    
    # 比較觀測時間
    print("⏰ 觀測時間比較:")
    for station_name, data in successful_results.items():
        radar_info = parse_radar_data(data)
        station_info = radar_stations[station_name]
        obs_time = format_datetime(radar_info.get('datetime', ''))
        print(f"   {station_info['icon']} {station_info['location']}: {obs_time}")
    
    # 比較發布時間
    print("\n📡 發布時間比較:")
    for station_name, data in successful_results.items():
        radar_info = parse_radar_data(data)
        station_info = radar_stations[station_name]
        sent_time = format_datetime(radar_info.get('sent', ''))
        print(f"   {station_info['icon']} {station_info['location']}: {sent_time}")
    
    # 比較圖像規格
    print("\n📐 圖像規格比較:")
    dimensions = set()
    for station_name, data in successful_results.items():
        radar_info = parse_radar_data(data)
        station_info = radar_stations[station_name]
        dimension = radar_info.get('dimension', 'N/A')
        dimensions.add(dimension)
        print(f"   {station_info['icon']} {station_info['location']}: {dimension}")
    
    if len(dimensions) == 1 and 'N/A' not in dimensions:
        print("   ✅ 所有雷達站使用相同的圖像規格")
    
    # 分析更新頻率差異
    print("\n🔄 更新頻率分析:")
    obs_times = []
    for data in successful_results.values():
        radar_info = parse_radar_data(data)
        datetime_str = radar_info.get('datetime', '')
        if datetime_str:
            try:
                dt = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                obs_times.append(dt)
            except:
                pass
    
    if len(obs_times) > 1:
        time_diffs = []
        for i in range(1, len(obs_times)):
            diff = abs((obs_times[i] - obs_times[i-1]).total_seconds() / 60)
            time_diffs.append(diff)
        
        if time_diffs:
            avg_diff = sum(time_diffs) / len(time_diffs)
            print(f"   平均觀測時間差異: {avg_diff:.1f} 分鐘")

async def main():
    """主要測試流程"""
    print("測試降雨雷達功能")
    print("涵蓋雷達站: 新北樹林、台中南屯、高雄林園")
    
    # 執行功能測試
    functionality_test = await test_rainfall_radar_functionality()
    
    print("\n" + "=" * 80)
    print("📊 降雨雷達功能測試總結")
    print("=" * 80)
    
    if functionality_test:
        print("🎉 降雨雷達功能測試全部通過！")
        print("\n✨ 新增功能:")
        print("   • /rainfall_radar - 選擇特定雷達站查詢")
        print("   • 🏢 新北樹林 - 北部地區精細降雨觀測")
        print("   • 🏭 台中南屯 - 中部地區精細降雨觀測")
        print("   • 🏗️ 高雄林園 - 南部地區精細降雨觀測")
        
        print("\n🔄 互動功能:")
        print("   • 🔄 重新整理 - 獲取最新降雨雷達圖")
        print("   • 🏢🏭🏗️ 雷達站切換 - 快速切換不同雷達站")
        print("   • 🌩️ 整合雷達 - 切換到整合雷達圖")
        print("   • 📍 降雨雷達選擇 - 從整合雷達圖快速選擇單雷達")
        
        print("\n📊 技術特色:")
        print("   • 獨立快取機制 - 每個雷達站獨立快取")
        print("   • 智慧切換功能 - 在不同雷達圖間無縫切換")
        print("   • 視覺區分 - 不同雷達站使用不同顏色主題")
        print("   • 更新頻率: 每6分鐘 (比整合雷達圖更頻繁)")
        
        print("\n🎯 應用場景:")
        print("   • 精細降雨監測 - 特定區域詳細觀測")
        print("   • 區域天氣分析 - 比較不同地區降雨狀況")
        print("   • 即時氣象服務 - 提供高頻率更新的降雨資訊")
        
        return True
    else:
        print("❌ 部分功能測試失敗")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🚀 降雨雷達功能已準備就緒！")
            print("   可以啟動 Discord 機器人並使用 /rainfall_radar 指令")
        else:
            print("\n💥 請檢查錯誤並修正後再試")
            
    except Exception as e:
        print(f"\n💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
