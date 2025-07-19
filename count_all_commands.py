#!/usr/bin/env python3
"""
統計 Discord bot 中的所有指令數量
"""

import os
import re

def count_commands_in_file(file_path):
    """計算文件中的指令數量"""
    if not os.path.exists(file_path):
        return 0, []
    
    commands = []
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # 尋找 @app_commands.command 裝飾器
        pattern = r'@app_commands\.command\(name=["\']([^"\']+)["\']'
        matches = re.findall(pattern, content)
        commands.extend(matches)
    
    return len(commands), commands

def main():
    print("🔍 統計 Discord Bot 指令數量...")
    print("=" * 50)
    
    cogs_dir = "cogs"
    total_commands = 0
    all_commands = []
    
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py'):
                file_path = os.path.join(cogs_dir, filename)
                count, commands = count_commands_in_file(file_path)
                if count > 0:
                    print(f"📁 {filename}: {count} 個指令")
                    for cmd in commands:
                        print(f"   - {cmd}")
                    total_commands += count
                    all_commands.extend(commands)
                    print()
    
    print("=" * 50)
    print(f"📊 總計: {total_commands} 個指令")
    
    # 檢查台鐵相關指令
    tra_commands = [cmd for cmd in all_commands if '台鐵' in cmd]
    if tra_commands:
        print(f"🚆 台鐵相關指令: {len(tra_commands)} 個")
        for cmd in tra_commands:
            print(f"   - {cmd}")
    
    return total_commands

if __name__ == "__main__":
    main()
