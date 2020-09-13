from enum import Enum
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import os
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains 
from selenium.webdriver.common.keys import Keys
import selenium
import time
from webdriver_manager.chrome import ChromeDriverManager

FIREBASE_PROJECT_ID = "if-no-corona"
# GOOGLE_APPLICATION_CREDENTIALS = "if-no-corona-1851477ee5bc.json"

class DailyCheckResponse:
    SUBMITTED = 0
    ALREADY_SUBMITTED = 1
    FAILURE = 2
    UNKNOWN = 3

def fetch_only_element(driver, xpath_str):
    """ Helper function to fetch the only element expected from given xpath string """
    fetched_elements = driver.find_elements_by_xpath(xpath_str)
    assert len(fetched_elements) == 1
    return fetched_elements[0]

def traverse_login_pages(driver):
    """ Login with the user credentials saved on the environment variables """
    login_link = "https://dailycheck.cornell.edu/saml_login_user?redirect=%2Fdaily-checkin"
    driver.get(login_link)
    netid_textarea = fetch_only_element(driver, "//input[@name='netid']")
    netid_textarea.clear()
    cornell_email = os.environ.get('cornell_email', '')
    netid_textarea.send_keys(cornell_email)

    pwd_textarea = fetch_only_element(driver, "//input[@name='password']")
    pwd_textarea.clear()
    cornell_pwd = os.environ.get('cornell_pwd', '')
    pwd_textarea.send_keys(cornell_pwd)

    login_button = fetch_only_element(driver, "//input[@type='submit']")
    login_button.click()


def coronavirus_questions(driver):
    """ selects no for all default questions for Daily Check """
    button_ids = ["positivetest-no", "covidsymptoms-no", "contactdiagnosed-no", "contactsymptoms-no"]
    for button_id in button_ids:
        xpath_button = "//input[@id='%s' and @type='radio']" % button_id
        button = fetch_only_element(driver, xpath_button)
        button.click()

def is_you_may_proceed_prompt(driver):
    elements = driver.find_elements_by_xpath("//h2[contains(text(),'You May Proceed to Campus')]")
    return len(elements) > 0 

def expand_shadow_element(driver, element):
  shadow_root = driver.execute_script('return arguments[0].shadowRoot', element)
  return shadow_root

def daily_check_request():
    with webdriver.Chrome() as driver: 
        dailycheck_link = "https://dailycheck.cornell.edu/daily-checkin"
        driver.get(dailycheck_link)
        print(driver.title)

        assert "Daily Check" in driver.title
        login_prompt = "Choose Login"
        prompts = driver.find_elements_by_xpath("//*[contains(text(),'" + login_prompt + "')]")
        if (len(prompts) > 0):
            traverse_login_pages(driver)

        time.sleep(2)
        if(is_you_may_proceed_prompt(driver)):
            return DailyCheckResponse.ALREADY_SUBMITTED

        continue_button = fetch_only_element(driver, "//button[@id='continue']")
        continue_button.click()

        coronavirus_questions(driver)

        continue_button = fetch_only_element(driver, "//input[@type='submit' and @id='submit']")
        continue_button.click()

        submit_button = fetch_only_element(driver, "//input[@type='submit' and @id='submit']")
        submit_button.click()
        time.sleep(5)

        if(is_you_may_proceed_prompt(driver)):
            return DailyCheckResponse.SUBMITTED
        else:
            return DailyCheckResponse.UNKNOWN
    return DailyCheckResponse.FAILURE

def schedule_test_request():
    cornell_email = os.environ.get("cornell_email")
    cornell_netid = cornell_email[:cornell_email.find('@')]

    # Use the application default credentials
    cred = credentials.Certificate('if-no-corona-1851477ee5bc.json')
    firebase_admin.initialize_app(cred)
    
    db = firestore.client()
    user_ref = db.collection(u'users').document(cornell_netid)
    user_doc = user_ref.get()

    first_name = user_doc.get('firstName')
    last_name = user_doc.get('lastName')
    college = user_doc.get('college')
    date_of_birth = user_doc.get('dateOfBirth')
    print(str(date_of_birth))
    print(type(date_of_birth))

    addr_template = "https://register.cayugahealth.com/patient-registration/employee?employer=Cornell-Surveillance&hideInsurance=1&hideEmergencyContact=1&sourceSystemPatientId=%s&firstName=%s&lastName=%s"
    addr = addr_template % (cornell_netid, first_name, last_name)

    with webdriver.Chrome() as driver: 
        driver.get(addr)
        time.sleep(1)
        # next_form = fetch_only_element(driver, "//form")
        idk = driver.find_element_by_class_name('button-solid')
        # print(idk)
        shadow_section = expand_shadow_element(driver, idk)
        # print(shadow_section)
        next_button = shadow_section.find_element_by_class_name('button-native')
        # print(next_button)
        ActionChains(driver).move_to_element(next_button).click(next_button).perform()
        
        # next_button = fetch_only_element(driver, "//ion-button[@value='...']")

        # next_button.click()
        # prev_registered_button = fetch_only_element(driver, "//button[@value='']")
        # prev_registered_button.click()
        time.sleep(10)

    


if __name__ == '__main__':
    # print(daily_check_request())
    schedule_test_request()