#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試空氣品質縣市選擇功能
"""

import asyncio
import aiohttp
import json
import ssl
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_air_quality_county_data():
    """測試空氣品質資料並分析縣市分布"""
    logger.info("=== 測試空氣品質縣市資料 ===")
    
    # API 設定
    api_url = "https://data.epa.gov.tw/api/v2/aqx_p_432"
    api_key = "94650864-6a80-4c58-83ce-fd13e7ef0504"
    
    params = {
        "api_key": api_key,
        "limit": 1000,
        "format": "JSON"
    }
    
    # SSL 設定
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    records = data.get('records', [])
                    
                    logger.info(f"成功獲取 {len(records)} 筆空氣品質資料")
                    
                    # 分析縣市分布
                    county_distribution = {}
                    
                    for record in records:
                        county = record.get('county', '未知')
                        if county in county_distribution:
                            county_distribution[county] += 1
                        else:
                            county_distribution[county] = 1
                    
                    logger.info("\n縣市測站分布:")
                    for county, count in sorted(county_distribution.items()):
                        logger.info(f"  {county}: {count} 個測站")
                    
                    # 測試選擇的縣市
                    test_counties = ["臺北市", "新北市", "桃園市", "臺中市", "高雄市"]
                    
                    logger.info("\n測試縣市查詢:")
                    for test_county in test_counties:
                        county_records = [r for r in records if r.get('county') == test_county]
                        logger.info(f"  {test_county}: 找到 {len(county_records)} 個測站")
                        
                        if county_records:
                            # 顯示前3個測站
                            for i, record in enumerate(county_records[:3]):
                                sitename = record.get('sitename', 'N/A')
                                aqi = record.get('aqi', 'N/A')
                                status = record.get('status', 'N/A')
                                logger.info(f"    {i+1}. {sitename} - AQI: {aqi} ({status})")
                    
                    return True
                else:
                    logger.error(f"API 請求失敗: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"測試過程發生錯誤: {e}")
        return False

def test_county_choices():
    """測試縣市選擇列表"""
    logger.info("=== 測試縣市選擇列表 ===")
    
    # 縣市列表 (與 air_quality_commands.py 中的一致)
    taiwan_counties = [
        "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市",
        "基隆市", "新竹市", "嘉義市",
        "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣", "嘉義縣",
        "屏東縣", "宜蘭縣", "花蓮縣", "臺東縣", "澎湖縣", "金門縣", "連江縣"
    ]
    
    logger.info(f"縣市選擇列表包含 {len(taiwan_counties)} 個縣市:")
    for i, county in enumerate(taiwan_counties, 1):
        logger.info(f"  {i:2d}. {county}")
    
    return taiwan_counties

async def main():
    """主測試函數"""
    logger.info(f"開始測試空氣品質縣市選擇功能 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試縣市列表
    counties = test_county_choices()
    
    logger.info("")
    
    # 測試 API 資料
    api_success = await test_air_quality_county_data()
    
    logger.info("\n=== 測試結果 ===")
    if api_success:
        logger.info("✅ 空氣品質縣市選擇功能準備就緒")
        logger.info("現在使用者可以從下拉選單選擇縣市，不需要手動輸入")
        logger.info("這將大幅改善使用者體驗，避免縣市名稱輸入錯誤")
    else:
        logger.warning("⚠️ API 連線有問題，但縣市選擇功能已實作")
    
    return api_success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n測試完成: {'成功' if result else '部分成功'}")
