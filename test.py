import random
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Chrome 옵션 설정
chrome_options = Options()
chrome_options.add_argument("--disable-gpu")

# ChromeDriver 실행 경로 설정
driver_service = Service('C:/Users/jjdlw/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=driver_service, options=chrome_options)

# 로그 설정
logging.basicConfig(filename='survey.log', level=logging.INFO)

# EmBRAIN 로그인 정보
site_url = 'https://panel.co.kr/user/main'
survey_url = 'https://panel.co.kr/user/survey/online/list'  # 설문조사 페이지 URL
username = 'jj1324'  # 여기에 EmBRAIN ID 입력
password = 'Jj691105!!'  # 여기에 EmBRAIN 비밀번호 입력

# EmBRAIN 사이트 로그인 함수
def login_to_embrain():
    print("Attempting to log into EmBRAIN...")
    driver.get(site_url)
    time.sleep(3)  # 페이지 로드 대기

    try:
        username_input = driver.find_element(By.ID, 'userId')
        password_input = driver.find_element(By.ID, 'userPw')

        # 로그인 정보 입력
        username_input.send_keys(username)
        password_input.send_keys(password)

        # 로그인 버튼 클릭 (클래스 이름으로 버튼 찾기)
        login_button = driver.find_element(By.CLASS_NAME, 'bt90x30')
        login_button.click()

        time.sleep(3)  # 로그인 후 페이지 로드 대기
        print("Logged into EmBRAIN successfully!")
    except Exception as e:
        logging.error(f"Error during login: {e}")
        print(f"Error during login: {e}")

# 설문조사 페이지로 이동 후 설문조사 항목을 탐색하고 클릭하는 함수
def navigate_to_survey():
    try:
        driver.get(survey_url)  # 로그인 후 설문조사 페이지로 이동
        print(f"Navigated to survey page: {survey_url}")
        time.sleep(5)  # 페이지 로드 대기
        
        # 설문조사 목록을 가져옴
        survey_list = driver.find_elements(By.CSS_SELECTOR, 'li[data-ng-repeat]')

        for index, survey in enumerate(survey_list):
            try:
                # a href가 빈 경우, 클릭 이벤트가 정의된 span 태그를 클릭
                span_to_click = survey.find_element(By.CSS_SELECTOR, 'span[data-ng-click="fnMoveDetailView(item)"]')
                span_to_click.click()
                print(f"Survey link {index + 1} clicked through span!")

                time.sleep(5)  # 설문조사 페이지 로드 대기

                # 새로 열린 창으로 포커스 이동
                switch_to_new_window()

                # 설문 참여하기 버튼을 클릭
                participate_link = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[contains(text(), "조사참여하기")]'))
                )
                link_url = participate_link.get_attribute('href')  # 조사참여하기 링크 URL 가져오기
                print(f"Participate link found: {link_url}")
                participate_link.click()
                print(f"Participate link clicked! URL: {link_url}")

                time.sleep(5)  # 설문조사 페이지 로드 대기

                # 새로 열린 창으로 포커스 이동
                switch_to_new_window()

                # ID가 'smtBtn'인 버튼을 클릭
                submit_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, "smtBtn"))
                )
                submit_button.click()
                print("Submit button clicked!")

                # 페이지 유지
                print(f"Survey participation page opened and retained for review.")
                break  # 첫 설문조사만 열고 나머지는 열지 않음
            except StaleElementReferenceException:
                print(f"StaleElementReferenceException: Retrying survey link {index + 1}")
                continue  # 요소가 사라지면 다시 시도
            except NoSuchElementException:
                print(f"NoSuchElementException: Element not found for survey {index + 1}")
                continue

        print("Survey opened successfully!")
    except Exception as e:
        logging.error(f"Error during survey navigation: {e}")
        print(f"Error during survey navigation: {e}")

# 새 창으로 포커스를 전환하는 함수
def switch_to_new_window():
    try:
        original_window = driver.current_window_handle
        all_windows = driver.window_handles

        for window in all_windows:
            if window != original_window:
                driver.switch_to.window(window)
                print("Switched to new window.")
                break
    except Exception as e:
        print(f"Error switching to new window: {e}")
        logging.error(f"Error switching to new window: {e}")

# EmBRAIN 설문조사 자동화 수행
try:
    login_to_embrain()
    navigate_to_survey()  # 설문조사 페이지로 이동하고 설문조사 항목 선택
    input("Press Enter to exit after reviewing the survey page...")  # 사용자 입력 대기
except Exception as e:
    logging.error(f"Error occurred: {e}")
    print(f"Error occurred: {e}")

# 종료 후 ChromeDriver 닫기
driver.quit()
