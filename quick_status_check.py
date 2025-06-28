#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速狀態檢查腳本
檢查所有 API 的當前狀況
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

async def test_radar_api():
    """測試雷達圖 API"""
    logger.info("=== 測試雷達圖 API ===")
    
    # API 配置
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(api_url, params=params) as response:
                logger.info(f"雷達圖 API 回應狀態: {response.status}")
                logger.info(f"回應 Content-Type: {response.content_type}")
                
                if response.status == 200:
                    # 測試雙重解析機制
                    try:
                        response_text = await response.text()
                        data = json.loads(response_text)
                        logger.info("✓ 文本解析成功")
                    except json.JSONDecodeError as e:
                        logger.warning(f"文本解析失敗: {e}")
                        try:
                            data = await response.json(content_type=None)
                            logger.info("✓ 備用解析成功")
                        except Exception as e2:
                            logger.error(f"備用解析也失敗: {e2}")
                            return False
                    
                    # 檢查資料結構
                    if 'cwaopendata' in data:
                        logger.info("✓ 資料結構正確")
                        dataset = data['cwaopendata'].get('dataset', {})
                        logger.info(f"資料時間: {dataset.get('DateTime', 'N/A')}")
                        return True
                    else:
                        logger.error("✗ 資料結構異常")
                        return False
                else:
                    logger.error(f"✗ API 請求失敗: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"✗ 雷達圖 API 測試失敗: {e}")
        return False

async def test_air_quality_api():
    """測試空氣品質 API"""
    logger.info("=== 測試空氣品質 API ===")
    
    api_url = "https://data.epa.gov.tw/api/v2/aqx_p_432"
    api_key = "94650864-6a80-4c58-83ce-fd13e7ef0504"
    
    params = {
        "api_key": api_key,
        "limit": 10,
        "format": "JSON"
    }
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(api_url, params=params) as response:
                logger.info(f"空氣品質 API 回應狀態: {response.status}")
                logger.info(f"回應 Content-Type: {response.content_type}")
                
                if response.status == 200:
                    data = await response.json()
                    records = data.get('records', [])
                    logger.info(f"✓ 成功獲取 {len(records)} 筆空氣品質資料")
                    
                    if records:
                        sample_record = records[0]
                        logger.info(f"範例測站: {sample_record.get('sitename', 'N/A')}")
                        logger.info(f"AQI: {sample_record.get('aqi', 'N/A')}")
                        logger.info(f"更新時間: {sample_record.get('publishtime', 'N/A')}")
                    
                    return True
                else:
                    logger.error(f"✗ API 請求失敗: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"✗ 空氣品質 API 測試失敗: {e}")
        return False

async def test_rainfall_radar_api():
    """測試降雨雷達 API"""
    logger.info("=== 測試降雨雷達 API (樹林) ===")
    
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-001"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
        "format": "JSON"
    }
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            async with session.get(api_url, params=params) as response:
                logger.info(f"降雨雷達 API 回應狀態: {response.status}")
                logger.info(f"回應 Content-Type: {response.content_type}")
                
                if response.status == 200:
                    # 測試雙重解析機制
                    try:
                        response_text = await response.text()
                        data = json.loads(response_text)
                        logger.info("✓ 文本解析成功")
                    except json.JSONDecodeError as e:
                        logger.warning(f"文本解析失敗: {e}")
                        try:
                            data = await response.json(content_type=None)
                            logger.info("✓ 備用解析成功")
                        except Exception as e2:
                            logger.error(f"備用解析也失敗: {e2}")
                            return False
                    
                    # 檢查資料結構
                    if 'cwaopendata' in data:
                        logger.info("✓ 資料結構正確")
                        dataset = data['cwaopendata'].get('dataset', {})
                        logger.info(f"資料時間: {dataset.get('DateTime', 'N/A')}")
                        return True
                    else:
                        logger.error("✗ 資料結構異常")
                        return False
                else:
                    logger.error(f"✗ API 請求失敗: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"✗ 降雨雷達 API 測試失敗: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info(f"開始 API 狀態檢查 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 測試所有 API
    radar_ok = await test_radar_api()
    air_quality_ok = await test_air_quality_api()
    rainfall_radar_ok = await test_rainfall_radar_api()
    
    logger.info("=== 測試結果摘要 ===")
    logger.info(f"雷達圖 API: {'✓ 正常' if radar_ok else '✗ 異常'}")
    logger.info(f"空氣品質 API: {'✓ 正常' if air_quality_ok else '✗ 異常'}")
    logger.info(f"降雨雷達 API: {'✓ 正常' if rainfall_radar_ok else '✗ 異常'}")
    
    all_ok = radar_ok and air_quality_ok and rainfall_radar_ok
    logger.info(f"整體狀態: {'✓ 所有 API 正常' if all_ok else '✗ 有 API 異常'}")
    
    return all_ok

if __name__ == "__main__":
    asyncio.run(main())
