#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
機器人狀態測試腳本
測試機器人啟動時是否正確設定「正在玩 C. Y.」的狀態

作者: Discord Bot Project
日期: 2025-01-05
"""

import sys
import os
import asyncio
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

# 添加專案根目錄到 Python 路徑
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import discord
    from bot import CustomBot
except ImportError as e:
    print(f"❌ 無法導入模組: {e}")
    print("請確保您已安裝所有依賴套件：pip install -r requirements.txt")
    sys.exit(1)

class TestBotStatus(unittest.TestCase):
    """測試機器人狀態設定"""
    
    def setUp(self):
        """測試前的設置"""
        self.bot = None
        
    def tearDown(self):
        """測試後的清理"""
        if self.bot:
            # 清理測試用的機器人實例
            pass
    
    @patch('discord.Client.change_presence')
    async def test_on_ready_sets_status(self, mock_change_presence):
        """測試 on_ready 事件是否正確設定機器人狀態"""
        print("\n🧪 測試機器人狀態設定...")
        
        # 模擬機器人用戶和伺服器
        mock_user = MagicMock()
        mock_user.name = "TestBot"
        mock_user.__str__ = lambda: "TestBot#1234"
        
        mock_guild = MagicMock()
        mock_guild.name = "測試伺服器"
        mock_guild.id = 123456789
        mock_guild.member_count = 100
        
        # 創建機器人實例的模擬
        with patch('bot.CustomBot.__init__', return_value=None):
            bot = CustomBot()
            bot.user = mock_user
            bot.guilds = [mock_guild]
            bot.change_presence = AsyncMock()
            
            # 執行 on_ready 事件
            await bot.on_ready()
            
            # 驗證 change_presence 被正確調用
            bot.change_presence.assert_called_once()
            call_args = bot.change_presence.call_args
            
            # 檢查狀態參數
            self.assertEqual(call_args.kwargs['status'], discord.Status.online)
            
            # 檢查活動參數
            activity = call_args.kwargs['activity']
            self.assertIsInstance(activity, discord.Game)
            self.assertEqual(activity.name, "C. Y.")
            
            print("✅ 機器人狀態設定測試通過")
            print(f"   狀態: {call_args.kwargs['status']}")
            print(f"   活動: 正在玩 {activity.name}")
    
    def test_activity_object_creation(self):
        """測試 Discord.Game 活動物件的創建"""
        print("\n🧪 測試活動物件創建...")
        
        activity = discord.Game(name="C. Y.")
        
        self.assertIsInstance(activity, discord.Game)
        self.assertEqual(activity.name, "C. Y.")
        self.assertEqual(activity.type, discord.ActivityType.playing)
        
        print("✅ 活動物件創建測試通過")
        print(f"   活動名稱: {activity.name}")
        print(f"   活動類型: {activity.type.name}")
    
    def test_status_enum(self):
        """測試 Discord 狀態枚舉"""
        print("\n🧪 測試狀態枚舉...")
        
        status = discord.Status.online
        
        self.assertEqual(status, discord.Status.online)
        self.assertEqual(str(status), "online")
        
        print("✅ 狀態枚舉測試通過")
        print(f"   狀態: {status}")

async def run_async_tests():
    """運行異步測試"""
    test_case = TestBotStatus()
    test_case.setUp()
    
    try:
        await test_case.test_on_ready_sets_status()
        print("\n✅ 所有異步測試通過")
    except Exception as e:
        print(f"\n❌ 異步測試失敗: {e}")
        return False
    finally:
        test_case.tearDown()
    
    return True

def main():
    """主函數"""
    print("=" * 60)
    print("機器人狀態測試腳本")
    print("=" * 60)
    print("測試項目:")
    print("1. on_ready 事件是否正確設定機器人狀態")
    print("2. Discord.Game 活動物件創建")
    print("3. Discord 狀態枚舉")
    print("-" * 60)
    
    # 運行同步測試
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBotStatus)
    result = unittest.TextTestRunner(verbosity=0, stream=open(os.devnull, 'w')).run(suite)
    
    # 手動運行測試方法（因為 unittest 不支持異步）
    test_case = TestBotStatus()
    test_case.setUp()
    
    try:
        # 測試活動物件創建
        test_case.test_activity_object_creation()
        
        # 測試狀態枚舉
        test_case.test_status_enum()
        
        print("\n✅ 所有同步測試通過")
        
    except Exception as e:
        print(f"\n❌ 同步測試失敗: {e}")
        return False
    finally:
        test_case.tearDown()
    
    # 運行異步測試
    print("\n" + "-" * 40)
    print("運行異步測試...")
    
    try:
        # 檢查是否已有事件循環
        try:
            loop = asyncio.get_running_loop()
            print("⚠️  發現運行中的事件循環，創建新任務...")
            task = loop.create_task(run_async_tests())
            # 這在 Jupyter 等環境中可能需要不同的處理
        except RuntimeError:
            # 沒有運行中的事件循環，創建新的
            result = asyncio.run(run_async_tests())
            if not result:
                return False
        
    except Exception as e:
        print(f"❌ 異步測試執行失敗: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 所有測試完成！機器人狀態設定功能正常")
    print("=" * 60)
    print("\n機器人啟動時將自動設定為:")
    print("📊 狀態: 線上 (online)")
    print("🎮 活動: 正在玩 C. Y.")
    print("\n提示:")
    print("- 機器人狀態會在 on_ready 事件中自動設定")
    print("- 如果需要更改狀態文字，請修改 bot.py 中的 activity.name")
    print("- 可用的狀態類型: online, idle, dnd, invisible")
    print("- 可用的活動類型: playing, streaming, listening, watching")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
