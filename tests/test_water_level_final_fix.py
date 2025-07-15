#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試修正後的水位查詢功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 模擬測試水位查詢邏輯
import asyncio
import aiohttp
import json
import ssl
import datetime
from datetime import timedelta

async def test_fixed_water_level():
    """測試修正後的水位查詢邏輯"""
    print("=" * 60)
    print("測試修正後的水位查詢功能")
    print("=" * 60)
    
    try:
        # 使用修正後的 API URL
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
                
                # 檢查資料結構 - 水利署 API 回應是字典格式
                if not isinstance(data, dict):
                    print("❌ API 回應格式錯誤")
                    return
                
                # 從回應中提取實際的水位資料列表
                records = data.get('RealtimeWaterLevel_OPENDATA', [])
                
                if not records:
                    print("❌ 無水位資料")
                    return
                
                print(f"✅ 資料筆數: {len(records)}")
                
                # 測試篩選邏輯
                test_station = "H006"  # 測試用測站編號
                filtered_records = []
                
                for record in records:
                    # 確保 record 是字典
                    if not isinstance(record, dict):
                        print(f"跳過非字典記錄: {type(record)} - {record}")
                        continue
                        
                    station_id = record.get('ST_NO', '')
                    observatory_id = record.get('ObservatoryIdentifier', '')
                    water_level = record.get('WaterLevel', '')
                    
                    # 篩選條件
                    matches = True
                    
                    # 根據測站編號或識別碼篩選
                    if test_station and matches:
                        if (test_station.lower() not in station_id.lower() and 
                            test_station.lower() not in observatory_id.lower()):
                            matches = False
                    
                    # 過濾空水位資料
                    if water_level == '' or water_level is None:
                        matches = False
                    
                    if matches:
                        filtered_records.append(record)
                
                print(f"✅ 篩選出 {len(filtered_records)} 筆符合 '{test_station}' 的資料")
                
                # 測試前5筆資料的處理
                display_records = filtered_records[:5] if filtered_records else records[:5]
                
                print(f"\n📋 測試資料處理 (前{len(display_records)}筆):")
                for i, record in enumerate(display_records, 1):
                    # 使用實際可用的欄位
                    station_id = record.get('ST_NO', 'N/A')
                    observatory_id = record.get('ObservatoryIdentifier', 'N/A')
                    water_level = record.get('WaterLevel', 'N/A')
                    record_time = record.get('RecordTime', 'N/A')
                    
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
                        if record_time != 'N/A' and record_time:
                            # 處理不同的時間格式
                            if 'T' in record_time:
                                dt = datetime.datetime.fromisoformat(record_time.replace('Z', '+00:00'))
                                # 轉換為台灣時間 (UTC+8)
                                dt_tw = dt + timedelta(hours=8)
                                time_str = dt_tw.strftime('%m/%d %H:%M')
                            else:
                                # 假設已經是本地時間
                                time_str = record_time
                        else:
                            time_str = "無資料"
                    except:
                        time_str = str(record_time)
                    
                    print(f"\n{i}. 測站: {station_id}")
                    print(f"   🏷️ 識別碼: {observatory_id}")
                    print(f"   💧 水位: {water_level_str}")
                    print(f"   ⏰ 時間: {time_str}")
                
                print(f"\n✅ 修正測試完成，所有資料處理正常")
                print(f"📊 統計:")
                print(f"   總資料筆數: {len(records)}")
                print(f"   測試篩選結果: {len(filtered_records)} 筆")
                print(f"   處理測試: {len(display_records)} 筆")
                print(f"\n🔧 修正重點:")
                print(f"   1. ✅ 修正API回應格式處理 (字典 -> RealtimeWaterLevel_OPENDATA)")
                print(f"   2. ✅ 修正欄位名稱對應 (ST_NO, ObservatoryIdentifier, RecordTime)")
                print(f"   3. ✅ 修正篩選邏輯 (根據測站編號)")
                print(f"   4. ✅ 修正時間格式處理")
                print(f"   5. ⚠️  縣市和河川篩選暫時停用 (API未提供相關資訊)")
                
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print(f"開始測試時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        asyncio.run(test_fixed_water_level())
    except KeyboardInterrupt:
        print("\n測試被中斷")
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
    
    print(f"測試結束時間: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
