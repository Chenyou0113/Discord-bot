#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整地震功能測試
測試整個地震指令流程
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

async def test_earthquake_command_complete():
    """測試完整的地震指令功能"""
    print("🔧 測試完整的地震指令功能")
    print("=" * 60)
    
    try:
        # 匯入必要的模組
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        import aiohttp
        import ssl
        
        # 創建模擬 Discord 交互
        mock_interaction = MagicMock()
        mock_response = MagicMock()
        mock_response.defer = AsyncMock()
        mock_interaction.response = mock_response
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        
        # 創建模擬 bot
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        mock_bot.loop = asyncio.get_event_loop()
        mock_bot.wait_until_ready = AsyncMock()
        
        # 初始化 InfoCommands（不啟動背景任務）
        info_commands = InfoCommands(mock_bot)
        
        # 手動設置 session
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100, limit_per_host=30)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        info_commands.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        print("✅ 環境設置完成")
        
        # 測試一般地震指令
        print("\n📋 測試一般地震指令...")
        print("-" * 40)
        
        try:
            await info_commands.earthquake.callback(info_commands, mock_interaction, "normal")
            
            # 檢查是否有發送訊息
            if mock_interaction.followup.send.called:
                call_args = mock_interaction.followup.send.call_args
                if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                    embed = call_args[1]['embed']
                    print("✅ 一般地震指令成功生成 Discord Embed")
                    print(f"   📋 標題: {embed.title}")
                    print(f"   📋 描述: {embed.description[:100] if embed.description else 'None'}...")
                    print(f"   📋 欄位數量: {len(embed.fields)}")
                    print(f"   📋 顏色: {embed.color}")
                else:
                    print("❌ 一般地震指令沒有生成有效的 Discord Embed")
                    print(f"   詳細: {call_args}")
                    return False
            else:
                print("❌ 一般地震指令沒有發送任何訊息")
                return False
                
        except Exception as e:
            print(f"❌ 一般地震指令執行失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 重置 mock 並測試小區域地震
        mock_interaction.followup.send.reset_mock()
        
        print("\n🏘️ 測試小區域地震指令...")
        print("-" * 40)
        
        try:
            await info_commands.earthquake.callback(info_commands, mock_interaction, "small_area")
            
            # 檢查是否有發送訊息
            if mock_interaction.followup.send.called:
                call_args = mock_interaction.followup.send.call_args
                if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                    embed = call_args[1]['embed']
                    print("✅ 小區域地震指令成功生成 Discord Embed")
                    print(f"   📋 標題: {embed.title}")
                    print(f"   📋 描述: {embed.description[:100] if embed.description else 'None'}...")
                    print(f"   📋 欄位數量: {len(embed.fields)}")
                else:
                    print("❌ 小區域地震指令沒有生成有效的 Discord Embed")
                    print(f"   詳細: {call_args}")
                    return False
            else:
                print("❌ 小區域地震指令沒有發送任何訊息")
                return False
                
        except Exception as e:
            print(f"❌ 小區域地震指令執行失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        print("\n" + "=" * 60)
        print("🎉 所有地震指令測試通過！")
        print("🎯 地震功能修復完成！")
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
    success = await test_earthquake_command_complete()
    
    if success:
        print("\n🎯 最終測試結果: ✅ 地震功能完全修復")
        print("💡 Discord Bot 地震指令現在可以正常工作了！")
    else:
        print("\n🎯 最終測試結果: ❌ 還有問題需要解決")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
