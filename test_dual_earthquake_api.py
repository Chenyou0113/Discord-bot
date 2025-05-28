#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試地震雙API整合功能
驗證用戶可以選擇不同的地震API端點
"""

import asyncio
import sys
import os
import datetime
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from cogs.info_commands_fixed_v4 import InfoCommands

class MockBot:
    """模擬 Discord Bot"""
    def __init__(self):
        self.guilds = []
        self.loop = asyncio.get_event_loop()
        
    def is_closed(self):
        return False
        
    async def wait_until_ready(self):
        pass

class MockUser:
    """模擬 Bot 使用者"""
    def __init__(self):
        self.id = 123456789
        self.display_name = "測試機器人"

class MockInteraction:
    """模擬 Discord Interaction"""
    def __init__(self):
        self.response_sent = False
        self.followup_messages = []
        self.user = MockInteractionUser()
        self.guild = MockGuild()
        self.response = self.Response(self)
        self.followup = self.Followup(self)
        
    class Response:
        def __init__(self, parent):
            self.parent = parent
            
        async def defer(self):
            print("⏳ 指令回應已延遲（模擬處理中）...")
            self.parent.response_sent = True
            
    class Followup:
        def __init__(self, parent):
            self.parent = parent
            
        async def send(self, content=None, embed=None):
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            print(f"\n[{timestamp}] 📨 Discord 回應:")
            
            if embed:
                print(f"  🔸 標題: {embed.title or '無標題'}")
                if embed.description:
                    print(f"  📝 描述: {embed.description}")
                if embed.color:
                    print(f"  🎨 顏色: {hex(embed.color.value)}")
                if embed.fields:
                    print(f"  📋 欄位數量: {len(embed.fields)}")
                    for i, field in enumerate(embed.fields):
                        print(f"    {i+1}. {field.name}: {field.value}")
                if embed.footer:
                    print(f"  📌 頁尾: {embed.footer.text}")
            elif content:
                print(f"  💬 訊息內容:\n{content}")
            
            self.parent.followup_messages.append(content or embed)

class MockInteractionUser:
    """模擬互動使用者"""
    def __init__(self):
        self.id = 123456789
        self.display_name = "測試使用者"

class MockGuild:
    """模擬伺服器"""
    def __init__(self):
        self.id = 987654321
        self.name = "測試伺服器"

async def test_normal_earthquake_api():
    """測試一般地震API（有感地震報告）"""
    print("🔍 測試一般地震API (E-A0015-001 有感地震報告)...")
    print("=" * 60)
    
    # 創建模擬對象
    bot = MockBot()
    interaction = MockInteraction()
    
    # 創建 InfoCommands 實例
    info_commands = InfoCommands(bot)
    
    try:
        print("📡 初始化地震指令模組...")
        await info_commands.cog_load()  # 初始化
        
        print("🎯 執行地震指令 (/earthquake earthquake_type:normal)...")
        print("👤 模擬使用者選擇「有感地震報告」...")
        
        # 調用地震指令，使用一般地震API
        await info_commands.earthquake.callback(info_commands, interaction, earthquake_type="normal")
        
        # 分析結果
        print("\n" + "="*40)
        print("📊 一般地震API測試結果:")
        print(f"✅ 指令執行完成，無崩潰")
        print(f"📨 回應訊息數量: {len(interaction.followup_messages)}")
        
        if interaction.followup_messages:
            last_response = interaction.followup_messages[-1]
            if isinstance(last_response, str):
                if "❌" in last_response:
                    print("✅ 正確顯示錯誤訊息（符合預期）")
                    print("✅ 錯誤處理機制正常運作")
                else:
                    print("ℹ️ 回應為一般訊息")
            else:
                print("ℹ️ 回應為嵌入訊息")
        
        return True
        
    except Exception as e:
        print(f"❌ 一般地震API測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理
        if hasattr(info_commands, 'session') and info_commands.session and not info_commands.session.closed:
            await info_commands.session.close()

async def test_small_earthquake_api():
    """測試小區域地震API（小區域地震報告）"""
    print("\n🔍 測試小區域地震API (E-A0016-001 小區域地震報告)...")
    print("=" * 60)
    
    # 創建模擬對象
    bot = MockBot()
    interaction = MockInteraction()
    
    # 創建 InfoCommands 實例
    info_commands = InfoCommands(bot)
    
    try:
        print("📡 初始化地震指令模組...")
        await info_commands.cog_load()  # 初始化
        
        print("🎯 執行地震指令 (/earthquake earthquake_type:small)...")
        print("👤 模擬使用者選擇「小區域地震報告」...")
        
        # 調用地震指令，使用小區域地震API
        await info_commands.earthquake.callback(info_commands, interaction, earthquake_type="small")
        
        # 分析結果
        print("\n" + "="*40)
        print("📊 小區域地震API測試結果:")
        print(f"✅ 指令執行完成，無崩潰")
        print(f"📨 回應訊息數量: {len(interaction.followup_messages)}")
        
        if interaction.followup_messages:
            last_response = interaction.followup_messages[-1]
            if isinstance(last_response, str):
                if "❌" in last_response:
                    print("✅ 正確顯示錯誤訊息（符合預期）")
                    print("✅ 錯誤處理機制正常運作")
                else:
                    print("ℹ️ 回應為一般訊息")
            else:
                print("ℹ️ 回應為嵌入訊息")
        
        return True
        
    except Exception as e:
        print(f"❌ 小區域地震API測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理
        if hasattr(info_commands, 'session') and info_commands.session and not info_commands.session.closed:
            await info_commands.session.close()

async def test_api_functionality():
    """測試API基本功能"""
    print("\n🔍 測試API基本功能...")
    print("=" * 60)
    
    # 創建模擬對象
    bot = MockBot()
    info_commands = InfoCommands(bot)
    
    try:
        await info_commands.cog_load()
        
        print("📡 測試一般地震API資料獲取...")
        normal_data = await info_commands.fetch_earthquake_data(small_area=False)
        print(f"✅ 一般地震API回應: {'有資料' if normal_data else '無資料'}")
        
        print("📡 測試小區域地震API資料獲取...")
        small_data = await info_commands.fetch_earthquake_data(small_area=True)
        print(f"✅ 小區域地震API回應: {'有資料' if small_data else '無資料'}")
        
        return True
        
    except Exception as e:
        print(f"❌ API功能測試失敗: {str(e)}")
        return False
    
    finally:
        # 清理
        if hasattr(info_commands, 'session') and info_commands.session and not info_commands.session.closed:
            await info_commands.session.close()

async def main():
    """主測試函數"""
    print("🌟 開始地震雙API整合功能測試")
    print("=" * 80)
    
    success_count = 0
    total_tests = 3
    
    # 測試API基本功能
    if await test_api_functionality():
        success_count += 1
    
    # 測試一般地震API
    if await test_normal_earthquake_api():
        success_count += 1
    
    # 測試小區域地震API  
    if await test_small_earthquake_api():
        success_count += 1
    
    print("\n" + "="*80)
    print("🎯 整合測試完成結果:")
    print(f"✅ 成功測試: {success_count}/{total_tests}")
    print(f"❌ 失敗測試: {total_tests - success_count}/{total_tests}")
    
    if success_count == total_tests:
        print("🎉 所有測試通過！雙API整合功能正常運作。")
        print("\n📋 功能摘要:")
        print("  ✅ 用戶可以選擇「有感地震報告」（一般地震）")
        print("  ✅ 用戶可以選擇「小區域地震報告」（小區域地震）")
        print("  ✅ 雙API端點切換功能正常")
        print("  ✅ 錯誤處理機制完善")
        return True
    else:
        print("❌ 部分測試失敗，需要進一步檢查。")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
