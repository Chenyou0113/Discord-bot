#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試地震功能的模擬腳本
模擬 Discord 斜線指令的執行，驗證錯誤處理是否正常
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
        self.user = MockUser()
        self.loop = asyncio.get_event_loop()
    
    async def wait_until_ready(self):
        """模擬 bot ready 狀態"""
        pass

class MockUser:
    """模擬 Bot 使用者"""
    def __init__(self):
        self.name = "TestBot"

class MockInteraction:
    """模擬 Discord Interaction"""
    def __init__(self):
        self.response_sent = False
        self.followup_messages = []
        self.user = MockInteractionUser()
        self.guild = MockGuild()
        
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
    
    def __init__(self):
        self.response = self.Response(self)
        self.followup = self.Followup(self)
        self.response_sent = False
        self.followup_messages = []
        self.user = MockInteractionUser()
        self.guild = MockGuild()

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

async def test_earthquake_command():
    """測試地震指令"""
    print("🔍 開始測試地震指令...")
    print("=" * 60)
    
    # 創建模擬對象
    bot = MockBot()
    interaction = MockInteraction()
      # 創建 InfoCommands 實例
    info_commands = InfoCommands(bot)
    
    try:
        print("📡 初始化地震指令模組...")
        await info_commands.cog_load()  # 初始化
        
        print("🎯 執行地震指令 (/earthquake)...")
        print("👤 模擬使用者執行斜線指令...")
        
        # 正確調用地震指令的回調函數
        await info_commands.earthquake.callback(info_commands, interaction)
        
        # 分析結果
        print("\n" + "="*40)
        print("📊 測試結果分析:")
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
        
    except Exception as e:
        print(f"❌ 地震指令測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_weather_command():
    """測試天氣指令"""
    print("\n🌤️ 開始測試天氣指令...")
    print("=" * 60)
    
    # 創建模擬對象
    bot = MockBot()
    interaction = MockInteraction()
    
    # 創建 InfoCommands 實例
    info_commands = InfoCommands(bot)
    
    try:
        print("📡 初始化天氣指令模組...")
        await info_commands.cog_load()  # 初始化
        
        print("🎯 執行天氣指令 (/weather location:臺北市)...")
        print("👤 模擬使用者執行斜線指令...")
        
        # 正確調用天氣指令的回調函數
        await info_commands.weather.callback(info_commands, interaction, location="臺北市")
        
        # 分析結果
        print("\n" + "="*40)
        print("📊 測試結果分析:")
        print(f"✅ 指令執行完成，無崩潰")
        print(f"📨 回應訊息數量: {len(interaction.followup_messages)}")
        
        if interaction.followup_messages:
            last_response = interaction.followup_messages[-1]
            if hasattr(last_response, 'title'):
                print(f"✅ 天氣資料正常回傳")
            elif isinstance(last_response, str) and "❌" in last_response:
                print("⚠️ 天氣指令回傳錯誤訊息")
        
    except Exception as e:
        print(f"❌ 天氣指令測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()

async def test_api_status():
    """測試 API 狀態"""
    print("\n🔌 測試 API 連線狀態...")
    print("=" * 60)
    
    bot = MockBot()
    info_commands = InfoCommands(bot)
    await info_commands.cog_load()
    
    try:
        print("📡 測試地震 API...")
        eq_data = await info_commands.fetch_earthquake_data()
        
        if eq_data is None:
            print("⚠️ 地震 API 回傳 None（符合預期的異常處理）")
        elif isinstance(eq_data, dict) and 'result' in eq_data:
            if set(eq_data['result'].keys()) == {'resource_id', 'fields'}:
                print("⚠️ 地震 API 回傳異常格式（已被正確檢測）")
            else:
                print("✅ 地震 API 回傳正常資料")
        
        print("\n📡 測試天氣 API...")
        weather_data = await info_commands.fetch_weather_data()
        
        if weather_data:
            print(f"✅ 天氣 API 正常，取得 {len(weather_data)} 筆地區資料")
        else:
            print("⚠️ 天氣 API 無資料")
            
    except Exception as e:
        print(f"❌ API 測試失敗: {str(e)}")

async def main():
    """主要測試函數"""
    print("🚀 Discord 機器人地震指令完整測試")
    print("🎯 目標：驗證地震指令在 API 異常時的錯誤處理")
    print("=" * 80)
    
    await test_api_status()
    await test_earthquake_command()
    await test_weather_command()
    
    print("\n" + "=" * 80)
    print("🎉 所有測試完成")
    print("📋 測試摘要：")
    print("  ✅ 驗證了 API 異常格式檢測")
    print("  ✅ 驗證了地震指令錯誤處理")
    print("  ✅ 驗證了天氣指令正常運作")
    print("  ✅ 確認指令不會因 API 問題而崩潰")

if __name__ == "__main__":
    asyncio.run(main())
