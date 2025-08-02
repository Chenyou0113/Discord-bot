#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Discord 指令同步腳本
同步所有 slash commands 到 Discord
"""

import asyncio
import discord
from discord.ext import commands
import os
import logging
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def sync_commands():
    """同步指令到 Discord"""
    
    # 取得 Discord Token
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        logger.error('找不到 DISCORD_TOKEN 環境變數')
        return False
    
    # 建立機器人實例
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        logger.info(f'已登入為 {bot.user}')
        
        try:
            # 載入所有 cogs
            cogs_to_load = [
                'cogs.admin_commands_fixed',
                'cogs.basic_commands',
                'cogs.info_commands_fixed_v4_clean',
                'cogs.level_system',
                'cogs.monitor_system',
                'cogs.voice_system',
                'cogs.chat_commands',
                'cogs.search_commands',
                'cogs.weather_commands',
                'cogs.air_quality_commands',
                'cogs.radar_commands',
                'cogs.temperature_commands',
                'cogs.reservoir_commands'
            ]
            
            successful_loads = 0
            for cog in cogs_to_load:
                try:
                    await bot.load_extension(cog)
                    logger.info(f'✅ 成功載入: {cog}')
                    successful_loads += 1
                except Exception as e:
                    logger.error(f'❌ 載入失敗 {cog}: {e}')
            
            logger.info(f'載入完成: {successful_loads}/{len(cogs_to_load)} 個 cogs')
            
            # 同步指令
            logger.info('開始同步指令...')
            synced = await bot.tree.sync()
            logger.info(f'✅ 成功同步 {len(synced)} 個指令')
            
            # 顯示同步的指令
            for command in synced:
                logger.info(f'  - /{command.name}: {command.description}')
            
        except Exception as e:
            logger.error(f'同步過程發生錯誤: {e}')
        finally:
            await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        logger.error(f'機器人啟動失敗: {e}')
        return False
    
    return True

if __name__ == "__main__":
    print("🔄 Discord 指令同步工具")
    print("=" * 40)
    
    try:
        result = asyncio.run(sync_commands())
        if result:
            print("\n🎉 指令同步完成！")
        else:
            print("\n❌ 指令同步失敗")
    except KeyboardInterrupt:
        print("\n\n👋 用戶取消操作")
    except Exception as e:
        print(f"\n❌ 執行過程中發生錯誤: {e}")
