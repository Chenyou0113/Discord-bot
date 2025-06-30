#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
診斷水利監視器縣市資料顯示問題
檢查 API 回應的實際欄位名稱和內容
"""

import asyncio
import json
import sys

async def diagnose_county_data():
    """診斷縣市資料問題"""
    
    print("🔍 診斷水利監視器縣市資料問題")
    print("=" * 60)
    
    try:
        # 導入相關模組
        from cogs.reservoir_commands import ReservoirCommands
        
        # 創建實例
        mock_bot = None
        reservoir_cog = ReservoirCommands(mock_bot)
        
        print("1️⃣ 獲取實際的水利防災影像資料...")
        try:
            image_data = await reservoir_cog.get_water_disaster_images()
            if image_data:
                print(f"✅ 成功獲取 {len(image_data)} 筆資料")
                
                print("\n2️⃣ 檢查前5筆資料的欄位結構...")
                for i in range(min(5, len(image_data))):
                    data = image_data[i]
                    print(f"\n📋 資料 {i+1}:")
                    print(f"   所有可用欄位: {list(data.keys())}")
                    
                    # 檢查縣市相關欄位
                    county_fields = [
                        'CountiesAndCitiesWhereTheMonitoringPointsAreLocated',
                        'AdministrativeDistrictWhereTheMonitoringPointIsLocated',
                        'County', 'City', 'Location', 'Area', 'Region'
                    ]
                    
                    print(f"   🏙️ 縣市相關欄位:")
                    for field in county_fields:
                        if field in data:
                            value = data[field]
                            print(f"      {field}: '{value}'")
                    
                    # 檢查監控站名稱和地址
                    station_name = data.get('VideoSurveillanceStationName', '')
                    address = data.get('VideoSurveillanceStationAddress', '')
                    
                    print(f"   📸 監控站名稱: '{station_name}'")
                    print(f"   📍 監控站地址: '{address}'")
                    
                    # 使用現有的格式化方法
                    formatted = reservoir_cog.format_water_image_info(data)
                    if formatted:
                        print(f"   🔄 格式化結果:")
                        print(f"      縣市: '{formatted['county']}'")
                        print(f"      區域: '{formatted['district']}'")
                        print(f"      地址: '{formatted['address']}'")
                
                print("\n3️⃣ 統計縣市分布...")
                county_stats = {}
                for data in image_data:
                    county = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '未知')
                    county_stats[county] = county_stats.get(county, 0) + 1
                
                print(f"縣市分布統計 (前10名):")
                sorted_counties = sorted(county_stats.items(), key=lambda x: x[1], reverse=True)
                for county, count in sorted_counties[:10]:
                    print(f"   {county}: {count} 個監控點")
                
                print("\n4️⃣ 檢查欄位名稱是否可能有變化...")
                # 檢查所有可能的縣市欄位變化
                all_fields = set()
                for data in image_data[:50]:  # 檢查前50筆
                    all_fields.update(data.keys())
                
                possible_county_fields = [field for field in all_fields 
                                        if any(keyword in field.lower() 
                                              for keyword in ['county', 'city', 'location', 'area', 'region', 'place'])]
                
                print(f"可能的縣市相關欄位:")
                for field in possible_county_fields:
                    print(f"   {field}")
                
                return True
                
            else:
                print("❌ 無法獲取水利防災影像資料")
                return False
                
        except Exception as e:
            print(f"❌ 獲取資料失敗: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ 診斷失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_county_mapping():
    """測試縣市對應關係"""
    
    print("\n5️⃣ 測試縣市對應關係")
    print("=" * 40)
    
    # 測試可能的縣市名稱對應
    test_mappings = {
        '台北': ['台北市', '臺北市', 'Taipei', 'TPE'],
        '新北': ['新北市', '新北市政府', 'New Taipei', 'NTC'],
        '桃園': ['桃園市', '桃園縣', 'Taoyuan', 'TYC'],
        '台中': ['台中市', '臺中市', 'Taichung', 'TXG'],
        '台南': ['台南市', '臺南市', 'Tainan', 'TNN'],
        '高雄': ['高雄市', 'Kaohsiung', 'KHH']
    }
    
    print("可能的縣市名稱對應:")
    for standard, variants in test_mappings.items():
        print(f"   {standard}: {', '.join(variants)}")

async def main():
    """主函數"""
    
    print("🚀 水利監視器縣市資料診斷")
    print("=" * 80)
    
    # 診斷縣市資料
    data_test = await diagnose_county_data()
    
    # 測試縣市對應
    await test_county_mapping()
    
    # 結果報告
    print("\n" + "=" * 80)
    print("📊 診斷結果:")
    print(f"資料檢查: {'✅ 完成' if data_test else '❌ 失敗'}")
    
    if data_test:
        print("\n💡 可能的問題和解決方案:")
        print("1. 檢查 API 欄位名稱是否有變更")
        print("2. 確認縣市名稱格式是否一致")
        print("3. 檢查是否需要縣市名稱標準化")
        print("4. 確認地址解析邏輯是否正確")
        
        print("\n🔧 建議的修復步驟:")
        print("1. 更新欄位名稱對應")
        print("2. 實作縣市名稱標準化")
        print("3. 增加地址解析備用方案")
        print("4. 驗證修復結果")
    
    return data_test

if __name__ == "__main__":
    try:
        result = asyncio.run(main())
        sys.exit(0 if result else 1)
    except Exception as e:
        print(f"💥 診斷程序錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
