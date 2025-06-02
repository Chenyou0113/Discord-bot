#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終檔案清理腳本
移除測試檔案和不必要的報告檔案
"""

import os
import shutil
from pathlib import Path

def final_cleanup():
    """執行最終檔案清理"""
    base_dir = Path("c:/Users/xiaoy/Desktop/Discord bot")
    
    # 要清理的檔案列表
    files_to_remove = [
        "cleanup_files.py",  # 空檔案
        "tsunami_function.py",  # 空檔案
        "fix_verification_report.md",  # 小型報告
        "comprehensive_test_report.json",  # 可整合到最終報告
        "final_test_report.json",  # 已整合到最終報告
    ]
    
    # 要清理的測試檔案
    test_files_to_remove = [
        "simple_earthquake_test.py",  # 測試完成可移除
        "comprehensive_diagnostics.py",  # 診斷完成可移除
        "ultimate_function_test.py",  # 已完成測試
        "final_earthquake_dual_api_verification_clean.py",  # API測試完成
        "verify_30_issues_fix_clean.py",  # 驗證完成
    ]
    
    removed_files = []
    
    print("🧹 開始最終檔案清理...")
    
    # 清理主要檔案
    for file_name in files_to_remove:
        file_path = base_dir / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                removed_files.append(file_name)
                print(f"✅ 已移除: {file_name}")
            except Exception as e:
                print(f"❌ 移除失敗 {file_name}: {e}")
    
    # 詢問是否移除測試檔案（保留選項）
    print("\n📋 以下測試檔案已完成功能，是否要移除？")
    for file_name in test_files_to_remove:
        print(f"   - {file_name}")
    
    # 自動移除測試檔案到archive
    archive_dir = base_dir / "archive"
    if not archive_dir.exists():
        archive_dir.mkdir()
    
    for file_name in test_files_to_remove:
        file_path = base_dir / file_name
        if file_path.exists():
            try:
                archive_path = archive_dir / file_name
                shutil.move(str(file_path), str(archive_path))
                removed_files.append(f"{file_name} → archive/")
                print(f"📦 已移至archive: {file_name}")
            except Exception as e:
                print(f"❌ 移動失敗 {file_name}: {e}")
    
    # 清理cogs中的old_versions
    old_versions_dir = base_dir / "cogs" / "old_versions"
    if old_versions_dir.exists():
        try:
            # 移動到archive而不是刪除
            for file_path in old_versions_dir.glob("*.py"):
                archive_path = archive_dir / f"cogs_old_{file_path.name}"
                shutil.move(str(file_path), str(archive_path))
                print(f"📦 已移至archive: cogs/old_versions/{file_path.name}")
            
            # 移除空資料夾
            old_versions_dir.rmdir()
            print("✅ 已移除空資料夾: cogs/old_versions/")
        except Exception as e:
            print(f"❌ 清理old_versions失敗: {e}")
    
    print(f"\n🎉 清理完成！總共處理了 {len(removed_files)} 個項目")
    
    return removed_files

if __name__ == "__main__":
    removed = final_cleanup()
    
    print("\n📊 清理總結:")
    for item in removed:
        print(f"  ✓ {item}")
    
    print("\n✨ Discord Bot 專案已完全整理完成！")
    print("核心檔案:")
    print("  • bot.py - 主要機器人檔案")
    print("  • cogs/info_commands_fixed_v4_clean.py - 核心指令模組")
    print("  • .env - 環境配置")
    print("  • requirements.txt - 依賴清單")
    print("  • levels.json & level_config.json - 等級系統")
    print("  • archive/ - 歷史檔案保存")
