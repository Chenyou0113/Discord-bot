#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修正後的水位查詢功能
驗證 'str' object has no attribute 'get' 錯誤是否已解決
"""

import asyncio
import aiohttp
import json
import ssl
import datetime
from datetime import timedelta

async def test_water_level_fix():
    """測試修正後的水位查詢邏輯"""
    print("=" * 60)
    print("測試修正後的水位查詢功能")
    print("=" * 60)
    
    try:
        # API 設定 (使用修正後的 URL)
        api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=2D09DB8B-6A1B-485E-88B5-923A462F475C"
        
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                print(f"狀態碼: {response.status}")
                
                if response.status != 200:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    return
                
                # 處理 UTF-8 BOM 問題
                text = await response.text()
                if text.startswith('\ufeff'):
                    text = text[1:]
                
                try:
                    data = json.loads(text)
                    print(f"✅ JSON 解析成功")
                except json.JSONDecodeError as e:
                    print(f"❌ JSON 解析失敗: {str(e)}")
                    return
                
                # 檢查資料是否為列表格式
                print(f"資料類型: {type(data)}")
                if not isinstance(data, list):
                    print("❌ API 回應格式錯誤 - 不是列表")
                    return
                
                if not data:
                    print("❌ 無水位資料")
                    return
                
                print(f"✅ 資料筆數: {len(data)}")
                
                # 測試資料處理邏輯
                test_city = "台北"
                filtered_records = []
                
                for record in data:
                    # 確保 record 是字典
                    if not isinstance(record, dict):
                        print(f"跳過非字典記錄: {type(record)} - {record}")
                        continue
                        
                    station_name = record.get('StationName', '')
                    county_name = record.get('CountyName', '')
                    river_name = record.get('RiverName', '')
                    
                    # 測試篩選邏輯 (台北市相關測站)
                    if test_city in county_name or test_city in station_name:
                        filtered_records.append(record)
                
                print(f"✅ 篩選出 {len(filtered_records)} 筆 {test_city} 相關資料")
                
                # 測試前5筆資料的處理
                display_records = filtered_records[:5] if filtered_records else data[:5]
                
                print(f"\n📋 測試資料處理 (前{len(display_records)}筆):")
                for i, record in enumerate(display_records, 1):
                    station_name = record.get('StationName', 'N/A')
                    county_name = record.get('CountyName', 'N/A')
                    river_name = record.get('RiverName', 'N/A')
                    water_level = record.get('WaterLevel', 'N/A')
                    obs_time = record.get('ObservationTime', 'N/A')
                    
                    # 格式化水位資料
                    if water_level != 'N/A' and water_level is not None and str(water_level).strip():
                        try:
                            water_level_num = float(water_level)
                            water_level_str = f"{water_level_num:.2f} 公尺"
                        except:
                            water_level_str = str(water_level)
                    else:
                        water_level_str = "無資料"
                    
                    # 格式化時間
                    try:
                        if obs_time != 'N/A' and obs_time:
                            # 處理不同的時間格式
                            if 'T' in obs_time:
                                dt = datetime.datetime.fromisoformat(obs_time.replace('Z', '+00:00'))
                                # 轉換為台灣時間 (UTC+8)
                                dt_tw = dt + timedelta(hours=8)
                                time_str = dt_tw.strftime('%m/%d %H:%M')
                            else:
                                # 假設已經是本地時間
                                time_str = obs_time
                        else:
                            time_str = "無資料"
                    except:
                        time_str = str(obs_time)
                    
                    print(f"\n{i}. {station_name}")
                    print(f"   🏞️ 河川: {river_name}")
                    print(f"   💧 水位: {water_level_str}")
                    print(f"   📍 縣市: {county_name}")
                    print(f"   ⏰ 時間: {time_str}")
                
                print(f"\n✅ 測試完成，所有資料處理正常")
                print(f"📊 統計:")
                print(f"   總資料筆數: {len(data)}")
                print(f"   測試篩選結果: {len(filtered_records)} 筆")
                print(f"   處理測試: {len(display_records)} 筆")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print(f"開始測試時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_water_level_fix())
    except KeyboardInterrupt:
        print("\n測試被中斷")
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    
    print(f"測試結束時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
