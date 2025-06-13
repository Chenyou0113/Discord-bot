#!/usr/bin/env python3
"""
測試 format_earthquake_data 函數
目標：找出為什麼格式化函數返回 None
"""
import asyncio
import sys
import os
import logging

# 添加 cogs 目錄到 sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))

from info_commands_fixed_v4_clean import InfoCommands

# 設置日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 測試地震數據樣本 (從API測試中獲得的真實數據)
TEST_EARTHQUAKE_DATA = {
    "EarthquakeNo": 11410005,
    "ReportType": "地震報告",
    "ReportColor": "綠色",
    "ReportContent": "06/12-00:01臺東縣近海發生規模5.0有感地震，最大震度花蓮縣石梯坪4級。",
    "ReportImageURI": "https://scweb.cwa.gov.tw/webdata/OLDEQ/202506/2025061200014810005_H.png",
    "ReportRemark": "本報告係中央氣象署地震觀測網即時地震資料地震速報之結果。",
    "Web": "https://scweb.cwa.gov.tw/zh-tw/earthquake/details/11410005",
    "ShakemapImageURI": "https://scweb.cwa.gov.tw/webdata/drawTrace/plotContour/2025/11410005i.png",
    "EarthquakeInfo": {
        "OriginTime": "2025-06-12 00:01:48",
        "Source": "中央氣象署",
        "FocalDepth": 25.8,
        "Epicenter": {
            "Location": "臺東縣政府東北東方  55.3  公里 (位於臺東縣近海)",
            "EpicenterLatitude": 23.03,
            "EpicenterLongitude": 121.71
        },
        "EarthquakeMagnitude": {
            "MagnitudeType": "芮氏規模",
            "MagnitudeValue": 5.0
        }
    },
    "Intensity": {
        "ShakingArea": [
            {
                "AreaDesc": "花蓮縣地區",
                "CountyName": "花蓮縣",
                "InfoStatus": "observe",
                "AreaIntensity": "4級",
                "EqStation": [
                    {
                        "StationName": "石梯坪",
                        "StationID": "STP",
                        "InfoStatus": "observe",
                        "SeismicIntensity": "4級",
                        "StationLatitude": 23.592,
                        "StationLongitude": 121.494
                    }
                ]
            }
        ]
    }
}

async def test_format_function():
    """測試 format_earthquake_data 函數"""
    print("🧪 開始測試 format_earthquake_data 函數")
    print("=" * 60)
    
    try:
        # 創建 InfoCommands 實例
        info_commands = InfoCommands(bot=None)  # Bot 為 None 在測試中沒關係
        
        print("✅ InfoCommands 實例創建成功")
        print(f"📋 測試數據: {TEST_EARTHQUAKE_DATA['EarthquakeNo']} - {TEST_EARTHQUAKE_DATA['ReportContent'][:50]}...")
        
        # 檢查必要欄位
        required_fields = ['ReportContent', 'EarthquakeNo']
        missing_fields = [field for field in required_fields if field not in TEST_EARTHQUAKE_DATA]
        
        if missing_fields:
            print(f"❌ 缺少必要欄位: {missing_fields}")
            return False
        else:
            print(f"✅ 所有必要欄位都存在: {required_fields}")
        
        # 測試格式化函數
        print("\n🔄 正在調用 format_earthquake_data...")
        embed = await info_commands.format_earthquake_data(TEST_EARTHQUAKE_DATA)
        
        if embed:
            print("✅ format_earthquake_data 返回了有效的 Discord Embed")
            print(f"📝 標題: {embed.title}")
            print(f"📄 描述: {embed.description[:100]}...")
            print(f"🎨 顏色: {embed.color}")
            print(f"🔗 URL: {embed.url}")
            print(f"🖼️ 圖片: {embed.image.url if embed.image else '無'}")
            print(f"📊 欄位數量: {len(embed.fields)}")
            
            # 顯示所有欄位
            for i, field in enumerate(embed.fields):
                print(f"   欄位 {i+1}: {field.name} = {field.value}")
                
            print(f"📄 頁尾: {embed.footer.text if embed.footer else '無'}")
            
            return True
        else:
            print("❌ format_earthquake_data 返回了 None")
            return False
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        logger.exception("詳細錯誤信息:")
        return False

async def test_debug_steps():
    """逐步調試格式化函數"""
    print("\n🔍 開始逐步調試")
    print("=" * 60)
    
    try:
        # 測試數據檢查
        eq_data = TEST_EARTHQUAKE_DATA
        
        # 步驟1: 檢查必要欄位
        required = ['ReportContent', 'EarthquakeNo']
        has_required = all(k in eq_data for k in required)
        print(f"1️⃣ 必要欄位檢查: {has_required}")
        
        if not has_required:
            print("❌ 缺少必要欄位，函數應該返回 None")
            return False
        
        # 步驟2: 提取基本資訊
        report_content = eq_data.get('ReportContent', '地震資料不完整')
        report_color = eq_data.get('ReportColor', '綠色')
        report_time = eq_data.get('OriginTime', '未知時間')
        report_web = eq_data.get('Web', '')
        report_image = eq_data.get('ReportImageURI', '')
        
        print(f"2️⃣ 基本資訊提取:")
        print(f"   - 報告內容: {report_content[:50]}...")
        print(f"   - 報告顏色: {report_color}")
        print(f"   - 報告時間: {report_time}")
        print(f"   - 網址: {report_web}")
        print(f"   - 圖片: {report_image}")
        
        # 步驟3: 檢查 EarthquakeInfo
        has_eq_info = 'EarthquakeInfo' in eq_data
        print(f"3️⃣ EarthquakeInfo 存在: {has_eq_info}")
        
        if has_eq_info:
            eq_info = eq_data['EarthquakeInfo']
            epicenter = eq_info.get('Epicenter', {})
            magnitude = eq_info.get('EarthquakeMagnitude', {})
            
            location = epicenter.get('Location', '未知位置')
            focal_depth = eq_info.get('FocalDepth', '未知')
            magnitude_value = magnitude.get('MagnitudeValue', '未知')
            
            print(f"   - 位置: {location}")
            print(f"   - 深度: {focal_depth}")
            print(f"   - 規模: {magnitude_value}")
        
        # 步驟4: 檢查 Intensity
        has_intensity = 'Intensity' in eq_data and 'ShakingArea' in eq_data['Intensity']
        print(f"4️⃣ Intensity 資訊存在: {has_intensity}")
        
        if has_intensity:
            shaking_areas = eq_data['Intensity']['ShakingArea']
            print(f"   - 有感地區數量: {len(shaking_areas)}")
            for area in shaking_areas:
                area_desc = area.get('AreaDesc', '')
                intensity = area.get('AreaIntensity', '')
                print(f"     {area_desc}: {intensity}")
        
        print("✅ 所有檢查步驟都完成，數據看起來正常")
        return True
        
    except Exception as e:
        print(f"❌ 調試過程中發生錯誤: {str(e)}")
        logger.exception("詳細錯誤信息:")
        return False

async def main():
    """主測試函數"""
    print("🚀 開始 format_earthquake_data 函數測試")
    print("目標：找出為什麼格式化函數返回 None")
    print("=" * 60)
    
    # 測試1: 基本功能測試
    success1 = await test_format_function()
    
    # 測試2: 逐步調試
    success2 = await test_debug_steps()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 所有測試通過！format_earthquake_data 函數工作正常")
    else:
        print("❌ 測試失敗，發現問題需要修復")
    
    print("🧹 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
