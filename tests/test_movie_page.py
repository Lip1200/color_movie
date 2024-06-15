import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from conftest import login

@pytest.mark.usefixtures("driver")
class TestMoviePage:

    @pytest.fixture(autouse=True)
    def setup_method(self, driver):
        login(driver)

    def test_load_movie_details(self, driver):
        driver.get("http://localhost:3000/movies/27205")

        movie_title = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/h1"))
        )
        assert movie_title.text == "Inception"

    def test_add_movie_to_list(self, driver):
        driver.get("http://localhost:3000/movies/27205")

        list_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select"))
        )
        list_dropdown.click()
        list_option = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "select option[value='36']"))
        )
        list_option.click()

        add_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div/div[2]/div/div/button[1]"))
        )
        add_button.click()

        WebDriverWait(driver, 10).until(EC.url_contains("/add-movie?id=27205&list_id=36"))
        assert driver.current_url == "http://localhost:3000/add-movie?id=27205&list_id=36"

    def test_suggest_similar_movies(self, driver):
        driver.get("http://localhost:3000/movies/27205")

        suggest_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button.bg-green-500"))
        )
        suggest_button.click()

        similar_movies = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.border.p-2.mt-2.rounded.shadow.bg-white.space-y-2 li"))
        )
        assert len(similar_movies) > 0

    def test_display_error_message(self, driver):
        driver.get("http://localhost:3000/movies/9999")

        error_message = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".text-red-500"))
        )
        assert "Failed to fetch movie details" in error_message.text
