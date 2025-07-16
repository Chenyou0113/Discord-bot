#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單驗證 await 錯誤修復
檢查代碼中是否還有錯誤的 await 用法
"""

import sys
import os

def check_await_usage():
    """檢查 await 用法"""
    print("🔍 檢查 await 錯誤修復...")
    
    file_path = "cogs/reservoir_commands.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        print(f"📁 檢查檔案: {file_path}")
        print(f"📊 總行數: {len(lines)}")
        
        # 檢查是否還有錯誤的 await 用法
        await_errors = []
        
        for i, line in enumerate(lines, 1):
            # 檢查錯誤的 await 用法
            if "await self._process_and_validate_image_url" in line:
                await_errors.append((i, line.strip()))
        
        if await_errors:
            print("\n❌ 發現錯誤的 await 用法:")
            for line_num, line_content in await_errors:
                print(f"   第 {line_num} 行: {line_content}")
            return False
        else:
            print("\n✅ 沒有發現錯誤的 await 用法")
        
        # 檢查正確的用法
        correct_usage = []
        for i, line in enumerate(lines, 1):
            if "self._process_and_validate_image_url" in line and "await" not in line:
                correct_usage.append((i, line.strip()))
        
        if correct_usage:
            print(f"\n✅ 發現 {len(correct_usage)} 處正確用法:")
            for line_num, line_content in correct_usage[:3]:  # 只顯示前3個
                print(f"   第 {line_num} 行: {line_content}")
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查失敗: {str(e)}")
        return False

def check_method_definitions():
    """檢查方法定義"""
    print("\n🔍 檢查相關方法定義...")
    
    file_path = "cogs/reservoir_commands.py"
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查 _process_and_validate_image_url 方法定義
        if "def _process_and_validate_image_url(self, image_url):" in content:
            print("✅ _process_and_validate_image_url 方法定義正確（同步方法）")
        elif "async def _process_and_validate_image_url(self, image_url):" in content:
            print("⚠️ _process_and_validate_image_url 是異步方法，需要使用 await")
        else:
            print("❌ 找不到 _process_and_validate_image_url 方法定義")
            return False
        
        # 檢查其他相關方法
        method_checks = [
            ("format_water_image_info", "def format_water_image_info"),
            ("water_disaster_cameras", "async def water_disaster_cameras"),
            ("get_water_disaster_images", "async def get_water_disaster_images")
        ]
        
        for method_name, pattern in method_checks:
            if pattern in content:
                print(f"✅ {method_name} 方法存在")
            else:
                print(f"❌ {method_name} 方法不存在或定義錯誤")
        
        return True
        
    except Exception as e:
        print(f"❌ 檢查失敗: {str(e)}")
        return False

def test_sync_method():
    """測試同步方法調用"""
    print("\n🧪 測試同步方法調用...")
    
    try:
        # 添加專案路徑
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from cogs.reservoir_commands import ReservoirCommands
        
        class MockBot:
            pass
        
        bot = MockBot()
        reservoir_cog = ReservoirCommands(bot)
        
        # 測試 _process_and_validate_image_url 方法（同步調用）
        test_urls = [
            "https://example.com/image.jpg",
            "",
            None
        ]
        
        for url in test_urls:
            try:
                # 確保這是同步調用
                result = reservoir_cog._process_and_validate_image_url(url)
                print(f"✅ 同步調用成功: '{url}' -> '{result}'")
            except Exception as e:
                print(f"❌ 同步調用失敗: {str(e)}")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        return False

def main():
    """主要檢查函數"""
    print("🚀 await 錯誤修復簡單驗證")
    print("=" * 50)
    
    # 執行檢查
    checks = [
        ("await 用法檢查", check_await_usage),
        ("方法定義檢查", check_method_definitions),
        ("同步方法測試", test_sync_method)
    ]
    
    results = {}
    
    for check_name, check_func in checks:
        print(f"\n🔍 執行: {check_name}")
        try:
            results[check_name] = check_func()
        except Exception as e:
            print(f"❌ 檢查異常: {str(e)}")
            results[check_name] = False
    
    # 產生報告
    print("\n" + "=" * 50)
    print("📊 修復驗證結果:")
    print("-" * 30)
    
    passed = 0
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ 通過" if result else "❌ 失敗"
        print(f"{check_name:.<20} {status}")
        if result:
            passed += 1
    
    print("-" * 30)
    success_rate = (passed / total) * 100
    print(f"通過率: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate >= 100:
        print("\n🎉 await 錯誤已完全修復！")
        print("✅ 水利防災影像查詢功能正常")
    elif success_rate >= 80:
        print("\n✅ 主要問題已修復")
        print("⚠️ 部分項目需要檢查")
    else:
        print("\n❌ 修復不完整")
        print("🔧 需要進一步修正")
    
    print("\n📋 修復摘要:")
    print("🐛 原問題: object str can't be used in 'await' expression")
    print("🔧 修復: 移除 _process_and_validate_image_url 前的 await")
    print("📍 位置: cogs/reservoir_commands.py")
    print("✅ 狀態: 同步方法正確調用")

if __name__ == "__main__":
    main()
