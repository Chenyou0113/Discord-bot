#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終地震功能驗證
驗證地震指令修復是否成功
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

async def final_earthquake_test():
    """最終地震功能驗證"""
    print("🎯 最終地震功能驗證")
    print("=" * 50)
    
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        import aiohttp
        import ssl
        
        # 建立 Discord 交互模擬
        mock_interaction = MagicMock()
        mock_interaction.response = MagicMock()
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        
        # 建立 Bot 模擬
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        mock_bot.loop = asyncio.get_event_loop()
        mock_bot.wait_until_ready = AsyncMock()
        
        # 初始化 InfoCommands
        info_commands = InfoCommands(mock_bot)
        
        # 手動設置會話
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        info_commands.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        print("✅ 測試環境準備完成")
        
        # 測試一般地震
        print("\n🌋 測試一般地震指令...")
        success1 = await test_earthquake_type(info_commands, mock_interaction, "normal")
        
        if not success1:
            return False
        
        # 重置 mock
        mock_interaction.followup.send.reset_mock()
        
        # 測試小區域地震
        print("\n🏘️ 測試小區域地震指令...")
        success2 = await test_earthquake_type(info_commands, mock_interaction, "small_area")
        
        if not success2:
            return False
        
        print("\n" + "=" * 50)
        print("🎉 所有測試成功！地震功能完全修復！")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        if 'info_commands' in locals() and hasattr(info_commands, 'session'):
            if info_commands.session and not info_commands.session.closed:
                await info_commands.session.close()

async def test_earthquake_type(info_commands, mock_interaction, eq_type):
    """測試特定類型的地震指令"""
    try:
        # 執行地震指令
        await info_commands.earthquake.callback(info_commands, mock_interaction, eq_type)
        
        # 檢查結果
        if mock_interaction.followup.send.called:
            call_args = mock_interaction.followup.send.call_args
            print(f"🔍 {eq_type} 指令調用參數: {call_args}")
            
            if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                embed = call_args[1]['embed']
                print(f"✅ {eq_type} 地震指令成功")
                print(f"   標題: {embed.title}")
                print(f"   描述: {embed.description[:80] if embed.description else 'None'}...")
                print(f"   欄位數: {len(embed.fields)}")
                return True
            else:
                print(f"❌ {eq_type} 地震指令沒有生成 embed")
                print(f"   調用參數詳細: {call_args}")
                return False
        else:
            print(f"❌ {eq_type} 地震指令沒有發送訊息")
            return False
            
    except Exception as e:
        print(f"❌ {eq_type} 地震指令執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函數"""
    success = await final_earthquake_test()
    
    if success:
        print("\n🎯 最終結果: ✅ 地震功能完全修復")
        print("💡 Discord Bot 地震指令現在可以正常使用！")
    else:
        print("\n🎯 最終結果: ❌ 還有問題需要解決")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
