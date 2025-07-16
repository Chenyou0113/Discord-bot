#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
統計並診斷 Discord 機器人所有指令
分析為什麼 reservoir_commands 指令沒有同步
"""

import os
import sys
import re
import json
from datetime import datetime

def count_all_commands():
    """統計所有 cog 文件中的指令"""
    print("🔍 Discord 機器人指令統計與診斷")
    print("=" * 80)
    
    # 切換到機器人目錄
    os.chdir(r'C:\Users\xiaoy\Desktop\Discord bot')
    
    print(f"📁 分析目錄: {os.getcwd()}")
    print(f"🕐 分析時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 列出所有 cog 文件
    print("\n1️⃣ 掃描 cog 文件...")
    cog_files = []
    if os.path.exists('cogs'):
        for file in os.listdir('cogs'):
            if file.endswith('.py') and not file.startswith('__'):
                cog_files.append(file)
    
    print(f"找到 {len(cog_files)} 個 cog 文件")
    
    # 2. 分析每個 cog 文件
    total_commands = 0
    cog_analysis = {}
    
    print("\n2️⃣ 分析各 cog 文件的指令...")
    print("-" * 80)
    print(f"{'Cog 文件':<35} {'指令數':<8} {'語法':<6} {'Setup':<6} {'指令列表'}")
    print("-" * 80)
    
    for cog_file in sorted(cog_files):
        try:
            with open(f'cogs/{cog_file}', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 語法檢查
            syntax_ok = True
            try:
                compile(content, f'cogs/{cog_file}', 'exec')
            except SyntaxError:
                syntax_ok = False
            
            # 統計指令
            command_pattern = r'@app_commands\.command\([^)]*name\s*=\s*["\']([^"\']+)["\']'
            commands = re.findall(command_pattern, content)
            
            # 檢查 setup 函數
            has_setup = 'async def setup(' in content
            
            # 記錄分析結果
            cog_analysis[cog_file] = {
                'commands': commands,
                'command_count': len(commands),
                'syntax_ok': syntax_ok,
                'has_setup': has_setup,
                'file_size': len(content)
            }
            
            total_commands += len(commands)
            
            # 格式化輸出
            syntax_status = "✅" if syntax_ok else "❌"
            setup_status = "✅" if has_setup else "❌"
            commands_str = ", ".join(commands[:3])  # 顯示前3個指令
            if len(commands) > 3:
                commands_str += "..."
            
            print(f"{cog_file:<35} {len(commands):<8} {syntax_status:<6} {setup_status:<6} {commands_str}")
            
        except Exception as e:
            print(f"{cog_file:<35} {'ERROR':<8} {'❌':<6} {'❌':<6} {str(e)[:30]}")
            cog_analysis[cog_file] = {
                'error': str(e),
                'commands': [],
                'command_count': 0,
                'syntax_ok': False,
                'has_setup': False
            }
    
    print("-" * 80)
    print(f"總指令數量: {total_commands}")
    
    # 3. 特別分析 reservoir_commands
    print("\n3️⃣ 特別分析 reservoir_commands...")
    reservoir_file = 'reservoir_commands.py'
    
    if reservoir_file in cog_analysis:
        reservoir_info = cog_analysis[reservoir_file]
        print(f"📋 reservoir_commands 狀態:")
        print(f"  檔案大小: {reservoir_info.get('file_size', 0):,} 字元")
        print(f"  語法檢查: {'✅ 通過' if reservoir_info['syntax_ok'] else '❌ 失敗'}")
        print(f"  setup 函數: {'✅ 存在' if reservoir_info['has_setup'] else '❌ 缺失'}")
        print(f"  指令數量: {reservoir_info['command_count']}")
        
        if reservoir_info['commands']:
            print(f"  指令列表:")
            for cmd in reservoir_info['commands']:
                print(f"    - {cmd}")
        
        # 檢查預期的指令是否存在
        expected_commands = ['water_level', 'water_cameras', 'water_disaster_cameras', 
                           'national_highway_cameras', 'general_road_cameras']
        missing_commands = set(expected_commands) - set(reservoir_info['commands'])
        
        if missing_commands:
            print(f"  ❌ 缺失的指令: {', '.join(missing_commands)}")
        else:
            print(f"  ✅ 所有預期指令都存在")
    else:
        print("❌ 找不到 reservoir_commands.py")
    
    # 4. 檢查 bot.py 的載入配置
    print("\n4️⃣ 檢查 bot.py 載入配置...")
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        # 查找 initial_extensions
        extension_pattern = r'self\.initial_extensions\s*=\s*\[(.*?)\]'
        extension_match = re.search(extension_pattern, bot_content, re.DOTALL)
        
        if extension_match:
            extensions_str = extension_match.group(1)
            extensions = re.findall(r'["\']([^"\']+)["\']', extensions_str)
            
            print(f"📋 bot.py 中配置的擴展 ({len(extensions)} 個):")
            for ext in extensions:
                if ext in [f'cogs.{f[:-3]}' for f in cog_files]:
                    print(f"  ✅ {ext}")
                else:
                    print(f"  ❌ {ext} (文件不存在)")
            
            # 檢查 reservoir_commands 是否在列表中
            if 'cogs.reservoir_commands' in extensions:
                print("✅ reservoir_commands 在載入列表中")
            else:
                print("❌ reservoir_commands 不在載入列表中")
        else:
            print("❌ 找不到 initial_extensions 配置")
            
    except Exception as e:
        print(f"❌ 檢查 bot.py 時發生錯誤: {e}")
    
    # 5. 分析同步的指令列表
    print("\n5️⃣ 分析已同步的指令...")
    synced_commands_str = """clear_startup_channel, shutdown, status, send, admin_monitor, set_startup_channel, emergency_restart, dev, get_id, restart, broadcast, hello, ping, earthquake, set_earthquake_channel, tsunami, level, rank, leaderboard, set_level_channel, clear_level_channel, toggle_level_system, level_system_status, set_monitor_channel, monitor, setup_voice, clear_chat, current_model, chat, set_model, toggle_responses, api_status, set_rate_limit, reset_quota, dev_mode, add_developer, remove_developer, list_developers, dev_debug, search, search_summarize, search_settings, search_stats, auto_search, weather_station, weather_station_by_county, weather_station_info, weather, air_quality, air_quality_county, air_quality_site, radar, radar_info, radar_large, rainfall_radar, temperature"""
    
    synced_commands = [cmd.strip() for cmd in synced_commands_str.split(',')]
    print(f"已同步指令數量: {len(synced_commands)}")
    
    # 檢查哪些指令沒有同步
    all_expected_commands = []
    for cog_file, info in cog_analysis.items():
        if info['syntax_ok'] and info['has_setup']:
            all_expected_commands.extend(info['commands'])
    
    missing_synced = set(all_expected_commands) - set(synced_commands)
    extra_synced = set(synced_commands) - set(all_expected_commands)
    
    if missing_synced:
        print(f"⚠️ 未同步但應該存在的指令 ({len(missing_synced)} 個):")
        for cmd in sorted(missing_synced):
            print(f"  - {cmd}")
    
    if extra_synced:
        print(f"ℹ️ 已同步但在 cog 中找不到的指令 ({len(extra_synced)} 個):")
        for cmd in sorted(extra_synced):
            print(f"  - {cmd}")
    
    # 6. 診斷建議
    print("\n6️⃣ 診斷建議...")
    
    if reservoir_file in cog_analysis:
        reservoir_info = cog_analysis[reservoir_file]
        
        if not reservoir_info['syntax_ok']:
            print("🔧 reservoir_commands.py 有語法錯誤，需要修復")
        elif not reservoir_info['has_setup']:
            print("🔧 reservoir_commands.py 缺少 setup 函數，需要添加")
        elif reservoir_info['command_count'] == 0:
            print("🔧 reservoir_commands.py 沒有定義任何指令")
        elif missing_synced:
            print("🔧 reservoir_commands 的指令沒有同步，可能是載入問題")
            print("   建議操作:")
            print("   1. 重新啟動機器人")
            print("   2. 檢查機器人日誌中的載入錯誤")
            print("   3. 手動重新載入 cog")
        else:
            print("✅ reservoir_commands 看起來正常，可能是同步延遲")
    
    # 7. 生成報告文件
    print("\n7️⃣ 生成分析報告...")
    
    report_data = {
        "analysis_time": datetime.now().isoformat(),
        "total_cog_files": len(cog_files),
        "total_commands_found": total_commands,
        "total_commands_synced": len(synced_commands),
        "cog_analysis": cog_analysis,
        "synced_commands": synced_commands,
        "missing_from_sync": list(missing_synced),
        "extra_in_sync": list(extra_synced)
    }
    
    with open('command_analysis_report.json', 'w', encoding='utf-8') as f:
        json.dump(report_data, f, ensure_ascii=False, indent=2)
    
    print("📁 詳細報告已儲存至: command_analysis_report.json")
    
    # 8. 總結
    print("\n" + "=" * 80)
    print("📊 分析總結:")
    print(f"  總 cog 文件: {len(cog_files)}")
    print(f"  總指令定義: {total_commands}")
    print(f"  已同步指令: {len(synced_commands)}")
    print(f"  未同步指令: {len(missing_synced)}")
    
    if missing_synced and 'water_level' in missing_synced:
        print("\n🎯 重點問題: reservoir_commands 的指令沒有同步")
        print("建議立即重新啟動機器人以重新載入 cog")
    else:
        print("\n✅ 指令同步狀態正常")

if __name__ == "__main__":
    count_all_commands()
