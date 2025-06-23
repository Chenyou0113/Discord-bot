#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速氣象站功能測試
"""

import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_weather_station():
    try:
        from cogs.info_commands_fixed_v4_clean import InfoCommands
        from unittest.mock import MagicMock, AsyncMock
        import aiohttp
        import ssl
        
        mock_interaction = MagicMock()
        mock_interaction.response = MagicMock()
        mock_interaction.response.defer = AsyncMock()
        mock_interaction.followup = MagicMock()
        mock_interaction.followup.send = AsyncMock()
        
        mock_bot = MagicMock()
        mock_bot.user = MagicMock()
        mock_bot.user.id = 123456789
        mock_bot.loop = asyncio.get_event_loop()
        mock_bot.wait_until_ready = AsyncMock()
        
        info_commands = InfoCommands(mock_bot)
        
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=100)
        timeout = aiohttp.ClientTimeout(total=30)
        info_commands.session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        
        print("🌡️ 測試氣象站功能")
        print("=" * 40)
        
        # 測試全台概況
        print("1. 測試全台概況...")
        await info_commands.weather_station.callback(info_commands, mock_interaction)
        
        if mock_interaction.followup.send.called:
            call_args = mock_interaction.followup.send.call_args
            if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                embed = call_args[1]['embed']
                print(f"✅ 成功生成全台概況")
                print(f"   標題: {embed.title}")
                print(f"   欄位數: {len(embed.fields)}")
            else:
                print("❌ 沒有生成 embed")
                return False
        else:
            print("❌ 沒有發送訊息")
            return False
        
        # 測試地區查詢
        print("\n2. 測試台北地區查詢...")
        mock_interaction.followup.send.reset_mock()
        await info_commands.weather_station.callback(info_commands, mock_interaction, None, "台北")
        
        if mock_interaction.followup.send.called:
            call_args = mock_interaction.followup.send.call_args
            if call_args and len(call_args[1]) > 0 and 'embed' in call_args[1]:
                embed = call_args[1]['embed']
                print(f"✅ 成功生成台北地區資料")
                print(f"   標題: {embed.title}")
            else:
                print("❌ 沒有生成 embed")
        
        print("\n🎉 氣象站功能測試完成！")
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

if __name__ == "__main__":
    result = asyncio.run(test_weather_station())
    if result:
        print("\n✅ 氣象站功能正常工作！")
    else:
        print("\n❌ 氣象站功能有問題")
