#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
詳細分析水庫水情 API 資料結構
"""

import asyncio
import aiohttp
import json
import ssl
from datetime import datetime

async def analyze_reservoir_data():
    """分析水庫水情 API 資料"""
    print("🏞️ 分析水庫水情 API 資料結構...")
    print("=" * 50)
    
    # 設定 SSL 上下文
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    try:
        async with aiohttp.ClientSession(connector=connector) as session:
            url = "https://opendata.wra.gov.tw/Service/OpenData.aspx?format=json&id=1602CA19-B224-4CC3-AA31-11B1B124530F"
            
            print(f"📡 請求 URL: {url}")
            
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    # 處理 UTF-8 BOM 問題
                    text = await response.text()
                    if text.startswith('\ufeff'):
                        text = text[1:]
                    
                    data = json.loads(text)
                    
                    # 取得實際的水庫資料
                    reservoir_data = data.get('ReservoirConditionData_OPENDATA', [])
                    
                    print(f"✅ 成功獲取 {len(reservoir_data)} 筆水庫資料")
                    
                    if reservoir_data:
                        # 分析第一筆資料的所有欄位
                        first_item = reservoir_data[0]
                        print("\n🔍 資料欄位分析:")
                        print(f"{'欄位名稱':<35} {'值':<20} {'類型'}")
                        print("-" * 70)
                        
                        for key, value in first_item.items():
                            value_str = str(value)[:20] if value is not None else "None"
                            print(f"{key:<35} {value_str:<20} {type(value).__name__}")
                        
                        # 顯示幾個重要水庫的資料
                        print("\n📊 重要水庫資料範例:")
                        print("=" * 60)
                        
                        # 尋找一些知名的水庫
                        important_reservoirs = ['石門水庫', '曾文水庫', '日月潭水庫', '德基水庫', '翡翠水庫']
                        
                        for reservoir in reservoir_data[:10]:  # 檢查前10筆
                            reservoir_name = reservoir.get('ReservoirName', 'N/A')
                            if any(name in reservoir_name for name in important_reservoirs) or len([r for r in reservoir_data[:10] if r == reservoir]) <= 5:
                                print(f"\n🏞️ {reservoir_name}")
                                print(f"   📍 位置: {reservoir.get('ReservoirIdentifier', 'N/A')}")
                                print(f"   💧 有效蓄水量: {reservoir.get('EffectiveWaterStorageCapacity', 'N/A')} 萬立方公尺")
                                print(f"   📊 蓄水率: {reservoir.get('Percentage', 'N/A')}%")
                                print(f"   🌊 水位: {reservoir.get('WaterLevel', 'N/A')} 公尺")
                                print(f"   📅 更新時間: {reservoir.get('ReservoirInfo', {}).get('UpdateTime', 'N/A') if isinstance(reservoir.get('ReservoirInfo'), dict) else 'N/A'}")
                        
                        # 儲存範例資料
                        sample_data = {
                            'total_count': len(reservoir_data),
                            'sample_fields': list(first_item.keys()),
                            'sample_data': reservoir_data[:5]  # 前5筆作為範例
                        }
                        
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"reservoir_analysis_{timestamp}.json"
                        
                        with open(filename, 'w', encoding='utf-8') as f:
                            json.dump(sample_data, f, ensure_ascii=False, indent=2)
                        
                        print(f"\n💾 分析結果已儲存至: {filename}")
                        
                        # 分析統計資訊
                        print("\n📈 統計資訊:")
                        print(f"   總水庫數量: {len(reservoir_data)}")
                        
                        # 統計有效蓄水量
                        valid_capacity = [r for r in reservoir_data if r.get('EffectiveWaterStorageCapacity') not in [None, '', 0]]
                        print(f"   有蓄水量資料: {len(valid_capacity)} 個")
                        
                        # 統計蓄水率
                        valid_percentage = [r for r in reservoir_data if r.get('Percentage') not in [None, '', 0]]
                        print(f"   有蓄水率資料: {len(valid_percentage)} 個")
                        
                        return True
                    
                else:
                    print(f"❌ API 請求失敗: {response.status}")
                    return False
                    
    except Exception as e:
        print(f"❌ 分析過程發生錯誤: {str(e)}")
        import traceback
        print(f"錯誤詳情: {traceback.format_exc()}")
        return False
    
    finally:
        await connector.close()

if __name__ == "__main__":
    success = asyncio.run(analyze_reservoir_data())
    
    if success:
        print("\n🎯 下一步準備工作:")
        print("  ✅ API 資料結構已分析完成")
        print("  📝 可以開始開發 Discord 指令")
        print("  🔧 主要欄位:")
        print("     - ReservoirName: 水庫名稱")
        print("     - EffectiveWaterStorageCapacity: 有效蓄水量")
        print("     - Percentage: 蓄水率")
        print("     - WaterLevel: 水位")
        print("  🚀 準備建立 cogs/reservoir_commands.py")
