import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

@pytest.fixture(scope="module")
def driver():
    # Vérifiez les permissions et la configuration
    try:
        driver = webdriver.Safari()
        driver.implicitly_wait(10)
        yield driver
    except Exception as e:
        print(f"Erreur lors de la création de la session WebDriver pour Safari : {e}")
    finally:
        if 'driver' in locals():
            driver.quit()

def login(driver):
    driver.get("http://localhost:3000/login")

    while True:
        try:
            email_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "email")))
            password_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "password")))
            login_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".btn-primary")))

            email_field.send_keys("testuser@example.com")
            password_field.send_keys("password123")
            login_button.click()

            WebDriverWait(driver, 10).until(EC.url_contains("/user"))
            break
        except (StaleElementReferenceException, TimeoutException):
            driver.refresh()
