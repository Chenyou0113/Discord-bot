#!/usr/bin/env python3
"""
簡化的指令檢查腳本
"""
import sys
import os

# 設置路徑
sys.path.insert(0, r'C:\Users\xiaoy\Desktop\Discord bot')
os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')

print("🔍 檢查 reservoir_commands.py 中的指令...")

try:
    # 讀取文件內容
    with open('cogs/reservoir_commands.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有 @app_commands.command 裝飾器
    import re
    
    # 查找指令定義
    command_pattern = r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']'
    commands = re.findall(command_pattern, content)
    
    # 查找 async def 函數名（作為備用）
    function_pattern = r'async def (water_level|water_cameras|water_disaster_cameras|national_highway_cameras|general_road_cameras)\('
    functions = re.findall(function_pattern, content)
    
    print(f"📋 找到的指令（通過裝飾器）: {len(commands)}")
    for cmd in commands:
        print(f"  - {cmd}")
    
    print(f"📋 找到的函數（通過函數名）: {len(functions)}")
    for func in functions:
        print(f"  - {func}")
    
    # 檢查是否有 setup 函數
    if 'async def setup(' in content:
        print("✅ 找到 setup 函數")
    else:
        print("❌ 未找到 setup 函數")
    
    # 檢查語法
    try:
        compile(content, 'cogs/reservoir_commands.py', 'exec')
        print("✅ 語法檢查通過")
    except SyntaxError as e:
        print(f"❌ 語法錯誤: {e}")
        print(f"   行號: {e.lineno}")
        print(f"   位置: {e.offset}")
    
    print("\n🔍 檢查機器人日誌...")
    
    # 檢查最新的機器人日誌
    try:
        with open('bot.log', 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 取最後50行
        recent_lines = lines[-50:]
        
        print("📊 最近的日誌記錄:")
        for line in recent_lines:
            line = line.strip()
            if any(keyword in line for keyword in ['同步', 'sync', '指令', 'command', 'reservoir', 'Cog']):
                print(f"  {line}")
    
    except Exception as e:
        print(f"❌ 讀取日誌失敗: {e}")

except Exception as e:
    print(f"❌ 檢查過程發生錯誤: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ 檢查完成")
