#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
格式化函數專項測試
直接測試 format_earthquake_data 函數
"""

import sys
import os
import asyncio
import logging

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_format_function_directly():
    """直接測試格式化函數"""
    print("🔧 直接測試格式化函數")
    print("=" * 60)
    
    try:
        # 匯入必要的模組
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        
        # 創建簡單的模擬 bot
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        mock_bot.loop = asyncio.get_event_loop()
        mock_bot.wait_until_ready = AsyncMock()
        
        # 初始化 InfoCommands（但避免啟動後台任務）
        info_commands = InfoCommands(mock_bot)
        # 直接設置session而不是通過cog_load
        import aiohttp
        import ssl
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        info_commands.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        print("✅ InfoCommands 初始化完成")
        
        # 獲取真實地震數據
        print("\n📥 獲取真實地震數據...")
        earthquake_data = await info_commands.fetch_earthquake_data(small_area=False)
        
        if not earthquake_data:
            print("❌ 無法獲取地震數據")
            return False
            
        print("✅ 成功獲取地震數據")
        
        # 增強地震數據
        print("\n🔧 增強地震數據...")
        enhanced_data = await info_commands.enhance_earthquake_data(earthquake_data)
        
        if not enhanced_data:
            print("❌ 數據增強失敗")
            return False
            
        print("✅ 數據增強成功")
        
        # 格式化地震數據
        print("\n📋 格式化地震數據...")
        formatted_embed = info_commands.format_earthquake_data(enhanced_data)
        
        if formatted_embed is None:
            print("❌ 格式化失敗 - 返回 None")
            
            # 讓我們檢查數據結構
            print("\n🔍 調試增強後的數據結構:")
            print(f"Type: {type(enhanced_data)}")
            if isinstance(enhanced_data, dict):
                print(f"Keys: {list(enhanced_data.keys())}")
                if 'records' in enhanced_data:
                    print(f"Records type: {type(enhanced_data['records'])}")
                    if isinstance(enhanced_data['records'], dict):
                        print(f"Records keys: {list(enhanced_data['records'].keys())}")
            
            return False
        else:
            print("✅ 格式化成功")
            print(f"   📋 Embed 標題: {formatted_embed.title}")
            print(f"   📋 Embed 描述長度: {len(formatted_embed.description) if formatted_embed.description else 0}")
            print(f"   📋 Embed 欄位數量: {len(formatted_embed.fields)}")
            print(f"   📋 Embed 顏色: {formatted_embed.color}")
            
            # 檢查主要欄位
            for field in formatted_embed.fields:
                print(f"     - {field.name}: {field.value[:50]}...")
        
        # 同樣測試小區域地震
        print("\n🏘️ 測試小區域地震格式化...")
        small_earthquake_data = await info_commands.fetch_earthquake_data(small_area=True)
        
        if small_earthquake_data:
            enhanced_small_data = await info_commands.enhance_earthquake_data(small_earthquake_data)
            if enhanced_small_data:
                formatted_small_embed = info_commands.format_earthquake_data(enhanced_small_data)
                if formatted_small_embed:
                    print("✅ 小區域地震格式化成功")
                    print(f"   📋 標題: {formatted_small_embed.title}")
                else:
                    print("❌ 小區域地震格式化失敗")
                    return False
            else:
                print("❌ 小區域地震數據增強失敗")
                return False
        else:
            print("❌ 無法獲取小區域地震數據")
            return False
        
        print("\n" + "=" * 60)
        print("🎉 所有格式化測試通過！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理資源
        if 'info_commands' in locals() and hasattr(info_commands, 'session'):
            if info_commands.session and not info_commands.session.closed:
                await info_commands.session.close()
                print("🧹 已清理網路會話資源")

async def main():
    """主函數"""
    success = await test_format_function_directly()
    
    if success:
        print("\n🎯 格式化測試結果: ✅ 格式化功能完全正常")
        print("💡 所有地震功能修復完成！")
    else:
        print("\n🎯 格式化測試結果: ❌ 格式化仍有問題")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
