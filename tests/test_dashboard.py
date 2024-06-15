import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from conftest import login


def test_dashboard_page(driver):
    login(driver)
    driver.get("http://localhost:3000/dashboard")

    # Vérifier que le texte "dashboard" apparaît dans un élément <h1>
    try:
        h1_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[1]/h1"))
        )
        assert h1_element.is_displayed()
        print("Le texte 'dashboard' apparaît dans un élément <h1>.")
    except Exception as e:
        print("Erreur lors de la vérification du texte 'dashboard' dans un élément <h1>:", e)
        raise

    # Vérifier le champ de recherche
    try:
        search_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[2]/input"))
        )
        assert search_field.is_displayed()
        print("Le champ de recherche est visible.")
    except Exception as e:
        print("Erreur lors de la vérification du champ de recherche:", e)
        raise

    search_field.send_keys("Inception")
    search_field.send_keys(Keys.RETURN)

    # Vérifier les résultats de recherche
    try:
        results = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "/html/body/div/div[2]/div[2]/ul/li"))
        )
        assert len(results) > 0
        print(f"{len(results)} résultats trouvés pour 'Inception'.")
    except Exception as e:
        print("Erreur lors de la vérification des résultats de recherche:", e)
        raise


def test_dashboard_logout(driver):
    login(driver)
    driver.get("http://localhost:3000/dashboard")

    # Vérifier le bouton de déconnexion
    try:
        logout_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div[1]/div/button[2]"))
        )
        assert logout_button.is_displayed()
        print("Le bouton de déconnexion est visible.")
    except Exception as e:
        print("Erreur lors de la vérification du bouton de déconnexion:", e)
        raise

    logout_button.click()

    # Vérifier la redirection vers la page de connexion
    try:
        WebDriverWait(driver, 10).until(EC.url_to_be("http://localhost:3000/login"))
        assert driver.current_url == "http://localhost:3000/login"
        print("Redirigé avec succès vers la page de connexion.")
    except Exception as e:
        print("Erreur lors de la redirection vers la page de connexion:", e)
        raise
