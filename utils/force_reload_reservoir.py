#!/usr/bin/env python3
"""
強制重新載入 reservoir_commands 並檢查指令同步
"""
import asyncio
import sys
import os
from datetime import datetime

# 設置路徑
sys.path.insert(0, r'C:\Users\xiaoy\Desktop\Discord bot')
os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')

async def force_reload_reservoir_commands():
    """強制重新載入 reservoir_commands"""
    print("🔄 強制重新載入 reservoir_commands")
    print("=" * 60)
    
    try:
        # 1. 檢查模組狀態
        print("1️⃣ 檢查模組狀態...")
        module_name = 'cogs.reservoir_commands'
        
        if module_name in sys.modules:
            print(f"   ✅ {module_name} 已在模組快取中")
            del sys.modules[module_name]
            print(f"   🗑️ 已清除模組快取")
        else:
            print(f"   ℹ️ {module_name} 不在模組快取中")
        
        # 2. 導入測試
        print("\n2️⃣ 重新導入測試...")
        from cogs.reservoir_commands import ReservoirCommands, setup
        print("   ✅ 成功導入 ReservoirCommands 和 setup")
        
        # 3. 檢查指令數量
        print("\n3️⃣ 檢查指令數量...")
        import re
        with open('cogs/reservoir_commands.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        commands = re.findall(r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']', content)
        print(f"   📊 找到 {len(commands)} 個指令:")
        for cmd in commands:
            print(f"     - {cmd}")
        
        return True
        
    except Exception as e:
        print(f"❌ 重新載入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_bot_status():
    """檢查機器人狀態"""
    print("\n4️⃣ 檢查機器人狀態...")
    
    # 檢查日誌
    if os.path.exists('bot.log'):
        with open('bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if lines:
            print(f"   📊 日誌總行數: {len(lines)}")
            
            # 查找最近的載入日誌
            recent_lines = lines[-100:]
            load_lines = [line.strip() for line in recent_lines 
                         if any(keyword in line.lower() for keyword in 
                               ['載入', 'load', 'cog', 'reservoir', '同步', 'sync'])]
            
            if load_lines:
                print("   📝 最近的載入相關日誌:")
                for line in load_lines[-10:]:
                    print(f"     {line}")
            else:
                print("   ⚠️ 沒有找到載入相關日誌")
        else:
            print("   ⚠️ 日誌文件為空")
    else:
        print("   ❌ 找不到 bot.log")

def create_manual_reload_script():
    """創建手動重新載入腳本"""
    print("\n5️⃣ 創建手動重新載入腳本...")
    
    script_content = '''#!/usr/bin/env python3
"""
手動重新載入 reservoir_commands cog
在機器人運行時執行此腳本
"""
import asyncio
import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

async def reload_reservoir_cog():
    """重新載入 reservoir_commands cog"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("❌ 找不到 DISCORD_TOKEN")
        return
    
    # 創建臨時機器人實例
    intents = discord.Intents.default()
    intents.message_content = True
    
    bot = commands.Bot(command_prefix='!', intents=intents)
    
    @bot.event
    async def on_ready():
        print(f"✅ 臨時機器人已連線: {bot.user}")
        
        try:
            # 嘗試重新載入 cog
            if 'cogs.reservoir_commands' in bot.extensions:
                await bot.reload_extension('cogs.reservoir_commands')
                print("🔄 成功重新載入 reservoir_commands")
            else:
                await bot.load_extension('cogs.reservoir_commands')
                print("📥 成功載入 reservoir_commands")
            
            # 同步指令
            synced = await bot.tree.sync()
            print(f"🔄 指令同步完成，共 {len(synced)} 個指令")
            
        except Exception as e:
            print(f"❌ 重新載入失敗: {e}")
        
        finally:
            await bot.close()
    
    try:
        await bot.start(token)
    except Exception as e:
        print(f"❌ 機器人啟動失敗: {e}")

if __name__ == "__main__":
    asyncio.run(reload_reservoir_cog())
'''
    
    with open('manual_reload_reservoir.py', 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    print("   ✅ 已創建 manual_reload_reservoir.py")

async def main():
    """主函數"""
    print(f"🕐 開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 強制重新載入
    success = await force_reload_reservoir_commands()
    
    # 2. 檢查機器人狀態
    check_bot_status()
    
    # 3. 創建手動重新載入腳本
    create_manual_reload_script()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 reservoir_commands 模組檢查完成！")
        print("\n💡 建議執行步驟:")
        print("1. 停止當前機器人: Ctrl+C 或 taskkill /f /im python.exe")
        print("2. 重新啟動機器人: python bot.py")
        print("3. 檢查新指令是否出現在同步列表中")
        print("4. 如果仍有問題，執行: python manual_reload_reservoir.py")
    else:
        print("❌ reservoir_commands 模組有問題，請檢查錯誤訊息")
    
    print(f"\n🕐 結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    asyncio.run(main())
