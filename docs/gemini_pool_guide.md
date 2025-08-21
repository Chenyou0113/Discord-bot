# Gemini API 連接池實現與使用指南

本文檔提供關於 Discord 機器人中 Gemini API 連接池的詳細說明，包括設計理念、實現方式、使用方法和最佳實踐。

## 目錄

1. [設計理念](#設計理念)
2. [架構概述](#架構概述)
3. [關鍵功能](#關鍵功能)
4. [使用方法](#使用方法)
5. [API 金鑰輪換機制](#api-金鑰輪換機制)
6. [統計與監控](#統計與監控)
7. [常見問題](#常見問題)
8. [進階應用](#進階應用)

## 設計理念

Gemini API 連接池的設計目標是提高 AI 功能的可靠性、效能和資源利用率。主要解決的問題包括：

- **API 限額問題**：Google Gemini API 對每個 API 金鑰有請求限制
- **資源優化**：避免重複創建連接，減少資源浪費
- **負載均衡**：平均分配請求到多個 API 實例
- **錯誤處理**：自動重試和故障轉移
- **可擴展性**：支援多種 Gemini 模型和多個 API 金鑰

## 架構概述

連接池的核心是 `GeminiAPIPool` 類，它管理多個 Gemini API 實例。每個實例與特定的 API 金鑰關聯：

```
┌─────────────────────────┐
│    GeminiAPIPool        │
├─────────────────────────┤
│  ┌─────────────────┐    │
│  │ API 實例集合    │    │
│  │ ┌───────────┐   │    │
│  │ │ 實例 1    │───┼────┼──► API 金鑰 1
│  │ └───────────┘   │    │
│  │ ┌───────────┐   │    │
│  │ │ 實例 2    │───┼────┼──► API 金鑰 2
│  │ └───────────┘   │    │
│  │ ┌───────────┐   │    │
│  │ │ 實例 3    │───┼────┼──► API 金鑰 3
│  │ └───────────┘   │    │
│  │ ┌───────────┐   │    │
│  │ │ 實例 4    │───┼────┼──► API 金鑰 1
│  │ └───────────┘   │    │
│  │ ┌───────────┐   │    │
│  │ │ 實例 5    │───┼────┼──► API 金鑰 2
│  │ └───────────┘   │    │
│  └─────────────────┘    │
└─────────────────────────┘
```

## 關鍵功能

### 1. 連接池管理

- **初始化**：創建多個 API 實例並分配 API 金鑰
- **實例選擇**：基於負載和健康狀態選擇最佳實例
- **自動修復**：自動修復失敗或不健康的實例
- **異步支援**：所有操作都支援異步調用

### 2. 多 API 金鑰支援

- **金鑰輪換**：在多個 API 金鑰之間輪換使用
- **健康監測**：追蹤每個 API 金鑰的使用量和錯誤率
- **智能分配**：根據健康狀況選擇最佳的 API 金鑰
- **自動替換**：自動替換不健康的 API 金鑰

### 3. 錯誤處理

- **自動重試**：請求失敗時自動重試
- **指數退避**：重試間隔隨著重試次數增加而增加
- **錯誤統計**：記錄每個實例和 API 金鑰的錯誤
- **故障轉移**：當某個實例或金鑰出現問題時，轉移到其他可用的實例或金鑰

### 4. 統計與監控

- **使用統計**：記錄每個實例和金鑰的使用量
- **執行時間**：追蹤請求的執行時間
- **錯誤分析**：分析錯誤類型和頻率
- **健康指標**：提供連接池和 API 金鑰的健康指標

## 使用方法

### 基本使用

```python
from utils.gemini_pool import generate_content

# 生成文本內容
response, success = await generate_content(
    prompt="請介紹台灣的天氣特點",
    model_name="gemini-2.0-flash-exp",
    temperature=0.7
)

if success:
    print(response.text)
else:
    print("生成內容失敗")
```

### 創建聊天會話

```python
from utils.gemini_pool import create_chat

# 創建聊天會話
chat, instance_index = await create_chat(model_name="gemini-2.0-flash-exp")

if chat:
    # 發送消息
    response = await asyncio.get_event_loop().run_in_executor(
        None, lambda: chat.send_message("你好，請問明天台北天氣如何？")
    )
    print(response.text)
    
    # 延續對話
    follow_up = await asyncio.get_event_loop().run_in_executor(
        None, lambda: chat.send_message("我需要帶傘嗎？")
    )
    print(follow_up.text)
```

### 查看統計信息

```python
from utils.gemini_pool import get_pool_stats, get_api_key_stats

# 獲取連接池統計
pool_stats = get_pool_stats()
for model_name, stats in pool_stats.items():
    print(f"模型: {model_name}")
    print(f"  - 活躍連接: {stats['active_instances']}/{stats['pool_size']}")
    print(f"  - 總請求數: {stats['total_usage']}")

# 獲取 API 金鑰統計
key_stats = get_api_key_stats()
print(f"總請求數: {key_stats['total_requests']}")
print(f"失敗請求: {key_stats['failed_requests']}")
```

### 重置連接池

```python
from utils.gemini_pool import reset_api_pool, reset_api_stats

# 重置特定模型的連接池
reset_api_pool("gemini-2.0-flash-exp")

# 重置所有模型的連接池
reset_api_pool()

# 重置 API 統計數據
reset_api_stats()
```

## API 金鑰輪換機制

連接池實現了智能 API 金鑰輪換機制，主要包括以下方面：

### 1. 金鑰分配

初始化時，API 金鑰以循環方式分配給各個實例：

```python
# API 金鑰循環分配
api_keys_cycle = self.api_keys * (self.pool_size // len(self.api_keys) + 1)
for i in range(self.pool_size):
    api_key = api_keys_cycle[i % len(self.api_keys)]
    # 使用 api_key 創建實例...
```

### 2. 健康檢查

定期檢查 API 金鑰的健康狀況：

```python
def _check_and_rotate_api_keys(self):
    # 檢查輪換時間間隔 (至少間隔 5 分鐘)
    current_time = time.time()
    if current_time - self.api_stats["last_rotation"] < 300:
        return
        
    # 計算每個金鑰的健康狀況
    # 替換不健康的金鑰...
```

### 3. 智能選擇

為新請求選擇最健康的 API 金鑰：

```python
def _select_healthy_api_key(self):
    # 計算健康分數
    health_scores = {}
    for key in self.api_keys:
        usage = self.api_stats["key_usage"].get(key, 0) + 1
        errors = self.api_stats["key_errors"].get(key, 0)
        error_rate = errors / usage if usage > 0 else 0
        
        # 健康分數 = 使用量的倒數 * (1 - 錯誤率)
        health_scores[key] = (1 / usage) * (1 - error_rate)
    
    # 選擇分數最高的金鑰
    return max(health_scores.items(), key=lambda x: x[1])[0]
```

### 4. 動態輪換

當某個金鑰的錯誤率過高或使用量過大時，自動替換該金鑰：

```python
# 如果錯誤率 > 20% 或使用次數 > 總請求的 50%，標記為不健康
if error_rate > 0.2 or usage > self.api_stats["total_requests"] * 0.5:
    key_health[key] = False
else:
    key_health[key] = True
```

## 統計與監控

連接池提供了全面的統計和監控功能：

### 1. 連接池統計

```python
def get_model_stats(self):
    # 收集各個模型的統計信息
    stats = {}
    for model_name in self.models:
        # 計算活躍實例、錯誤實例等...
        stats[model_name] = {
            "pool_size": self.pool_size,
            "active_instances": active_instances,
            "error_instances": error_instances,
            "total_usage": total_usage,
            "usage_distribution": usage_distribution,
            "key_distribution": key_distribution
        }
    return stats
```

### 2. API 金鑰統計

```python
def get_api_key_stats(self):
    # 收集 API 金鑰的使用統計
    stats = {
        "total_keys": len(self.api_keys),
        "total_requests": self.api_stats["total_requests"],
        "failed_requests": self.api_stats["failed_requests"],
        # 其他統計數據...
        "key_usage": {
            f"Key #{i+1}": {
                "usage": usage,
                "errors": errors,
                "avg_time": avg_time,
                "error_rate": error_rate
            }
            for i, key in enumerate(self.api_keys)
        }
    }
    return stats
```

## 常見問題

### Q1: API 金鑰超出限額怎麼辦？
A1: 連接池會自動檢測限額問題，並切換到其他可用的 API 金鑰。如果所有金鑰都超出限額，將返回錯誤，應考慮增加 API 金鑰或減少請求頻率。

### Q2: 如何添加新的 API 金鑰？
A2: 在 `utils/gemini_pool.py` 中的 `API_KEYS` 列表中添加新的 API 金鑰，然後重啟機器人或執行 `/重置連接池` 指令。

### Q3: 如何診斷 API 問題？
A3: 使用 `/api密鑰統計` 指令查看詳細的 API 使用情況和錯誤率，識別有問題的金鑰，必要時可以使用 `/重置api統計` 重置統計數據。

### Q4: 連接池大小應該設置為多少？
A4: 連接池大小取決於預期的並發請求數量，通常設置為 5-10 之間。較大的池可以處理更多並發請求，但會消耗更多資源。

## 進階應用

### 1. 自定義處理流程

```python
from utils.gemini_pool import gemini_pool

# 直接訪問連接池實例
custom_response = await gemini_pool.generate_content(
    model_name="gemini-pro",
    prompt="自定義提示",
    temperature=0.9,
    max_retries=5
)
```

### 2. 整合 Discord 指令

```python
@bot.tree.command(name="ai藝術", description="生成藝術描述")
async def ai_art(interaction: discord.Interaction, 主題: str):
    await interaction.response.defer()
    
    prompt = f"請為以下藝術主題創作一段優美的描述：{主題}"
    response, success = await generate_content(prompt=prompt)
    
    if success:
        embed = discord.Embed(
            title=f"🎨 {主題}",
            description=response.text,
            color=discord.Color.purple()
        )
        await interaction.followup.send(embed=embed)
    else:
        await interaction.followup.send("❌ 生成藝術描述失敗")
```

### 3. 批量處理

```python
async def process_multiple_queries(queries):
    tasks = []
    for query in queries:
        task = asyncio.create_task(generate_content(
            prompt=query,
            model_name="gemini-2.0-flash-exp"
        ))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return results
```

---

通過本文檔和 `examples/gemini_pool_example.py` 範例，您應該能夠充分理解和利用 Gemini API 連接池的功能，提高機器人 AI 功能的可靠性和效能。如有更多問題，請參考代碼註釋或聯繫開發團隊。
