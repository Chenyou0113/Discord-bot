#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單快速檢查
"""

import os
import sys

def main():
    print("🔍 簡單系統檢查...")
    
    # 檢查關鍵檔案
    files_check = [
        ("bot.py", os.path.exists("bot.py")),
        ("cogs/reservoir_commands.py", os.path.exists("cogs/reservoir_commands.py")),
        ("requirements.txt", os.path.exists("requirements.txt"))
    ]
    
    print("\n📋 檔案檢查:")
    for filename, exists in files_check:
        status = "✅" if exists else "❌"
        print(f"{status} {filename}")
    
    # 檢查模組導入
    print("\n📋 模組檢查:")
    
    try:
        import discord
        print(f"✅ discord.py {discord.__version__}")
    except ImportError:
        print("❌ discord.py")
    
    try:
        import aiohttp
        print(f"✅ aiohttp {aiohttp.__version__}")
    except ImportError:
        print("❌ aiohttp")
    
    try:
        import requests
        print(f"✅ requests {requests.__version__}")
    except ImportError:
        print("❌ requests")
    
    # 檢查 Cog 文件
    print("\n📋 Cog 檢查:")
    
    if os.path.exists("cogs/reservoir_commands.py"):
        with open("cogs/reservoir_commands.py", "r", encoding="utf-8") as f:
            content = f.read()
            
        checks = [
            ("ReservoirCommands 類別", "class ReservoirCommands" in content),
            ("setup 函數", "async def setup(bot)" in content),
            ("reservoir 指令", "async def reservoir(" in content),
            ("reservoir_operation 指令", "async def reservoir_operation(" in content),
            ("reservoir_info 指令", "async def reservoir_info(" in content),
            ("water_cameras 指令", "async def water_cameras(" in content),
            ("reservoir_list 指令", "async def reservoir_list(" in content)
        ]
        
        for check_name, result in checks:
            status = "✅" if result else "❌"
            print(f"{status} {check_name}")
    
    print("\n🎯 系統狀態:")
    all_good = all([exists for _, exists in files_check])
    
    if all_good:
        print("✅ 系統檔案完整")
        print("💡 可以嘗試啟動機器人測試")
    else:
        print("❌ 系統檔案不完整")
        print("💡 需要修復缺失的檔案")

if __name__ == "__main__":
    main()
