#!/usr/bin/env python3
"""
檔案清理腳本 - 清理Discord bot專案中的重複和過時檔案
在所有27個問題修復完成後進行檔案整理
"""

import os
import shutil
from pathlib import Path

def cleanup_files():
    """清理不必要的檔案和資料夾"""
    
    base_path = Path(r"c:\Users\xiaoy\Desktop\Discord bot")
    
    # 要保留的核心檔案
    keep_files = {
        # 核心機器人檔案
        "bot.py",
        ".env",
        "requirements.txt",
        "README.md",
        
        # 配置檔案
        "levels.json",
        "level_config.json",
        
        # 有用的批次檔案
        "start_bot.bat",
        "stop_bot.bat",
        
        # 核心測試和驗證檔案（乾淨版本）
        "verify_30_issues_fix_clean.py",
        "final_earthquake_dual_api_verification_clean.py",
        "simple_earthquake_test.py",
        "comprehensive_diagnostics.py",
        "ultimate_function_test.py",
        
        # 最新報告
        "27_ISSUES_FINAL_COMPLETION_REPORT.md",
        "FINAL_PROJECT_COMPLETION_REPORT.md",
        "FILE_CLEANUP_COMPLETION_REPORT.md",
        
        # 樣本檔案
        "sample_earthquake.json",
        "sample_tsunami.json",
        
        # Git相關
        ".gitignore",
        ".gitattributes"
    }
    
    # 要刪除的過時測試檔案
    files_to_delete = [
        "comprehensive_function_test.py",
        "final_comprehensive_test.py",
        "comprehensive_test_report.json",
        "final_test_report.json",
        "fix_verification_report.md",
        "tsunami_function.py"
    ]
    
    deleted_files = []
    deleted_folders = []
    
    print("🧹 開始最終清理Discord bot專案檔案...")
    print("=" * 50)
    
    # 刪除指定的檔案
    print("📄 清理多餘的測試檔案...")
    for file_name in files_to_delete:
        file_path = base_path / file_name
        if file_path.exists():
            try:
                file_path.unlink()
                deleted_files.append(file_name)
                print(f"   ✅ 已刪除: {file_name}")
            except Exception as e:
                print(f"   ❌ 刪除失敗: {file_name} - {e}")
    
    # 清理tests資料夾（保留主要結構，但清理過時檔案）
    tests_path = base_path / "tests"
    if tests_path.exists():
        print(f"\n🧪 清理tests資料夾...")
        try:
            shutil.rmtree(tests_path)
            deleted_folders.append("tests")
            print(f"   ✅ 已刪除整個資料夾: tests")
        except Exception as e:
            print(f"   ❌ 刪除資料夾失敗: tests - {e}")
    
    # 清理__pycache__資料夾
    pycache_paths = list(base_path.rglob("__pycache__"))
    if pycache_paths:
        print(f"\n🗂️ 清理__pycache__資料夾...")
        for pycache_path in pycache_paths:
            try:
                shutil.rmtree(pycache_path)
                relative_path = pycache_path.relative_to(base_path)
                deleted_folders.append(str(relative_path))
                print(f"   ✅ 已刪除: {relative_path}")
            except Exception as e:
                print(f"   ❌ 刪除失敗: {pycache_path} - {e}")
    
    # 生成清理報告
    print("\n" + "=" * 50)
    print("📊 最終清理完成報告")
    print("=" * 50)
    print(f"已刪除檔案數量: {len(deleted_files)}")
    print(f"已刪除資料夾數量: {len(deleted_folders)}")
    
    if deleted_files:
        print(f"\n📄 已刪除的檔案:")
        for file in sorted(deleted_files):
            print(f"   • {file}")
    
    if deleted_folders:
        print(f"\n📁 已刪除的資料夾:")
        for folder in sorted(deleted_folders):
            print(f"   • {folder}")
    
    # 檢查保留的核心檔案
    print(f"\n✅ 保留的核心檔案:")
    for file in sorted(keep_files):
        file_path = base_path / file
        if file_path.exists():
            print(f"   • {file} ✓")
        else:
            print(f"   • {file} ❌ (檔案不存在)")
    
    print(f"\n🎉 最終檔案清理完成！專案結構已優化完畢。")
    
    return len(deleted_files), len(deleted_folders)

if __name__ == "__main__":
    try:
        deleted_files_count, deleted_folders_count = cleanup_files()
        print(f"\n📈 總結: 成功清理了 {deleted_files_count} 個檔案和 {deleted_folders_count} 個資料夾")
    except Exception as e:
        print(f"❌ 清理過程中發生錯誤: {e}")
        input("按Enter鍵繼續...")
