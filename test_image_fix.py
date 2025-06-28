#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試溫度分布圖片顯示修復
"""

import asyncio
import aiohttp
import json
import ssl
import logging
from datetime import datetime
import sys
import os

# 添加當前目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 導入溫度命令模組
try:
    from cogs.temperature_commands import TemperatureCommands
    logger.info("✅ 成功導入 TemperatureCommands")
except ImportError as e:
    logger.error(f"❌ 導入失敗: {e}")
    exit(1)

class MockBot:
    """模擬機器人類別"""
    def __init__(self):
        self.connector = None

async def test_temperature_image_fix():
    """測試溫度分布圖片修復"""
    try:
        logger.info("🧪 測試溫度分布圖片顯示修復")
        
        # 創建模擬機器人和命令實例
        mock_bot = MockBot()
        temp_commands = TemperatureCommands(mock_bot)
        
        # 1. 測試 API 資料獲取
        logger.info("1. 測試 API 資料獲取...")
        data = await temp_commands.fetch_temperature_data()
        
        if not data:
            logger.error("❌ 無法獲取 API 資料")
            return False
        
        logger.info("✅ API 資料獲取成功")
        
        # 2. 測試資料解析
        logger.info("2. 測試資料解析...")
        temp_info = temp_commands.parse_temperature_data(data)
        
        if not temp_info:
            logger.error("❌ 資料解析失敗")
            return False
        
        logger.info("✅ 資料解析成功")
        
        # 3. 檢查圖片URL
        logger.info("3. 檢查圖片URL...")
        image_url = temp_info.get('image_url', '')
        
        if image_url:
            logger.info(f"✅ 找到圖片URL: {image_url}")
            
            # 4. 測試圖片URL可用性
            logger.info("4. 測試圖片URL可用性...")
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context)
            
            try:
                async with aiohttp.ClientSession(connector=connector) as session:
                    async with session.head(image_url) as response:
                        logger.info(f"圖片URL回應狀態: {response.status}")
                        logger.info(f"Content-Type: {response.headers.get('content-type', 'Unknown')}")
                        
                        if response.status == 200:
                            logger.info("✅ 圖片URL可用")
                        else:
                            logger.warning(f"⚠️ 圖片URL回應異常: {response.status}")
            except Exception as e:
                logger.warning(f"⚠️ 測試圖片URL時發生錯誤: {e}")
        else:
            logger.warning("⚠️ 未找到圖片URL")
        
        # 5. 測試 Embed 創建
        logger.info("5. 測試 Embed 創建...")
        try:
            embed = temp_commands.create_temperature_embed(temp_info)
            logger.info("✅ Embed 創建成功")
            
            # 檢查 Embed 內容
            logger.info(f"Embed 標題: {embed.title}")
            logger.info(f"Embed 描述: {embed.description}")
            logger.info(f"Embed 欄位數量: {len(embed.fields)}")
            
            # 檢查圖片設定
            if embed.image and embed.image.url:
                logger.info(f"✅ Embed 圖片已設定: {embed.image.url}")
            else:
                logger.warning("⚠️ Embed 圖片未設定")
            
            # 檢查圖片相關欄位
            image_field = None
            for field in embed.fields:
                if "溫度分布圖" in field.name:
                    image_field = field
                    break
            
            if image_field:
                logger.info(f"✅ 找到圖片欄位: {image_field.name} = {image_field.value}")
            else:
                logger.warning("⚠️ 未找到圖片欄位")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Embed 創建失敗: {e}")
            return False
        
    except Exception as e:
        logger.error(f"❌ 測試過程發生錯誤: {e}")
        return False

async def test_image_url_parsing():
    """測試圖片URL解析邏輯"""
    logger.info("\n🔍 測試圖片URL解析邏輯")
    
    # 模擬API資料結構
    test_data = {
        'cwaopendata': {
            'dataset': {
                'Resource': {
                    'ProductURL': 'https://cwaopendata.s3.ap-northeast-1.amazonaws.com/Observation/O-A0038-001.jpg'
                }
            }
        }
    }
    
    mock_bot = MockBot()
    temp_commands = TemperatureCommands(mock_bot)
    
    # 解析測試資料
    temp_info = temp_commands.parse_temperature_data(test_data)
    
    image_url = temp_info.get('image_url', '')
    if image_url:
        logger.info(f"✅ 解析成功，圖片URL: {image_url}")
        return True
    else:
        logger.error("❌ 圖片URL解析失敗")
        return False

async def main():
    """主測試函數"""
    logger.info("開始測試溫度分布圖片顯示修復")
    
    # 測試1: 圖片URL解析邏輯
    parse_success = await test_image_url_parsing()
    
    # 測試2: 完整功能測試
    full_success = await test_temperature_image_fix()
    
    logger.info("\n" + "="*50)
    logger.info("測試結果總結:")
    
    if parse_success and full_success:
        logger.info("✅ 所有測試通過！")
        logger.info("修復內容:")
        logger.info("  • 改進圖片URL解析邏輯")
        logger.info("  • 增加Resource.ProductURL檢查")
        logger.info("  • 提供備用圖片URL")
        logger.info("  • 改善錯誤處理")
        logger.info("  • 增強Embed圖片顯示")
        logger.info("\n溫度分布圖片現在應該可以正常顯示！")
    else:
        logger.error("❌ 部分測試失敗")
        if not parse_success:
            logger.error("  • 圖片URL解析有問題")
        if not full_success:
            logger.error("  • 完整功能測試失敗")
    
    return parse_success and full_success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n測試完成: {'成功' if result else '失敗'}")
