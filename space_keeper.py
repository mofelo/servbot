#!/usr/bin/env python3
import os
import sys
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # GitHub Actions 环境配置
    if 'GITHUB_ACTIONS' in os.environ:
        chrome_options.binary_location = "/usr/bin/google-chrome"
    
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def ping_space_with_selenium(space_url, max_retries=3, wait_time=10):
    """使用 Selenium 访问 Gradio Space"""
    driver = None
    
    for attempt in range(1, max_retries + 1):
        print(f"🔄 尝试 {attempt}/{max_retries}")
        
        try:
            print(f"🌐 正在访问: {space_url}")
            driver = setup_driver()
            
            # 访问 Space
            driver.get(space_url)
            print(f"⏱️  等待页面加载...")
            
            # 等待页面加载完成（最多30秒）
            wait = WebDriverWait(driver, 30)
            
            # 等待 Gradio 相关元素出现或页面完全加载
            try:
                # 尝试找到 Gradio 界面元素
                wait.until(
                    lambda d: (
                        "gradio" in d.page_source.lower() or 
                        "hf.space" in d.page_source.lower() or
                        d.execute_script("return document.readyState") == "complete"
                    )
                )
                print("✅ 页面加载成功！")
                
                # 额外等待让 Gradio 完全初始化
                time.sleep(wait_time)
                
                # 检查是否成功加载
                page_source = driver.page_source
                if any(keyword in page_source.lower() for keyword in ["gradio", "hf.space", "your app"]):
                    print("🎉 Gradio Space 保持活跃！")
                    return True
                else:
                    print("⚠️  页面加载但未找到 Gradio 内容")
                    return True  # 还是算成功
                    
            except TimeoutException:
                print("⏰ 页面加载超时，但可能仍在初始化...")
                # 检查是否至少到达了页面
                if driver.current_url.startswith(space_url.split('/')[0:3]):
                    print("✅ 至少到达了 Space 页面")
                    return True
                else:
                    print("❌ 未到达目标页面")
                    
        except WebDriverException as e:
            print(f"💥 WebDriver 错误: {str(e)}")
        except Exception as e:
            print(f"❌ 意外错误: {str(e)}")
        
        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass
        
        if attempt < max_retries:
            print(f"⏳ 等待 {5 * attempt} 秒后重试...")
            time.sleep(5 * attempt)
    
    return False

def main():
    parser = argparse.ArgumentParser(description='自动保活 Gradio Space')
    parser.add_argument('url', nargs='?', default=os.environ.get('HF_SPACE_URL'), 
                       help='Gradio Space URL')
    parser.add_argument('--wait', type=int, default=10, 
                       help='页面加载后等待时间(秒)')
    
    args = parser.parse_args()
    
    if not args.url:
        parser.error("需要提供 Space URL。设置 HF_SPACE_URL 环境变量或作为参数传入。")
    
    print(f"🚀 Gradio Space 保活器 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 目标: {args.url}")
    print("=" * 60)
    
    success = ping_space_with_selenium(args.url, wait_time=args.wait)
    
    if success:
        print("\n🎉 成功！你的 Gradio Space 保持活跃！✨")
        print("💡 建议：每2-4小时运行一次")
        sys.exit(0)
    else:
        print("\n😱 失败！Space 可能仍在休眠！💤")
        print("🔧 检查日志并尝试调整等待时间")
        sys.exit(1)

if __name__ == "__main__":
    main()
