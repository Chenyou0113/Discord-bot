import sys
import traceback

try:
    from cogs.info_commands_fixed_v4_clean import MetroNewsPaginationView
    print("✅ 成功導入 MetroNewsPaginationView")
except Exception as e:
    print(f"❌ 導入失敗: {type(e).__name__}: {e}")
    traceback.print_exc()
