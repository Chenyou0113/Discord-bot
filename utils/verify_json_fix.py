#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
針對 JSON 解析問題的修復驗證腳本
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

async def test_json_parsing_fix():
    """測試 JSON 解析修復是否有效"""
    logger.info("=== 測試 JSON 解析修復 ===")
    
    # API 配置 - 使用會返回 binary/octet-stream 的 API
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
                logger.info(f"API 回應狀態: {response.status}")
                logger.info(f"Content-Type: {response.content_type}")
                
                if response.status == 200:
                    logger.info("開始測試雙重解析機制...")
                    
                    # 測試方法 1: 標準 response.json() (預期會失敗)
                    try:
                        data_standard = await response.json()
                        logger.info("✓ 標準解析成功 (意外!)")
                        method_used = "standard"
                        data = data_standard
                    except Exception as e:
                        logger.warning(f"✗ 標準解析失敗 (預期): {e}")
                        
                        # 測試方法 2: 文本 + json.loads
                        try:
                            response_text = await response.text()
                            data = json.loads(response_text)
                            logger.info("✓ 文本解析成功!")
                            method_used = "text+json.loads"
                        except json.JSONDecodeError as e2:
                            logger.warning(f"✗ 文本解析失敗: {e2}")
                            
                            # 測試方法 3: 強制 JSON 解析
                            try:
                                # 需要重新請求，因為 response 已經被讀取過
                                async with session.get(api_url, params=params) as response2:
                                    data = await response2.json(content_type=None)
                                    logger.info("✓ 強制解析成功!")
                                    method_used = "json(content_type=None)"
                            except Exception as e3:
                                logger.error(f"✗ 強制解析也失敗: {e3}")
                                return False
                    
                    # 驗證資料結構
                    if 'cwaopendata' in data:
                        logger.info("✓ 資料結構驗證通過")
                        dataset = data['cwaopendata'].get('dataset', {})
                        logger.info(f"資料時間: {dataset.get('DateTime', 'N/A')}")
                        logger.info(f"成功解析方法: {method_used}")
                        
                        # 檢查圖片 URL
                        dataset_info = dataset.get('datasetInfo', {})
                        if dataset_info:
                            parameter_set = dataset_info.get('parameterSet', {})
                            parameter = parameter_set.get('parameter', {})
                            if isinstance(parameter, list) and parameter:
                                first_param = parameter[0]
                                image_url = first_param.get('parameterValue', '')
                                if image_url:
                                    logger.info(f"圖片 URL: {image_url[:100]}...")
                        
                        return True
                    else:
                        logger.error("✗ 資料結構異常")
                        logger.info(f"實際資料鍵: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                        return False
                else:
                    logger.error(f"✗ API 請求失敗: HTTP {response.status}")
                    return False
                    
    except Exception as e:
        logger.error(f"✗ 測試過程發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info(f"開始 JSON 解析修復驗證 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await test_json_parsing_fix()
    
    logger.info("=== 測試結果 ===")
    if success:
        logger.info("✅ JSON 解析修復驗證成功!")
        logger.info("雷達圖 API 可以正常處理 binary/octet-stream MIME 類型")
    else:
        logger.error("❌ JSON 解析修復驗證失敗!")
        logger.error("需要檢查代碼實現或 API 狀況")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    if result:
        print("\n🎉 修復驗證成功! 可以繼續使用機器人。")
    else:
        print("\n⚠️ 修復驗證失敗! 需要進一步檢查。")
