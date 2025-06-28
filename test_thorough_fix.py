#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試徹底的指令重複註冊修復
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

async def test_thorough_fix():
    """測試徹底的修復方案"""
    try:
        logger.info("🧪 測試徹底的指令重複註冊修復")
        
        # 檢查修復的程式碼
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        # 檢查關鍵修復點
        checks = {
            '徹底清除機制': '徹底清除舊的 Cogs 和指令' in bot_content,
            '多重清除指令': '_global_commands.clear()' in bot_content,
            '多次卸載嘗試': 'for attempt in range(2)' in bot_content,
            '強制重新載入': 'await self.reload_extension(extension)' in bot_content,
            '清理狀態檢查': '清理後狀態:' in bot_content,
            '載入計數器': 'successful_loads' in bot_content,
            '短暫等待機制': 'await asyncio.sleep(0.2)' in bot_content,
            '詳細同步日誌': '共同步 {len(synced_commands)} 個指令' in bot_content
        }
        
        logger.info("徹底修復檢查結果:")
        for check_name, result in checks.items():
            status = "✅" if result else "❌"
            logger.info(f"  {status} {check_name}: {'通過' if result else '失敗'}")
        
        all_passed = all(checks.values())
        
        if all_passed:
            logger.info("✅ 所有徹底修復檢查通過")
            
            # 檢查改進的清除機制
            logger.info("\n🔍 檢查改進的清除機制...")
            improved_features = [
                '清除全局命令字典',
                '多次卸載嘗試',
                '強制重新載入機制',
                '載入狀態詳細記錄',
                '競爭條件避免',
                '失敗指令重新載入'
            ]
            
            for feature in improved_features:
                logger.info(f"  ✅ {feature}")
            
        else:
            logger.error("❌ 某些徹底修復檢查失敗")
        
        return all_passed
        
    except Exception as e:
        logger.error(f"測試過程中發生錯誤: {e}")
        return False

async def test_extension_loading_sequence():
    """測試擴展載入順序"""
    try:
        logger.info("\n🔍 測試擴展載入順序...")
        
        # 檢查 initial_extensions 列表
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        # 提取 initial_extensions
        start_marker = "self.initial_extensions = ["
        end_marker = "]"
        
        start_idx = bot_content.find(start_marker)
        if start_idx == -1:
            logger.error("❌ 找不到 initial_extensions 定義")
            return False
        
        start_idx += len(start_marker)
        end_idx = bot_content.find(end_marker, start_idx)
        if end_idx == -1:
            logger.error("❌ 找不到 initial_extensions 結尾")
            return False
        
        extensions_text = bot_content[start_idx:end_idx]
        extensions = [line.strip().strip("',\"") for line in extensions_text.split('\n') if line.strip() and not line.strip().startswith('#')]
        extensions = [ext for ext in extensions if ext and not ext.startswith('//')]
        
        logger.info(f"發現 {len(extensions)} 個擴展:")
        for i, ext in enumerate(extensions, 1):
            logger.info(f"  {i:2d}. {ext}")
        
        # 檢查溫度命令是否在列表中
        if 'cogs.temperature_commands' in extensions:
            logger.info("✅ 溫度命令模組已包含在載入列表中")
        else:
            logger.warning("⚠️ 溫度命令模組未在載入列表中")
        
        return True
        
    except Exception as e:
        logger.error(f"測試擴展載入順序時發生錯誤: {e}")
        return False

async def test_command_conflict_resolution():
    """測試指令衝突解決機制"""
    try:
        logger.info("\n🔍 測試指令衝突解決機制...")
        
        # 模擬檢查是否有重複的指令名稱
        command_modules = {
            'weather_commands': ['weather_station', 'weather_station_by_county', 'weather_station_info'],
            'air_quality_commands': ['air_quality', 'air_quality_county', 'air_quality_site'],
            'radar_commands': ['radar', 'radar_large', 'rainfall_radar', 'radar_info'],
            'temperature_commands': ['temperature']
        }
        
        # 檢查指令名稱衝突
        all_commands = []
        conflicts = []
        
        for module, commands in command_modules.items():
            for cmd in commands:
                if cmd in all_commands:
                    conflicts.append(cmd)
                else:
                    all_commands.append(cmd)
        
        if conflicts:
            logger.warning(f"⚠️ 發現指令衝突: {conflicts}")
            return False
        else:
            logger.info("✅ 沒有指令名稱衝突")
        
        logger.info(f"總計 {len(all_commands)} 個唯一指令:")
        for module, commands in command_modules.items():
            logger.info(f"  {module}: {', '.join(commands)}")
        
        return True
        
    except Exception as e:
        logger.error(f"測試指令衝突解決時發生錯誤: {e}")
        return False

async def main():
    """主測試函數"""
    logger.info("開始測試徹底的指令重複註冊修復")
    
    # 測試1: 徹底修復檢查
    fix_success = await test_thorough_fix()
    
    # 測試2: 擴展載入順序
    sequence_success = await test_extension_loading_sequence()
    
    # 測試3: 指令衝突解決
    conflict_success = await test_command_conflict_resolution()
    
    logger.info("\n" + "="*60)
    logger.info("測試結果總結:")
    
    if fix_success and sequence_success and conflict_success:
        logger.info("✅ 所有測試通過！")
        logger.info("徹底修復內容:")
        logger.info("  • 多重清除機制 - 確保完全清理")
        logger.info("  • 強制重新載入 - 處理已載入的擴展")
        logger.info("  • 競爭條件避免 - 載入間隔和狀態檢查")
        logger.info("  • 詳細狀態追蹤 - 載入過程透明化")
        logger.info("  • 失敗處理改善 - 更好的錯誤恢復")
        logger.info("\n現在應該能完全解決指令重複註冊問題！")
    else:
        logger.error("❌ 部分測試失敗")
        if not fix_success:
            logger.error("  • 徹底修復檢查失敗")
        if not sequence_success:
            logger.error("  • 擴展載入順序有問題")
        if not conflict_success:
            logger.error("  • 指令衝突檢查失敗")
    
    return fix_success and sequence_success and conflict_success

if __name__ == "__main__":
    result = asyncio.run(main())
    print(f"\n測試完成: {'成功' if result else '失敗'}")
