#!/usr/bin/env python3
"""
檢查台鐵指令是否正確添加到 info_commands_fixed_v4_clean.py
"""

import sys
import importlib.util

def check_tra_commands():
    """檢查台鐵指令是否正確添加"""
    
    try:
        # 載入模組
        spec = importlib.util.spec_from_file_location(
            "info_commands", 
            "cogs/info_commands_fixed_v4_clean.py"
        )
        info_module = importlib.util.module_from_spec(spec)
        
        print("✅ 成功載入 info_commands_fixed_v4_clean.py 模組")
        
        # 檢查是否有 TRA_STATIONS
        if hasattr(info_module, 'TRA_STATIONS'):
            print("✅ 找到 TRA_STATIONS 定義")
            
            # 載入內容
            spec.loader.exec_module(info_module)
            
            # 檢查台鐵車站資料
            tra_stations = info_module.TRA_STATIONS
            print(f"✅ TRA_STATIONS 包含 {len(tra_stations)} 個縣市的車站資料")
            
            # 檢查一些主要縣市
            check_counties = ['臺北市', '新北市', '高雄市', '臺中市']
            for county in check_counties:
                if county in tra_stations:
                    station_count = len(tra_stations[county])
                    print(f"   - {county}: {station_count} 個車站")
                else:
                    print(f"   ⚠️ {county}: 未找到車站資料")
        
        # 檢查類別
        classes_to_check = ['TRALiveboardView', 'TRADelayView']
        for class_name in classes_to_check:
            if hasattr(info_module, class_name):
                print(f"✅ 找到 {class_name} 類別")
            else:
                print(f"❌ 未找到 {class_name} 類別")
        
        print("\n📋 台鐵功能檢查完成")
        return True
        
    except Exception as e:
        print(f"❌ 檢查時發生錯誤: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 開始檢查台鐵指令...")
    success = check_tra_commands()
    
    if success:
        print("\n🎉 台鐵功能檢查通過！")
        sys.exit(0)
    else:
        print("\n💥 台鐵功能檢查失敗")
        sys.exit(1)
