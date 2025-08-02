#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全面 await/sync 調用檢查
檢查所有可能的 await 使用錯誤和方法調用問題
"""

import ast
import re
import sys
from pathlib import Path

def check_await_usage():
    """檢查 await 使用是否正確"""
    
    print("🔍 全面 await/sync 調用檢查")
    print("=" * 60)
    
    file_path = Path("cogs/reservoir_commands.py")
    
    if not file_path.exists():
        print(f"❌ 檔案不存在: {file_path}")
        return False
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📁 檢查檔案: {file_path}")
    print(f"📏 檔案大小: {len(content)} 字符")
    
    issues_found = []
    
    # 1. 檢查 await 使用的同步方法
    sync_methods = [
        '_process_and_validate_image_url',
        'format_water_image_info'
    ]
    
    print("\n1️⃣ 檢查錯誤的 await 同步方法調用...")
    for method in sync_methods:
        pattern = rf'await\s+.*\.{method}\s*\('
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            issues_found.append(f"行 {line_num}: 錯誤地對同步方法 {method} 使用 await")
            print(f"❌ 行 {line_num}: await {method}(...) - 這是同步方法!")
    
    # 2. 檢查缺少 await 的異步方法調用
    async_methods = [
        'defer',
        'followup.send',
        'edit',
        'send'
    ]
    
    print("\n2️⃣ 檢查缺少 await 的異步方法調用...")
    for method in async_methods:
        # 查找沒有 await 的異步方法調用
        pattern = rf'(?<!await\s)(?<!await\s\s)(?<!await\s\s\s)\.{method}\s*\('
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            context_start = max(0, match.start() - 20)
            context_end = min(len(content), match.end() + 20)
            context = content[context_start:context_end].strip()
            
            # 排除註解和字符串
            lines = content.split('\n')
            if line_num <= len(lines):
                line = lines[line_num - 1].strip()
                if not line.startswith('#') and 'await' not in line:
                    issues_found.append(f"行 {line_num}: 可能缺少 await 的異步方法 {method}")
                    print(f"⚠️ 行 {line_num}: {method}(...) - 可能需要 await")
    
    # 3. 檢查 AST 語法錯誤
    print("\n3️⃣ 檢查 Python 語法正確性...")
    try:
        tree = ast.parse(content, filename=str(file_path))
        print("✅ Python 語法檢查通過")
    except SyntaxError as e:
        issues_found.append(f"語法錯誤: {e}")
        print(f"❌ 語法錯誤: {e}")
    
    # 4. 檢查常見的 await 模式錯誤
    print("\n4️⃣ 檢查常見 await 模式錯誤...")
    
    # 檢查 await 字符串
    await_string_pattern = r'await\s+["\'][^"\']*["\']'
    matches = re.finditer(await_string_pattern, content, re.MULTILINE)
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        issues_found.append(f"行 {line_num}: await 用於字符串")
        print(f"❌ 行 {line_num}: await 用於字符串 - {match.group()}")
    
    # 檢查 await 數字或變量
    await_non_callable_pattern = r'await\s+(?![\w\.]+\s*\()[a-zA-Z_]\w*(?!\s*\()'
    matches = re.finditer(await_non_callable_pattern, content, re.MULTILINE)
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        issues_found.append(f"行 {line_num}: await 用於非可調用對象")
        print(f"❌ 行 {line_num}: await 用於非可調用對象 - {match.group()}")
    
    # 5. 檢查嵌套 await 錯誤
    print("\n5️⃣ 檢查嵌套 await 錯誤...")
    nested_await_pattern = r'await\s+await'
    matches = re.finditer(nested_await_pattern, content, re.MULTILINE)
    for match in matches:
        line_num = content[:match.start()].count('\n') + 1
        issues_found.append(f"行 {line_num}: 嵌套 await")
        print(f"❌ 行 {line_num}: 嵌套 await - {match.group()}")
    
    # 6. 報告結果
    print("\n" + "=" * 60)
    if issues_found:
        print(f"❌ 發現 {len(issues_found)} 個潜在問題:")
        for i, issue in enumerate(issues_found, 1):
            print(f"   {i}. {issue}")
        return False
    else:
        print("✅ 所有 await/sync 調用檢查通過！")
        print("✅ 沒有發現 await 使用錯誤")
        return True

def check_specific_error_patterns():
    """檢查特定錯誤模式"""
    
    print("\n🔍 特定錯誤模式檢查")
    print("=" * 40)
    
    file_path = Path("cogs/reservoir_commands.py")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 檢查 "object str can't be used in 'await' expression" 錯誤
    print("1️⃣ 檢查字符串 await 錯誤...")
    
    # 常見的字符串 await 錯誤模式
    string_await_patterns = [
        r'await\s+"[^"]*"',
        r"await\s+'[^']*'",
        r'await\s+f"[^"]*"',
        r"await\s+f'[^']*'",
        r'await\s+\w+\s*\[\s*["\'][^"\']*["\']\s*\]',  # await obj['key']
    ]
    
    found_issues = False
    for pattern in string_await_patterns:
        matches = re.finditer(pattern, content, re.MULTILINE)
        for match in matches:
            line_num = content[:match.start()].count('\n') + 1
            print(f"❌ 行 {line_num}: 字符串 await 錯誤 - {match.group()}")
            found_issues = True
    
    if not found_issues:
        print("✅ 沒有發現字符串 await 錯誤")
    
    return not found_issues

def main():
    """主函數"""
    print("🚀 Discord Bot await/sync 調用全面檢查")
    print("=" * 80)
    
    # 檢查 await 使用
    await_check = check_await_usage()
    
    # 檢查特定錯誤模式  
    pattern_check = check_specific_error_patterns()
    
    # 最終結果
    print("\n" + "=" * 80)
    if await_check and pattern_check:
        print("🎉 所有檢查通過！代碼中沒有 await/sync 調用錯誤。")
        print("✅ 可以安全部署和運行")
        return True
    else:
        print("❌ 發現問題，需要修復後再部署")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
