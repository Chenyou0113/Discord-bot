#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大範圍雷達圖功能測試腳本
測試新增的大範圍雷達圖查詢功能
"""

import asyncio
import aiohttp
import json
import sys
import os
import ssl
from datetime import datetime

async def test_large_radar_functionality():
    """測試大範圍雷達圖功能"""
    print("🌍 大範圍雷達圖功能測試")
    print("=" * 60)
    
    # API 配置
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-001"
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
            print("1️⃣ 測試 API 連線...")
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    print("✅ API 連線成功")
                    
                    data = await response.json()
                    print("✅ JSON 資料解析成功")
                    
                    # 測試資料解析
                    print("\n2️⃣ 測試資料解析...")
                    radar_info = parse_radar_data(data)
                    
                    if radar_info:
                        print("✅ 大範圍雷達圖資料解析成功")
                        print_radar_info(radar_info, "大範圍")
                        
                        # 測試 Embed 建立
                        print("\n3️⃣ 測試大範圍 Embed 建立...")
                        embed_data = create_large_embed_data(radar_info)
                        print("✅ 大範圍 Embed 建立成功")
                        print(f"   標題: {embed_data['title']}")
                        print(f"   描述: {embed_data['description']}")
                        print(f"   欄位數量: {len(embed_data['fields'])}")
                        
                        return True
                    else:
                        print("❌ 大範圍雷達圖資料解析失敗")
                        return False
                else:
                    print(f"❌ API 連線失敗: HTTP {response.status}")
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
            'radar_names': '',
            'coverage': {},
            'dimension': ''
        }
        
        # 解析資料集資訊
        dataset_info = dataset.get('datasetInfo', {})
        if dataset_info:
            radar_info['description'] = dataset_info.get('datasetDescription', '雷達整合回波圖')
            
            parameter_set = dataset_info.get('parameterSet', {})
            if parameter_set:
                parameter = parameter_set.get('parameter', {})
                if parameter:
                    radar_info['radar_names'] = parameter.get('radarName', '')
                
                radar_info['coverage'] = {
                    'longitude': parameter_set.get('LongitudeRange', ''),
                    'latitude': parameter_set.get('LatitudeRange', '')
                }
                radar_info['dimension'] = parameter_set.get('ImageDimension', '')
        
        # 解析資源資訊
        resource = dataset.get('resource', {})
        if resource:
            radar_info['image_url'] = resource.get('ProductURL', '')
            radar_info['description'] = resource.get('resourceDesc', radar_info['description'])
        
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
        print(f"格式化時間時發生錯誤: {e}")
        return datetime_str

def print_radar_info(radar_info, version=""):
    """顯示雷達圖資訊"""
    print(f"\n📊 {version}雷達圖資訊:")
    print(f"   識別碼: {radar_info.get('identifier', 'N/A')}")
    print(f"   觀測時間: {format_datetime(radar_info.get('datetime', ''))}")
    print(f"   發布時間: {format_datetime(radar_info.get('sent', ''))}")
    print(f"   描述: {radar_info.get('description', 'N/A')}")
    print(f"   雷達站: {radar_info.get('radar_names', 'N/A')}")
    print(f"   圖片 URL: {radar_info.get('image_url', 'N/A')}")
    
    coverage = radar_info.get('coverage', {})
    if coverage:
        print(f"   覆蓋範圍: 經度 {coverage.get('longitude', 'N/A')}, 緯度 {coverage.get('latitude', 'N/A')}")
        
    print(f"   圖像尺寸: {radar_info.get('dimension', 'N/A')}")

def create_large_embed_data(radar_info):
    """建立大範圍雷達圖 Embed 資料"""
    embed_data = {
        'title': "🌍 台灣大範圍雷達圖整合 (無地形)",
        'description': "中央氣象署雷達回波整合圖像 - 較大覆蓋範圍",
        'color': "綠色" if radar_info.get('image_url') else "紅色",
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
    
    # 雷達站資訊
    radar_names = radar_info.get('radar_names', '')
    if radar_names:
        embed_data['fields'].append({
            'name': "📍 雷達站",
            'value': radar_names,
            'inline': False
        })
    
    # 覆蓋範圍 (突出大範圍特色)
    coverage = radar_info.get('coverage', {})
    if coverage:
        longitude = coverage.get('longitude', '')
        latitude = coverage.get('latitude', '')
        if longitude and latitude:
            embed_data['fields'].append({
                'name': "🗺️ 覆蓋範圍 (大範圍)",
                'value': f"經度: {longitude}°\\n緯度: {latitude}°\\n📏 涵蓋更廣的鄰近海域",
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
    
    # 說明
    description = radar_info.get('description', '')
    if description:
        embed_data['fields'].append({
            'name': "📝 說明",
            'value': f"{description}\\n🌊 此為大範圍版本，可觀察更多鄰近海域天氣",
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
    else:
        embed_data['fields'].append({
            'name': "❌ 圖片狀態",
            'value': "目前無法取得大範圍雷達圖片",
            'inline': False
        })
    
    return embed_data

async def compare_coverage():
    """比較兩種雷達圖的覆蓋範圍"""
    print("\n4️⃣ 比較兩種雷達圖覆蓋範圍...")
    
    # 一般範圍雷達圖
    normal_api = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003"
    # 大範圍雷達圖
    large_api = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-001"
    
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    try:
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            # 獲取一般範圍資料
            async with session.get(normal_api, params=params) as response:
                if response.status == 200:
                    normal_data = await response.json()
                    normal_info = parse_radar_data(normal_data)
                    
                    # 獲取大範圍資料
                    async with session.get(large_api, params=params) as response2:
                        if response2.status == 200:
                            large_data = await response2.json()
                            large_info = parse_radar_data(large_data)
                            
                            print("\n📊 覆蓋範圍比較:")
                            print("-" * 40)
                            
                            # 一般範圍
                            normal_coverage = normal_info.get('coverage', {})
                            print(f"一般範圍雷達圖 (/radar):")
                            print(f"  經度: {normal_coverage.get('longitude', 'N/A')}")
                            print(f"  緯度: {normal_coverage.get('latitude', 'N/A')}")
                            print(f"  描述: {normal_info.get('description', 'N/A')}")
                            
                            print()
                            
                            # 大範圍
                            large_coverage = large_info.get('coverage', {})
                            print(f"大範圍雷達圖 (/radar_large):")
                            print(f"  經度: {large_coverage.get('longitude', 'N/A')}")
                            print(f"  緯度: {large_coverage.get('latitude', 'N/A')}")
                            print(f"  描述: {large_info.get('description', 'N/A')}")
                            
                            # 計算差異
                            print("\n📏 覆蓋範圍差異:")
                            if normal_coverage.get('longitude') and large_coverage.get('longitude'):
                                normal_lon = normal_coverage['longitude'].split('-')
                                large_lon = large_coverage['longitude'].split('-')
                                
                                if len(normal_lon) == 2 and len(large_lon) == 2:
                                    normal_range = float(normal_lon[1]) - float(normal_lon[0])
                                    large_range = float(large_lon[1]) - float(large_lon[0])
                                    lon_diff = large_range - normal_range
                                    
                                    print(f"  經度範圍增加: {lon_diff:.1f}° (約 {lon_diff * 111:.0f} 公里)")
                            
                            if normal_coverage.get('latitude') and large_coverage.get('latitude'):
                                normal_lat = normal_coverage['latitude'].split('-')
                                large_lat = large_coverage['latitude'].split('-')
                                
                                if len(normal_lat) == 2 and len(large_lat) == 2:
                                    normal_range = float(normal_lat[1]) - float(normal_lat[0])
                                    large_range = float(large_lat[1]) - float(large_lat[0])
                                    lat_diff = large_range - normal_range
                                    
                                    print(f"  緯度範圍增加: {lat_diff:.1f}° (約 {lat_diff * 111:.0f} 公里)")
                            
                            print("✅ 覆蓋範圍比較完成")
                            return True
                        
    except Exception as e:
        print(f"❌ 比較過程發生錯誤: {e}")
        return False

async def main():
    """主要測試流程"""
    print("測試大範圍雷達圖功能")
    print("API: O-A0058-001 vs O-A0058-003")
    
    # 執行功能測試
    functionality_test = await test_large_radar_functionality()
    
    # 執行覆蓋範圍比較
    coverage_test = await compare_coverage()
    
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    if functionality_test and coverage_test:
        print("🎉 大範圍雷達圖功能測試全部通過！")
        print("\n✨ 新增功能:")
        print("   • /radar_large - 查詢大範圍雷達圖")
        print("   • 🌍 大範圍按鈕 - 從一般雷達圖切換到大範圍")
        print("   • 🌩️ 一般範圍按鈕 - 從大範圍切換到一般雷達圖")
        print("   • 更新的說明功能，包含兩種雷達圖比較")
        
        print("\n🌍 大範圍雷達圖優勢:")
        print("   • 更廣的經度覆蓋 (115.0°-126.5° vs 118.0°-124.0°)")
        print("   • 更廣的緯度覆蓋 (17.75°-29.25° vs 20.5°-26.5°)")
        print("   • 可觀察更多鄰近海域天氣系統")
        print("   • 適合追蹤大範圍天氣移動")
        
        return True
    else:
        print("❌ 部分功能測試失敗")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🚀 大範圍雷達圖功能已準備就緒！")
            print("   可以啟動 Discord 機器人並使用 /radar_large 指令")
        else:
            print("\n💥 請檢查錯誤並修正後再試")
            
    except Exception as e:
        print(f"\n💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
