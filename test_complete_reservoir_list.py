#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水庫 API 並獲取完整水庫列表和容量資訊
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def test_reservoir_list_with_capacity():
    """測試水庫列表和容量資訊"""
    print("=" * 60)
    print("測試水庫列表和容量資訊")
    print("=" * 60)
    
    # 測試水庫水情 API
    api_url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-AA31-11B1B124530F"
    
    try:
        # 設定 SSL 上下文
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            print("正在請求水庫水情 API...")
            
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    # 處理 UTF-8 BOM 問題
                    raw_text = await response.text()
                    if raw_text.startswith('\ufeff'):
                        raw_text = raw_text[1:]
                    
                    data = json.loads(raw_text)
                    
                    print(f"✅ 成功獲取水庫資料")
                    print(f"📊 資料類型: {type(data)}")
                    print(f"📊 資料長度: {len(data) if isinstance(data, list) else 'N/A'}")
                    print("-" * 50)
                    
                    # 檢查資料結構
                    if isinstance(data, list) and len(data) > 0:
                        print("🔍 檢查第一筆資料結構:")
                        first_item = data[0]
                        if isinstance(first_item, dict):
                            print("欄位列表:")
                            for key in first_item.keys():
                                print(f"  - {key}")
                        else:
                            print(f"第一筆資料類型: {type(first_item)}")
                            print(f"第一筆資料內容: {first_item}")
                    elif isinstance(data, dict):
                        print("🔍 資料是字典格式，檢查結構:")
                        print("頂層鍵值:")
                        for key in data.keys():
                            print(f"  - {key}")
                    
                    if data and len(data) > 0:
                        # 分析水庫容量資訊
                        print("🏞️ 水庫容量資訊分析:")
                        print("-" * 30)
                        
                        # 正確解析資料結構
                        reservoir_data = None
                        if isinstance(data, dict):
                            # 如果是字典，查找包含水庫資料的鍵
                            if 'ReservoirConditionData_OPENDATA' in data:
                                reservoir_data = data['ReservoirConditionData_OPENDATA']
                            else:
                                # 嘗試找第一個包含列表的值
                                for key, value in data.items():
                                    if isinstance(value, list):
                                        reservoir_data = value
                                        break
                        elif isinstance(data, list):
                            reservoir_data = data
                        
                        if not reservoir_data:
                            print("❌ 無法找到水庫資料")
                            return
                        
                        print(f"找到 {len(reservoir_data)} 個水庫")
                        
                        # 檢查第一個水庫的資料結構
                        if reservoir_data and len(reservoir_data) > 0:
                            print("\n🔍 第一個水庫的資料結構:")
                            first_reservoir = reservoir_data[0]
                            if isinstance(first_reservoir, dict):
                                print("欄位名稱和值:")
                                for key, value in first_reservoir.items():
                                    print(f"  {key}: {value} ({type(value).__name__})")
                            else:
                                print(f"第一個水庫資料類型: {type(first_reservoir)}")
                        
                        # 收集所有水庫資訊
                        reservoirs_info = []
                        
                        for item in reservoir_data:
                            if isinstance(item, dict):
                                # 使用正確的欄位名稱
                                reservoir_id = item.get('ReservoirIdentifier', 'N/A')
                                effective_capacity = item.get('EffectiveWaterStorageCapacity', 'N/A')
                                water_level = item.get('WaterLevel', 'N/A')
                                inflow = item.get('InflowDischarge', 'N/A')
                                outflow = item.get('TotalOutflow', 'N/A')
                                obs_time = item.get('ObservationTime', 'N/A')
                                
                                # 使用簡單的水庫名稱
                                reservoir_name = f"水庫{reservoir_id}"
                                
                                reservoirs_info.append({
                                    'id': reservoir_id,
                                    'name': reservoir_name,
                                    'effective_capacity': effective_capacity,
                                    'water_level': water_level,
                                    'inflow': inflow,
                                    'outflow': outflow,
                                    'obs_time': obs_time
                                })
                            else:
                                print(f"警告: 項目不是字典格式: {type(item)}")
                        
                        if not reservoirs_info:
                            print("❌ 沒有有效的水庫資料")
                            return
                        
                        # 按容量排序（由大到小）
                        def get_capacity_for_sort(reservoir):
                            try:
                                if reservoir['effective_capacity'] != 'N/A' and reservoir['effective_capacity']:
                                    return float(reservoir['effective_capacity'])
                                else:
                                    return 0
                            except:
                                return 0
                        
                        reservoirs_info.sort(key=get_capacity_for_sort, reverse=True)
                        
                        # 顯示前 20 大水庫
                        print("🏆 台灣前 20 大水庫（按有效容量排序）:")
                        print("-" * 80)
                        print(f"{'排名':<4} {'水庫ID':<8} {'水庫名稱':<15} {'有效容量(萬m³)':<15} {'目前水位(m)':<12} {'入流量':<8}")
                        print("-" * 80)
                        
                        for i, reservoir in enumerate(reservoirs_info[:20], 1):
                            reservoir_id = reservoir['id'][:7]
                            name = reservoir['name'][:12] + '...' if len(reservoir['name']) > 12 else reservoir['name']
                            capacity = reservoir['effective_capacity'][:12] if reservoir['effective_capacity'] != 'N/A' else 'N/A'
                            water_level = reservoir['water_level'][:10] if reservoir['water_level'] != 'N/A' else 'N/A'
                            inflow = reservoir['inflow'][:6] if reservoir['inflow'] != 'N/A' else 'N/A'
                            
                            print(f"{i:<4} {reservoir_id:<8} {name:<15} {capacity:<15} {water_level:<12} {inflow:<8}")
                        
                        # 建立水庫 ID 到名稱的對應表（用於更新 Discord 指令）
                        print(f"\n📋 可建立的水庫 ID 對應表（前 30 個）:")
                        print("-" * 50)
                        for i, reservoir in enumerate(reservoirs_info[:30], 1):
                            reservoir_id = reservoir['id']
                            capacity = reservoir['effective_capacity']
                            print(f'"{reservoir_id}": "水庫{reservoir_id}",  # 容量: {capacity}')
                            if i % 10 == 0:
                                print()  # 每10個換行
                        
                        # 統計資訊
                        print(f"\n📊 統計資訊:")
                        print("-" * 30)
                        
                        total_reservoirs = len(reservoirs_info)
                        has_capacity_data = len([r for r in reservoirs_info if r['effective_capacity'] != 'N/A'])
                        has_percentage_data = len([r for r in reservoirs_info if r['percentage'] != 'N/A'])
                        
                        print(f"總水庫數量: {total_reservoirs}")
                        print(f"有容量資料: {has_capacity_data}")
                        print(f"有蓄水率資料: {has_percentage_data}")
                        
                        # 按蓄水率分類
                        high_percentage = len([r for r in reservoirs_info if r['percentage'] != 'N/A' and float(r['percentage']) >= 80])
                        medium_percentage = len([r for r in reservoirs_info if r['percentage'] != 'N/A' and 50 <= float(r['percentage']) < 80])
                        low_percentage = len([r for r in reservoirs_info if r['percentage'] != 'N/A' and float(r['percentage']) < 50])
                        
                        print(f"\n💧 蓄水率分布:")
                        print(f"高水位 (≥80%): {high_percentage} 個")
                        print(f"中水位 (50-79%): {medium_percentage} 個")
                        print(f"低水位 (<50%): {low_percentage} 個")
                        
                        # 地區分布（粗略分類）
                        print(f"\n🗺️ 地區分布分析:")
                        north_keywords = ['翡翠', '石門', '新山', '寶山']
                        central_keywords = ['德基', '鯉魚潭', '明德', '永和山', '日月潭']
                        south_keywords = ['曾文', '南化', '烏山頭', '白河', '牡丹', '阿公店']
                        
                        north_count = len([r for r in reservoirs_info if any(kw in r['name'] for kw in north_keywords)])
                        central_count = len([r for r in reservoirs_info if any(kw in r['name'] for kw in central_keywords)])
                        south_count = len([r for r in reservoirs_info if any(kw in r['name'] for kw in south_keywords)])
                        other_count = total_reservoirs - north_count - central_count - south_count
                        
                        print(f"北部地區: {north_count} 個")
                        print(f"中部地區: {central_count} 個")
                        print(f"南部地區: {south_count} 個")
                        print(f"其他地區: {other_count} 個")
                        
                        # 儲存完整資料
                        output_data = {
                            "total_reservoirs": total_reservoirs,
                            "timestamp": datetime.now().isoformat(),
                            "reservoirs": reservoirs_info
                        }
                        
                        with open("complete_reservoir_list.json", "w", encoding="utf-8") as f:
                            json.dump(output_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"\n💾 完整水庫列表已儲存至: complete_reservoir_list.json")
                        
                    else:
                        print("❌ 沒有水庫資料")
                else:
                    print(f"❌ API 請求失敗，狀態碼: {response.status}")
                    
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()

def main():
    """主函數"""
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(test_reservoir_list_with_capacity())
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
