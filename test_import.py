#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import traceback

try:
    import cogs.info_commands_fixed_v4_clean
    print("✅ 模塊導入成功!")
except Exception as e:
    print(f"❌ 導入失敗:")
    print(f"錯誤類型: {type(e).__name__}")
    print(f"錯誤訊息: {str(e)}")
    print("\n完整堆疊追蹤:")
    traceback.print_exc()
    sys.exit(1)
