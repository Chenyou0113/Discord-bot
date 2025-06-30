
import asyncio
import discord
from discord.ext import commands
from cogs.reservoir_commands import ReservoirCommands

async def runtime_test():
    """運行時測試"""
    
    # 創建模擬環境
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    # 添加 cog
    await bot.add_cog(ReservoirCommands(bot))
    
    print("✅ 成功創建 bot 和 cog")
    
    # 模擬指令執行
    # 注意：這只是模擬，不會真正連接到 Discord
    
    return True

if __name__ == "__main__":
    try:
        result = asyncio.run(runtime_test())
        print("✅ 運行時測試通過")
    except Exception as e:
        print(f"❌ 運行時測試失敗: {e}")
        import traceback
        traceback.print_exc()
