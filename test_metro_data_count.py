#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
捷運電子看板資料筆數測試腳本
測試修改後的API是否能取得更多資料
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.info_commands_fixed_v4_clean import InfoCommands

async def test_metro_data_count():
    """測試捷運電子看板資料筆數"""
    print("🚇 測試捷運電子看板資料筆數...")
    print("=" * 50)
    
    # 建立InfoCommands實例
    info_cog = InfoCommands(None)  # 不需要bot實例來測試API
    
    # 測試各捷運系統
    systems = {
        'TRTC': '台北捷運',
        'KRTC': '高雄捷運', 
        'KLRT': '高雄輕軌'
    }
    
    for system_id, system_name in systems.items():
        print(f"\n📊 測試 {system_name} ({system_id})")
        print("-" * 30)
        
        try:
            # 獲取資料
            data = await info_cog.fetch_metro_liveboard(system_id)
            
            if data:
                print(f"✅ 成功取得 {len(data)} 筆資料")
                
                # 統計各路線資料
                line_stats = {}
                for station in data:
                    line_id = station.get('LineID', '未知路線')
                    if line_id not in line_stats:
                        line_stats[line_id] = 0
                    line_stats[line_id] += 1
                
                print("📈 各路線資料統計:")
                for line_id, count in sorted(line_stats.items()):
                    print(f"   {line_id}: {count} 個車站")
                
                # 顯示部分資料範例
                print("\n📋 資料範例 (前3筆):")
                for i, station in enumerate(data[:3]):
                    station_name = station.get('StationName', {})
                    if isinstance(station_name, dict):
                        name = station_name.get('Zh_tw', '未知')
                    else:
                        name = str(station_name)
                    
                    line_id = station.get('LineID', '未知')
                    print(f"   {i+1}. {name} ({line_id}線)")
                    
            else:
                print("❌ 無法取得資料")
                
        except Exception as e:
            print(f"❌ 錯誤: {str(e)}")
    
    print("\n" + "=" * 50)
    print("🎯 測試完成！")
    
    # 關閉aiohttp session
    if hasattr(info_cog, 'session') and info_cog.session:
        await info_cog.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(test_metro_data_count())
    except KeyboardInterrupt:
        print("\n\n👋 測試被使用者中斷")
    except Exception as e:
        print(f"\n❌ 執行錯誤: {e}")
