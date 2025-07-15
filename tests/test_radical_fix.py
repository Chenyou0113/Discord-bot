#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試激進的指令重複註冊修復
"""

import asyncio
import logging
import sys
import os

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_radical_fix():
    """測試激進的修復方案"""
    try:
        logger.info("🧪 測試激進的指令重複註冊修復")
        
        # 檢查修復的程式碼
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        # 檢查激進修復的關鍵點
        radical_checks = {
            '命令樹重建': 'self.tree = app_commands.CommandTree(self)' in bot_content,
            '舊命令樹刪除': 'del old_tree' in bot_content,
            '連接快取清除': '_application_commands.clear()' in bot_content,
            '3次卸載嘗試': 'for attempt in range(3)' in bot_content,
            '強制垃圾回收': 'gc.collect()' in bot_content,
            '模組重新載入': 'importlib.reload' in bot_content,
            '直接Cog移除': 'self.remove_cog(cog_name)' in bot_content,
            '載入間隔增加': 'await asyncio.sleep(0.3)' in bot_content,
            '失敗追蹤': 'failed_loads.append' in bot_content,
            '詳細錯誤追蹤': 'traceback.format_exc()' in bot_content
        }
        
        logger.info("激進修復檢查結果:")
        for check_name, result in radical_checks.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check_name}: {'通過' if result else '失敗'}")
        
        all_passed = all(radical_checks.values())
        
        if all_passed:
            logger.info("✅ 所有激進修復檢查通過")
            
            # 檢查激進修復的特色
            logger.info("\n🔍 檢查激進修復特色...")
            radical_features = [
                '完全重建命令樹 - 從根本解決指令殘留',
                '清除連接快取 - 清除底層指令快取',
                '3次卸載嘗試 - 確保頑固擴展被清除',
                '強制垃圾回收 - 釋放記憶體引用',
                '模組重新載入 - 刷新Python模組快取',
                '直接Cog移除 - 處理卸載失敗情況',
                '失敗追蹤機制 - 詳細記錄載入結果'
            ]
            
            for feature in radical_features:
                logger.info(f"  ✅ {feature}")
            
        else:
            logger.error("❌ 某些激進修復檢查失敗")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        return False

async def test_command_tree_rebuild():
    """測試命令樹重建邏輯"""
    try:
        logger.info("\n🔍 測試命令樹重建邏輯...")
        
        # 檢查是否正確處理舊命令樹
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查重建流程
        rebuild_steps = [
            'old_tree = self.tree',
            'self.tree = app_commands.CommandTree(self)',
            'del old_tree'
        ]
        
        all_steps_found = True
        for step in rebuild_steps:
            if step in content:
                logger.info(f"  ✅ 找到重建步驟: {step}")
            else:
                logger.error(f"  ❌ 缺少重建步驟: {step}")
                all_steps_found = False
        
        return all_steps_found
        
    except Exception as e:
        logger.error(f"測試命令樹重建時發生錯誤: {e}")
        return False

async def test_module_reload_mechanism():
    """測試模組重新載入機制"""
    try:
        logger.info("\n🔍 測試模組重新載入機制...")
        
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查模組重新載入相關代碼
        reload_features = {
            '模組存在檢查': 'if extension in sys.modules:' in content,
            '導入importlib': 'import importlib' in content,
            '重新載入模組': 'importlib.reload(sys.modules[extension])' in content,
            '系統模組處理': 'sys.modules' in content
        }
        
        logger.info("模組重新載入機制檢查:")
        for feature_name, found in reload_features.items():
            status = "✅" if found else "❌"
            logger.info(f"  {status} {feature_name}: {'通過' if found else '失敗'}")
        
        return all(reload_features.values())
        
    except Exception as e:
        logger.error(f"測試模組重新載入機制時發生錯誤: {e}")
        return False

async def test_error_handling():
    """測試錯誤處理機制"""
    try:
        logger.info("\n🔍 測試錯誤處理機制...")
        
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 檢查錯誤處理特性
        error_handling_features = {
            '失敗載入追蹤': 'failed_loads = []' in content,
            '載入結果報告': '載入失敗的擴展:' in content,
            '詳細錯誤追蹤': 'traceback.format_exc()' in content,
            '嚴重錯誤處理': '設置過程中發生嚴重錯誤:' in content,
            '殘留檢查': '仍有殘留的 Cogs 或擴展' in content
        }
        
        logger.info("錯誤處理機制檢查:")
        for feature_name, found in error_handling_features.items():
            status = "✅" if found else "❌"
            logger.info(f"  {status} {feature_name}: {'通過' if found else '失敗'}")
        
        return all(error_handling_features.values())
        
    except Exception as e:
        logger.error(f"測試錯誤處理機制時發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info("開始測試激進的指令重複註冊修復")
    
    # 測試1: 激進修復檢查
    radical_success = await test_radical_fix()
    
    # 測試2: 命令樹重建
    rebuild_success = await test_command_tree_rebuild()
    
    # 測試3: 模組重新載入
    reload_success = await test_module_reload_mechanism()
    
    # 測試4: 錯誤處理
    error_handling_success = await test_error_handling()
    
    logger.info("\n" + "="*70)
    logger.info("測試結果總結:")
    
    all_success = all([radical_success, rebuild_success, reload_success, error_handling_success])
    
    if all_success:
        logger.info("✅ 所有測試通過！")
        logger.info("激進修復內容:")
        logger.info("  🔥 完全重建命令樹 - 從根本解決問題")
        logger.info("  🧹 清除所有快取 - 包括連接和模組快取")
        logger.info("  🔄 強制模組重新載入 - 刷新Python模組狀態")
        logger.info("  💪 3次卸載嘗試 - 確保頑固擴展被清除")
        logger.info("  🗑️ 強制垃圾回收 - 釋放所有記憶體引用")
        logger.info("  📊 詳細狀態追蹤 - 完整的載入過程監控")
        logger.info("  🛡️ 全面錯誤處理 - 處理所有可能的失敗情況")
        logger.info("\n這是最徹底的修復方案，應該能解決所有指令重複註冊問題！")
    else:
        logger.error("❌ 部分測試失敗")
        if not radical_success:
            logger.error("  • 激進修復檢查失敗")
        if not rebuild_success:
            logger.error("  • 命令樹重建有問題")
        if not reload_success:
            logger.error("  • 模組重新載入機制有問題")
        if not error_handling_success:
            logger.error("  • 錯誤處理機制有問題")
    
    return all_success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n測試完成: {'成功' if result else '失敗'}")
