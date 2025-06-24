#!/usr/bin/env python3
"""
簡化的格式化函數測試
直接測試format_earthquake_data方法，避免初始化問題
"""
import asyncio
import discord
import logging
from typing import Dict, Any, Optional

# 設置日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 測試地震數據樣本
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

# 缺少必要欄位的測試數據
TEST_MISSING_FIELDS = {
    "ReportType": "地震報告",
    "ReportColor": "綠色",
    # 缺少 ReportContent 和 EarthquakeNo
}

async def format_earthquake_data_standalone(eq_data: Dict[str, Any]) -> Optional[discord.Embed]:
    """獨立的地震資料格式化函數（從原始代碼複製）"""
    try:
        # 確認必要的欄位是否存在
        if not all(k in eq_data for k in ['ReportContent', 'EarthquakeNo']):
            logger.warning(f"缺少必要欄位，數據: {list(eq_data.keys())}")
            return None
            
        # 取得地震資訊
        report_content = eq_data.get('ReportContent', '地震資料不完整')
        report_color = eq_data.get('ReportColor', '綠色')
        report_time = eq_data.get('OriginTime', '未知時間')
        report_web = eq_data.get('Web', '')
        report_image = eq_data.get('ReportImageURI', '')
        
        # 設定嵌入顏色
        color = discord.Color.green()
        if report_color == '黃色':
            color = discord.Color.gold()
        elif report_color == '橘色':
            color = discord.Color.orange()
        elif report_color == '紅色':
            color = discord.Color.red()
            
        # 建立嵌入訊息
        embed = discord.Embed(
            title="🌋 地震報告",
            description=report_content,
            color=color,
            url=report_web if report_web else None
        )
        
        # 添加地震相關資訊
        if 'EarthquakeInfo' in eq_data:
            eq_info = eq_data['EarthquakeInfo']
            epicenter = eq_info.get('Epicenter', {})
            magnitude = eq_info.get('EarthquakeMagnitude', {})
            
            location = epicenter.get('Location', '未知位置')
            focal_depth = eq_info.get('FocalDepth', '未知')
            magnitude_value = magnitude.get('MagnitudeValue', '未知')
            
            embed.add_field(
                name="📍 震央位置",
                value=location,
                inline=True
            )
            
            embed.add_field(
                name="🔍 規模",
                value=f"{magnitude_value}",
                inline=True
            )
            
            embed.add_field(
                name="⬇️ 深度",
                value=f"{focal_depth} 公里",
                inline=True
            )
            
        # 添加有感地區資訊
        if 'Intensity' in eq_data and 'ShakingArea' in eq_data['Intensity']:
            max_intensity = "0級"
            max_areas = []
            
            for area in eq_data['Intensity']['ShakingArea']:
                area_desc = area.get('AreaDesc', '')
                intensity = area.get('AreaIntensity', '')
                
                # 記錄最大震度和對應地區
                if intensity in ['7級', '6強', '6弱', '5強', '5弱', '4級']:
                    if max_intensity == "0級" or max_intensity < intensity:
                        max_intensity = intensity
                        max_areas = [area_desc]
                    elif max_intensity == intensity:
                        max_areas.append(area_desc)
            
            if max_intensity != "0級" and max_areas:
                embed.add_field(
                    name=f"⚠️ 最大震度 {max_intensity} 地區",
                    value=", ".join(max_areas),
                    inline=False
                )
        
        # 添加地震報告圖片
        if report_image:
            embed.set_image(url=report_image)
        
        # 添加頁尾資訊
        embed.set_footer(text=f"地震報告編號: {eq_data.get('EarthquakeNo', '未知')} | 震源時間: {report_time}")
        
        return embed
        
    except Exception as e:
        logger.error(f"格式化地震資料時發生錯誤: {str(e)}")
        return None

async def test_format_function():
    """測試格式化函數"""
    print("🧪 開始測試獨立格式化函數")
    print("=" * 60)
    
    # 測試1: 正常資料
    print("1️⃣ 測試正常地震資料...")
    embed1 = await format_earthquake_data_standalone(TEST_EARTHQUAKE_DATA)
    
    if embed1:
        print("✅ 正常資料測試通過")
        print(f"   標題: {embed1.title}")
        print(f"   描述: {embed1.description[:50]}...")
        print(f"   欄位數量: {len(embed1.fields)}")
        for i, field in enumerate(embed1.fields):
            print(f"   欄位 {i+1}: {field.name}")
    else:
        print("❌ 正常資料測試失敗 - 返回 None")
    
    # 測試2: 缺少必要欄位
    print("\n2️⃣ 測試缺少必要欄位的資料...")
    embed2 = await format_earthquake_data_standalone(TEST_MISSING_FIELDS)
    
    if embed2 is None:
        print("✅ 缺少欄位測試通過 - 正確返回 None")
    else:
        print("❌ 缺少欄位測試失敗 - 應該返回 None")
    
    # 測試3: 空資料
    print("\n3️⃣ 測試空資料...")
    embed3 = await format_earthquake_data_standalone({})
    
    if embed3 is None:
        print("✅ 空資料測試通過 - 正確返回 None")
    else:
        print("❌ 空資料測試失敗 - 應該返回 None")
    
    return embed1 is not None

async def test_data_issue():
    """測試原始 enhance_earthquake_data 處理過的資料"""
    print("\n🔍 檢查是否是 enhance_earthquake_data 的問題")
    print("=" * 60)
    
    # 模擬可能被 enhance_earthquake_data 修改的數據
    enhanced_data = TEST_EARTHQUAKE_DATA.copy()
    
    # 檢查可能的問題：OriginTime 位置
    if 'EarthquakeInfo' in enhanced_data and 'OriginTime' in enhanced_data['EarthquakeInfo']:
        # 將OriginTime移到根層級 (這是enhance函數可能做的)
        enhanced_data['OriginTime'] = enhanced_data['EarthquakeInfo']['OriginTime']
        print(f"📝 將 OriginTime 移到根層級: {enhanced_data['OriginTime']}")
    
    embed = await format_earthquake_data_standalone(enhanced_data)
    
    if embed:
        print("✅ 增強後的資料格式化成功")
        print(f"   頁尾: {embed.footer.text}")
    else:
        print("❌ 增強後的資料格式化失敗")
    
    return embed is not None

async def main():
    """主測試函數"""
    print("🚀 開始獨立格式化函數測試")
    print("目標：檢查 format_earthquake_data 是否正常工作")
    print("=" * 60)
    
    success1 = await test_format_function()
    success2 = await test_data_issue()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 格式化函數工作正常！")
        print("💡 問題可能在於：")
        print("   1. enhance_earthquake_data 函數修改了數據結構")
        print("   2. 實際調用時傳入的數據與測試數據不同")
        print("   3. 某個異常被捕獲但沒有記錄詳細信息")
    else:
        print("❌ 格式化函數有問題")
    
    print("🧹 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
