#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 指令同步腳本
手動同步所有斜線指令到 Discord
"""

import discord
from discord.ext import commands
import asyncio
import logging
import os
from dotenv import load_dotenv

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

class CommandSyncBot(commands.Bot):
    """專門用於同步指令的機器人"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix='!', intents=intents)
        
        self.extensions_to_load = [
            'cogs.reservoir_commands',
            'cogs.weather_commands', 
            'cogs.info_commands_fixed_v4_clean'
        ]
    
    async def setup_hook(self):
        """設置 Cog 並同步指令"""
        logger.info("🚀 開始載入 Cogs 並同步指令...")
        
        # 載入所有 Cogs
        for extension in self.extensions_to_load:
            try:
                await self.load_extension(extension)
                logger.info(f"✅ 載入 {extension} 成功")
            except Exception as e:
                logger.error(f"❌ 載入 {extension} 失敗: {str(e)}")
        
        # 同步指令
        try:
            logger.info("🔄 開始同步指令到 Discord...")
            synced = await self.tree.sync()
            logger.info(f"✅ 成功同步 {len(synced)} 個指令到 Discord")
            
            # 顯示所有同步的指令
            if synced:
                command_names = [cmd.name for cmd in synced]
                logger.info(f"📋 已同步的指令: {', '.join(command_names)}")
            
        except Exception as e:
            logger.error(f"❌ 指令同步失敗: {str(e)}")
    
    async def on_ready(self):
        """機器人準備就緒"""
        logger.info(f"🎉 機器人 {self.user} 已上線！")
        logger.info(f"📊 已載入 {len(self.cogs)} 個 Cogs")
        logger.info(f"🎯 指令同步完成，可以在 Discord 中使用斜線指令了！")
        
        # 顯示所有可用指令
        commands = await self.tree.fetch_commands()
        if commands:
            logger.info(f"🎮 Discord 中的可用指令 ({len(commands)} 個):")
            for cmd in commands:
                logger.info(f"   /{cmd.name} - {cmd.description}")
        
        # 同步完成後關閉機器人
        logger.info("🏁 指令同步完成，關閉機器人...")
        await asyncio.sleep(2)
        await self.close()

async def main():
    """主函數"""
    
    # 檢查 Discord Token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error("❌ 找不到 DISCORD_TOKEN 環境變數")
        logger.info("請設定環境變數或創建 .env 檔案")
        return
    
    # 創建並啟動機器人
    bot = CommandSyncBot()
    
    try:
        await bot.start(token)
    except discord.LoginFailure:
        logger.error("❌ Discord Token 無效，請檢查 Token 是否正確")
    except Exception as e:
        logger.error(f"❌ 機器人啟動失敗: {str(e)}")

if __name__ == "__main__":
    print("🎯 Discord 指令同步工具")
    print("=" * 50)
    print("這個工具會:")
    print("1. 載入所有 Cogs")
    print("2. 同步斜線指令到 Discord")
    print("3. 顯示同步結果")
    print("4. 自動關閉")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 用戶中斷操作")
    except Exception as e:
        print(f"\n❌ 執行失敗: {str(e)}")
    
    print("\n🎉 同步作業完成！")
