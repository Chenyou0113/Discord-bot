#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試水利防災影像查詢指令修復
驗證 format_water_image_info 函數回傳的欄位是否完整，避免 KeyError
"""

import sys
import os
import asyncio
import aiohttp
import ssl

# 添加專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.reservoir_commands import ReservoirCommands

class MockBot:
    """模擬機器人"""
    pass

async def test_format_water_image_info():
    """測試 format_water_image_info 函數回傳欄位"""
    print("🧪 測試 format_water_image_info 函數...")
    
    # 建立模擬的 ReservoirCommands 實例
    bot = MockBot()
    reservoir_cog = ReservoirCommands(bot)
    
    # 模擬 API 回傳的資料結構
    mock_image_data = {
        'VideoSurveillanceStationName': '測試監控站',
        'CameraName': '測試攝影機',
        'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
        'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
        'BasinName': '淡水河',
        'TRIBUTARY': '基隆河',
        'ImageURL': 'https://example.com/image.jpg',
        'Status': '1',
        'latitude_4326': '25.0330',
        'Longitude_4326': '121.5654',
        'StationID': 'TP001'
    }
    
    # 測試 format_water_image_info 函數
    print("\n📋 測試 format_water_image_info 回傳結構...")
    result = reservoir_cog.format_water_image_info(mock_image_data)
    
    if result:
        print("✅ format_water_image_info 函數執行成功")
        print(f"📊 回傳資料結構: {result.keys()}")
        
        # 檢查所有必要欄位
        required_fields = [
            'station_name', 'camera_name', 'location', 'county', 'district', 
            'address', 'station_id', 'source', 'river', 'image_url', 'status', 'coordinates'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
        
        if missing_fields:
            print(f"❌ 缺少欄位: {missing_fields}")
            return False
        else:
            print("✅ 所有必要欄位都存在")
            
            # 顯示欄位內容
            print("\n📄 欄位內容:")
            for field, value in result.items():
                print(f"  {field}: {value}")
            
            return True
    else:
        print("❌ format_water_image_info 函數回傳 None")
        return False

async def test_get_water_disaster_images():
    """測試獲取水利防災影像 API"""
    print("\n🌐 測試水利防災影像 API...")
    
    bot = MockBot()
    reservoir_cog = ReservoirCommands(bot)
    
    try:
        # 測試 API 呼叫
        image_data = await reservoir_cog.get_water_disaster_images()
        
        if image_data:
            print(f"✅ API 呼叫成功，取得 {len(image_data)} 筆資料")
            
            # 測試第一筆資料的格式化
            if len(image_data) > 0:
                print("\n📝 測試第一筆資料格式化...")
                first_data = image_data[0]
                formatted = reservoir_cog.format_water_image_info(first_data)
                
                if formatted:
                    print("✅ 第一筆資料格式化成功")
                    print(f"📊 監控站: {formatted['station_name']}")
                    print(f"📍 位置: {formatted['county']} {formatted['district']}")
                    print(f"🆔 ID: {formatted['station_id']}")
                    print(f"📡 來源: {formatted['source']}")
                    return True
                else:
                    print("❌ 第一筆資料格式化失敗")
                    return False
            else:
                print("⚠️ API 回傳空資料")
                return False
        else:
            print("❌ API 呼叫失敗")
            return False
            
    except Exception as e:
        print(f"❌ API 測試發生錯誤: {str(e)}")
        return False

async def test_water_cameras_command_simulation():
    """模擬 /water_cameras 指令的關鍵部分"""
    print("\n🤖 模擬 /water_cameras 指令執行...")
    
    bot = MockBot()
    reservoir_cog = ReservoirCommands(bot)
    
    try:
        # 取得水利防災影像資料
        image_data = await reservoir_cog.get_water_disaster_images()
        
        if not image_data:
            print("❌ 無法取得影像資料")
            return False
        
        # 模擬搜尋特定地區（台北）
        location = "台北"
        found_cameras = []
        location_lower = location.lower()
        
        for data in image_data:
            loc = data.get('CountiesAndCitiesWhereTheMonitoringPointsAreLocated', '')
            district = data.get('AdministrativeDistrictWhereTheMonitoringPointIsLocated', '')
            station_name = data.get('VideoSurveillanceStationName', '')
            
            # 檢查是否符合搜尋條件
            if (location_lower in loc.lower() or 
                location_lower in district.lower() or
                location_lower in station_name.lower()):
                found_cameras.append(data)
        
        print(f"🔍 找到 {len(found_cameras)} 個符合「{location}」的監控點")
        
        if found_cameras:
            # 過濾有效的監控點
            valid_cameras = []
            for data in found_cameras:
                info = reservoir_cog.format_water_image_info(data)
                if info and info['image_url'] and info['image_url'] != 'N/A':
                    valid_cameras.append(data)
            
            print(f"📸 其中 {len(valid_cameras)} 個有有效影像")
            
            if valid_cameras:
                # 測試第一個監控器的資料格式化
                camera_data = valid_cameras[0]
                info = reservoir_cog.format_water_image_info(camera_data)
                
                # 這是原本會出現 KeyError 的地方
                try:
                    test_embed_data = {
                        'county': info['county'],
                        'district': info['district'], 
                        'address': info['address'],
                        'station_id': info['station_id'],
                        'source': info['source'],
                        'image_url': info['image_url']
                    }
                    
                    print("✅ 成功模擬 embed 資料建立")
                    print(f"📊 測試資料: {test_embed_data}")
                    return True
                    
                except KeyError as e:
                    print(f"❌ KeyError 仍然存在: {str(e)}")
                    return False
            else:
                print("⚠️ 沒有找到有效影像的監控點")
                return True  # 這不是錯誤，只是沒有可用影像
        else:
            print("⚠️ 沒有找到符合條件的監控點")
            return True  # 這不是錯誤，只是沒有找到
            
    except Exception as e:
        print(f"❌ 模擬指令執行發生錯誤: {str(e)}")
        return False

async def main():
    """主要測試函數"""
    print("🚀 開始水利防災影像查詢指令修復測試")
    print("=" * 60)
    
    # 測試 1: format_water_image_info 函數欄位完整性
    test1_result = await test_format_water_image_info()
    
    # 測試 2: API 呼叫與資料格式化
    test2_result = await test_get_water_disaster_images()
    
    # 測試 3: 模擬完整指令執行
    test3_result = await test_water_cameras_command_simulation()
    
    print("\n" + "=" * 60)
    print("📊 測試結果總結:")
    print(f"✅ format_water_image_info 欄位測試: {'通過' if test1_result else '失敗'}")
    print(f"✅ API 呼叫測試: {'通過' if test2_result else '失敗'}")
    print(f"✅ 指令模擬測試: {'通過' if test3_result else '失敗'}")
    
    if all([test1_result, test2_result, test3_result]):
        print("\n🎉 所有測試通過！/water_cameras 指令修復成功")
    else:
        print("\n❌ 部分測試失敗，需要進一步檢查")

if __name__ == "__main__":
    asyncio.run(main())
