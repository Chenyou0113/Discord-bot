#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
調查用戶報告的30個新問題
"""

import os
import sys
import subprocess
import json
import traceback
from datetime import datetime

def check_process_status():
    """檢查機器人進程狀態"""
    print("=== 機器人進程狀態 ===")
    try:
        result = subprocess.run(['tasklist', '/fi', 'imagename eq python.exe'], 
                              capture_output=True, text=True, encoding='utf-8')
        print(result.stdout)
    except Exception as e:
        print(f"無法檢查進程狀態: {e}")

def check_recent_logs():
    """檢查最近的日誌"""
    print("\n=== 檢查最近日誌 ===")
    try:
        # 檢查是否有日誌文件
        log_files = [f for f in os.listdir('.') if f.endswith('.log')]
        if log_files:
            print(f"找到日誌文件: {log_files}")
            # 讀取最新的日誌
            for log_file in log_files[-2:]:  # 只檢查最新的2個日誌文件
                print(f"\n--- {log_file} ---")
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        # 只顯示最後50行
                        for line in lines[-50:]:
                            print(line.strip())
                except Exception as e:
                    print(f"無法讀取 {log_file}: {e}")
        else:
            print("未找到日誌文件")
    except Exception as e:
        print(f"檢查日誌時出錯: {e}")

def check_error_files():
    """檢查錯誤相關文件"""
    print("\n=== 檢查錯誤文件 ===")
    error_patterns = ['error', 'debug', 'issue', 'problem']
    
    for pattern in error_patterns:
        matching_files = [f for f in os.listdir('.') if pattern.lower() in f.lower()]
        if matching_files:
            print(f"\n找到與 '{pattern}' 相關的文件:")
            for file in matching_files:
                print(f"  - {file}")
                # 如果是最近創建的文件，讀取內容
                try:
                    stat = os.stat(file)
                    file_age = (datetime.now().timestamp() - stat.st_mtime) / 3600  # 小時
                    if file_age < 24:  # 24小時內的文件
                        print(f"    (最近 {file_age:.1f} 小時內修改)")
                        if os.path.getsize(file) < 10000:  # 小於10KB的文件
                            try:
                                with open(file, 'r', encoding='utf-8', errors='ignore') as f:
                                    content = f.read()
                                    print(f"    內容預覽:\n{content[:500]}...")
                            except:
                                pass
                except:
                    pass

def check_code_syntax():
    """檢查主要代碼文件的語法"""
    print("\n=== 檢查代碼語法 ===")
    main_files = [
        'bot.py',
        'cogs/info_commands_fixed_v4_clean.py',
        'cogs/weather.py',
        'cogs/earthquake.py'
    ]
    
    for file_path in main_files:
        if os.path.exists(file_path):
            print(f"\n檢查 {file_path}:")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    code = f.read()
                compile(code, file_path, 'exec')
                print("  ✅ 語法正確")
            except SyntaxError as e:
                print(f"  ❌ 語法錯誤: {e}")
            except Exception as e:
                print(f"  ⚠️ 其他問題: {e}")
        else:
            print(f"  ⚠️ 文件不存在: {file_path}")

def check_import_issues():
    """檢查模組匯入問題"""
    print("\n=== 檢查模組匯入 ===")
    try:
        # 檢查主要模組
        sys.path.insert(0, os.getcwd())
        
        modules_to_test = [
            'discord',
            'aiohttp',
            'requests',
            'cogs.info_commands_fixed_v4_clean'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"  ✅ {module_name}")
            except ImportError as e:
                print(f"  ❌ {module_name}: {e}")
            except Exception as e:
                print(f"  ⚠️ {module_name}: {e}")
                
    except Exception as e:
        print(f"模組檢查失敗: {e}")

def main():
    print("調查用戶報告的30個問題...")
    print("=" * 60)
    
    check_process_status()
    check_recent_logs()
    check_error_files()
    check_code_syntax()
    check_import_issues()
    
    print("\n" + "=" * 60)
    print("調查完成。請查看上述輸出以識別具體問題。")

if __name__ == "__main__":
    main()
