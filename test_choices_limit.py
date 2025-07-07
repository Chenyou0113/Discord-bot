#!/usr/bin/env python3
"""
測試 Discord app_commands choices 數量限制修正
"""

import discord
from discord.ext import commands
from discord import app_commands
import sys
import os

# 添加 cogs 目錄到 Python 路徑
sys.path.append(os.path.join(os.path.dirname(__file__), 'cogs'))

def test_choices_limit():
    """測試 choices 數量是否符合 Discord 限制"""
    
    # 手動定義 road_type 選項（從程式碼中複製）
    road_type_choices = [
        "台1線", "台2線", "台3線", "台4線", "台5線", "台7線", "台8線", "台9線",
        "台11線", "台14線", "台15線", "台17線", "台18線", "台19線", "台20線",
        "台21線", "台24線", "台26線", "台61線", "台62線", "台64線", "台65線",
        "台66線", "台68線", "台88線"
    ]
    
    # 手動定義 county 選項（從程式碼中複製）
    county_choices = [
        "臺北市", "新北市", "桃園市", "臺中市", "臺南市", "高雄市", "基隆市",
        "新竹市", "嘉義市", "新竹縣", "苗栗縣", "彰化縣", "南投縣", "雲林縣",
        "嘉義縣", "屏東縣", "宜蘭縣", "花蓮縣", "台東縣"
    ]
    
    print(f"road_type 選項數量: {len(road_type_choices)}")
    print(f"Discord 限制: 25")
    
    if len(road_type_choices) <= 25:
        print("✅ road_type 符合 Discord choices 數量限制")
    else:
        print("❌ road_type 超過 Discord choices 數量限制")
    
    print("\n現有 road_type 選項:")
    for i, choice in enumerate(road_type_choices, 1):
        print(f"{i:2d}. {choice}")
    
    print(f"\ncounty 選項數量: {len(county_choices)}")
    if len(county_choices) <= 25:
        print("✅ county 符合 Discord choices 數量限制")
    else:
        print("❌ county 超過 Discord choices 數量限制")
    
    print("\n現有 county 選項:")
    for i, choice in enumerate(county_choices, 1):
        print(f"{i:2d}. {choice}")

if __name__ == "__main__":
    print("=== Discord Choices 數量限制測試 ===")
    test_choices_limit()
    print("\n測試完成!")
