#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自動重啟機器人腳本
監控機器人狀態，自動重啟
"""

import subprocess
import time
import os
import sys
import signal
import logging
from datetime import datetime

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('restart_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BotRestarter:
    def __init__(self):
        self.bot_process = None
        self.restart_flag_path = 'restart_flag.txt'
        self.bot_script = 'bot.py'
        self.running = True
        
    def start_bot(self):
        """啟動機器人"""
        try:
            logger.info("正在啟動機器人...")
            self.bot_process = subprocess.Popen(
                [sys.executable, self.bot_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            logger.info(f"機器人已啟動，PID: {self.bot_process.pid}")
            return True
        except Exception as e:
            logger.error(f"啟動機器人失敗: {e}")
            return False
    
    def stop_bot(self):
        """停止機器人"""
        if self.bot_process and self.bot_process.poll() is None:
            try:
                logger.info("正在停止機器人...")
                self.bot_process.terminate()
                
                # 等待進程終止
                try:
                    self.bot_process.wait(timeout=10)
                    logger.info("機器人已正常停止")
                except subprocess.TimeoutExpired:
                    logger.warning("機器人未在規定時間內停止，強制結束")
                    self.bot_process.kill()
                    self.bot_process.wait()
                    
            except Exception as e:
                logger.error(f"停止機器人失敗: {e}")
    
    def check_restart_flag(self):
        """檢查重啟標記"""
        if os.path.exists(self.restart_flag_path):
            try:
                with open(self.restart_flag_path, 'r', encoding='utf-8') as f:
                    flag_content = f.read().strip()
                
                os.remove(self.restart_flag_path)
                logger.info(f"發現重啟標記: {flag_content}")
                return True
            except Exception as e:
                logger.error(f"處理重啟標記失敗: {e}")
        return False
    
    def check_bot_status(self):
        """檢查機器人狀態"""
        if self.bot_process is None:
            return False
        
        return_code = self.bot_process.poll()
        if return_code is not None:
            logger.warning(f"機器人進程已結束，返回碼: {return_code}")
            return False
        
        return True
    
    def restart_bot(self):
        """重啟機器人"""
        logger.info("開始重啟機器人...")
        self.stop_bot()
        time.sleep(2)  # 等待完全停止
        
        if self.start_bot():
            logger.info("機器人重啟成功")
            return True
        else:
            logger.error("機器人重啟失敗")
            return False
    
    def handle_signal(self, signum, frame):
        """處理信號"""
        logger.info(f"收到信號 {signum}，正在關閉...")
        self.running = False
        self.stop_bot()
        sys.exit(0)
    
    def run(self):
        """主循環"""
        # 設定信號處理
        if os.name != 'nt':  # Unix/Linux
            signal.signal(signal.SIGINT, self.handle_signal)
            signal.signal(signal.SIGTERM, self.handle_signal)
        
        logger.info("自動重啟監控器已啟動")
        
        # 初始啟動機器人
        if not self.start_bot():
            logger.error("無法啟動機器人，退出監控")
            return
        
        check_interval = 5  # 檢查間隔（秒）
        last_check = time.time()
        
        try:
            while self.running:
                time.sleep(1)
                current_time = time.time()
                
                # 每隔一定時間檢查一次
                if current_time - last_check >= check_interval:
                    last_check = current_time
                    
                    # 檢查重啟標記
                    if self.check_restart_flag():
                        logger.info("收到重啟請求，正在重啟機器人...")
                        if not self.restart_bot():
                            logger.error("重啟失敗，嘗試重新啟動...")
                            time.sleep(5)
                            if not self.start_bot():
                                logger.error("重新啟動失敗，監控器將退出")
                                break
                        continue
                    
                    # 檢查機器人狀態
                    if not self.check_bot_status():
                        logger.warning("機器人進程異常，嘗試重啟...")
                        if not self.restart_bot():
                            logger.error("自動重啟失敗，等待手動處理...")
                            time.sleep(30)  # 等待更長時間再嘗試
                            if not self.start_bot():
                                logger.error("無法重新啟動機器人，監控器將退出")
                                break
                
        except KeyboardInterrupt:
            logger.info("收到中斷信號，正在關閉...")
        except Exception as e:
            logger.error(f"監控器發生未預期的錯誤: {e}")
        finally:
            self.stop_bot()
            logger.info("自動重啟監控器已關閉")

def main():
    """主函數"""
    print("=" * 60)
    print("Discord Bot 自動重啟監控器")
    print("=" * 60)
    print("功能:")
    print("• 自動啟動機器人")
    print("• 監控機器人狀態")
    print("• 檢測重啟請求")
    print("• 自動重啟機器人")
    print("• 異常恢復")
    print("-" * 60)
    print("使用方法:")
    print("• 在 Discord 中使用 /restart 指令")
    print("• 機器人將自動重新啟動")
    print("• 按 Ctrl+C 停止監控器")
    print("=" * 60)
    
    # 檢查機器人腳本是否存在
    if not os.path.exists('bot.py'):
        print("❌ 找不到 bot.py 文件，請確保在正確的目錄中運行此腳本")
        sys.exit(1)
    
    # 啟動監控器
    restarter = BotRestarter()
    restarter.run()

if __name__ == "__main__":
    main()
