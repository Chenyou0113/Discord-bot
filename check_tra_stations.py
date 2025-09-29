"""
台鐵車站代碼檢查和更新工具
根據官方網站 https://www.railway.gov.tw/tra-tip-web/tip/tip001/tip111/view 提供的資訊
"""
import sys
sys.path.append('.')

def check_current_tra_stations():
    print("🚆 台鐵車站代碼檢查和更新")
    print("=" * 60)
    print()
    
    print("📍 **目前的台鐵車站數據統計**：")
    
    # 讀取現有的車站資料
    from cogs.info_commands_fixed_v4_clean import TRA_STATIONS
    
    total_stations = 0
    for county, stations in TRA_STATIONS.items():
        total_stations += len(stations)
        print(f"   {county}: {len(stations)} 個車站")
    
    print(f"   **總計**: {total_stations} 個車站")
    print()
    
    print("🔍 **已知的車站代碼範圍**：")
    
    all_ids = []
    for county, stations in TRA_STATIONS.items():
        for station in stations:
            try:
                station_id = int(station['id'])
                all_ids.append(station_id)
            except:
                print(f"   ⚠️ 無效代碼: {station['name']} - {station['id']}")
    
    all_ids.sort()
    
    print(f"   🔢 **代碼範圍**: {min(all_ids)} ~ {max(all_ids)}")
    print(f"   📊 **代碼統計**:")
    print(f"      0900-0999: 基隆-南港段 ({len([x for x in all_ids if 900 <= x <= 999])} 個)")
    print(f"      1000-1999: 西部幹線北段 ({len([x for x in all_ids if 1000 <= x <= 1999])} 個)")
    print(f"      2000-2999: 西部幹線中段 ({len([x for x in all_ids if 2000 <= x <= 2999])} 個)")
    print(f"      3000-3999: 西部幹線南段 ({len([x for x in all_ids if 3000 <= x <= 3999])} 個)")
    print(f"      4000-4999: 西部幹線南段 ({len([x for x in all_ids if 4000 <= x <= 4999])} 個)")
    print(f"      5000-5999: 南迴線/屏東線 ({len([x for x in all_ids if 5000 <= x <= 5999])} 個)")
    print(f"      6000-6999: 臺東線/花蓮線 ({len([x for x in all_ids if 6000 <= x <= 6999])} 個)")
    print(f"      7000-7999: 宜蘭線/平溪線等 ({len([x for x in all_ids if 7000 <= x <= 7999])} 個)")
    print()
    
    print("🔍 **檢查可能的問題**：")
    
    # 檢查重複的車站代碼
    id_count = {}
    duplicate_ids = []
    
    for county, stations in TRA_STATIONS.items():
        for station in stations:
            station_id = station['id']
            if station_id in id_count:
                duplicate_ids.append(station_id)
                id_count[station_id].append(f"{station['name']} ({county})")
            else:
                id_count[station_id] = [f"{station['name']} ({county})"]
    
    if duplicate_ids:
        print("   ❌ **重複的車站代碼**：")
        for dup_id in set(duplicate_ids):
            stations_with_id = id_count[dup_id]
            print(f"      代碼 {dup_id}: {', '.join(stations_with_id)}")
    else:
        print("   ✅ 沒有重複的車站代碼")
    
    print()
    
    # 檢查代碼格式
    invalid_formats = []
    for county, stations in TRA_STATIONS.items():
        for station in stations:
            station_id = station['id']
            if not station_id.isdigit() or len(station_id) != 4:
                invalid_formats.append(f"{station['name']} ({county}): {station_id}")
    
    if invalid_formats:
        print("   ❌ **無效的代碼格式**：")
        for invalid in invalid_formats:
            print(f"      {invalid}")
    else:
        print("   ✅ 所有代碼格式正確 (4位數字)")
    
    print()
    
    print("📋 **建議的更新方向**：")
    print("   1. 🔍 **驗證現有代碼**：對照官方最新車站代碼表")
    print("   2. 🆕 **新增車站**：檢查是否有新開通的車站")
    print("   3. 🏗️ **建設中車站**：關注建設中的新車站")
    print("   4. 🔄 **代碼變更**：檢查是否有車站代碼異動")
    print("   5. 📍 **站名變更**：檢查是否有車站改名")
    print()
    
    print("🌟 **重要車站檢查**：")
    important_stations = [
        ("臺北", "1000"), ("板橋", "1020"), ("桃園", "1080"), 
        ("新竹", "1210"), ("臺中", "3300"), ("嘉義", "4080"),
        ("臺南", "4220"), ("左營", "4350"), ("高雄", "4400"),
        ("花蓮", "7000"), ("臺東", "6000"), ("宜蘭", "7190")
    ]
    
    for station_name, expected_id in important_stations:
        found = False
        for county, stations in TRA_STATIONS.items():
            for station in stations:
                if station['name'] == station_name and station['id'] == expected_id:
                    print(f"   ✅ {station_name} ({expected_id}) - {county}")
                    found = True
                    break
            if found:
                break
        
        if not found:
            print(f"   ❌ {station_name} ({expected_id}) - 未找到或代碼不符")
    
    print()
    
    print("🔧 **更新建議**：")
    print("   1. 📥 **手動檢查**: 訪問官方網站確認最新車站列表")
    print("   2. 🆕 **新增遺漏**: 補充任何遺漏的車站")
    print("   3. 🔄 **修正錯誤**: 更正任何不正確的代碼")
    print("   4. 🧹 **清理重複**: 移除重複或無效的車站")
    print("   5. 📊 **重新分類**: 確保車站按正確縣市分類")
    print()
    
    print("📝 **更新範例格式**：")
    print('   {"name": "車站名稱", "id": "4位數代碼"}')
    print()
    
    print("⚠️ **注意事項**：")
    print("   - 車站代碼必須是4位數字")
    print("   - 每個代碼必須唯一")
    print("   - 車站名稱要與官方一致")
    print("   - 按縣市正確分類")
    print("   - 保持既有的JSON格式")
    
    return TRA_STATIONS

if __name__ == "__main__":
    stations = check_current_tra_stations()
