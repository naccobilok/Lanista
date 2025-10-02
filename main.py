import os
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ---------- KONFIGURATION ----------
LOGIN_URL = "https://beta.lanista.se/"
TARGET_URL = "https://beta.lanista.se/game/arena/teambattles/create"

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

WAIT = 15  # sekunder för element att laddas

# ---------- Funktion för ett försök ----------
def make_attempt(driver):
    try:
        driver.get(TARGET_URL)
        WebDriverWait(driver, WAIT).until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(2)

        # Dropdown 3 vs 3
        select_elem = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "team-battle-type")))
        select = Select(select_elem)
        select.select_by_value("3")
        print("Selected 3 vs 3 in dropdown")

        # Checkbox Slumpade lag
        checkbox = WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.ID, "randomTeams")))
        if not checkbox.is_selected():
            checkbox.click()
            print("Checked 'Slumpade lag'")
        else:
            print("'Slumpade lag' already checked")

        time.sleep(1)  # liten fördröjning

        # Klicka på Skapa lagspel
        create_button = WebDriverWait(driver, WAIT).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Skapa lagspel')]"))
        )
        create_button.click()
        print("SUCCESS: 'Skapa lagspel' clicked!")

    except Exception as e:
        print("ERROR:", type(e).__name__, e)
        try:
            driver.save_screenshot("error_screenshot.png")
            print("Saved screenshot to error_screenshot.png")
        except:
            pass


# ---------- Huvudprogram ----------
def main():
    if not EMAIL or not PASSWORD:
        print("ERROR: Missing EMAIL or PASSWORD environment variables!")
        return

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
        # ---------- Logga in ----------
        driver.get(LOGIN_URL)
        WebDriverWait(driver, WAIT).until(EC.presence_of_element_located((By.NAME, "email")))
        driver.find_element(By.NAME, "email").send_keys(EMAIL)
        driver.find_element(By.NAME, "password").send_keys(PASSWORD)
        driver.find_element(By.XPATH, "//button[contains(text(),'Logga in')]").click()
        WebDriverWait(driver, WAIT).until(lambda d: d.current_url != LOGIN_URL)
        print("Login successful")
        time.sleep(3)

        # ---------- Loop: gör försök var 10–12 minut ----------
        while True:
            print("Starting new attempt...")
            make_attempt(driver)
            sleep_time = random.randint(600, 720)  # 10–12 minuter
            print(f"Waiting {sleep_time//60} min {sleep_time%60} sec until next attempt...")
            time.sleep(sleep_time)

    finally:
        driver.quit()


if __name__ == "__main__":
    main()
