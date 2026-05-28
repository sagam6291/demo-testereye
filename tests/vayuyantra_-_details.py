import os
import time
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException


@pytest.fixture(scope="function")
def driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    drv = webdriver.Chrome(options=options)
    drv.implicitly_wait(0)
    yield drv
    drv.quit()


def _save_screenshot(drv, name):
    try:
        out_dir = os.path.join(os.getcwd(), "screenshots")
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, name)
        drv.save_screenshot(path)
        print(f"Saved screenshot: {path}")
    except WebDriverException as e:
        print(f"Failed to save screenshot: {e}")


def test_vayuyantra_contact_us_form_submission(driver):
    wait = WebDriverWait(driver, 20)
    try:
        # Step 1: Navigate to home
        driver.get("https://www.vayuyantra.com/home")
        wait.until(EC.title_contains("VayuYantra"))
        assert "vayuyantra.com" in driver.current_url.lower()

        # Step 2: Click ABOUT link
        about_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/about' and (normalize-space(.)='ABOUT' or contains(translate(., 'about', 'ABOUT'), 'ABOUT'))]")
        ))
        about_link.click()
        wait.until(EC.url_contains("/about"))
        assert "/about" in driver.current_url

        # Step 3: Click CONTACT US link
        contact_link = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/contact']")
        ))
        contact_link.click()
        wait.until(EC.url_contains("/contact"))
        assert "/contact" in driver.current_url

        # Wait for contact heading
        wait.until(EC.presence_of_element_located(
            (By.XPATH, "//*[contains(normalize-space(.), 'How can we help you today?')]")
        ))

        # Step 4: First Name
        first_name = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[placeholder='First Name *']")
        ))
        first_name.click()
        first_name.clear()
        first_name.send_keys("Agam")

        # Step 5: Last Name
        last_name = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[placeholder='Last Name']")
        ))
        last_name.click()
        last_name.clear()
        last_name.send_keys("Singh")

        # Step 6: Email
        email = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[placeholder='Email Address *']")
        ))
        email.click()
        email.clear()
        email.send_keys("agam.singh@intellicredence.com")

        # Step 7: Phone
        phone = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[placeholder='Phone Number']")
        ))
        phone.click()
        phone.clear()
        phone.send_keys("7409521159")

        # Step 8: Select inquiry category
        select_el = wait.until(EC.presence_of_element_located(
            (By.TAG_NAME, "select")
        ))
        Select(select_el).select_by_visible_text("Drone for Agriculture")

        # Step 9: Click Send Message (first attempt) - may surface message required
        send_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space(.)='Send Message']")
        ))
        send_btn.click()

        # Step 10: Fill message textarea
        message = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "textarea[placeholder='How can we assist you?']")
        ))
        message.click()
        message.clear()
        message.send_keys("ass")

        # Step 11: Click Send Message again
        send_btn2 = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space(.)='Send Message']")
        ))
        send_btn2.click()

        # Brief wait for any post-submit UI change
        time.sleep(2)

        # Assertions: still on /contact and page title intact
        assert "/contact" in driver.current_url, f"Unexpected URL: {driver.current_url}"
        assert "VayuYantra" in driver.title, f"Unexpected title: {driver.title}"

    except TimeoutException as e:
        _save_screenshot(driver, "vayuyantra_contact_timeout.png")
        pytest.fail(f"Timeout during contact form flow: {e}")
    except AssertionError:
        _save_screenshot(driver, "vayuyantra_contact_assertion.png")
        raise
    except Exception as e:
        _save_screenshot(driver, "vayuyantra_contact_error.png")
        pytest.fail(f"Unexpected error: {e}")
