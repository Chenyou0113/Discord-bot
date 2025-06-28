#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化狀態檢查腳本
"""

import asyncio
import aiohttp
import json
import ssl
import logging

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def quick_test():
    """快速測試所有 API"""
    
    # 測試配置
    tests = [
        {
            "name": "雷達圖 API",
            "url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0058-003",
            "params": {
                "Authorization": "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A",
                "downloadType": "WEB",
                "format": "JSON"
            }
        },
        {
            "name": "空氣品質 API",
            "url": "https://data.epa.gov.tw/api/v2/aqx_p_432",
            "params": {
                "api_key": "94650864-6a80-4c58-83ce-fd13e7ef0504",
                "limit": 5,
                "format": "JSON"
            }
        },
        {
            "name": "降雨雷達 API",
            "url": "https://opendata.cwa.gov.tw/fileapi/v1/opendataapi/O-A0084-001",
            "params": {
                "Authorization": "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A",
                "downloadType": "WEB",
                "format": "JSON"
            }
        }
    ]
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    results = []
    
    for test in tests:
        try:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            timeout = aiohttp.ClientTimeout(total=15)
            
            async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
                async with session.get(test["url"], params=test["params"]) as response:
                    status = response.status
                    content_type = response.content_type
                    
                    if status == 200:
                        # 嘗試解析資料
                        try:
                            if "cwa.gov.tw" in test["url"]:
                                # 雷達圖 API - 使用雙重解析
                                try:
                                    response_text = await response.text()
                                    data = json.loads(response_text)
                                    parse_method = "text"
                                except json.JSONDecodeError:
                                    data = await response.json(content_type=None)
                                    parse_method = "json"
                                
                                # 檢查資料結構
                                if 'cwaopendata' in data:
                                    result = f"✓ {test['name']}: 正常 (解析方式: {parse_method})"
                                else:
                                    result = f"✗ {test['name']}: 資料結構異常"
                            else:
                                # 空氣品質 API
                                data = await response.json()
                                records = data.get('records', [])
                                result = f"✓ {test['name']}: 正常 ({len(records)} 筆資料)"
                        except Exception as e:
                            result = f"✗ {test['name']}: 解析失敗 - {e}"
                    else:
                        result = f"✗ {test['name']}: HTTP {status}"
                        
                    results.append(result)
                    logger.info(result)
                    
        except Exception as e:
            result = f"✗ {test['name']}: 連線失敗 - {e}"
            results.append(result)
            logger.info(result)
    
    logger.info("=== 測試完成 ===")
    return results

if __name__ == "__main__":
    asyncio.run(quick_test())
