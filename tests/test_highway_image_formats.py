#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試公路監視器圖片 URL 處理
"""

import asyncio
import aiohttp
import ssl

async def test_highway_image_urls():
    """測試不同的公路監視器圖片 URL 格式"""
    
    print("🖼️ 測試公路監視器圖片 URL")
    print("=" * 50)
    
    # 測試不同的 URL 格式
    base_url = "https://cctv-ss02.thb.gov.tw:443/T62-9K+020"
    test_formats = [
        base_url,
        base_url + "/snapshot",
        base_url + "/image",
        base_url + "/snap",
        base_url + ".jpg",
        base_url + "/latest.jpg",
        base_url + "/capture"
    ]
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for url_format in test_formats:
            print(f"\n🔗 測試: {url_format}")
            
            try:
                async with session.head(url_format, ssl=ssl_context, timeout=10) as response:
                    print(f"   狀態碼: {response.status}")
                    print(f"   Content-Type: {response.headers.get('Content-Type', 'N/A')}")
                    
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'image' in content_type.lower():
                            print(f"   ✅ 成功 - 圖片格式")
                        else:
                            print(f"   ⚠️ 成功但非圖片格式")
                    else:
                        print(f"   ❌ 失敗")
                        
            except Exception as e:
                print(f"   ❌ 錯誤: {str(e)[:50]}")
    
    print(f"\n" + "=" * 50)
    print("🔍 嘗試實際下載圖片")
    print("=" * 50)
    
    # 嘗試實際下載圖片來測試
    working_urls = []
    
    async with aiohttp.ClientSession(headers=headers) as session:
        for url_format in test_formats:
            try:
                async with session.get(url_format, ssl=ssl_context, timeout=10) as response:
                    if response.status == 200:
                        content_type = response.headers.get('Content-Type', '')
                        if 'image' in content_type.lower():
                            content = await response.read()
                            if len(content) > 1000:  # 至少有點內容
                                working_urls.append(url_format)
                                print(f"✅ {url_format} - 大小: {len(content)} bytes")
                            else:
                                print(f"⚠️ {url_format} - 內容太小: {len(content)} bytes")
                        else:
                            print(f"❌ {url_format} - 非圖片格式: {content_type}")
                    else:
                        print(f"❌ {url_format} - 狀態碼: {response.status}")
            except Exception as e:
                print(f"❌ {url_format} - 錯誤: {str(e)[:50]}")
    
    print(f"\n📊 結果總結:")
    print(f"   可用的 URL 格式: {len(working_urls)} 個")
    for url in working_urls:
        print(f"   ✅ {url}")
    
    return working_urls

def main():
    """主函數"""
    asyncio.run(test_highway_image_urls())

if __name__ == "__main__":
    main()
