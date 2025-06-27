#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
氣象測站基本資料查詢測試腳本
測試新增的 /station_info 指令功能

作者: Discord Bot Project
日期: 2025-01-05
"""

import sys
import os
import asyncio
import aiohttp
import ssl
import json
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_api_connection():
    """測試氣象測站基本資料 API 連線"""
    print("=" * 60)
    print("🧪 氣象測站基本資料 API 連線測試")
    print("=" * 60)
    
    api_url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/C-B0074-001"
    api_key = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    print(f"📡 API 端點: {api_url}")
    print(f"🔑 授權金鑰: {api_key[:20]}...")
    print("-" * 60)
    
    return api_url, api_key

async def fetch_station_info_data(api_url: str, api_key: str):
    """非同步獲取氣象測站基本資料"""
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        params = {
            'Authorization': api_key,
            'format': 'JSON'
        }
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("🔄 正在發送 API 請求...")
            async with session.get(api_url, params=params, timeout=30) as response:
                print(f"📊 HTTP 狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    print("✅ API 請求成功")
                    return data
                else:
                    print(f"❌ API 請求失敗: HTTP {response.status}")
                    text = await response.text()
                    print(f"回應內容: {text[:200]}...")
                    return None
                    
    except Exception as e:
        print(f"❌ API 請求發生錯誤: {str(e)}")
        return None

def analyze_station_data(data):
    """分析氣象測站資料結構"""
    print("\n" + "=" * 60)
    print("📊 氣象測站資料結構分析")
    print("=" * 60)
    
    if not data:
        print("❌ 沒有資料可分析")
        return
    
    print("🔍 資料結構分析:")
    print(f"  根層級鍵值: {list(data.keys())}")
    
    if 'success' in data:
        print(f"  成功狀態: {data['success']}")
    
    if 'result' in data:
        result = data['result']
        print(f"  結果結構: {list(result.keys())}")
        
        if 'resource_id' in result:
            print(f"  資源ID: {result['resource_id']}")
    
    if 'records' in data:
        records = data['records']
        print(f"  記錄結構: {list(records.keys())}")
        
        if 'data' in records:
            data_section = records['data']
            print(f"  資料區結構: {list(data_section.keys())}")
            
            if 'stationStatus' in data_section:
                station_status = data_section['stationStatus']
                print(f"  測站狀態結構: {list(station_status.keys())}")
                
                if 'station' in station_status:
                    stations = station_status['station']
                    print(f"  測站數量: {len(stations)}")
                    
                    if stations:
                        # 分析第一個測站的結構
                        first_station = stations[0]
                        print(f"  測站欄位: {list(first_station.keys())}")
                        
                        # 顯示測站狀態統計
                        status_counts = {}
                        county_counts = {}
                        
                        for station in stations:
                            status = station.get('status', '未知')
                            county = station.get('CountyName', '未知')
                            
                            status_counts[status] = status_counts.get(status, 0) + 1
                            county_counts[county] = county_counts.get(county, 0) + 1
                        
                        print("\n📊 測站狀態統計:")
                        for status, count in sorted(status_counts.items()):
                            print(f"  {status}: {count} 個")
                        
                        print("\n🗺️ 縣市分布統計 (前10名):")
                        sorted_counties = sorted(county_counts.items(), key=lambda x: x[1], reverse=True)
                        for county, count in sorted_counties[:10]:
                            print(f"  {county}: {count} 個測站")
                        
                        return stations
    
    return None

def demonstrate_station_queries(stations):
    """示範測站查詢功能"""
    print("\n" + "=" * 60)
    print("🎯 測站查詢功能示範")
    print("=" * 60)
    
    if not stations:
        print("❌ 沒有測站資料可示範")
        return
    
    # 示範1：按測站ID查詢
    print("1️⃣ 按測站ID查詢示範:")
    sample_station = stations[0]
    station_id = sample_station.get('StationID', '')
    station_name = sample_station.get('StationName', '')
    print(f"   範例: /station_info station_id:{station_id}")
    print(f"   結果: {station_name} ({station_id}) 的詳細資料")
    
    # 示範2：按縣市查詢
    print("\n2️⃣ 按縣市查詢示範:")
    county_stations = {}
    for station in stations:
        county = station.get('CountyName', '')
        if county:
            if county not in county_stations:
                county_stations[county] = []
            county_stations[county].append(station)
    
    # 選擇有多個測站的縣市
    for county, county_station_list in county_stations.items():
        if len(county_station_list) >= 2:
            print(f"   範例: /station_info county:{county}")
            print(f"   結果: {county} 的 {len(county_station_list)} 個測站列表")
            break
    
    # 示範3：按狀態篩選
    print("\n3️⃣ 按狀態篩選示範:")
    active_count = sum(1 for s in stations if s.get('status') == '現存測站')
    inactive_count = sum(1 for s in stations if s.get('status') == '已撤銷')
    
    print(f"   範例: /station_info status:現存測站")
    print(f"   結果: {active_count} 個現存測站")
    print(f"   範例: /station_info status:已撤銷")
    print(f"   結果: {inactive_count} 個已撤銷測站")
    
    # 示範4：組合查詢
    print("\n4️⃣ 組合查詢示範:")
    print("   範例: /station_info county:臺北市 status:現存測站")
    print("   結果: 臺北市的現存測站列表")

def create_sample_embed_data(stations):
    """創建範例嵌入資料展示"""
    print("\n" + "=" * 60)
    print("📋 Discord Embed 顯示效果預覽")
    print("=" * 60)
    
    if not stations:
        print("❌ 沒有測站資料可展示")
        return
    
    # 選擇一個有完整資料的測站
    sample_station = None
    for station in stations:
        if (station.get('StationName') and station.get('StationID') and 
            station.get('CountyName') and station.get('Location')):
            sample_station = station
            break
    
    if not sample_station:
        sample_station = stations[0]
    
    print("📱 單一測站詳細資料顯示效果:")
    print("-" * 40)
    
    station_name = sample_station.get('StationName', '未知測站')
    station_id = sample_station.get('StationID', '未知')
    station_name_en = sample_station.get('StationNameEN', 'Unknown')
    status = sample_station.get('status', '未知狀態')
    county_name = sample_station.get('CountyName', 'N/A')
    location = sample_station.get('Location', 'N/A')
    altitude = sample_station.get('StationAltitude', 'N/A')
    start_date = sample_station.get('StationStartDate', 'N/A')
    end_date = sample_station.get('StationEndDate', 'N/A')
    notes = sample_station.get('Notes', '')
    
    status_emoji = "🟢" if status == "現存測站" else "🔴"
    
    print(f"🏢 {station_name} 測站資料")
    print(f"測站代碼: {station_id} | 英文名稱: {station_name_en}")
    print()
    print(f"📊 狀態: {status_emoji} {status}")
    print(f"📍 縣市: {county_name}")
    if altitude != 'N/A':
        print(f"⛰️ 海拔高度: {altitude} 公尺")
    if location != 'N/A':
        print(f"🏠 詳細地址: {location}")
    if start_date != 'N/A':
        date_info = f"📅 營運時間: 開始 {start_date}"
        if end_date and end_date != 'N/A':
            date_info += f" | 結束 {end_date}"
        elif status == "現存測站":
            date_info += " | 持續營運中"
        print(date_info)
    if notes:
        print(f"📝 備註: {notes[:100]}{'...' if len(notes) > 100 else ''}")
    
    print("\n" + "-" * 40)
    print("📱 測站列表顯示效果:")
    print("-" * 40)
    
    # 顯示前3個測站的列表效果
    print(f"🏢 氣象測站基本資料 - 範例縣市")
    print(f"找到 X 個測站")
    print()
    
    for i, station in enumerate(stations[:3]):
        name = station.get('StationName', '未知測站')
        sid = station.get('StationID', '未知')
        st = station.get('status', '未知狀態')
        county = station.get('CountyName', 'N/A')
        alt = station.get('StationAltitude', 'N/A')
        start = station.get('StationStartDate', 'N/A')
        
        emoji = "🟢" if st == "現存測站" else "🔴"
        alt_str = f" | 🏔️ {alt}m" if alt != 'N/A' else ""
        date_str = f" | 📅 自 {start}" if start != 'N/A' else ""
        
        print(f"{emoji} {name} ({sid})")
        print(f"📍 {county}{alt_str}{date_str}")
        if i < 2:
            print()

async def main():
    """主測試函數"""
    print("🚀 開始氣象測站基本資料查詢功能測試")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試 API 連線
    api_url, api_key = test_api_connection()
    
    # 獲取資料
    print("\n📡 正在獲取氣象測站基本資料...")
    data = await fetch_station_info_data(api_url, api_key)
    
    # 分析資料
    stations = analyze_station_data(data)
    
    # 示範查詢功能
    if stations:
        demonstrate_station_queries(stations)
        create_sample_embed_data(stations)
    
    print("\n" + "=" * 60)
    print("🎉 測試完成！新功能總結")
    print("=" * 60)
    print("✅ 新增指令: /station_info")
    print("📋 功能說明:")
    print("   • 查詢氣象測站基本資料（有人測站）")
    print("   • 支援按測站代碼、縣市、狀態篩選")
    print("   • 顯示詳細測站資訊（位置、海拔、營運時間等）")
    print("   • 支援分頁瀏覽多個測站")
    print("   • 區分現存測站和已撤銷測站")
    print()
    print("🎯 使用方式:")
    print("   /station_info station_id:466920  # 查詢特定測站")
    print("   /station_info county:臺北市      # 查詢特定縣市測站")
    print("   /station_info status:現存測站     # 查詢現存測站")
    print("   /station_info county:臺北市 status:現存測站  # 組合查詢")
    print()
    print("💡 提示: 建議重啟機器人以載入新功能")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️ 測試被用戶中止")
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {str(e)}")
    
    print("\n👋 測試結束")
