#!/usr/bin/env python3
"""
測試 enhance_earthquake_data 函數問題
找出為什麼它會破壞數據結構
"""
import asyncio
import logging
from typing import Dict, Any
import datetime

# 設置日誌
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 模擬原始地震數據（從API獲取的標準格式）
STANDARD_EARTHQUAKE_DATA = {
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

def enhance_earthquake_data_original(eq_data: Dict[str, Any]) -> Dict[str, Any]:
    """原始的 enhance_earthquake_data 函數 (複製自代碼)"""
    try:
        enhanced_data = eq_data.copy()
        
        # 確保有基本的記錄結構
        if 'records' not in enhanced_data:
            logger.info("🔧 地震資料缺少 records 欄位，正在修復...")
            enhanced_data = {
                'records': enhanced_data
            }
        
        # 確保記錄中有 Earthquake 結構
        if isinstance(enhanced_data.get('records'), dict):
            records = enhanced_data['records']
            
            # 如果 records 直接包含地震資料，包裝為 Earthquake 結構
            if 'EarthquakeNo' in records or 'EarthquakeInfo' in records:
                logger.info("🔧 將根層級地震資料包裝為標準 Earthquake 結構...")
                enhanced_data['records'] = {
                    'Earthquake': [records]
                }
            # 如果已經有 Earthquake 但是字典格式，轉換為列表格式
            elif 'Earthquake' in records and isinstance(records['Earthquake'], dict):
                logger.info("🔧 將字典格式 Earthquake 轉換為列表格式...")
                enhanced_data['records']['Earthquake'] = [records['Earthquake']]
        
        # 確保地震資料完整性
        if 'records' in enhanced_data and 'Earthquake' in enhanced_data['records']:
            earthquakes = enhanced_data['records']['Earthquake']
            if isinstance(earthquakes, list) and len(earthquakes) > 0:
                eq = earthquakes[0]
                
                # 修復缺失的基本欄位
                if 'EarthquakeNo' not in eq:
                    eq['EarthquakeNo'] = f"UNKNOWN_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    logger.info("🔧 補充缺失的 EarthquakeNo 欄位")
                
                # 確保有基本的地震資訊結構
                if 'EarthquakeInfo' not in eq:
                    eq['EarthquakeInfo'] = {}
                    logger.info("🔧 補充缺失的 EarthquakeInfo 結構")
                
                # 確保有震央位置資訊
                if 'Epicenter' not in eq['EarthquakeInfo']:
                    eq['EarthquakeInfo']['Epicenter'] = {}
                    logger.info("🔧 補充缺失的 Epicenter 結構")
                
                # 確保有規模資訊
                if 'EarthquakeMagnitude' not in eq['EarthquakeInfo']:
                    eq['EarthquakeInfo']['EarthquakeMagnitude'] = {}
                    logger.info("🔧 補充缺失的 EarthquakeMagnitude 結構")
        
        logger.info("✅ 地震資料結構增強完成")
        return enhanced_data
        
    except Exception as e:
        logger.error(f"增強地震資料時發生錯誤: {str(e)}")
        return eq_data  # 返回原始資料

def enhance_earthquake_data_fixed(eq_data: Dict[str, Any]) -> Dict[str, Any]:
    """修復後的 enhance_earthquake_data 函數"""
    try:
        # 如果數據已經是一個有效的地震記錄，直接返回
        if all(k in eq_data for k in ['ReportContent', 'EarthquakeNo']):
            logger.info("✅ 數據已經是有效的地震記錄，無需增強")
            return eq_data
            
        enhanced_data = eq_data.copy()
        
        # 確保有基本的記錄結構
        if 'records' not in enhanced_data:
            logger.info("🔧 地震資料缺少 records 欄位，正在修復...")
            enhanced_data = {
                'records': enhanced_data
            }
        
        # 確保記錄中有 Earthquake 結構
        if isinstance(enhanced_data.get('records'), dict):
            records = enhanced_data['records']
            
            # 如果 records 直接包含地震資料，包裝為 Earthquake 結構
            if 'EarthquakeNo' in records or 'EarthquakeInfo' in records:
                logger.info("🔧 將根層級地震資料包裝為標準 Earthquake 結構...")
                enhanced_data['records'] = {
                    'Earthquake': [records]
                }
            # 如果已經有 Earthquake 但是字典格式，轉換為列表格式
            elif 'Earthquake' in records and isinstance(records['Earthquake'], dict):
                logger.info("🔧 將字典格式 Earthquake 轉換為列表格式...")
                enhanced_data['records']['Earthquake'] = [records['Earthquake']]
        
        # 確保地震資料完整性
        if 'records' in enhanced_data and 'Earthquake' in enhanced_data['records']:
            earthquakes = enhanced_data['records']['Earthquake']
            if isinstance(earthquakes, list) and len(earthquakes) > 0:
                eq = earthquakes[0]
                
                # 修復缺失的基本欄位
                if 'EarthquakeNo' not in eq:
                    eq['EarthquakeNo'] = f"UNKNOWN_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
                    logger.info("🔧 補充缺失的 EarthquakeNo 欄位")
                
                # 確保有基本的地震資訊結構
                if 'EarthquakeInfo' not in eq:
                    eq['EarthquakeInfo'] = {}
                    logger.info("🔧 補充缺失的 EarthquakeInfo 結構")
                
                # 確保有震央位置資訊
                if 'Epicenter' not in eq['EarthquakeInfo']:
                    eq['EarthquakeInfo']['Epicenter'] = {}
                    logger.info("🔧 補充缺失的 Epicenter 結構")
                
                # 確保有規模資訊
                if 'EarthquakeMagnitude' not in eq['EarthquakeInfo']:
                    eq['EarthquakeInfo']['EarthquakeMagnitude'] = {}
                    logger.info("🔧 補充缺失的 EarthquakeMagnitude 結構")
        
        logger.info("✅ 地震資料結構增強完成")
        return enhanced_data
        
    except Exception as e:
        logger.error(f"增強地震資料時發生錯誤: {str(e)}")
        return eq_data  # 返回原始資料

async def test_enhance_function():
    """測試 enhance_earthquake_data 函數"""
    print("🧪 測試 enhance_earthquake_data 函數")
    print("=" * 60)
    
    # 測試原始函數
    print("\n1️⃣ 測試原始 enhance_earthquake_data 函數...")
    print(f"輸入數據類型: {type(STANDARD_EARTHQUAKE_DATA)}")
    print(f"輸入數據具有必要欄位: {all(k in STANDARD_EARTHQUAKE_DATA for k in ['ReportContent', 'EarthquakeNo'])}")
    
    enhanced_original = enhance_earthquake_data_original(STANDARD_EARTHQUAKE_DATA)
    
    print(f"\n原始函數處理後的結構:")
    print(f"- 根級別鍵: {list(enhanced_original.keys())}")
    if 'records' in enhanced_original:
        print(f"- records 類型: {type(enhanced_original['records'])}")
        if isinstance(enhanced_original['records'], dict):
            print(f"- records 鍵: {list(enhanced_original['records'].keys())}")
            if 'Earthquake' in enhanced_original['records']:
                print(f"- Earthquake 類型: {type(enhanced_original['records']['Earthquake'])}")
                if isinstance(enhanced_original['records']['Earthquake'], list):
                    if len(enhanced_original['records']['Earthquake']) > 0:
                        eq_data = enhanced_original['records']['Earthquake'][0]
                        print(f"- 第一個地震記錄具有必要欄位: {all(k in eq_data for k in ['ReportContent', 'EarthquakeNo'])}")
                        print(f"- 第一個地震記錄鍵: {list(eq_data.keys())[:10]}...")  # 只顯示前10個鍵
    
    # 測試修復後的函數
    print("\n2️⃣ 測試修復後 enhance_earthquake_data 函數...")
    enhanced_fixed = enhance_earthquake_data_fixed(STANDARD_EARTHQUAKE_DATA)
    
    print(f"\n修復後函數處理後的結構:")
    print(f"- 根級別鍵: {list(enhanced_fixed.keys())}")
    print(f"- 具有必要欄位: {all(k in enhanced_fixed for k in ['ReportContent', 'EarthquakeNo'])}")
    
    # 比較結果
    print("\n3️⃣ 結果比較:")
    original_has_required = False
    fixed_has_required = False
    
    # 檢查原始函數結果是否有必要欄位
    if ('records' in enhanced_original and 
        isinstance(enhanced_original['records'], dict) and
        'Earthquake' in enhanced_original['records'] and
        isinstance(enhanced_original['records']['Earthquake'], list) and
        len(enhanced_original['records']['Earthquake']) > 0):
        eq_data = enhanced_original['records']['Earthquake'][0]
        original_has_required = all(k in eq_data for k in ['ReportContent', 'EarthquakeNo'])
    
    # 檢查修復後函數結果是否有必要欄位
    fixed_has_required = all(k in enhanced_fixed for k in ['ReportContent', 'EarthquakeNo'])
    
    print(f"原始函數結果可以直接格式化: {original_has_required}")
    print(f"修復後函數結果可以直接格式化: {fixed_has_required}")
    
    if fixed_has_required and not original_has_required:
        print("✅ 修復成功！修復後的函數保持了數據的直接可用性")
        return True
    else:
        print("❌ 修復未達到預期效果")
        return False

async def main():
    """主測試函數"""
    print("🚀 enhance_earthquake_data 函數問題診斷")
    print("目標：找出並修復 enhance_earthquake_data 函數破壞數據結構的問題")
    print("=" * 60)
    
    success = await test_enhance_function()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 問題診斷成功！需要修復 enhance_earthquake_data 函數")
        print("💡 建議：修改函數以避免對已經有效的地震記錄進行不必要的包裝")
    else:
        print("❌ 需要進一步調查問題")
    
    print("🧹 測試完成")

if __name__ == "__main__":
    asyncio.run(main())
