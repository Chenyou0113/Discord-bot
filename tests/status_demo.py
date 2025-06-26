#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
機器人狀態設定示範腳本
展示如何在 Discord 機器人中設定「正在玩 C. Y.」的狀態

作者: Discord Bot Project
日期: 2025-01-05
"""

import discord

def demonstrate_status_setting():
    """示範機器人狀態設定"""
    print("=" * 60)
    print("🤖 Discord 機器人狀態設定示範")
    print("=" * 60)
    
    print("\n📋 機器人狀態設定說明:")
    print("1. 在 bot.py 的 on_ready 事件中設定機器人狀態")
    print("2. 使用 discord.Game 創建「正在玩」活動")
    print("3. 使用 change_presence 方法更新機器人狀態")
    
    print("\n🎮 狀態設定代碼示例:")
    print("```python")
    print("async def on_ready(self):")
    print("    # 設定機器人狀態為「正在玩 C. Y.」")
    print("    activity = discord.Game(name=\"C. Y.\")")
    print("    await self.change_presence(status=discord.Status.online, activity=activity)")
    print("    print('機器人狀態已設定為「正在玩 C. Y.」')")
    print("```")
    
    print("\n📊 可用的狀態類型:")
    try:
        statuses = [
            ("online", "線上", "🟢"),
            ("idle", "閒置", "🟡"),
            ("dnd", "請勿打擾", "🔴"),
            ("invisible", "隱身", "⚫")
        ]
        
        for status_name, status_desc, emoji in statuses:
            print(f"   {emoji} discord.Status.{status_name} - {status_desc}")
    except Exception as e:
        print(f"   ⚠️  無法列出狀態類型: {e}")
    
    print("\n🎯 可用的活動類型:")
    try:
        activities = [
            ("Game", "正在玩", "🎮"),
            ("Streaming", "正在直播", "📺"),
            ("Listening", "正在聽", "🎵"),
            ("Watching", "正在看", "👀"),
            ("Custom", "自定義", "✨")
        ]
        
        for activity_class, activity_desc, emoji in activities:
            print(f"   {emoji} discord.{activity_class} - {activity_desc}")
    except Exception as e:
        print(f"   ⚠️  無法列出活動類型: {e}")
    
    print("\n📝 實際設定示例:")
    try:
        # 創建活動物件
        activity = discord.Game(name="C. Y.")
        status = discord.Status.online
        
        print(f"✅ 狀態: {status}")
        print(f"✅ 活動: {activity}")
        print(f"✅ 活動名稱: {activity.name}")
        print(f"✅ 活動類型: {activity.type.name}")
        
        print("\n🎉 機器人將顯示為:")
        print(f"   🤖 {status.name.title()} • 正在玩 {activity.name}")
        
    except Exception as e:
        print(f"❌ 創建狀態物件時發生錯誤: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 狀態設定示範完成")
    print("=" * 60)
    
    print("\n📋 實施檢查清單:")
    print("□ 1. 在 CustomBot 類中添加 on_ready 方法")
    print("□ 2. 創建 discord.Game(name='C. Y.') 活動物件")
    print("□ 3. 調用 change_presence 設定狀態和活動")
    print("□ 4. 重啟機器人以應用新設定")
    print("□ 5. 在 Discord 中確認機器人狀態顯示正確")
    
    print("\n💡 提示:")
    print("- 機器人需要重新啟動才能看到狀態變更")
    print("- 狀態設定在 on_ready 事件中執行")
    print("- 可以隨時使用 change_presence 更改狀態")
    
    return True

if __name__ == "__main__":
    try:
        demonstrate_status_setting()
    except Exception as e:
        print(f"❌ 示範過程發生錯誤: {e}")
        exit(1)
