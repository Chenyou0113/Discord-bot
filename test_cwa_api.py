#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
中央氣象署 API 測試工具
用於診斷和解決 API 異常資料結構問題
"""

import aiohttp
import asyncio
import json
import ssl
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CWA_API_Tester:
    def __init__(self):
        self.api_key = "CWA-675CED45-09DF-4249-9599-B9B5A5AB761A"  # 目前使用的 API 金鑰
        self.session = None
        
    async def init_session(self):
        """初始化 HTTP 工作階段"""
        try:
            # 設定 SSL 上下文
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            connector = aiohttp.TCPConnector(ssl=ssl_context, limit=10)
            
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30, connect=10, sock_read=20),
                connector=connector,
                trust_env=True
            )
            logger.info("✅ HTTP 工作階段初始化成功")
            
        except Exception as e:
            logger.error(f"❌ 初始化 HTTP 工作階段失敗: {e}")
            raise

    async def test_api_endpoint(self, url, params, endpoint_name):
        """測試特定的 API 端點"""
        logger.info(f"\n🔍 測試 {endpoint_name}")
        logger.info(f"📡 URL: {url}")
        logger.info(f"📝 參數: {params}")
        
        try:
            # 構建完整 URL
            param_string = "&".join([f"{k}={v}" for k, v in params.items()])
            full_url = f"{url}?{param_string}"
            
            logger.info(f"🌐 完整請求 URL: {full_url}")
            
            # 發送請求
            async with self.session.get(full_url) as response:
                logger.info(f"📊 HTTP 狀態碼: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    
                    # 分析回應結構
                    logger.info("📋 API 回應分析:")
                    logger.info(f"  ✅ 成功獲取資料")
                    logger.info(f"  📦 根層級鍵: {list(data.keys())}")
                    
                    if 'success' in data:
                        logger.info(f"  🎯 success: {data['success']}")
                    
                    if 'result' in data:
                        result = data['result']
                        logger.info(f"  📂 result 類型: {type(result)}")
                        
                        if isinstance(result, dict):
                            logger.info(f"  🔑 result 鍵: {list(result.keys())}")
                            
                            # 檢查是否只有 resource_id 和 fields
                            if set(result.keys()) == {'resource_id', 'fields'}:
                                logger.warning("  ⚠️ 發現異常資料結構！只有 resource_id 和 fields")
                                logger.warning("  📌 這正是造成警告的原因")
                                
                                if 'resource_id' in result:
                                    logger.info(f"    🆔 resource_id: {result['resource_id']}")
                                
                                if 'fields' in result:
                                    fields = result['fields']
                                    logger.info(f"    📋 fields 數量: {len(fields) if isinstance(fields, list) else 'N/A'}")
                                    if isinstance(fields, list) and len(fields) > 0:
                                        logger.info(f"    📝 第一個欄位: {fields[0]}")
                                
                                # 檢查可能的錯誤原因
                                logger.info("\n🔍 可能的錯誤原因:")
                                logger.info("  1. API 金鑰已過期或無效")
                                logger.info("  2. API 金鑰沒有存取此資源的權限")
                                logger.info("  3. API 端點參數錯誤")
                                logger.info("  4. API 服務暫時不可用")
                                
                            elif 'records' in result:
                                records = result['records']
                                logger.info(f"  📊 records 類型: {type(records)}")
                                
                                if isinstance(records, dict):
                                    logger.info(f"  🗂️ records 鍵: {list(records.keys())}")
                                    
                                    if 'Earthquake' in records:
                                        earthquakes = records['Earthquake']
                                        logger.info(f"  🌍 地震資料數量: {len(earthquakes) if isinstance(earthquakes, list) else 'N/A'}")
                                        
                                        if isinstance(earthquakes, list) and len(earthquakes) > 0:
                                            eq = earthquakes[0]
                                            logger.info(f"  📍 第一筆地震資料鍵: {list(eq.keys()) if isinstance(eq, dict) else 'N/A'}")
                                            
                                            if isinstance(eq, dict) and 'EarthquakeInfo' in eq:
                                                eq_info = eq['EarthquakeInfo']
                                                if isinstance(eq_info, dict) and 'OriginTime' in eq_info:
                                                    logger.info(f"  ⏰ 地震時間: {eq_info['OriginTime']}")
                                                if isinstance(eq_info, dict) and 'EarthquakeMagnitude' in eq_info:
                                                    magnitude = eq_info['EarthquakeMagnitude']
                                                    if isinstance(magnitude, dict) and 'MagnitudeValue' in magnitude:
                                                        logger.info(f"  📊 地震規模: {magnitude['MagnitudeValue']}")
                                        else:
                                            logger.warning("  ⚠️ 地震資料為空或格式錯誤")
                                    else:
                                        logger.warning("  ⚠️ records 中沒有 Earthquake 資料")
                                else:
                                    logger.warning(f"  ⚠️ records 不是字典類型: {type(records)}")
                            else:
                                logger.warning("  ⚠️ result 中沒有 records 欄位")
                    else:
                        logger.warning("  ⚠️ 回應中沒有 result 欄位")
                    
                    # 儲存回應以供調試
                    filename = f"api_response_{endpoint_name.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(filename, 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=2)
                    logger.info(f"  💾 回應已儲存至: {filename}")
                    
                    return True, data
                    
                elif response.status == 401:
                    logger.error("  ❌ 認證失敗 (401) - API 金鑰可能無效")
                    return False, "認證失敗"
                
                elif response.status == 403:
                    logger.error("  ❌ 權限拒絕 (403) - API 金鑰可能沒有存取權限")
                    return False, "權限拒絕"
                
                elif response.status == 429:
                    logger.error("  ❌ 請求過於頻繁 (429) - 已達到速率限制")
                    return False, "速率限制"
                
                else:
                    logger.error(f"  ❌ HTTP 錯誤: {response.status}")
                    response_text = await response.text()
                    logger.error(f"  📄 回應內容: {response_text[:500]}...")
                    return False, f"HTTP {response.status}"
                    
        except asyncio.TimeoutError:
            logger.error(f"  ❌ 請求超時")
            return False, "超時"
            
        except Exception as e:
            logger.error(f"  ❌ 請求失敗: {e}")
            return False, str(e)

    async def test_all_endpoints(self):
        """測試所有地震相關的 API 端點"""
        endpoints = [
            {
                "name": "一般地震 API",
                "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001",
                "params": {
                    'Authorization': self.api_key,
                    'limit': 1,
                    'format': 'JSON'
                }
            },
            {
                "name": "小區域地震 API", 
                "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0016-001",
                "params": {
                    'Authorization': self.api_key,
                    'limit': 1,
                    'format': 'JSON'
                }
            },
            {
                "name": "不含認證的一般地震 API",
                "url": "https://opendata.cwa.gov.tw/api/v1/rest/datastore/E-A0015-001",
                "params": {
                    'limit': 1,
                    'format': 'JSON'
                }
            }
        ]
        
        results = []
        
        for endpoint in endpoints:
            success, data = await self.test_api_endpoint(
                endpoint["url"], 
                endpoint["params"], 
                endpoint["name"]
            )
            results.append((endpoint["name"], success, data))
            
            # 在測試之間稍作停頓
            await asyncio.sleep(2)
        
        return results

    async def diagnose_api_issue(self):
        """診斷 API 問題"""
        logger.info("🔬 開始 CWA API 診斷")
        logger.info("=" * 60)
        
        # 測試所有端點
        results = await self.test_all_endpoints()
        
        # 分析結果
        logger.info("\n📊 診斷結果摘要:")
        logger.info("=" * 40)
        
        success_count = 0
        auth_errors = 0
        abnormal_structure = 0
        
        for name, success, data in results:
            if success:
                success_count += 1
                # 檢查是否有異常資料結構
                if isinstance(data, dict) and 'result' in data:
                    result = data['result']
                    if isinstance(result, dict) and set(result.keys()) == {'resource_id', 'fields'}:
                        abnormal_structure += 1
                        logger.warning(f"  ⚠️ {name}: 異常資料結構")
                    else:
                        logger.info(f"  ✅ {name}: 正常")
            else:
                if "認證失敗" in str(data) or "權限拒絕" in str(data):
                    auth_errors += 1
                logger.error(f"  ❌ {name}: {data}")
        
        logger.info(f"\n📈 統計:")
        logger.info(f"  總測試數: {len(results)}")
        logger.info(f"  成功數: {success_count}")
        logger.info(f"  認證錯誤: {auth_errors}")
        logger.info(f"  異常資料結構: {abnormal_structure}")
        
        # 提供建議
        logger.info(f"\n💡 建議:")
        if auth_errors > 0:
            logger.info("  🔐 API 金鑰問題:")
            logger.info("    - 檢查 API 金鑰是否仍然有效")
            logger.info("    - 確認 API 金鑰有存取地震資料的權限")
            logger.info("    - 考慮申請新的 API 金鑰")
            
        if abnormal_structure > 0:
            logger.info("  📊 資料結構問題:")
            logger.info("    - API 回傳了欄位定義而非實際資料")
            logger.info("    - 這通常表示認證問題或權限不足")
            logger.info("    - 建議使用備用資料或不需認證的 API")
            
        if success_count == 0:
            logger.info("  🚨 所有 API 測試都失敗了:")
            logger.info("    - 檢查網路連接")
            logger.info("    - 確認 API 端點是否正確")
            logger.info("    - 檢查是否有防火牆阻擋")

    async def close(self):
        """關閉 HTTP 工作階段"""
        if self.session:
            await self.session.close()
            logger.info("✅ HTTP 工作階段已關閉")

async def main():
    """主函數"""
    tester = CWA_API_Tester()
    
    try:
        await tester.init_session()
        await tester.diagnose_api_issue()
        
    except Exception as e:
        logger.error(f"❌ 診斷過程中發生錯誤: {e}")
        
    finally:
        await tester.close()

if __name__ == "__main__":
    print("🧪 中央氣象署 API 診斷工具")
    print("這個工具將幫助診斷 API 異常資料結構的問題")
    print()
    
    asyncio.run(main())
