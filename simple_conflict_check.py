#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的指令衝突檢測
"""

import os
import sys
import re

def simple_conflict_check():
    """簡單的指令衝突檢測"""
    print("🔍 檢查指令衝突...")
    
    command_map = {}
    cog_files = [
        'cogs/admin_commands_fixed.py',
        'cogs/basic_commands.py',
        'cogs/info_commands_fixed_v4_clean.py',
        'cogs/level_system.py',
        'cogs/monitor_system.py',
        'cogs/voice_system.py',
        'cogs/chat_commands.py',
        'cogs/search_commands.py',
        'cogs/weather_commands.py',
        'cogs/air_quality_commands.py',
        'cogs/radar_commands.py',
        'cogs/temperature_commands.py'
    ]
    
    # 檢查每個檔案
    for cog_file in cog_files:
        if not os.path.exists(cog_file):
            print(f"⚠️ 檔案不存在: {cog_file}")
            continue
            
        print(f"📝 檢查檔案: {cog_file}")
        
        try:
            with open(cog_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 使用正則表達式找到 @app_commands.command 裝飾器
            pattern = r'@app_commands\.command\s*\(\s*name\s*=\s*["\']([^"\']+)["\']'
            matches = re.findall(pattern, content)
            
            for command_name in matches:
                if command_name in command_map:
                    print(f"❌ 指令衝突: '{command_name}'")
                    print(f"   原始位置: {command_map[command_name]}")
                    print(f"   衝突位置: {cog_file}")
                    return False
                else:
                    command_map[command_name] = cog_file
                    print(f"   ✅ 指令: {command_name}")
                    
        except Exception as e:
            print(f"❌ 讀取檔案 {cog_file} 時發生錯誤: {str(e)}")
    
    print(f"\n📊 總計找到 {len(command_map)} 個唯一指令")
    print("✅ 沒有發現指令衝突!")
    
    # 顯示所有指令的分類
    print("\n📋 指令分類:")
    categories = {}
    for cmd, file in command_map.items():
        category = os.path.basename(file).replace('.py', '')
        if category not in categories:
            categories[category] = []
        categories[category].append(cmd)
    
    for category, commands in categories.items():
        print(f"  {category}: {', '.join(commands)}")
    
    return True

if __name__ == "__main__":
    os.chdir(r"c:\Users\xiaoy\Desktop\Discord bot")
    print("🔥 簡化指令衝突檢測")
    print("=" * 50)
    
    success = simple_conflict_check()
    
    print("=" * 50)
    if success:
        print("✅ 檢測完成，沒有發現衝突!")
    else:
        print("❌ 發現指令衝突，需要修復!")
