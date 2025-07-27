#!/usr/bin/env python3
"""
快速安全性檢查
檢查是否還有硬編碼的 API 密鑰
"""

import os
import re

def quick_security_scan():
    print("🔍 快速安全性掃描")
    print("=" * 40)
    
    # 要檢查的硬編碼模式
    dangerous_patterns = [
        'CWA-675CED45-09DF-4249-9599-B9B5A5AB761A',
        'xiaoyouwu5-08c8f7b1-3ac2-431b',
        '9946bb49-0cc5-463c-ba79-c669140df4ef',
        '94650864-6a80-4c58-83ce-fd13e7ef0504'
    ]
    
    findings = []
    
    # 檢查 cogs 目錄
    cogs_dir = 'cogs'
    if os.path.exists(cogs_dir):
        for filename in os.listdir(cogs_dir):
            if filename.endswith('.py'):
                filepath = os.path.join(cogs_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    for pattern in dangerous_patterns:
                        if pattern in content:
                            findings.append(f"{filepath}: 發現 {pattern[:20]}...")
                except Exception as e:
                    print(f"無法讀取 {filepath}: {e}")
    
    if findings:
        print("❌ 發現硬編碼密鑰:")
        for finding in findings:
            print(f"  - {finding}")
        return False
    else:
        print("✅ 未發現硬編碼密鑰")
        return True

if __name__ == "__main__":
    quick_security_scan()
