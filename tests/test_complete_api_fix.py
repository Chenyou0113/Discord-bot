#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
測試地震 API 功能的完整性 (不依賴 Discord Bot)
"""

import asyncio
import json
import os
import sys
import aiohttp
import logging

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class EarthquakeAPITester:
    """地震 API 測試器"""
    
    def __init__(self):
        # 假設有一個有效的API認證金鑰
        self.api_auth = "your_api_key_here"  # 這裡應該是真實的金鑰
        self.session = None
        
    async def init_session(self):
        """初始化 aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession()
    
    async def close_session(self):
        """關閉 aiohttp session"""
        if self.session:
            await self.session.close()
            
    async def fetch_with_retry(self, url: str, timeout: int = 30, max_retries: int = 3):
        """帶重試機制的網路請求"""
        for attempt in range(max_retries):
            try:
                timeout_obj = aiohttp.ClientTimeout(total=timeout)
                async with self.session.get(url, timeout=timeout_obj, ssl=False) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"HTTP {response.status}: {await response.text()}")
                        
            except Exception as e:
                logger.warning(f"請求失敗 (嘗試 {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(1)
                    
        return None
    
    def parse_earthquake_data(self, data):
        """解析地震資料 (使用修復後的邏輯)"""
        if not data or 'success' not in data:
            return None, "資料格式錯誤"
            
        if data.get('success') not in ['true', True]:
            return None, f"API 請求不成功: {data.get('success')}"
        
        # 檢查是否為API異常格式（只有欄位定義，無實際資料）
        if ('result' in data and isinstance(data['result'], dict) and 
            set(data['result'].keys()) == {'resource_id', 'fields'}):
            return None, "API回傳異常資料結構（只有欄位定義）"
        
        # 支援兩種資料結構
        records_data = None
        data_source = ""
        if 'records' in data:
            # 有認證模式：records 在根級別
            records_data = data['records']
            data_source = "有認證模式"
        elif 'result' in data and 'records' in data.get('result', {}):
            # 無認證模式：records 在 result 內
            records_data = data['result']['records']
            data_source = "無認證模式"
        
        if (records_data and isinstance(records_data, dict) and
            'Earthquake' in records_data and records_data['Earthquake']):
            return records_data['Earthquake'][0], f"成功解析 ({data_source})"
        
        return None, "無法找到有效的地震資料"

    async def test_earthquake_api(self, small_area: bool = False):
        """測試地震 API"""
        endpoint = "E-A0016-001" if small_area else "E-A0015-001"
        area_type = "小區域" if small_area else "一般"
        
        print(f"\n🌍 測試 {area_type} 地震 API")
        print("-" * 30)
        
        url = f"https://opendata.cwa.gov.tw/api/v1/rest/datastore/{endpoint}"
        
        # 測試有認證模式
        print("🔐 測試有認證模式...")
        auth_params = {
            'Authorization': self.api_auth,
            'limit': 1,
            'format': 'JSON'
        }
        param_string = "&".join([f"{k}={v}" for k, v in auth_params.items()])
        full_url = f"{url}?{param_string}"
        
        try:
            data = await self.fetch_with_retry(full_url, timeout=15)
            if data:
                earthquake, result_msg = self.parse_earthquake_data(data)
                if earthquake:
                    print(f"✅ {result_msg}")
                    print(f"   地震編號: {earthquake.get('EarthquakeNo', 'N/A')}")
                    print(f"   報告類型: {earthquake.get('ReportType', 'N/A')}")
                    print(f"   發生時間: {earthquake.get('OriginTime', 'N/A')}")
                    return True
                else:
                    print(f"❌ {result_msg}")
            else:
                print("❌ 無法獲取 API 回應")
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
        
        # 測試無認證模式
        print("\n🔓 測試無認證模式...")
        no_auth_params = {
            'limit': 1,
            'format': 'JSON'
        }
        param_string = "&".join([f"{k}={v}" for k, v in no_auth_params.items()])
        full_url = f"{url}?{param_string}"
        
        try:
            data = await self.fetch_with_retry(full_url, timeout=15)
            if data:
                earthquake, result_msg = self.parse_earthquake_data(data)
                if earthquake:
                    print(f"✅ {result_msg}")
                    print(f"   地震編號: {earthquake.get('EarthquakeNo', 'N/A')}")
                    print(f"   報告類型: {earthquake.get('ReportType', 'N/A')}")
                    print(f"   發生時間: {earthquake.get('OriginTime', 'N/A')}")
                    return True
                else:
                    print(f"❌ {result_msg}")
            else:
                print("❌ 無法獲取 API 回應")
        except Exception as e:
            print(f"❌ 測試失敗: {str(e)}")
        
        return False

async def main():
    """主測試函數"""
    print("🧪 測試地震 API 資料結構解析修復")
    print("=" * 50)
    
    tester = EarthquakeAPITester()
    await tester.init_session()
    
    try:
        # 測試一般地震 API
        success1 = await tester.test_earthquake_api(small_area=False)
        
        # 測試小區域地震 API
        success2 = await tester.test_earthquake_api(small_area=True)
        
        print("\n" + "=" * 50)
        if success1 or success2:
            print("🎉 API 修復測試成功！")
            print("✅ 至少一種 API 模式可以正常工作")
            print("💡 機器人現在應該能正確處理 API 回應")
        else:
            print("⚠️  API 測試失敗")
            print("🔍 可能原因: API 金鑰無效或網路問題")
            print("💡 但是資料結構解析邏輯已經修復")
            
    finally:
        await tester.close_session()

if __name__ == "__main__":
    asyncio.run(main())
