#!/usr/bin/env python3
"""
指令狀態檢查腳本
用於檢查機器人所有指令是否正確註冊和同步
"""
import os
import sys
import asyncio
import logging
from dotenv import load_dotenv
import discord
from discord.ext import commands

# 載入環境變數
load_dotenv()

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('command_check.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 檢查 Token
token = os.getenv('DISCORD_TOKEN')
if not token:
    logger.error('錯誤: 找不到 DISCORD_TOKEN')
    exit(1)

# 機器人設定
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True

bot = commands.Bot(
    command_prefix='!',
    intents=intents,
    application_id=1357968654423162941
)

# 預期的指令列表
EXPECTED_COMMANDS = {
    # 基本指令
    'ping', 'help', 'info', 'serverinfo', 'userinfo',
    
    # 管理指令
    'purge', 'kick', 'ban', 'timeout', 'warn',
    
    # 功能指令
    'weather', 'air_quality', 'radar', 'temperature',
    
    # 監控指令
    'monitor_freeway', 'monitor_highway', 'monitor_city',
    
    # AI 聊天指令
    'chat', 'ask',
    
    # 搜尋指令
    'search_google', 'search_wiki',
    
    # 新增的水利防災指令
    'water_level', 'water_cameras', 'water_disaster_cameras',
    
    # 新增的道路監控指令
    'national_highway_cameras', 'general_road_cameras',
    
    # 語音系統指令
    'join', 'leave', 'create_voice', 'delete_voice',
    
    # 等級系統指令
    'level', 'leaderboard', 'setlevel',
}

@bot.event
async def on_ready():
    """機器人準備就緒時執行檢查"""
    try:
        logger.info(f'✅ 機器人 {bot.user} 已連線')
        logger.info(f'📊 連接到 {len(bot.guilds)} 個伺服器')
        
        # 檢查已載入的 Cogs
        logger.info('\n📋 已載入的 Cogs:')
        for cog_name in bot.cogs:
            logger.info(f'  - {cog_name}')
        
        # 檢查命令樹中的指令
        logger.info('\n🌳 命令樹指令檢查:')
        tree_commands = bot.tree._global_commands
        logger.info(f'  命令樹中的指令數量: {len(tree_commands)}')
        
        tree_command_names = set()
        for cmd in tree_commands.values():
            tree_command_names.add(cmd.name)
            logger.info(f'  - {cmd.name} (類型: {type(cmd).__name__})')
        
        # 檢查 Cog 中的指令
        logger.info('\n📦 Cog 指令檢查:')
        cog_commands = set()
        for cog_name, cog in bot.cogs.items():
            cog_app_commands = getattr(cog, '__cog_app_commands__', [])
            logger.info(f'  {cog_name}: {len(cog_app_commands)} 個指令')
            for cmd in cog_app_commands:
                cog_commands.add(cmd.name)
                logger.info(f'    - {cmd.name}')
        
        # 比較預期指令與實際指令
        logger.info('\n🔍 指令比對分析:')
        logger.info(f'  預期指令數量: {len(EXPECTED_COMMANDS)}')
        logger.info(f'  命令樹指令數量: {len(tree_command_names)}')
        logger.info(f'  Cog 指令數量: {len(cog_commands)}')
        
        # 找出缺失的指令
        missing_from_tree = EXPECTED_COMMANDS - tree_command_names
        missing_from_cogs = EXPECTED_COMMANDS - cog_commands
        
        if missing_from_tree:
            logger.warning(f'  ⚠️ 命令樹中缺失的指令 ({len(missing_from_tree)}):')
            for cmd in sorted(missing_from_tree):
                logger.warning(f'    - {cmd}')
        
        if missing_from_cogs:
            logger.warning(f'  ⚠️ Cog 中缺失的指令 ({len(missing_from_cogs)}):')
            for cmd in sorted(missing_from_cogs):
                logger.warning(f'    - {cmd}')
        
        # 找出多餘的指令
        extra_in_tree = tree_command_names - EXPECTED_COMMANDS
        if extra_in_tree:
            logger.info(f'  ℹ️ 命令樹中額外的指令 ({len(extra_in_tree)}):')
            for cmd in sorted(extra_in_tree):
                logger.info(f'    - {cmd}')
        
        # 檢查指令是否正確同步
        logger.info('\n🔄 執行指令同步檢查...')
        try:
            synced = await bot.tree.sync()
            logger.info(f'  ✅ 成功同步 {len(synced)} 個指令')
            
            synced_names = [cmd.name for cmd in synced]
            logger.info(f'  📋 已同步的指令: {", ".join(sorted(synced_names))}')
            
            # 檢查同步後的狀態
            sync_missing = EXPECTED_COMMANDS - set(synced_names)
            if sync_missing:
                logger.warning(f'  ⚠️ 同步後仍缺失的指令 ({len(sync_missing)}):')
                for cmd in sorted(sync_missing):
                    logger.warning(f'    - {cmd}')
            else:
                logger.info('  ✅ 所有預期指令都已同步')
                
        except Exception as sync_error:
            logger.error(f'  ❌ 指令同步失敗: {str(sync_error)}')
        
        # 生成報告
        logger.info('\n📊 最終報告:')
        logger.info(f'  Cogs 載入狀態: {len(bot.cogs)} 個已載入')
        logger.info(f'  指令註冊狀態: {len(tree_command_names)}/{len(EXPECTED_COMMANDS)} 個已註冊')
        logger.info(f'  指令同步狀態: {len(synced) if "synced" in locals() else 0} 個已同步')
        
        if not missing_from_tree and not missing_from_cogs:
            logger.info('  🎉 所有指令都已正確載入和註冊！')
        else:
            logger.warning('  ⚠️ 部分指令可能存在問題，請檢查上述詳情')
        
        # 結束檢查
        logger.info('\n✅ 檢查完成，正在關閉機器人...')
        await bot.close()
        
    except Exception as e:
        logger.error(f'❌ 檢查過程中發生錯誤: {str(e)}')
        import traceback
        logger.error(f'錯誤詳情: {traceback.format_exc()}')
        await bot.close()

@bot.event
async def on_error(event, *args, **kwargs):
    """處理錯誤事件"""
    logger.error(f'在事件 {event} 中發生錯誤')
    import traceback
    logger.error(f'錯誤詳情: {traceback.format_exc()}')

async def main():
    """主函數"""
    try:
        logger.info('🚀 開始檢查機器人指令狀態...')
        
        # 載入必要的 Cogs
        extensions = [
            'cogs.basic_commands',
            'cogs.admin_commands_fixed',
            'cogs.info_commands_fixed_v4_clean',
            'cogs.weather_commands',
            'cogs.air_quality_commands',
            'cogs.radar_commands',
            'cogs.temperature_commands',
            'cogs.monitor_system',
            'cogs.chat_commands',
            'cogs.search_commands',
            'cogs.voice_system',
            'cogs.level_system',
            'cogs.reservoir_commands'
        ]
        
        for extension in extensions:
            try:
                await bot.load_extension(extension)
                logger.info(f'✅ 成功載入 {extension}')
            except Exception as e:
                logger.error(f'❌ 載入 {extension} 失敗: {str(e)}')
        
        # 啟動機器人
        async with bot:
            await bot.start(token)
            
    except Exception as e:
        logger.error(f'❌ 主函數執行錯誤: {str(e)}')
        import traceback
        logger.error(f'錯誤詳情: {traceback.format_exc()}')

if __name__ == '__main__':
    asyncio.run(main())
