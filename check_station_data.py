"""
檢查車站資料載入情況
"""
import sys
sys.path.append('.')

# 直接導入車站資料
try:
    from cogs.info_commands_fixed_v4_clean import TRA_STATIONS
    print("✅ 成功導入 TRA_STATIONS")
    
    # 統計車站數量
    total_stations = 0
    for county, stations in TRA_STATIONS.items():
        total_stations += len(stations)
        print(f"{county}: {len(stations)} 站")
    
    print(f"\n📊 總計: {len(TRA_STATIONS)} 個縣市, {total_stations} 個車站")
    
    # 檢查志學站
    print("\n🔍 檢查志學站:")
    found = False
    for county, stations in TRA_STATIONS.items():
        for station in stations:
            if station['name'] == '志學':
                print(f"找到志學站: {station} (位於 {county})")
                found = True
    
    if not found:
        print("❌ 未找到志學站")
        
except ImportError as e:
    print(f"❌ 導入失敗: {e}")
except Exception as e:
    print(f"❌ 錯誤: {e}")
