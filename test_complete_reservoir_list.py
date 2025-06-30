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
                                reservoir_name = item.get('ReservoirName', f"水庫{reservoir_id}")
                                effective_capacity = item.get('EffectiveWaterStorageCapacity', 'N/A')
                                current_storage = item.get('EffectiveStorageWaterLevel', 'N/A')
                                water_level = item.get('WaterLevel', 'N/A')
                                inflow = item.get('InflowDischarge', 'N/A')
                                outflow = item.get('TotalOutflow', 'N/A')
                                obs_time = item.get('ObservationTime', 'N/A')
                                
                                # 計算蓄水率
                                percentage = 'N/A'
                                try:
                                    if (effective_capacity != 'N/A' and current_storage != 'N/A' and 
                                        effective_capacity and current_storage):
                                        capacity_val = float(effective_capacity)
                                        storage_val = float(current_storage)
                                        if capacity_val > 0:
                                            percentage = round((storage_val / capacity_val) * 100, 2)
                                except (ValueError, TypeError, ZeroDivisionError):
                                    percentage = 'N/A'
                                
                                reservoirs_info.append({
                                    'id': reservoir_id,
                                    'name': reservoir_name,
                                    'effective_capacity': effective_capacity,
                                    'current_storage': current_storage,
                                    'percentage': percentage,
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
                        print("-" * 90)
                        print(f"{'排名':<4} {'水庫ID':<8} {'水庫名稱':<20} {'有效容量(萬m³)':<15} {'蓄水率(%)':<10} {'目前水位(m)':<12}")
                        print("-" * 90)
                        
                        for i, reservoir in enumerate(reservoirs_info[:20], 1):
                            reservoir_id = reservoir['id'][:7]
                            name = reservoir['name'][:18] + '...' if len(reservoir['name']) > 18 else reservoir['name']
                            capacity = reservoir['effective_capacity'][:12] if reservoir['effective_capacity'] != 'N/A' else 'N/A'
                            percentage = f"{reservoir['percentage']:.1f}" if reservoir['percentage'] != 'N/A' else 'N/A'
                            water_level = reservoir['water_level'][:10] if reservoir['water_level'] != 'N/A' else 'N/A'
                            
                            print(f"{i:<4} {reservoir_id:<8} {name:<20} {capacity:<15} {percentage:<10} {water_level:<12}")
                        
                        # 建立水庫 ID 到名稱的對應表（用於更新 Discord 指令）
                        print(f"\n📋 可建立的水庫 ID 對應表（前 30 個，按容量排序）:")
                        print("-" * 70)
                        
                        # 建立更完整的對應表
                        reservoir_mapping = {}
                        for i, reservoir in enumerate(reservoirs_info[:30], 1):
                            reservoir_id = reservoir['id']
                            reservoir_name = reservoir['name']
                            capacity = reservoir['effective_capacity']
                            percentage = reservoir['percentage']
                            
                            # 格式化顯示
                            percentage_str = f"{percentage:.1f}%" if percentage != 'N/A' else 'N/A'
                            capacity_str = f"{capacity}" if capacity != 'N/A' else 'N/A'
                            
                            print(f'"{reservoir_id}": "{reservoir_name}",  # 容量: {capacity_str} 萬m³, 蓄水率: {percentage_str}')
                            reservoir_mapping[reservoir_id] = reservoir_name
                            
                            if i % 5 == 0:
                                print()  # 每5個換行
                        
                        # 額外統計
                        print(f"\n📊 詳細統計資訊:")
                        print("-" * 40)
                        
                        # 容量統計
                        valid_capacity_reservoirs = [r for r in reservoirs_info if r['effective_capacity'] != 'N/A']
                        if valid_capacity_reservoirs:
                            try:
                                capacities = [float(r['effective_capacity']) for r in valid_capacity_reservoirs]
                                total_capacity = sum(capacities)
                                avg_capacity = total_capacity / len(capacities)
                                max_capacity = max(capacities)
                                min_capacity = min(capacities)
                                
                                print(f"總有效容量: {total_capacity:,.0f} 萬m³")
                                print(f"平均容量: {avg_capacity:,.0f} 萬m³")
                                print(f"最大容量: {max_capacity:,.0f} 萬m³")
                                print(f"最小容量: {min_capacity:,.0f} 萬m³")
                            except (ValueError, TypeError) as e:
                                print(f"計算容量統計時發生錯誤: {e}")
                        else:
                            print("沒有有效的容量資料可供統計")
                        
                        # 蓄水率統計
                        if valid_percentage_reservoirs:
                            try:
                                percentages = [float(r['percentage']) for r in valid_percentage_reservoirs]
                                avg_percentage = sum(percentages) / len(percentages)
                                max_percentage = max(percentages)
                                min_percentage = min(percentages)
                                
                                print(f"\n平均蓄水率: {avg_percentage:.1f}%")
                                print(f"最高蓄水率: {max_percentage:.1f}%")
                                print(f"最低蓄水率: {min_percentage:.1f}%")
                            except (ValueError, TypeError) as e:
                                print(f"計算蓄水率統計時發生錯誤: {e}")
                        else:
                            print("\n沒有有效的蓄水率資料可供統計")
                        
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
                        valid_percentage_reservoirs = [r for r in reservoirs_info if r['percentage'] != 'N/A']
                        high_percentage = len([r for r in valid_percentage_reservoirs if float(r['percentage']) >= 80])
                        medium_percentage = len([r for r in valid_percentage_reservoirs if 50 <= float(r['percentage']) < 80])
                        low_percentage = len([r for r in valid_percentage_reservoirs if float(r['percentage']) < 50])
                        
                        print(f"\n💧 蓄水率分布:")
                        print(f"高水位 (≥80%): {high_percentage} 個")
                        print(f"中水位 (50-79%): {medium_percentage} 個")
                        print(f"低水位 (<50%): {low_percentage} 個")
                        
                        # 地區分布（使用水庫ID和名稱進行更準確的分類）
                        print(f"\n🗺️ 地區分布分析:")
                        
                        # 建立更完整的水庫地區對應
                        north_reservoirs = []
                        central_reservoirs = []
                        south_reservoirs = []
                        east_reservoirs = []
                        other_reservoirs = []
                        
                        for reservoir in reservoirs_info:
                            name = reservoir['name'].lower()
                            reservoir_id = reservoir['id']
                            
                            # 北部地區（基隆、台北、新北、桃園、新竹）
                            if any(keyword in name for keyword in ['翡翠', '石門', '新山', '寶山', '永和山']) or \
                               reservoir_id in ['10501', '10502', '10601', '10602']:
                                north_reservoirs.append(reservoir)
                            # 中部地區（苗栗、台中、彰化、南投、雲林）
                            elif any(keyword in name for keyword in ['德基', '鯉魚潭', '明德', '日月潭', '集集攔河堰']) or \
                                 reservoir_id in ['10701', '10702', '10801', '10901']:
                                central_reservoirs.append(reservoir)
                            # 南部地區（嘉義、台南、高雄、屏東）
                            elif any(keyword in name for keyword in ['曾文', '南化', '烏山頭', '白河', '牡丹', '阿公店']) or \
                                 reservoir_id in ['11001', '11002', '11101', '11301']:
                                south_reservoirs.append(reservoir)
                            # 東部地區（宜蘭、花蓮、台東）
                            elif any(keyword in name for keyword in ['龍溪壩', '利澤簡']) or \
                                 reservoir_id in ['12001', '12002']:
                                east_reservoirs.append(reservoir)
                            else:
                                other_reservoirs.append(reservoir)
                        
                        print(f"北部地區: {len(north_reservoirs)} 個")
                        print(f"中部地區: {len(central_reservoirs)} 個")
                        print(f"南部地區: {len(south_reservoirs)} 個")
                        print(f"東部地區: {len(east_reservoirs)} 個")
                        print(f"其他地區: {len(other_reservoirs)} 個")
                        
                        # 儲存完整資料
                        output_data = {
                            "metadata": {
                                "total_reservoirs": total_reservoirs,
                                "has_capacity_data": has_capacity_data,
                                "has_percentage_data": len(valid_percentage_reservoirs),
                                "timestamp": datetime.now().isoformat(),
                                "api_url": api_url
                            },
                            "statistics": {
                                "capacity_stats": {
                                    "total_capacity": sum([float(r['effective_capacity']) for r in valid_capacity_reservoirs]) if valid_capacity_reservoirs else 0,
                                    "average_capacity": sum([float(r['effective_capacity']) for r in valid_capacity_reservoirs]) / len(valid_capacity_reservoirs) if valid_capacity_reservoirs else 0,
                                    "max_capacity": max([float(r['effective_capacity']) for r in valid_capacity_reservoirs]) if valid_capacity_reservoirs else 0,
                                    "min_capacity": min([float(r['effective_capacity']) for r in valid_capacity_reservoirs]) if valid_capacity_reservoirs else 0
                                } if valid_capacity_reservoirs else {},
                                "percentage_distribution": {
                                    "high_percentage": high_percentage,
                                    "medium_percentage": medium_percentage,
                                    "low_percentage": low_percentage
                                },
                                "regional_distribution": {
                                    "north": len(north_reservoirs),
                                    "central": len(central_reservoirs),
                                    "south": len(south_reservoirs),
                                    "east": len(east_reservoirs),
                                    "other": len(other_reservoirs)
                                }
                            },
                            "reservoir_mapping": reservoir_mapping,
                            "reservoirs": reservoirs_info
                        }
                        
                        with open("complete_reservoir_list.json", "w", encoding="utf-8") as f:
                            json.dump(output_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"\n💾 完整水庫列表已儲存至: complete_reservoir_list.json")
                        print(f"📁 檔案包含 {total_reservoirs} 個水庫的完整資訊")
                        
                        # 顯示一些特別的水庫資訊
                        print(f"\n🏆 特別關注的水庫:")
                        special_reservoirs = ['10501', '10901', '11001', '11101']  # 石門、日月潭、曾文、南化
                        for res_id in special_reservoirs:
                            special_res = next((r for r in reservoirs_info if r['id'] == res_id), None)
                            if special_res:
                                percentage_str = f"{special_res['percentage']:.1f}%" if special_res['percentage'] != 'N/A' else 'N/A'
                                capacity_str = f"{special_res['effective_capacity']}" if special_res['effective_capacity'] != 'N/A' else 'N/A'
                                print(f"  {special_res['name']}: 容量 {capacity_str} 萬m³, 蓄水率 {percentage_str}")
                        
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
