#!/usr/bin/env python3
"""
完整地震指令流程測試
模擬完整的earthquake指令執行流程，找出format_earthquake_data返回None的真正原因
"""
import asyncio
import discord
import logging
from typing import Dict, Any, Optional
import datetime

# 設置日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 測試數據：模擬從API獲取的真實數據
REAL_API_RESPONSE = {
    "success": "true",
    "result": {
        "resource_id": "E-A0015-001",
        "fields": [
            {"id": "EarthquakeNo", "type": "Integer"},
            {"id": "ReportType", "type": "String"},
            {"id": "ReportColor", "type": "String"},
            {"id": "ReportContent", "type": "String"},
            {"id": "ReportImageURI", "type": "String"},
            {"id": "ReportRemark", "type": "String"},
            {"id": "Web", "type": "String"},
            {"id": "ShakemapImageURI", "type": "String"},
            {"id": "EarthquakeInfo", "type": "Object"}
        ]
    },
    "records": [
        {
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
    ]
}

def simulate_earthquake_parsing(eq_data: Dict[str, Any]):
    """模擬earthquake指令中的解析邏輯"""
    print("🔍 模擬earthquake指令的解析邏輯...")
    print("-" * 40)
    
    latest_eq = None
    records = None
    
    # 步驟1：檢查資料結構 - 這是修復的核心邏輯
    if 'records' in eq_data:
        records = eq_data['records']
        print("✅ 檢測到有認證模式資料結構 (根級別records)")
    elif 'result' in eq_data and 'records' in eq_data['result']:
        records = eq_data['result']['records']
        print("✅ 檢測到無認證模式資料結構 (result.records)")
    else:
        print("❌ 未檢測到有效的records結構")
        return None
    
    if records:
        print(f"📋 records 類型: {type(records)}")
        
        # 檢查不同可能的資料格式
        if isinstance(records, dict) and 'Earthquake' in records:
            earthquake_data = records['Earthquake']
            if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                latest_eq = earthquake_data[0]
                print("✅ 使用標準列表格式地震資料")
            elif isinstance(earthquake_data, dict):
                latest_eq = earthquake_data
                print("✅ 使用標準字典格式地震資料")
        
        # v4 新增：處理直接資料格式（無 Earthquake 層級）
        elif isinstance(records, list) and len(records) > 0:
            # 檢查列表中的第一個元素是否包含地震資料特徵
            if all(key in records[0] for key in ['EarthquakeNo', 'ReportContent']):
                latest_eq = records[0]
                print("✅ 使用直接列表格式地震資料")
        
        # v4 新增：檢查2025年新格式（字典包含 datasetDescription）
        elif isinstance(records, dict) and 'datasetDescription' in records:
            # 2025年新格式可能直接在 records 級別包含地震數據
            if 'Earthquake' in records and isinstance(records['Earthquake'], (list, dict)):
                earthquake_data = records['Earthquake']
                if isinstance(earthquake_data, list) and len(earthquake_data) > 0:
                    latest_eq = earthquake_data[0]
                    print("✅ 使用2025年新格式列表地震資料")
                elif isinstance(earthquake_data, dict):
                    latest_eq = earthquake_data
                    print("✅ 使用2025年新格式字典地震資料")
        
        # v4 新增：處理根級別直接包含地震資料的情況
        elif isinstance(eq_data, dict) and ('EarthquakeNo' in eq_data or 'EarthquakeInfo' in eq_data):
            latest_eq = eq_data
            print("✅ 使用根層級單一地震資料")
    
    if latest_eq:
        print(f"📊 解析成功，地震編號: {latest_eq.get('EarthquakeNo', 'N/A')}")
        print(f"📄 報告內容: {latest_eq.get('ReportContent', 'N/A')[:50]}...")
        print(f"🔑 數據鍵: {list(latest_eq.keys())}")
        
        # 檢查必要欄位
        required_fields = ['ReportContent', 'EarthquakeNo']
        has_required = all(k in latest_eq for k in required_fields)
        print(f"✅ 具有必要欄位 {required_fields}: {has_required}")
        
        return latest_eq
    else:
        print("❌ 未能解析出有效的地震資料")
        return None

def simulate_enhance_earthquake_data(eq_data: Dict[str, Any]) -> Dict[str, Any]:
    """模擬enhance_earthquake_data函數"""
    print("\n🔧 模擬enhance_earthquake_data處理...")
    print("-" * 40)
    
    try:
        # 如果數據已經是一個有效的地震記錄，直接返回
        if all(k in eq_data for k in ['ReportContent', 'EarthquakeNo']):
            print("✅ 數據已經是有效的地震記錄，無需增強")
            return eq_data
            
        enhanced_data = eq_data.copy()
        
        # 確保有基本的記錄結構
        if 'records' not in enhanced_data:
            print("🔧 地震資料缺少 records 欄位，正在修復...")
            enhanced_data = {
                'records': enhanced_data
            }
        
        print("✅ 地震資料結構增強完成")
        return enhanced_data
        
    except Exception as e:
        print(f"❌ 增強地震資料時發生錯誤: {str(e)}")
        return eq_data

async def simulate_format_earthquake_data(eq_data: Dict[str, Any]) -> Optional[discord.Embed]:
    """模擬format_earthquake_data函數"""
    print("\n🎨 模擬format_earthquake_data處理...")
    print("-" * 40)
    
    try:
        # 確認必要的欄位是否存在
        required_fields = ['ReportContent', 'EarthquakeNo']
        if not all(k in eq_data for k in required_fields):
            missing = [k for k in required_fields if k not in eq_data]
            print(f"❌ 缺少必要欄位: {missing}")
            print(f"可用的欄位: {list(eq_data.keys())}")
            return None
        
        print("✅ 必要欄位檢查通過")
        
        # 取得地震資訊
        report_content = eq_data.get('ReportContent', '地震資料不完整')
        report_color = eq_data.get('ReportColor', '綠色')
        report_time = eq_data.get('OriginTime', '未知時間')
        report_web = eq_data.get('Web', '')
        report_image = eq_data.get('ReportImageURI', '')
        
        print(f"📄 報告內容: {report_content[:50]}...")
        print(f"🎨 報告顏色: {report_color}")
        
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
        
        print("✅ Discord Embed 創建成功")
        
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
            
            print("✅ 地震詳細資訊添加成功")
        
        # 添加頁尾資訊
        embed.set_footer(text=f"地震報告編號: {eq_data.get('EarthquakeNo', '未知')} | 震源時間: {report_time}")
        
        print("✅ Discord Embed 格式化完成")
        return embed
        
    except Exception as e:
        print(f"❌ 格式化地震資料時發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def test_complete_flow():
    """測試完整的earthquake指令流程"""
    print("🚀 完整earthquake指令流程測試")
    print("=" * 60)
    
    # 步驟1：模擬API數據獲取
    print("1️⃣ 模擬API數據獲取")
    eq_data = REAL_API_RESPONSE
    print(f"✅ 獲取API數據，根鍵: {list(eq_data.keys())}")
    
    # 步驟2：模擬earthquake指令解析
    print("\n2️⃣ 模擬earthquake指令解析邏輯")
    latest_eq = simulate_earthquake_parsing(eq_data)
    
    if not latest_eq:
        print("❌ 解析失敗，無法繼續")
        return False
    
    # 步驟3：模擬enhance_earthquake_data處理
    print("\n3️⃣ 模擬enhance_earthquake_data處理")
    enhanced_eq = simulate_enhance_earthquake_data(latest_eq)
    
    # 步驟4：模擬format_earthquake_data處理
    print("\n4️⃣ 模擬format_earthquake_data處理")
    embed = await simulate_format_earthquake_data(enhanced_eq)
    
    if embed:
        print("✅ 完整流程成功！")
        print(f"📝 最終Embed標題: {embed.title}")
        print(f"📄 最終Embed描述: {embed.description[:50]}...")
        print(f"🎨 最終Embed顏色: {embed.color}")
        print(f"📊 欄位數量: {len(embed.fields)}")
        return True
    else:
        print("❌ 格式化失敗")
        return False

async def main():
    """主測試函數"""
    print("🔍 完整地震指令流程問題診斷")
    print("目標：找出format_earthquake_data返回None的真正原因")
    print("=" * 80)
    
    success = await test_complete_flow()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 完整流程測試成功！")
        print("💡 這表明代碼邏輯本身沒有問題")
        print("🤔 問題可能在於：")
        print("   1. 實際API返回的數據格式與測試數據不同")
        print("   2. 某個特定條件觸發了異常路徑")
        print("   3. 環境或依賴問題")
    else:
        print("❌ 發現問題！需要進一步修復")
    
    print("🧹 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
