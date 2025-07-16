#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
檢查公路監視器國道資料問題
"""

import sys
import os
import asyncio

# 新增專案路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_highway_search():
    """測試公路監視器搜尋功能"""
    print("🔍 測試公路監視器搜尋功能")
    print("=" * 50)
    
    try:
        from cogs.reservoir_commands import ReservoirCommands
        
        # 建立測試實例
        reservoir_cog = ReservoirCommands(None)
        
        print("📡 正在獲取監視器資料...")
        cameras = await reservoir_cog._get_highway_cameras()
        
        if not cameras:
            print("❌ 無法獲取監視器資料")
            return False
        
        print(f"✅ 成功獲取 {len(cameras)} 個監視器")
        
        # 分析前50個監視器的資料格式
        print(f"\n📊 分析監視器資料格式:")
        
        road_names = set()
        surveillance_descriptions = []
        
        for i, camera in enumerate(cameras[:50]):
            road_name = camera.get('RoadName', '')
            surveillance_desc = camera.get('SurveillanceDescription', '')
            
            if road_name:
                road_names.add(road_name)
            
            if surveillance_desc:
                surveillance_descriptions.append(surveillance_desc)
            
            # 顯示前5個監視器的詳細資料
            if i < 5:
                print(f"\n   監視器 {i+1}:")
                print(f"      ID: {camera.get('CCTVID', '未知')}")
                print(f"      道路名稱: {road_name}")
                print(f"      監視描述: {surveillance_desc}")
                print(f"      道路分類: {camera.get('RoadClass', '未知')}")
                print(f"      道路ID: {camera.get('RoadID', '未知')}")
        
        print(f"\n🛣️ 道路名稱清單:")
        for road in sorted(road_names):
            print(f"   • {road}")
        
        # 測試國道相關關鍵字搜尋
        test_keywords = ['國道', '國1', '國3', '國5', 'freeway', 'highway', '高速', 'N1', 'N3']
        
        print(f"\n🔍 測試國道關鍵字搜尋:")
        
        for keyword in test_keywords:
            matches = []
            keyword_lower = keyword.lower()
            
            for camera in cameras:
                road_name = camera.get('RoadName', '').lower()
                surveillance_desc = camera.get('SurveillanceDescription', '').lower()
                cctv_id = camera.get('CCTVID', '').lower()
                
                if (keyword_lower in road_name or 
                    keyword_lower in surveillance_desc or 
                    keyword_lower in cctv_id):
                    matches.append(camera)
            
            print(f"   {keyword}: {len(matches)} 個匹配")
            
            # 顯示前3個匹配結果
            for i, match in enumerate(matches[:3]):
                print(f"      {i+1}. {match.get('RoadName', '未知')} - {match.get('SurveillanceDescription', '未知')}")
        
        # 特別檢查可能的國道格式
        print(f"\n🏛️ 特別檢查可能的國道格式:")
        
        possible_national_highways = []
        
        for camera in cameras:
            road_name = camera.get('RoadName', '')
            surveillance_desc = camera.get('SurveillanceDescription', '')
            road_class = camera.get('RoadClass', '')
            road_id = camera.get('RoadID', '')
            
            # 檢查各種可能的國道表示方式
            if (road_class == '1' or  # 道路分類可能是1代表國道
                '1' in road_id or '3' in road_id or '5' in road_id or  # RoadID包含國道號碼
                any(term in surveillance_desc for term in ['高速公路', '國道', 'Freeway', 'Highway'])):
                possible_national_highways.append(camera)
        
        print(f"   找到 {len(possible_national_highways)} 個可能的國道監視器")
        
        # 顯示前10個可能的國道監視器
        for i, camera in enumerate(possible_national_highways[:10]):
            print(f"   {i+1}. 道路: {camera.get('RoadName', '未知')}")
            print(f"      描述: {camera.get('SurveillanceDescription', '未知')}")
            print(f"      分類: {camera.get('RoadClass', '未知')}")
            print(f"      ID: {camera.get('RoadID', '未知')}")
            print(f"      CCTVID: {camera.get('CCTVID', '未知')}")
            print("      " + "-" * 30)
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函數"""
    asyncio.run(test_highway_search())

if __name__ == "__main__":
    main()
