#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查溫度分布API中的圖片URL結構
"""

import asyncio
import aiohttp
import json
import ssl
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def analyze_image_url_structure():
    """分析溫度分布API中的圖片URL結構"""
    try:
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
        
        connector = aiohttp.TCPConnector(ssl=ssl_context)
        
        async with aiohttp.ClientSession(connector=connector) as session:
            async with session.get(api_url, params=params) as response:
                if response.status == 200:
                    try:
                        response_text = await response.text()
                        data = json.loads(response_text)
                    except json.JSONDecodeError:
                        data = await response.json(content_type=None)
                    
                    logger.info("=== 分析圖片URL結構 ===")
                    
                    if 'cwaopendata' in data:
                        cwa_data = data['cwaopendata']
                        dataset = cwa_data.get('dataset', {})
                        
                        # 檢查 datasetInfo
                        dataset_info = dataset.get('datasetInfo', {})
                        logger.info(f"datasetInfo 存在: {'是' if dataset_info else '否'}")
                        
                        if dataset_info:
                            logger.info(f"datasetInfo 鍵值: {list(dataset_info.keys())}")
                            
                            # 檢查 parameterSet
                            parameter_set = dataset_info.get('parameterSet', {})
                            logger.info(f"parameterSet 存在: {'是' if parameter_set else '否'}")
                            
                            if parameter_set:
                                logger.info(f"parameterSet 鍵值: {list(parameter_set.keys())}")
                                
                                # 檢查 parameter
                                parameters = parameter_set.get('parameter', [])
                                logger.info(f"parameter 類型: {type(parameters)}")
                                logger.info(f"parameter 數量: {len(parameters) if isinstance(parameters, list) else 1}")
                                
                                if isinstance(parameters, list):
                                    for i, param in enumerate(parameters):
                                        logger.info(f"參數 {i+1}:")
                                        logger.info(f"  鍵值: {list(param.keys())}")
                                        param_name = param.get('parameterName', 'N/A')
                                        param_value = param.get('parameterValue', 'N/A')
                                        logger.info(f"  參數名稱: {param_name}")
                                        logger.info(f"  參數值: {param_value}")
                                        
                                        # 檢查是否可能是圖片URL
                                        if isinstance(param_value, str):
                                            if any(keyword in param_value.lower() for keyword in ['http', 'www', '.png', '.jpg', '.gif', 'image']):
                                                logger.info(f"  ✓ 可能的圖片URL: {param_value}")
                                elif isinstance(parameters, dict):
                                    logger.info(f"參數 (單一):")
                                    logger.info(f"  鍵值: {list(parameters.keys())}")
                                    param_name = parameters.get('parameterName', 'N/A')
                                    param_value = parameters.get('parameterValue', 'N/A')
                                    logger.info(f"  參數名稱: {param_name}")
                                    logger.info(f"  參數值: {param_value}")
                                    
                                    if isinstance(param_value, str):
                                        if any(keyword in param_value.lower() for keyword in ['http', 'www', '.png', '.jpg', '.gif', 'image']):
                                            logger.info(f"  ✓ 可能的圖片URL: {param_value}")
                        
                        # 檢查其他可能的圖片來源
                        logger.info("\n=== 搜尋其他可能的圖片來源 ===")
                        
                        def search_for_urls(obj, path=""):
                            """遞迴搜尋URL"""
                            found_urls = []
                            
                            if isinstance(obj, dict):
                                for key, value in obj.items():
                                    current_path = f"{path}.{key}" if path else key
                                    if isinstance(value, str):
                                        if any(keyword in value.lower() for keyword in ['http', 'www', '.png', '.jpg', '.gif', 'image']):
                                            found_urls.append((current_path, value))
                                    else:
                                        found_urls.extend(search_for_urls(value, current_path))
                            elif isinstance(obj, list):
                                for i, item in enumerate(obj):
                                    current_path = f"{path}[{i}]"
                                    found_urls.extend(search_for_urls(item, current_path))
                            
                            return found_urls
                        
                        found_urls = search_for_urls(data)
                        
                        if found_urls:
                            logger.info(f"找到 {len(found_urls)} 個可能的URL:")
                            for path, url in found_urls:
                                logger.info(f"  路徑: {path}")
                                logger.info(f"  URL: {url}")
                                logger.info("")
                        else:
                            logger.info("未找到任何URL")
                        
                        # 檢查是否有固定的圖片URL模式
                        logger.info("=== 檢查中央氣象署溫度分布圖URL模式 ===")
                        
                        # 中央氣象署常見的溫度分布圖URL模式
                        common_patterns = [
                            "https://www.cwa.gov.tw/Data/temperature/temp_",
                            "https://opendata.cwa.gov.tw/fileapi/opendata/MIC/",
                            "https://www.cwa.gov.tw/V8/assets/img/",
                            "https://www.cwa.gov.tw/Data/fcst_img/"
                        ]
                        
                        # 嘗試構建圖片URL
                        current_time = datetime.now()
                        possible_urls = []
                        
                        # 模式1: 基於時間的URL
                        time_str = current_time.strftime("%Y%m%d%H")
                        possible_urls.append(f"https://www.cwa.gov.tw/Data/temperature/temp_{time_str}.png")
                        
                        # 模式2: 固定的溫度分布圖
                        possible_urls.append("https://www.cwa.gov.tw/V8/assets/img/weather_icon/temp_distribution.png")
                        
                        logger.info("可能的圖片URL模式:")
                        for url in possible_urls:
                            logger.info(f"  {url}")
                        
                        return found_urls
                    
                else:
                    logger.error(f"API 請求失敗: HTTP {response.status}")
                    return []
                    
    except Exception as e:
        logger.error(f"分析圖片URL結構時發生錯誤: {e}")
        return []

async def test_image_urls(urls):
    """測試圖片URL是否可用"""
    logger.info("\n=== 測試圖片URL可用性 ===")
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    connector = aiohttp.TCPConnector(ssl=ssl_context)
    
    valid_urls = []
    
    async with aiohttp.ClientSession(connector=connector) as session:
        for path, url in urls:
            try:
                async with session.head(url) as response:
                    if response.status == 200:
                        content_type = response.headers.get('content-type', '')
                        if 'image' in content_type:
                            logger.info(f"✓ 可用圖片: {url} (Content-Type: {content_type})")
                            valid_urls.append(url)
                        else:
                            logger.info(f"✗ 非圖片: {url} (Content-Type: {content_type})")
                    else:
                        logger.info(f"✗ 無法存取: {url} (HTTP {response.status})")
            except Exception as e:
                logger.info(f"✗ 錯誤: {url} ({str(e)})")
    
    return valid_urls

async def main():
    """主函數"""
    logger.info("開始分析溫度分布API的圖片URL結構")
    
    # 分析API結構
    found_urls = await analyze_image_url_structure()
    
    if found_urls:
        # 測試找到的URL
        valid_urls = await test_image_urls(found_urls)
        
        logger.info(f"\n=== 分析結果 ===")
        logger.info(f"找到的URL總數: {len(found_urls)}")
        logger.info(f"可用的圖片URL: {len(valid_urls)}")
        
        if valid_urls:
            logger.info("建議使用的圖片URL:")
            for url in valid_urls:
                logger.info(f"  {url}")
        else:
            logger.info("未找到可用的圖片URL，建議使用備用圖片方案")
    else:
        logger.info("API資料中未找到圖片URL，需要實作備用圖片方案")

if __name__ == "__main__":
    asyncio.run(main())
