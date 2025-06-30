#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速診斷 Discord 圖片嵌入問題
專門檢查圖片 URL 處理和 embed 設定
"""

import asyncio
import sys

async def quick_image_embed_test():
    """快速測試圖片嵌入"""
    
    print("🔍 快速診斷 Discord 圖片嵌入問題")
    print("=" * 60)
    
    try:
        # 導入必要模組
        from cogs.reservoir_commands import WaterCameraView
        import discord
        
        # 模擬一些測試資料
        test_data = {
            'VideoSurveillanceStationName': '測試監控站',
            'VideoSurveillanceStationId': 'TEST001',
            'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '台北市',
            'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '信義區',
            'VideoSurveillanceStationAddress': '台北市信義區測試路1號',
            'ImageURL': 'https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg',
            'River': '淡水河'
        }
        
        # 測試不同的 URL 格式
        test_urls = [
            'https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg',
            '/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg',
            '//alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg',
            'https://fhy.wra.gov.tw/images/camera/test.jpg',
            '',
            None
        ]
        
        print("1️⃣ 測試 URL 處理...")
        view = WaterCameraView([test_data], 0, "測試")
        
        for i, url in enumerate(test_urls):
            test_data_copy = test_data.copy()
            test_data_copy['ImageURL'] = url
            
            print(f"\n測試 {i+1}: {url}")
            
            # 測試格式化
            info = view._format_water_image_info(test_data_copy)
            print(f"   格式化後: {info['image_url']}")
            
            # 測試 URL 處理
            if info['image_url']:
                processed = view._process_and_validate_image_url(info['image_url'])
                print(f"   處理後: {processed}")
                
                # 測試 Embed 創建
                embed = await view._create_water_camera_embed(test_data_copy)
                if embed.image and embed.image.url:
                    print(f"   ✅ Embed 圖片URL: {embed.image.url}")
                else:
                    print(f"   ❌ Embed 沒有圖片")
                    
                    # 詳細診斷
                    print(f"      info['image_url']: {info['image_url']}")
                    print(f"      processed != 'N/A': {processed != 'N/A'}")
                    print(f"      processed: {processed}")
            else:
                print(f"   ❌ 格式化後沒有 URL")
        
        print("\n2️⃣ 測試實際的 Discord Embed...")
        
        # 創建一個實際的 Discord Embed 進行測試
        embed = discord.Embed(
            title="測試圖片嵌入",
            description="測試 Discord 圖片嵌入功能",
            color=discord.Color.blue()
        )
        
        test_image_url = "https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10550011_20240904_0816.jpg"
        
        try:
            embed.set_image(url=test_image_url)
            print(f"✅ 成功設定圖片 URL: {test_image_url}")
            print(f"   Embed.image.url: {embed.image.url}")
        except Exception as e:
            print(f"❌ 設定圖片失敗: {e}")
        
        print("\n3️⃣ 測試 WaterCameraView 完整流程...")
        
        # 使用真實的測試資料
        real_test_data = {
            'VideoSurveillanceStationName': '淡水河淡水國中橋',
            'VideoSurveillanceStationId': '10450009',
            'CountiesAndCitiesWhereTheMonitoringPointsAreLocated': '新北市',
            'AdministrativeDistrictWhereTheMonitoringPointIsLocated': '淡水區',
            'VideoSurveillanceStationAddress': '新北市淡水區淡水國中橋',
            'ImageURL': 'https://alerts.ncdr.nat.gov.tw/HPWRI/2024/202409/20240904/10450009_20240904_0816.jpg',
            'River': '淡水河'
        }
        
        view = WaterCameraView([real_test_data], 0, "新北市")
        embed = await view._create_water_camera_embed(real_test_data)
        
        print(f"標題: {embed.title}")
        print(f"描述: {embed.description}")
        print(f"欄位數量: {len(embed.fields)}")
        
        if embed.image and embed.image.url:
            print(f"✅ 圖片 URL: {embed.image.url}")
        else:
            print("❌ 沒有圖片 URL")
            
            # 詳細診斷
            info = view._format_water_image_info(real_test_data)
            print(f"   原始 URL: {real_test_data['ImageURL']}")
            print(f"   格式化後: {info['image_url']}")
            
            processed = view._process_and_validate_image_url(info['image_url'])
            print(f"   處理後: {processed}")
            
            # 檢查條件
            print(f"   條件檢查:")
            print(f"     info['image_url']: {bool(info['image_url'])}")
            print(f"     info['image_url'] != 'N/A': {info['image_url'] != 'N/A'}")
            print(f"     processed: {processed}")
            print(f"     processed != 'N/A': {processed != 'N/A'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """主函數"""
    
    result = await quick_image_embed_test()
    
    print("\n" + "=" * 60)
    if result:
        print("✅ 診斷完成")
        print("\n💡 如果圖片仍然沒有在 Discord 中顯示，可能的原因:")
        print("1. 圖片 URL 需要認證或有存取限制")
        print("2. 圖片檔案過大或格式不支援")
        print("3. Discord 無法存取該 URL")
        print("4. 網路連線問題")
        print("5. 圖片 URL 已過期")
    else:
        print("❌ 診斷失敗")
    
    return result

if __name__ == "__main__":
    asyncio.run(main())
