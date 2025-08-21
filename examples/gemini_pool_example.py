#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini API 連接池使用範例
本範例展示如何使用 Gemini API 連接池進行 AI 內容生成
包含基本使用、聊天功能、多 API 密鑰管理與統計
"""

import os
import asyncio
import logging
from typing import Dict, Any
import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

# 導入 Gemini API 連接池相關功能
from utils.gemini_pool import (
    generate_content,         # 生成內容
    create_chat,              # 創建聊天會話
    get_pool_stats,           # 獲取連接池統計
    get_api_key_stats,        # 獲取 API 密鑰統計
    reset_api_pool,           # 重置連接池
    reset_api_stats           # 重置 API 統計
)

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 載入環境變數
load_dotenv()

async def example_generate_content():
    """展示如何使用連接池生成內容"""
    
    logger.info("=== 基本內容生成範例 ===")
    
    # 基本文本生成範例
    prompt = "請用繁體中文介紹台灣的四季特色，每季100字"
    logger.info(f"發送提示: {prompt}")
    
    # 使用 generate_content 函數生成內容
    # 第一個參數是提示文本，第二個參數是模型名稱（可選）
    response, success = await generate_content(
        prompt=prompt,
        model_name="gemini-2.0-flash-exp",
        temperature=0.7
    )
    
    if success:
        logger.info(f"成功生成內容: {response.text}")
    else:
        logger.error("生成內容失敗")
    
    # 生成圖像描述 (使用 gemini-pro-vision 模型)
    image_prompt = "這張圖顯示什麼？請提供詳細描述"
    logger.info("=== 圖像描述生成範例 (未提供實際圖像) ===")
    
    # 注意：實際使用時需要提供有效的圖像數據
    # 這裡僅作示範，不包含實際圖像
    # 實際使用方式:
    # image_data = ...  # PIL 圖像或 base64 編碼數據
    # response, success = await generate_content(
    #     prompt=[image_prompt, image_data],
    #     model_name="gemini-pro-vision"
    # )

async def example_chat_conversation():
    """展示如何使用連接池進行多輪對話"""
    
    logger.info("=== 多輪對話範例 ===")
    
    # 創建聊天會話 (使用 gemini-2.0-flash-exp 模型)
    chat, instance_index = await create_chat(model_name="gemini-2.0-flash-exp")
    
    if chat is None:
        logger.error("創建聊天會話失敗")
        return
    
    logger.info(f"成功創建聊天會話，使用實例 #{instance_index+1}")
    
    # 第一輪對話
    user_input = "你好，請問台北有哪些著名的旅遊景點？"
    logger.info(f"用戶: {user_input}")
    
    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: chat.send_message(user_input)
        )
        logger.info(f"AI: {response.text}")
        
        # 第二輪對話 (延續上下文)
        user_input = "這些地方哪個適合帶小孩去？"
        logger.info(f"用戶: {user_input}")
        
        response = await asyncio.get_event_loop().run_in_executor(
            None, lambda: chat.send_message(user_input)
        )
        logger.info(f"AI: {response.text}")
        
    except Exception as e:
        logger.error(f"聊天過程中發生錯誤: {str(e)}")

async def example_view_stats():
    """展示如何查看連接池統計信息"""
    
    logger.info("=== 連接池統計信息範例 ===")
    
    # 獲取連接池統計
    pool_stats = get_pool_stats()
    logger.info(f"連接池中共有 {len(pool_stats)} 種模型")
    
    # 顯示每個模型的詳細狀態
    for model_name, stats in pool_stats.items():
        # 計算健康度百分比
        health_percentage = 100 * stats['active_instances'] / stats['pool_size']
        health_status = "良好" if health_percentage >= 80 else "注意" if health_percentage >= 50 else "危險"
        
        logger.info(f"模型: {model_name}")
        logger.info(f"  - 連接池大小: {stats['pool_size']}")
        logger.info(f"  - 活躍連接: {stats['active_instances']}")
        logger.info(f"  - 錯誤連接: {stats['error_instances']}")
        logger.info(f"  - 總請求數: {stats['total_usage']}")
        logger.info(f"  - 健康狀態: {health_status}")
        logger.info(f"  - 使用分配: {stats['usage_distribution']}")
        logger.info(f"  - API 金鑰分佈: {stats['key_distribution']}")
    
    logger.info("=== API 密鑰統計信息範例 ===")
    
    # 獲取 API 密鑰統計
    key_stats = get_api_key_stats()
    
    logger.info(f"共有 {key_stats['total_keys']} 個 API 密鑰")
    logger.info(f"總請求數: {key_stats['total_requests']}")
    logger.info(f"失敗請求: {key_stats['failed_requests']} ({key_stats['failed_requests'] / max(1, key_stats['total_requests']) * 100:.2f}%)")
    logger.info(f"完全失敗: {key_stats['complete_failures']}")
    logger.info(f"平均執行時間: {key_stats['average_execution_time']}s")
    logger.info(f"最後輪換時間: {key_stats['last_rotation']}")
    
    # 顯示每個密鑰的詳細統計
    for key_id, stats in key_stats["key_usage"].items():
        logger.info(f"API 密鑰 {key_id}:")
        logger.info(f"  - 使用次數: {stats['usage']}")
        logger.info(f"  - 錯誤次數: {stats['errors']}")
        logger.info(f"  - 平均時間: {stats['avg_time']}s")
        logger.info(f"  - 錯誤率: {stats['error_rate']}%")

async def example_reset_pool():
    """展示如何重置連接池"""
    
    logger.info("=== 重置連接池範例 ===")
    
    # 重置特定模型的連接池
    model_name = "gemini-2.0-flash-exp"
    success = reset_api_pool(model_name)
    
    if success:
        logger.info(f"已重置模型 {model_name} 的連接池")
    else:
        logger.error(f"重置模型 {model_name} 的連接池失敗")
    
    # 重置所有模型的連接池
    # success = reset_api_pool()
    # if success:
    #     logger.info("已重置所有模型的連接池")
    # else:
    #     logger.error("重置所有模型的連接池失敗")
    
    # 重置 API 統計數據
    success = reset_api_stats()
    if success:
        logger.info("已重置 API 統計數據")
    else:
        logger.error("重置 API 統計數據失敗")

async def example_discord_integration(bot: commands.Bot):
    """展示如何在 Discord 機器人中整合 API 連接池"""
    
    @bot.tree.command(name="ai問答", description="使用 AI 回答問題")
    async def ai_qa(interaction: discord.Interaction, 問題: str):
        """AI 問答指令"""
        await interaction.response.defer()
        
        try:
            # 使用 API 連接池生成回應
            response, success = await generate_content(
                prompt=f"請回答以下問題: {問題}",
                model_name="gemini-2.0-flash-exp"
            )
            
            if success:
                await interaction.followup.send(f"**問題:** {問題}\n\n**回答:** {response.text}")
            else:
                await interaction.followup.send("❌ 生成回應時發生錯誤，請稍後再試。")
        
        except Exception as e:
            logger.error(f"處理 AI 問答時發生錯誤: {str(e)}")
            await interaction.followup.send("❌ 處理請求時發生錯誤，請稍後再試。")
    
    @bot.tree.command(name="api統計", description="查看 API 使用統計")
    @app_commands.checks.has_permissions(administrator=True)
    async def api_stats(interaction: discord.Interaction):
        """API 統計指令 (僅限管理員)"""
        
        # 獲取 API 密鑰統計
        key_stats = get_api_key_stats()
        
        embed = discord.Embed(
            title="🔑 Gemini API 密鑰統計",
            description=(
                f"共有 **{key_stats['total_keys']}** 個 API 密鑰\n"
                f"總請求數: **{key_stats['total_requests']}**\n"
                f"失敗請求: **{key_stats['failed_requests']}** "
                f"({key_stats['failed_requests'] / max(1, key_stats['total_requests']) * 100:.2f}%)\n"
                f"完全失敗: **{key_stats['complete_failures']}**\n"
                f"平均執行時間: **{key_stats['average_execution_time']}**s\n"
                f"最後輪換時間: {key_stats['last_rotation']}"
            ),
            color=discord.Color.gold()
        )
        
        # 添加每個密鑰的詳細統計
        for key_id, stats in key_stats["key_usage"].items():
            # 計算健康狀況
            error_rate = stats["error_rate"]
            health_status = "✅ 良好" if error_rate < 5 else "⚠️ 注意" if error_rate < 20 else "❌ 危險"
            
            embed.add_field(
                name=f"🔑 {key_id}",
                value=(
                    f"使用次數: **{stats['usage']}**\n"
                    f"錯誤次數: **{stats['errors']}**\n"
                    f"平均時間: **{stats['avg_time']}**s\n"
                    f"錯誤率: **{stats['error_rate']}%**\n"
                    f"狀態: {health_status}"
                ),
                inline=True
            )
        
        await interaction.response.send_message(embed=embed)

async def run_examples():
    """運行所有範例"""
    await example_generate_content()
    print("\n" + "-" * 50 + "\n")
    
    await example_chat_conversation()
    print("\n" + "-" * 50 + "\n")
    
    await example_view_stats()
    print("\n" + "-" * 50 + "\n")
    
    await example_reset_pool()

if __name__ == "__main__":
    """當作為獨立腳本運行時"""
    asyncio.run(run_examples())

"""
===== Gemini API 連接池使用說明 =====

