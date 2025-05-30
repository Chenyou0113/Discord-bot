#!/usr/bin/env python3
"""
簡化的機器人問題檢查
"""
import os
import json

def check_basic_issues():
    """檢查基本問題"""
    issues = []
    
    print("🔍 檢查基本配置...")
    
    # 1. 檢查 .env 文件
    if not os.path.exists('.env'):
        issues.append("1. 缺少 .env 文件")
    
    # 2. 檢查必要的 Python 文件
    required_files = [
        'bot.py',
        'cogs/info_commands_fixed_v4_clean.py',
        'cogs/admin_commands_fixed.py',
        'cogs/basic_commands.py',
        'cogs/level_system.py',
        'cogs/monitor_system.py',
        'cogs/voice_system.py',
        'cogs/chat_commands.py'
    ]
    
    for i, file_path in enumerate(required_files):
        if not os.path.exists(file_path):
            issues.append(f"{len(issues)+1}. 缺少文件: {file_path}")
    
    # 3. 檢查 requirements.txt
    if not os.path.exists('requirements.txt'):
        issues.append(f"{len(issues)+1}. 缺少 requirements.txt")
    
    # 4. 檢查樣本資料文件
    if not os.path.exists('sample_tsunami.json'):
        issues.append(f"{len(issues)+1}. 缺少 sample_tsunami.json")
    else:
        try:
            with open('sample_tsunami.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'records' not in data or 'Tsunami' not in data['records']:
                issues.append(f"{len(issues)+1}. sample_tsunami.json 結構不正確")
        except Exception as e:
            issues.append(f"{len(issues)+1}. sample_tsunami.json 格式錯誤: {e}")
    
    # 5. 檢查地震樣本資料
    if os.path.exists('sample_earthquake.json'):
        try:
            with open('sample_earthquake.json', 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    issues.append(f"{len(issues)+1}. sample_earthquake.json 是空文件")
        except Exception as e:
            issues.append(f"{len(issues)+1}. sample_earthquake.json 讀取錯誤: {e}")
    
    # 6. 檢查日誌文件編碼問題
    if os.path.exists('bot.log'):
        try:
            with open('bot.log', 'r', encoding='utf-8') as f:
                log_content = f.read()
                if '???' in log_content:
                    issues.append(f"{len(issues)+1}. 日誌文件存在編碼問題")
        except Exception as e:
            issues.append(f"{len(issues)+1}. 無法讀取日誌文件: {e}")
    
    # 7. 檢查 bot.py 中的缺失函數
    if os.path.exists('bot.py'):
        try:
            with open('bot.py', 'r', encoding='utf-8') as f:
                content = f.read()
                if '_try_register_basic_commands' in content and 'def _try_register_basic_commands' not in content:
                    issues.append(f"{len(issues)+1}. bot.py 缺少 _try_register_basic_commands 函數定義")
                if 'force_sync_commands' in content and 'def force_sync_commands' not in content:
                    issues.append(f"{len(issues)+1}. bot.py 缺少 force_sync_commands 函數定義")
        except Exception as e:
            issues.append(f"{len(issues)+1}. 無法檢查 bot.py: {e}")
    
    # 8. 檢查 Cog 文件語法
    cog_files = [
        'cogs/info_commands_fixed_v4_clean.py',
        'cogs/admin_commands_fixed.py',
        'cogs/basic_commands.py',
        'cogs/level_system.py',
        'cogs/monitor_system.py',
        'cogs/voice_system.py',
        'cogs/chat_commands.py'
    ]
    
    for cog_file in cog_files:
        if os.path.exists(cog_file):
            try:
                with open(cog_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    compile(content, cog_file, 'exec')
            except SyntaxError as e:
                issues.append(f"{len(issues)+1}. {cog_file} 語法錯誤: 第{e.lineno}行")
            except Exception as e:
                issues.append(f"{len(issues)+1}. {cog_file} 檢查錯誤: {e}")
    
    # 9. 檢查重複或過時的文件
    old_files = [
        'cogs/info_commands_fixed_v4.py',
        'cogs/info_commands_fixed_v3.py',
        'cogs/info_commands_fixed_v2.py',
        'cogs/info_commands_fixed_v1.py'
    ]
    
    for old_file in old_files:
        if os.path.exists(old_file):
            issues.append(f"{len(issues)+1}. 存在過時文件: {old_file} (可能導致載入衝突)")
    
    # 10. 檢查配置文件
    config_files = ['level_config.json', 'levels.json']
    for config_file in config_files:
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    json.load(f)
            except json.JSONDecodeError:
                issues.append(f"{len(issues)+1}. {config_file} JSON 格式錯誤")
    
    return issues

def main():
    print("🚀 Discord 機器人問題快速檢查")
    print("=" * 50)
    
    issues = check_basic_issues()
    
    print("=" * 50)
    if issues:
        print(f"❌ 發現 {len(issues)} 個問題:")
        for issue in issues:
            print(f"   {issue}")
        print("\n🔧 建議按順序修復這些問題")
    else:
        print("✅ 沒有發現明顯問題")
        print("🎉 機器人應該可以正常運行")
    
    return len(issues)

if __name__ == "__main__":
    issue_count = main()
    exit(issue_count)
