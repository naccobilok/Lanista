import os
import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------- KONFIGURATION via GitHub Secrets ----------
LOGIN_URL = "https://beta.lanista.se/"
TARGET_URL = "https://beta.lanista.se/game/arena/teambattles/create"

EMAIL = os.getenv("EMAIL")       # GitHub Secret
PASSWORD = os.getenv("PASSWORD") # GitHub Secret

WAIT = 15  # sekunder

def main():
    if not EMAIL or not PASSWORD:
        print("ERROR: Missing EMAIL or PASSWORD environment variables!")
        return

    # ---------- Random delay mellan 0–2 minuter ----------
    delay = random.randint(0, 120)
    print(f"Waiting {delay} seconds before running script...")
    time.sleep(delay)

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0 Safari/537.36"
    )

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 1) Logga in
        driver.get(LOGIN_URL)
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.NAME, "email")))

        driver.find_element(By.NAME, "email").clear()
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").clear()
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)

        driver.find_element(By.XPATH, "//button[contains(text(),'Logga in')]").click()

        # 2) Vänta tills inloggning är klar
        WebDriverWait(driver, WAIT).until(lambda d: d.current_url != LOGIN_URL)
        print("Login successful")
        time.sleep(3)

        # 3) Navigera till Teambattle-sidan
        driver.get(TARGET_URL)
        WebDriverWait(driver, WAIT).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(2)
        print("Navigated to Teambattle page")

        # 4) Läs och uppdatera Local Storage
        current_settings = driver.execute_script("""
        let settings = JSON.parse(localStorage.getItem('defaultTeambattleS')) || {};
        return settings;
        """)
        print("Current Local Storage:", json.dumps(current_settings, indent=2))

        driver.execute_script("""
        let settings = JSON.parse(localStorage.getItem('defaultTeambattleS')) || {};
        settings.avatarsPerTeam = 3;
        settings.randomTeams = true;
        localStorage.setItem('defaultTeambattleS', JSON.stringify(settings));
        """)

        updated_settings = driver.execute_script("""
        return JSON.parse(localStorage.getItem('defaultTeambattleS'));
        """)
        print("Updated Local Storage:", json.dumps(updated_settings, indent=2))

        # 5) Klicka på "Skapa lagspel"
        create_button = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Skapa lagspel')]"))
        )
        create_button.click()
        print("SUCCESS: 'Skapa lagspel' button clicked!")

    except Exception as e:
        print("ERROR:", type(e).__name__, e)
        try:
            driver.save_screenshot("error_screenshot.png")
            print("Saved screenshot to error_screenshot.png")
        except:
            pass
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
