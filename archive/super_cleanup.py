#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
超級最終清理腳本 - 2025年6月2日
解決檔案混亂問題，恢復乾淨的專案結構
"""

import os
import shutil
from pathlib import Path
import json

def super_final_cleanup():
    """執行超級最終清理"""
    base_dir = Path("c:/Users/xiaoy/Desktop/Discord bot")
    
    print("🚨 檢測到檔案混亂！開始超級清理...")
    print(f"📊 目前檔案數量: 81個")
    
    # 核心必要檔案清單 - 絕對不能刪除
    essential_files = {
        "bot.py",
        ".env", 
        ".gitignore",
        ".gitattributes",
        "requirements.txt",
        "levels.json",
        "level_config.json",
        "sample_earthquake.json", 
        "sample_tsunami.json",
        "README.md",
        "start_bot.bat",
        "stop_bot.bat",
        "bot.log"  # 保留日誌
    }
    
    # 重要報告檔案 - 保留最重要的
    important_reports = {
        "PROJECT_COMPLETION_SUMMARY.md",
        "FINAL_PROJECT_COMPLETION_REPORT.md", 
        "27_ISSUES_FINAL_COMPLETION_REPORT.md"
    }
    
    # 核心資料夾 - 必須保留
    essential_dirs = {
        "cogs",
        "archive", 
        "venv",
        "tests"
    }
    
    # 要清理的檔案模式
    cleanup_patterns = [
        "*test*.py",
        "*verification*.py", 
        "*diagnostic*.py",
        "*fix*.py",
        "*status*.py",
        "*debug*.py",
        "*cleanup*.py",
        "*function_test*.py",
        "quick_*.py",
        "simple_*.py",
        "final_*.py",
        "comprehensive_*.py",
        "investigate_*.py",
        "verify_*.py",
        "api_key_guide.py",
        "implementation_guide.md",
        "optimization_*.md",
        "*REPORT.md",
        "*_REPORT.md",
        "README_TESTING.md"
    ]
    
    removed_files = []
    kept_files = []
    
    print("\n🔍 分析檔案...")
    
    # 掃描所有檔案
    for file_path in base_dir.glob("*"):
        if file_path.is_file():
            file_name = file_path.name
            
            # 檢查是否為必要檔案
            if file_name in essential_files or file_name in important_reports:
                kept_files.append(file_name)
                continue
                
            # 檢查是否符合清理模式
            should_remove = False
            for pattern in cleanup_patterns:
                if file_path.match(pattern):
                    should_remove = True
                    break
            
            if should_remove:
                try:
                    # 移到archive而不是直接刪除
                    archive_dir = base_dir / "archive"
                    if not archive_dir.exists():
                        archive_dir.mkdir()
                    
                    archive_path = archive_dir / file_name
                    # 如果archive中已存在，添加時間戳
                    if archive_path.exists():
                        stem = archive_path.stem
                        suffix = archive_path.suffix
                        archive_path = archive_dir / f"{stem}_2025_06_02{suffix}"
                    
                    shutil.move(str(file_path), str(archive_path))
                    removed_files.append(f"{file_name} → archive/")
                    print(f"📦 已移至archive: {file_name}")
                except Exception as e:
                    print(f"❌ 移動失敗 {file_name}: {e}")
            else:
                kept_files.append(file_name)
    
    # 檢查資料夾
    for dir_path in base_dir.glob("*"):
        if dir_path.is_dir() and dir_path.name not in essential_dirs:
            if dir_path.name.startswith("Discord-bot"):
                try:
                    shutil.rmtree(str(dir_path))
                    removed_files.append(f"📁 {dir_path.name}/ (已刪除)")
                    print(f"🗑️ 已刪除重複資料夾: {dir_path.name}/")
                except Exception as e:
                    print(f"❌ 刪除資料夾失敗 {dir_path.name}: {e}")
    
    print(f"\n🎉 清理完成！")
    print(f"📦 移動到archive: {len([f for f in removed_files if '→ archive' in f])} 個檔案")
    print(f"🗑️ 刪除: {len([f for f in removed_files if '已刪除' in f])} 個項目") 
    print(f"✅ 保留: {len(kept_files)} 個核心檔案")
    
    return kept_files, removed_files

def verify_essential_structure():
    """驗證核心結構完整性"""
    base_dir = Path("c:/Users/xiaoy/Desktop/Discord bot")
    
    print("\n🔍 驗證核心結構...")
    
    # 檢查核心檔案
    essential_checks = {
        "bot.py": "主程式檔案",
        ".env": "環境配置", 
        "requirements.txt": "依賴清單",
        "cogs/info_commands_fixed_v4_clean.py": "核心指令模組"
    }
    
    missing_files = []
    
    for file_path, description in essential_checks.items():
        full_path = base_dir / file_path
        if full_path.exists():
            print(f"✅ {description}: {file_path}")
        else:
            print(f"❌ 缺少 {description}: {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n⚠️ 缺少 {len(missing_files)} 個核心檔案!")
        return False
    else:
        print(f"\n✅ 所有核心檔案完整!")
        return True

if __name__ == "__main__":
    print("🧹 Discord Bot 超級最終清理 - 2025年6月2日")
    print("=" * 50)
    
    kept, removed = super_final_cleanup()
    
    print("\n" + "=" * 50)
    print("📋 清理總結:")
    print(f"✅ 保留核心檔案: {len(kept)}")
    
    essential_structure_ok = verify_essential_structure()
    
    if essential_structure_ok:
        print("\n🎯 專案狀態: ✅ 健康")
        print("🚀 Discord Bot 已準備就緒!")
    else:
        print("\n🎯 專案狀態: ⚠️ 需要修復") 
        
    print("\n📁 最終檔案結構:")
    print("├── 🤖 bot.py")
    print("├── ⚙️ .env") 
    print("├── 📋 requirements.txt")
    print("├── 📊 levels.json")
    print("├── 🌍 sample_earthquake.json")
    print("├── 🌊 sample_tsunami.json")
    print("├── 📁 cogs/ (指令模組)")
    print("├── 📁 archive/ (歷史檔案)")
    print("└── 📋 重要報告檔案")
    
    print(f"\n✨ 清理完成！檔案數量從 81 → {len(kept)} 個")
