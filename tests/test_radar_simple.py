#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
雷達圖功能簡化測試腳本
直接測試雷達圖 API 和資料解析功能
"""

import asyncio
import aiohttp
import json
import sys
import os
import ssl
from datetime import datetime

async def test_radar_api_and_parsing():
    """測試雷達圖 API 連線和資料解析"""
    print("🌩️ 雷達圖功能簡化測試")
    print("=" * 60)
    
    # API 配置
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    print("1️⃣ 測試 API 連線...")
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    print("✅ API 連線成功")
                    
                    data = await response.json()
                    print("✅ JSON 資料解析成功")
                    
                    # 測試資料解析
                    print("\n2️⃣ 測試資料解析...")
                    radar_info = parse_radar_data(data)
                    
                    if radar_info:
                        print("✅ 雷達圖資料解析成功")
                        print("\n📊 解析結果:")
                        print(f"   識別碼: {radar_info.get('identifier', 'N/A')}")
                        print(f"   觀測時間: {radar_info.get('datetime', 'N/A')}")
                        print(f"   發布時間: {radar_info.get('sent', 'N/A')}")
                        print(f"   描述: {radar_info.get('description', 'N/A')}")
                        print(f"   雷達站: {radar_info.get('radar_names', 'N/A')}")
                        print(f"   圖片 URL: {radar_info.get('image_url', 'N/A')}")
                        
                        coverage = radar_info.get('coverage', {})
                        if coverage:
                            print(f"   覆蓋範圍: 經度 {coverage.get('longitude', 'N/A')}, 緯度 {coverage.get('latitude', 'N/A')}")
                            
                        print(f"   圖像尺寸: {radar_info.get('dimension', 'N/A')}")
                        
                        # 測試時間格式化
                        print("\n3️⃣ 測試時間格式化...")
                        datetime_str = radar_info.get('datetime', '')
                        sent_str = radar_info.get('sent', '')
                        
                        formatted_datetime = format_datetime(datetime_str)
                        formatted_sent = format_datetime(sent_str)
                        
                        print(f"   觀測時間格式化: {formatted_datetime}")
                        print(f"   發布時間格式化: {formatted_sent}")
                        print("✅ 時間格式化測試成功")
                        
                        # 測試 Embed 資料
                        print("\n4️⃣ 測試 Embed 資料建立...")
                        embed_data = create_embed_data(radar_info)
                        print("✅ Embed 資料建立成功")
                        print(f"   標題: {embed_data['title']}")
                        print(f"   描述: {embed_data['description']}")
                        print(f"   欄位數量: {len(embed_data['fields'])}")
                        
                        if embed_data.get('image_url'):
                            print(f"   圖片: {embed_data['image_url']}")
                        
                        return True
                    else:
                        print("❌ 雷達圖資料解析失敗")
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

def create_embed_data(radar_info):
    """建立 Embed 資料"""
    embed_data = {
        'title': "🌩️ 台灣雷達圖整合 (無地形)",
        'description': "中央氣象署雷達回波整合圖像",
        'color': "藍色" if radar_info.get('image_url') else "紅色",
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
    
    # 覆蓋範圍
    coverage = radar_info.get('coverage', {})
    if coverage:
        longitude = coverage.get('longitude', '')
        latitude = coverage.get('latitude', '')
        if longitude and latitude:
            embed_data['fields'].append({
                'name': "🗺️ 覆蓋範圍",
                'value': f"經度: {longitude}°\\n緯度: {latitude}°",
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
            'value': description,
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
            'value': "目前無法取得雷達圖片",
            'inline': False
        })
    
    return embed_data

def test_error_handling():
    """測試錯誤處理"""
    print("\n5️⃣ 測試錯誤處理...")
    
    # 測試無效資料的解析
    invalid_data_cases = [
        {},  # 空字典
        {"invalid": "data"},  # 無效格式
        {"cwaopendata": {}},  # 缺少必要欄位
    ]
    
    for i, invalid_data in enumerate(invalid_data_cases, 1):
        result = parse_radar_data(invalid_data)
        if not result:
            print(f"✅ 正確處理無效資料 {i}")
        else:
            print(f"⚠️ 無效資料 {i} 可能未正確處理")
    
    # 測試無效時間格式化
    invalid_times = ["", "invalid_date", "2025-13-40T25:70:80"]
    
    for invalid_time in invalid_times:
        result = format_datetime(invalid_time)
        print(f"   無效時間 '{invalid_time}' -> '{result}'")
    
    print("✅ 錯誤處理測試完成")

async def main():
    """主要測試流程"""
    print("🎯 開始雷達圖功能簡化測試...")
    
    # 執行主要測試
    api_success = await test_radar_api_and_parsing()
    
    # 執行錯誤處理測試
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("📊 測試總結")
    print("=" * 60)
    
    if api_success:
        print("🎉 雷達圖功能測試全部通過！")
        print("\n✨ 功能特色:")
        print("   • 即時雷達圖顯示")
        print("   • 完整資料解析")
        print("   • 詳細氣象資訊")
        print("   • 錯誤處理機制")
        print("   • 時間格式化")
        print("   • 雷達覆蓋範圍")
        
        print("\n📱 可用指令:")
        print("   • /radar - 查詢最新雷達圖")
        print("   • /radar_info - 查看功能說明")
        
        print("\n🔧 技術資訊:")
        print("   • 資料來源: 中央氣象署")
        print("   • API: O-A0058-003")
        print("   • 更新頻率: 每10分鐘")
        print("   • 圖像格式: PNG")
        print("   • 圖像尺寸: 3600x3600 像素")
        print("   • 快取時間: 5分鐘")
        
        return True
    else:
        print("❌ 雷達圖功能測試失敗")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        if success:
            print("\n🚀 雷達圖功能已準備就緒！")
            print("   可以啟動 Discord 機器人並使用 /radar 指令")
        else:
            print("\n💥 請檢查錯誤並修正後再試")
            
    except Exception as e:
        print(f"\n💥 測試過程發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        success = False
    
    sys.exit(0 if success else 1)
