#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, WebDriverException
import argparse

def setup_driver():
    """设置无头 Chrome 浏览器"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def ping_space(space_url, max_retries=2):
    """访问 Gradio Space 保持活跃"""
    driver = None
    
    for attempt in range(1, max_retries + 1):
        print(f"🔄 尝试 {attempt}/{max_retries}: {space_url}")
        
        try:
            driver = setup_driver()
            driver.get(space_url)
            
            # 等待页面加载
            time.sleep(5)
            
            # 检查是否加载成功
            if "ka1q-shang.hf.space" in driver.current_url:
                print("✅ Space 访问成功！")
                
                # 模拟用户交互（可选）
                try:
                    # 找到输入框并输入测试文本
                    input_box = driver.find_element(By.TAG_NAME, "input")
                    input_box.send_keys("test")
                    print("✅ 模拟用户输入成功")
                except:
                    print("⚠️  跳过用户交互")
                
                time.sleep(3)  # 额外等待
                return True
                
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
        finally:
            if driver:
                driver.quit()
        
        if attempt < max_retries:
            time.sleep(3)
    
    return False

def main():
    parser = argparse.ArgumentParser(description='Gradio Space 保活')
    parser.add_argument('url', nargs='?', default=os.environ.get('HF_SPACE_URL'), 
                       help='Space URL')
    
    args = parser.parse_args()
    
    if not args.url:
        args.url = "https://ka1q-shang.hf.space"
        print(f"使用默认 URL: {args.url}")
    
    print(f"🚀 Space 保活 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标: {args.url}")
    print("=" * 50)
    
    success = ping_space(args.url)
    
    if success:
        print("\n🎉 保活成功！你的 Space 保持活跃！✨")
        print(f"💡 下次自动运行: {datetime.now() + timedelta(hours=6)}")
        sys.exit(0)
    else:
        print("\n😱 保活失败！请手动检查 Space 状态")
        sys.exit(1)

if __name__ == "__main__":
    main()