1. 基本概念
   - API 連接池: 管理多個 Gemini API 實例，實現負載均衡和資源優化
   - API 金鑰輪換: 自動輪換多個 API 金鑰，避免單一金鑰超出限額
   - 健康檢查: 監控 API 實例的健康狀況，自動修復問題實例
   - 統計追蹤: 記錄和分析 API 使用情況和錯誤率

2. 主要功能
   - generate_content: 使用連接池生成內容
   - create_chat: 創建聊天會話
   - get_pool_stats: 獲取連接池統計信息
   - get_api_key_stats: 獲取 API 密鑰統計
   - reset_api_pool: 重置連接池
   - reset_api_stats: 重置 API 統計

3. 內容生成流程
   a. 選擇最佳 API 實例 (基於負載和健康狀況)
   b. 選擇健康的 API 金鑰 (基於使用量和錯誤率)
   c. 使用選中的實例和金鑰發送請求
   d. 如果失敗，自動重試其他實例
   e. 記錄使用統計和結果

4. API 金鑰輪換策略
   - 定期檢查金鑰健康狀況 (每 5 分鐘)
   - 根據使用量和錯誤率計算健康分數
   - 自動替換不健康的金鑰
   - 新請求優先使用健康狀況良好的金鑰

5. 最佳實踐
   - 使用異步函數 (generate_content, create_chat)
   - 使用適當的模型名稱 (gemini-2.0-flash-exp, gemini-pro-vision)
   - 處理請求失敗的情況
   - 定期查看統計信息，監控 API 使用情況

6. 故障排除
   - 檢查 API 金鑰統計，找出問題金鑰
   - 重置出現問題的模型連接池
   - 如果問題持續，可以重置所有統計數據
   - 查看日誌獲取詳細錯誤信息

7. 進階功能
   - 支援多種 Gemini 模型
   - 可視化 API 使用統計
   - 自動調整連接池大小
   - 自動檢測和處理 API 限額問題
"""
