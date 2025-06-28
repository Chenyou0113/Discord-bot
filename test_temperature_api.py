#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試溫度分布 API 資料結構
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

async def test_temperature_distribution_api():
    """測試溫度分布 API"""
    logger.info("=== 測試溫度分布 API ===")
    
    # API 設定
    api_url = "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0038-001"
    authorization = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"
    
    params = {
        "Authorization": authorization,
        "downloadType": "WEB",
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
                logger.info(f"API 回應狀態: {response.status}")
                logger.info(f"Content-Type: {response.content_type}")
                
                if response.status == 200:
                    # 使用雙重解析機制（與雷達圖相同）
                    try:
                        response_text = await response.text()
                        data = json.loads(response_text)
                        logger.info("✓ 文本解析成功")
                    except json.JSONDecodeError:
                        try:
                            data = await response.json(content_type=None)
                            logger.info("✓ 備用解析成功")
                        except Exception as e2:
                            logger.error(f"✗ 備用解析也失敗: {e2}")
                            return False
                    
                    # 分析資料結構
                    logger.info("\n=== 資料結構分析 ===")
                    
                    if isinstance(data, dict):
                        logger.info(f"根層級鍵: {list(data.keys())}")
                        
                        if 'cwaopendata' in data:
                            cwa_data = data['cwaopendata']
                            logger.info(f"cwaopendata 鍵: {list(cwa_data.keys())}")
                            
                            # 基本資訊
                            logger.info(f"識別碼: {cwa_data.get('identifier', 'N/A')}")
                            logger.info(f"發送時間: {cwa_data.get('sent', 'N/A')}")
                            
                            # 資料集資訊
                            if 'dataset' in cwa_data:
                                dataset = cwa_data['dataset']
                                logger.info(f"資料時間: {dataset.get('DateTime', 'N/A')}")
                                
                                if 'datasetInfo' in dataset:
                                    dataset_info = dataset['datasetInfo']
                                    logger.info(f"資料集描述: {dataset_info.get('datasetDescription', 'N/A')}")
                                    
                                    # 參數資訊
                                    if 'parameterSet' in dataset_info:
                                        parameter_set = dataset_info['parameterSet']
                                        if 'parameter' in parameter_set:
                                            parameters = parameter_set['parameter']
                                            logger.info(f"參數數量: {len(parameters) if isinstance(parameters, list) else 1}")
                                            
                                            # 分析第一個參數
                                            if isinstance(parameters, list) and parameters:
                                                first_param = parameters[0]
                                                logger.info("\n=== 第一個參數分析 ===")
                                                for key, value in first_param.items():
                                                    if isinstance(value, str) and len(value) > 100:
                                                        logger.info(f"{key}: {value[:100]}... (長度: {len(value)})")
                                                    else:
                                                        logger.info(f"{key}: {value}")
                                            
                                            # 檢查是否有圖片 URL
                                            for i, param in enumerate(parameters[:3] if isinstance(parameters, list) else [parameters]):
                                                if 'parameterValue' in param:
                                                    value = param['parameterValue']
                                                    if isinstance(value, str) and ('http' in value or 'www' in value):
                                                        logger.info(f"參數 {i+1} 圖片 URL: {value}")
                                
                                # 位置資訊
                                if 'location' in dataset:
                                    locations = dataset['location']
                                    logger.info(f"位置數量: {len(locations) if isinstance(locations, list) else 1}")
                                    
                                    if isinstance(locations, list) and locations:
                                        first_location = locations[0]
                                        logger.info(f"\n=== 第一個位置資訊 ===")
                                        logger.info(f"位置名稱: {first_location.get('locationName', 'N/A')}")
                                        logger.info(f"經度: {first_location.get('lon', 'N/A')}")
                                        logger.info(f"緯度: {first_location.get('lat', 'N/A')}")
                                        
                                        if 'stationObsTimes' in first_location:
                                            obs_times = first_location['stationObsTimes']
                                            if 'stationObsTime' in obs_times:
                                                obs_time_list = obs_times['stationObsTime']
                                                logger.info(f"觀測時間數量: {len(obs_time_list) if isinstance(obs_time_list, list) else 1}")
                                                
                                                if isinstance(obs_time_list, list) and obs_time_list:
                                                    first_obs = obs_time_list[0]
                                                    logger.info(f"第一個觀測時間: {first_obs.get('DateTime', 'N/A')}")
                                                    
                                                    if 'weatherElements' in first_obs:
                                                        weather_elements = first_obs['weatherElements']
                                                        if 'weatherElement' in weather_elements:
                                                            elements = weather_elements['weatherElement']
                                                            logger.info(f"氣象要素數量: {len(elements) if isinstance(elements, list) else 1}")
                                                            
                                                            # 分析氣象要素
                                                            for element in (elements if isinstance(elements, list) else [elements]):
                                                                element_name = element.get('elementName', 'N/A')
                                                                element_value = element.get('elementValue', 'N/A')
                                                                logger.info(f"  {element_name}: {element_value}")
                    
                    return True
                else:
                    logger.error(f"✗ API 請求失敗: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"✗ 測試過程發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info(f"開始測試溫度分布 API - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_temperature_distribution_api()
    
    logger.info("\n=== 測試結果 ===")
    if success:
        logger.info("✅ 溫度分布 API 連線成功")
        logger.info("可以開始實作溫度分布查詢功能")
    else:
        logger.error("❌ 溫度分布 API 連線失敗")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n測試完成: {'成功' if result else '失敗'}")
