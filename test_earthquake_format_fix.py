#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
地震指令格式化測試
測試完整的地震指令流程，包括數據獲取、增強和格式化
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

async def test_earthquake_command_format():
    """測試地震指令的完整格式化流程"""
    print("🔧 測試地震指令完整格式化流程")
    print("=" * 60)
    
    try:
        # 模擬 Discord 環境
        from unittest.mock import MagicMock, AsyncMock
        
        # 匯入修復後的 InfoCommands
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        
        # 創建更完整的模擬 Bot
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        mock_bot.loop = asyncio.get_event_loop()
        
        # 初始化 InfoCommands
        info_commands = InfoCommands(mock_bot)
        await info_commands.cog_load()
        
        # 創建模擬 Discord 上下文
        mock_ctx = MagicMock()
        mock_channel = MagicMock()
        mock_channel.send = AsyncMock()
        mock_ctx.send = AsyncMock()
        mock_ctx.channel = mock_channel
        
        print("✅ Bot 和環境設置完成")
        
        # 測試一般地震指令
        print("\n📋 測試一般地震指令...")
        print("-" * 40)
        
        try:
            # 執行地震指令
            await info_commands.earthquake.callback(info_commands, mock_ctx)
            
            # 檢查是否有發送訊息
            if mock_ctx.send.called:
                call_args = mock_ctx.send.call_args
                if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                    embed = call_args[1]['embed']
                    print("✅ 一般地震指令成功生成 Discord Embed")
                    print(f"   📋 標題: {embed.title}")
                    print(f"   📋 描述長度: {len(embed.description) if embed.description else 0} 字元")
                    print(f"   📋 欄位數量: {len(embed.fields) if embed.fields else 0}")
                else:
                    print("❌ 地震指令沒有生成有效的 Discord Embed")
                    print(f"   詳細: {call_args}")
                    return False
            else:
                print("❌ 地震指令沒有發送任何訊息")
                return False
                
        except Exception as e:
            print(f"❌ 一般地震指令執行失敗: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
        
        # 測試小區域地震指令
        print("\n🏘️ 測試小區域地震指令...")
        print("-" * 40)
        
        # 重置 mock
        mock_ctx.send.reset_mock()
        
        try:
            # 執行小區域地震指令
            await info_commands.small_earthquake.callback(info_commands, mock_ctx)
            
            # 檢查是否有發送訊息
            if mock_ctx.send.called:
                call_args = mock_ctx.send.call_args
                if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                    embed = call_args[1]['embed']
                    print("✅ 小區域地震指令成功生成 Discord Embed")
                    print(f"   📋 標題: {embed.title}")
                    print(f"   📋 描述長度: {len(embed.description) if embed.description else 0} 字元")
                    print(f"   📋 欄位數量: {len(embed.fields) if embed.fields else 0}")
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
        print("🎉 所有地震指令格式化測試通過！")
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
    success = await test_earthquake_command_format()
    
    if success:
        print("\n🎯 格式化測試結果: ✅ 地震指令完全正常")
        print("💡 建議: Discord Bot 地震功能已完全修復")
    else:
        print("\n🎯 格式化測試結果: ❌ 仍有格式化問題需要解決")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
