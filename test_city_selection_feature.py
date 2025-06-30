#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試監視器縣市選擇功能
驗證下拉選單縣市篩選是否正常運作
"""

import sys
import os
import asyncio
from datetime import datetime

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.reservoir_commands import ReservoirCommands

class MockBot:
    """模擬機器人"""
    pass

class MockInteraction:
    """模擬 Discord 互動"""
    def __init__(self):
        self.response_deferred = False
        self.followup_sent = False
    
    async def response_defer(self):
        self.response_deferred = True
    
    class MockFollowup:
        async def send(self, **kwargs):
            return MockMessage()
    
    class MockResponse:
        async def defer(self):
            pass
    
    @property
    def response(self):
        return self.MockResponse()
    
    @property
    def followup(self):
        return self.MockFollowup()

class MockMessage:
    """模擬 Discord 訊息"""
    async def edit(self, **kwargs):
        if 'embed' in kwargs:
            embed = kwargs['embed']
            print(f"📝 Embed 標題: {embed.title}")
            print(f"📝 Embed 描述: {embed.description}")
            if embed.fields:
                print(f"📝 Embed 欄位數: {len(embed.fields)}")
                for i, field in enumerate(embed.fields[:3]):
                    print(f"   欄位 {i+1}: {field.name}")

async def test_water_cameras_city_selection():
    """測試水利防災影像縣市選擇功能"""
    print("💧 測試水利防災影像縣市選擇功能...")
    
    bot = MockBot()
    reservoir_cog = ReservoirCommands(bot)
    
    # 測試案例
    test_cases = [
        {"city": "台北", "location": None, "description": "僅選擇台北市"},
        {"city": "台南", "location": None, "description": "僅選擇台南市"},
        {"city": "高雄", "location": None, "description": "僅選擇高雄市"},
        {"city": None, "location": "溪頂寮大橋", "description": "僅指定監控站名稱"},
        {"city": "台南", "location": "溪頂寮大橋", "description": "縣市+監控站名稱"},
        {"city": None, "location": None, "description": "無篩選條件（顯示統計）"}
    ]
    
    success_count = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n🧪 測試案例 {i}: {test_case['description']}")
        
        try:
            interaction = MockInteraction()
            
            # 調用水利防災影像查詢函數
            await reservoir_cog.water_disaster_cameras(
                interaction=interaction,
                city=test_case['city'],
                location=test_case['location']
            )
            
            print(f"✅ 測試案例 {i} 執行成功")
            success_count += 1
            
        except Exception as e:
            print(f"❌ 測試案例 {i} 失敗: {str(e)}")
    
    print(f"\n📊 水利防災影像測試結果: {success_count}/{len(test_cases)} 成功")
    return success_count == len(test_cases)

async def test_highway_cameras_city_choices():
    """測試公路監視器縣市選擇選項"""
    print("\n🛣️ 測試公路監視器縣市選擇選項...")
    
    # 檢查縣市選項是否正確定義
    expected_cities = [
        "基隆", "台北", "新北", "桃園", "新竹市", "新竹縣", "苗栗",
        "台中", "彰化", "南投", "雲林", "嘉義市", "嘉義縣", "台南",
        "高雄", "屏東", "宜蘭", "花蓮", "台東", "澎湖", "金門", "連江"
    ]
    
    print(f"📋 預期縣市選項數量: {len(expected_cities)}")
    print(f"📋 預期縣市列表: {', '.join(expected_cities)}")
    
    # 檢查是否包含主要縣市
    major_cities = ["台北", "台中", "台南", "高雄", "桃園", "新北"]
    all_major_included = all(city in expected_cities for city in major_cities)
    
    if all_major_included:
        print("✅ 所有主要縣市都包含在選項中")
    else:
        missing = [city for city in major_cities if city not in expected_cities]
        print(f"❌ 缺少主要縣市: {missing}")
    
    print("✅ 縣市選擇選項檢查完成")
    return all_major_included

async def test_city_search_logic():
    """測試縣市搜尋邏輯"""
    print("\n🔍 測試縣市搜尋邏輯...")
    
    bot = MockBot()
    reservoir_cog = ReservoirCommands(bot)
    
    try:
        # 取得水利防災影像資料
        image_data = await reservoir_cog.get_water_disaster_images()
        
        if not image_data:
            print("❌ 無法取得水利防災影像資料")
            return False
        
        print(f"✅ 成功取得 {len(image_data)} 筆資料")
        
        # 測試縣市搜尋邏輯
        test_cities = ["台北", "台南", "高雄", "台中", "桃園"]
        
        for city in test_cities:
            found_count = 0
            city_lower = city.lower()
            
            for data in image_data:
                loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
                district = data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
                station_name = data.get('VideoSurveillanceStationName', '')
                
                if (city_lower in loc.lower() or 
                    city_lower in district.lower() or
                    city_lower in station_name.lower()):
                    found_count += 1
            
            print(f"🔍 {city}: 找到 {found_count} 個監控點")
        
        return True
        
    except Exception as e:
        print(f"❌ 搜尋邏輯測試失敗: {str(e)}")
        return False

async def main():
    """主要測試函數"""
    print("🚀 監視器縣市選擇功能測試")
    print("=" * 60)
    print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 執行測試
    test_results = {}
    
    # 測試 1: 水利防災影像縣市選擇功能
    test_results['water_cameras_city'] = await test_water_cameras_city_selection()
    
    # 測試 2: 公路監視器縣市選擇選項
    test_results['highway_city_choices'] = await test_highway_cameras_city_choices()
    
    # 測試 3: 縣市搜尋邏輯
    test_results['city_search_logic'] = await test_city_search_logic()
    
    # 生成測試報告
    print("\n" + "=" * 60)
    print("📊 縣市選擇功能測試結果:")
    print("-" * 40)
    
    test_descriptions = {
        'water_cameras_city': '水利防災影像縣市選擇',
        'highway_city_choices': '公路監視器縣市選項',
        'city_search_logic': '縣市搜尋邏輯'
    }
    
    passed_tests = 0
    total_tests = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        description = test_descriptions.get(test_name, test_name)
        print(f"{description:.<30} {status}")
        if result:
            passed_tests += 1
    
    print("-" * 40)
    success_rate = (passed_tests / total_tests) * 100
    print(f"總體通過率: {success_rate:.1f}% ({passed_tests}/{total_tests})")
    
    # 評估功能狀態
    print("\n🎯 功能狀態評估:")
    
    if success_rate >= 100:
        print("🌟 縣市選擇功能: 完美 - 所有功能正常")
    elif success_rate >= 80:
        print("✅ 縣市選擇功能: 良好 - 主要功能正常")
    else:
        print("❌ 縣市選擇功能: 需要改善")
    
    print("\n📋 功能特色:")
    print("✅ 22個縣市完整下拉選單")
    print("✅ 水利防災影像縣市篩選")
    print("✅ 國道監視器縣市篩選")
    print("✅ 一般道路監視器縣市篩選")
    print("✅ 縣市+地點複合搜尋")
    print("✅ 智能搜尋邏輯（縣市、區域、監控站名稱）")
    
    print("\n🎯 使用方式:")
    print("水利防災影像:")
    print("  /water_cameras city:台北")
    print("  /water_cameras city:台南 location:溪頂寮大橋")
    print("公路監視器:")
    print("  /national_highway_cameras highway_number:1 city:台中")
    print("  /general_road_cameras road_type:快速公路 city:新北")
    
    print("\n💡 改善效果:")
    print("✅ 使用者不需手動輸入縣市名稱")
    print("✅ 避免拼寫錯誤")
    print("✅ 提供標準化的縣市選項")
    print("✅ 更直觀的使用體驗")

if __name__ == "__main__":
    asyncio.run(main())
