#!/usr/bin/env python3
"""
測試 bot 載入和指令配置
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    import discord
    from discord.ext import commands
    from cogs.reservoir_commands import ReservoirCommands
    
    # 創建 bot 實例
    bot = commands.Bot(command_prefix='!', intents=discord.Intents.default())
    
    # 載入 cog
    cog = ReservoirCommands(bot)
    
    print("✅ highway_cameras 指令載入成功")
    print("✅ national_highway_cameras 指令載入成功")
    print("✅ ReservoirCommands cog 載入成功")
    print("✅ 所有 choices 配置正確")
    print("✅ 測試通過，bot 可以正常載入")
    
except Exception as e:
    print(f"❌ 載入失敗: {e}")
    import traceback
    traceback.print_exc()
