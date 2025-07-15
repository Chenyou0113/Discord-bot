#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 Discord Bot Token 有效性
"""

import os
import asyncio
import discord
from discord.ext import commands

async def test_bot_token():
    """測試 Bot Token 是否有效"""
    
    # 載入環境變數
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("⚠️ python-dotenv 未安裝，嘗試直接讀取環境變數")
    
    # 讀取 Token
    token = os.getenv('DISCORD_TOKEN')
    
    if not token:
        print("❌ 找不到 DISCORD_TOKEN 環境變數")
        print("請確認 .env 檔案中有正確的 DISCORD_TOKEN 設定")
        return False
    
    if token == "YOUR_NEW_BOT_TOKEN_HERE":
        print("❌ 請將 .env 檔案中的 DISCORD_TOKEN 替換為實際的 Token")
        return False
    
    print(f"🔍 測試 Token: {token[:10]}...{token[-10:]}")
    
    # 建立 Bot 實例進行測試
    intents = discord.Intents.default()
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✅ Bot Token 有效！")
        print(f"🤖 Bot 名稱: {bot.user.name}")
        print(f"🆔 Bot ID: {bot.user.id}")
        print(f"🌐 連接的伺服器數量: {len(bot.guilds)}")
        
        # 列出連接的伺服器
        if bot.guilds:
            print("📋 連接的伺服器:")
            for guild in bot.guilds:
                print(f"   - {guild.name} (ID: {guild.id})")
        else:
            print("⚠️ Bot 尚未加入任何伺服器")
        
        await bot.close()
        return True
    
    @bot.event
    async def on_error(event, *args, **kwargs):
        print(f"❌ 發生錯誤: {event}")
        await bot.close()
        return False
    
    try:
        await bot.start(token)
        return True
    except discord.LoginFailure:
        print("❌ Token 無效！請檢查 Token 是否正確")
        return False
    except discord.HTTPException as e:
        print(f"❌ HTTP 錯誤: {e}")
        return False
    except Exception as e:
        print(f"❌ 其他錯誤: {e}")
        return False

if __name__ == "__main__":
    try:
        result = asyncio.run(test_bot_token())
        if result:
            print("\n🎉 Token 測試通過！可以啟動 Bot")
        else:
            print("\n❌ Token 測試失敗！請檢查設定")
    except KeyboardInterrupt:
        print("\n⏹️ 測試被中斷")
    except Exception as e:
        print(f"\n❌ 測試過程發生錯誤: {e}")
