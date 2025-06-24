import os
import time
import random
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def accept_all_cookies(driver):
    selectors = [
        'button#onetrust-accept-btn-handler',
        'button.cookie-accept',
        'button[aria-label="Accept All"]',
        'button[class*="accept"]',
        'button[class*="agree"]',
        'button[id*="accept"]',
        '//button[contains(text(), "Aceptar")]',
        '//button[contains(text(), "Accept")]'
    ]
    for sel in selectors:
        try:
            if sel.startswith('//'):
                btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.XPATH, sel)))
            else:
                btn = WebDriverWait(driver, 3).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, sel)))
            btn.click()
            time.sleep(0.5)
            break
        except Exception:
            continue

def get_video_duration(driver, timeout=10):
    """Return video duration in seconds using multiple strategies."""
    start = time.time()
    # strategy 1: HTML5 video element
    try:
        duration = driver.execute_script(
            "var v=document.querySelector('video');return v && v.duration? v.duration: 0;")
        if duration:
            return float(duration)
    except Exception:
        pass
    # strategy 2: ytInitialPlayerResponse
    while time.time() - start < timeout:
        try:
            duration = driver.execute_script(
                "return window.ytInitialPlayerResponse && window.ytInitialPlayerResponse.videoDetails ? parseFloat(window.ytInitialPlayerResponse.videoDetails.lengthSeconds) : 0;"
            )
            if duration:
                return float(duration)
        except Exception:
            pass
        time.sleep(0.5)
    # strategy 3: meta tags
    try:
        duration = driver.execute_script(
            "var m=document.querySelector('meta[itemprop=duration]');"
            "if(m && m.content){var r=m.content.match(/PT(\d+)M(\d+)S/);if(r){return parseInt(r[1])*60+parseInt(r[2]);}};"
            "m=document.querySelector('meta[property=\'og:video:duration\']');"
            "return m?parseFloat(m.content):0;")
        if duration:
            return float(duration)
    except Exception:
        pass
    # fallback
    return 60.0

def watch_video(url):
    driver = webdriver.Chrome()
    driver.get(url)
    accept_all_cookies(driver)
    duration = get_video_duration(driver)
    watch_time = min(duration, random.uniform(20, 60))
    screenshot_time = random.uniform(1, max(1, watch_time-1))
    os.makedirs('screenshots', exist_ok=True)
    start = time.time()
    taken = False
    while time.time() - start < watch_time:
        if not taken and time.time() - start >= screenshot_time:
            fname = datetime.now().strftime('screenshots/snap_%Y%m%d_%H%M%S.png')
            driver.save_screenshot(fname)
            print(f"Screenshot saved to {fname}")
            taken = True
        time.sleep(1)
    driver.quit()

if __name__ == '__main__':
    watch_video('https://www.youtube.com/watch?v=xqjbR1BhI8c')
