#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單測試API連接
"""

import asyncio
import aiohttp
import ssl

async def test_api():
    url = "https://cctv-maintain.thb.gov.tw/opendataCCTVs.xml"
    
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, ssl=ssl_context, timeout=10) as response:
                print(f"狀態碼: {response.status}")
                if response.status == 200:
                    content = await response.text()
                    print(f"內容長度: {len(content)}")
                    print(f"前500字符:")
                    print(content[:500])
                    return True
                else:
                    print("API 請求失敗")
                    return False
    except Exception as e:
        print(f"錯誤: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_api())
