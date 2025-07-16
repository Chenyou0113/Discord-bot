#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
空氣品質 API 連線診斷腳本
診斷空氣品質 API 連線問題
"""

import asyncio
import aiohttp
import json
import ssl
import logging
import socket
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def diagnose_air_quality_connection():
    """診斷空氣品質 API 連線問題"""
    logger.info("=== 空氣品質 API 連線診斷 ===")
    
    # 1. DNS 解析測試
    logger.info("1. DNS 解析測試...")
    domains = ["data.epa.gov.tw", "data.moenv.gov.tw", "google.com"]
    
    for domain in domains:
        try:
            ip = socket.gethostbyname(domain)
            logger.info(f"  ✓ {domain} -> {ip}")
        except Exception as e:
            logger.error(f"  ✗ {domain} -> {e}")
    
    # 2. 基本連線測試
    logger.info("\n2. 基本連線測試...")
    
    api_endpoints = [
        "https://data.epa.gov.tw/api/v2/aqx_p_432",
        "https://data.moenv.gov.tw/api/v2/aqx_p_432",
        "https://opendata.epa.gov.tw/api/v2/aqx_p_432"
    ]
    
    params = {
        "api_key": "94650864-6a80-4c58-83ce-fd13e7ef0504",
        "limit": 1,
        "format": "JSON"
    }
    
    # 3. 不同 SSL 配置測試
    ssl_configs = [
        {
            "name": "標準 SSL",
            "ssl": ssl.create_default_context()
        },
        {
            "name": "寬鬆 SSL",
            "ssl": None
        }
    ]
    
    # 修改寬鬆 SSL 設定
    loose_ssl = ssl.create_default_context()
    loose_ssl.check_hostname = False
    loose_ssl.verify_mode = ssl.CERT_NONE
    ssl_configs[1]["ssl"] = loose_ssl
    
    for ssl_config in ssl_configs:
        logger.info(f"\n使用 {ssl_config['name']} 設定:")
        
        for endpoint in api_endpoints:
            try:
                connector = aiohttp.TCPConnector(
                    ssl=ssl_config["ssl"],
                    force_close=True,
                    enable_cleanup_closed=True
                )
                
                timeout = aiohttp.ClientTimeout(total=15)
                
                async with aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                ) as session:
                    async with session.get(endpoint, params=params) as response:
                        logger.info(f"  ✓ {endpoint} -> HTTP {response.status}")
                        if response.status == 200:
                            data = await response.json()
                            records = data.get('records', [])
                            logger.info(f"    獲取 {len(records)} 筆資料")
                            return True  # 找到可用端點
                        
            except Exception as e:
                logger.error(f"  ✗ {endpoint} -> {str(e)[:100]}")
    
    return False

async def main():
    """主診斷函數"""
    logger.info(f"開始診斷 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    success = await diagnose_air_quality_connection()
    
    logger.info("\n=== 診斷結果 ===")
    if success:
        logger.info("✅ 找到可用的空氣品質 API 端點")
    else:
        logger.error("❌ 所有空氣品質 API 端點都無法連線")
        logger.info("建議:")
        logger.info("1. 檢查網路連線")
        logger.info("2. 檢查防火牆設定")
        logger.info("3. 稍後再試")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
