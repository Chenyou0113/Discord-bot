#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
語言檢測和本地化工具模組
為機器人提供語言檢測和多語言回應功能
"""

import re
import logging
import langid
from typing import Dict, Any, Optional, List, Tuple

# 設定日誌
logger = logging.getLogger(__name__)

# 全局語言回應對照表
LANGUAGE_RESPONSES: Dict[str, Dict[str, str]] = {
    # 指令回應的多語言版本
    'ping': {
        'zh': 'Pong!\n延遲\n{}ms\n狀態\n 正常運行',
        'en': 'Pong!\nLatency\n{}ms\nStatus\n Running normally',
        'ja': 'Pong!\n遅延\n{}ms\n状態\n 正常に動作中',
        'ko': 'Pong!\n지연 시간\n{}ms\n상태\n 정상 작동 중',
        'fr': 'Pong!\nLatence\n{}ms\nStatut\n Fonctionnement normal',
        'de': 'Pong!\nLatenz\n{}ms\nStatus\n Läuft normal',
        'es': 'Pong!\nLatencia\n{}ms\nEstado\n Funcionando normalmente',
        'default': 'Pong!\n延遲\n{}ms\n狀態\n 正常運行'
    },
    'error': {
        'zh': '❌ 發生錯誤',
        'en': '❌ An error occurred',
        'ja': '❌ エラーが発生しました',
        'ko': '❌ 오류가 발생했습니다',
        'fr': '❌ Une erreur est survenue',
        'de': '❌ Ein Fehler ist aufgetreten',
        'es': '❌ Ha ocurrido un error',
        'default': '❌ 發生錯誤'
    },
    'welcome': {
        'zh': '你好！我會用中文回答你的問題。',
        'en': 'Hello! I will answer your question in English.',
        'ja': 'こんにちは！日本語で質問に答えます。',
        'ko': '안녕하세요! 한국어로 질문에 답변하겠습니다.',
        'fr': 'Bonjour! Je répondrai à votre question en français.',
        'de': 'Hallo! Ich werde Ihre Frage auf Deutsch beantworten.',
        'es': '¡Hola! Responderé a tu pregunta en español.',
        'default': '你好！我會嘗試用你的語言回答問題。'
    }
}

def detect_language(text: str) -> str:
    """檢測文本的語言
    
    Args:
        text: 要檢測的文本
        
    Returns:
        語言代碼 (如 'zh', 'en', 'ja', 等)
    """
    # 預處理文本以移除網址、表情符號等
    text = re.sub(r'http\S+', '', text)
    text = re.sub(r'[^\w\s]', '', text)
    
    if not text.strip():
        return 'default'
    
    # 使用 langid 檢測語言
    lang, _ = langid.classify(text)
    return lang

def get_response_in_language(message_content: str, response_key: str, *args) -> str:
    """根據消息內容提供適合的語言回應
    
    Args:
        message_content: 使用者的消息內容
        response_key: 回應類型鍵值 (如 'ping', 'error', 'welcome')
        *args: 格式化回應所需的參數
    
    Returns:
        適合語言的回應文字
    """
    # 檢測語言
    detected_lang = detect_language(message_content)
    
    # 獲取對應類型的回應集
    responses = LANGUAGE_RESPONSES.get(response_key, LANGUAGE_RESPONSES['welcome'])
    
    # 獲取對應語言的回應
    response = responses.get(detected_lang, responses['default'])
    
    # 如果有參數，套用到回應中
    if args:
        try:
            response = response.format(*args)
        except Exception as e:
            logger.error(f"格式化回應時發生錯誤: {e}")
    
    return response

# 擴充回應字典的函數
def add_language_responses(key: str, responses: Dict[str, str]) -> None:
    """新增或更新語言回應字典
    
    Args:
        key: 回應類型鍵值
        responses: 不同語言對應的回應
    """
    if key not in LANGUAGE_RESPONSES:
        LANGUAGE_RESPONSES[key] = {}
    
    LANGUAGE_RESPONSES[key].update(responses)
