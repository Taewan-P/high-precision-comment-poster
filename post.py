from bs4 import BeautifulSoup
import ntplib
import os
import platform
import pyperclip
import sys
import time
import urllib
import requests


from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


# Copy and Paste function
def copy_input(driver: webdriver.Chrome, xpath: str, input: str) -> None:
    os_base = platform.system()
    pyperclip.copy(input)
    driver.find_element(By.XPATH, xpath).click()
    
    # Paste Clipboard
    if os_base == 'Darwin':
        ActionChains(driver).key_down(Keys.COMMAND).send_keys('v').key_up(Keys.COMMAND).perform()
    else:
        ActionChains(driver).key_down(Keys.CONTROL).send_keys('v').key_up(Keys.CONTROL).perform()
    time.sleep(1)


# Get the current time from the NTP server
def get_time(server_address='time.google.com'):
    c = ntplib.NTPClient()
    response = c.request(server_address, version=3)
    return datetime.fromtimestamp(response.tx_time)


# Update the system time to the NTP server time
def update_time(loc='time.google.com'):
    os_name = sys.platform
    try:
        # If OS is Windows
        if os_name == 'win32':
            import win32api

            # Get the current time from the NTP server
            current_time = get_time(loc)

            # Update the system time
            print('Updating system time to: ' + str(current_time))
            time_string = current_time.strftime('%Y-%m-%d %H:%M:%S')

            win32api.SetSystemTime(current_time.year, current_time.month, 0, current_time.day, current_time.hour, current_time.minute, current_time.second, 0)

        # If OS is MacOS
        elif os_name == 'darwin':
            os.system(f'sudo sntp -sS {loc}')

        # If OS is Linux
        elif os_name == 'linux' or os_name == 'linux2':
            os.system(f'sudo sntp -sS {loc}')
        
        else:
            print('OS not supported')
            sys.exit(1)

    except Exception as e:
        print('Error updating system time: ' + str(e))
        sys.exit(1)
    else:
        print('System time updated successfully')


# Get GRP ID from the cafe link (Daum Cafe Only)
def get_grp_id(cafe_link: str) -> str:
    session = requests.Session()
    res = session.get(cafe_link)

    bs = BeautifulSoup(res.text, 'html.parser')
    query = bs.find("meta", property="og:url")['content'].split('/')[-1]
    result = query.split('=')[-1]

    return result


# Get fld ID <- from the user


# Webdriver Functions
def open_browser() -> webdriver.Chrome:
    service = ChromeService(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(service=service)


def quit_browser(d: webdriver.Chrome) -> bool:
    try:
        d.quit()
    except Exception:
        return False
    else:
        return True


def goto_url(d: webdriver.Chrome, url: str) -> bool:
    try:
        d.get(url)
    except Exception:
        print('Goto URL has failed')
        return False
    else:
        return True


# Login to the cafe with Kakao ID
def login(d: webdriver.Chrome, cafe_link: str, id: str, pw: str) -> bool:
    print("- Login Sequence -")
    url_encoded = urllib.parse.quote(cafe_link)
    url = f"https://accounts.kakao.com/login?continue=https%3A%2F%2Flogins.daum.net%2Faccounts%2Fksso.do%3Frescue%3Dtrue%26url%3D{url_encoded}"
    goto_url(d, url)
    
    copy_input(d, '//*[@id="loginEmailField"]/div', id)
    copy_input(d, '//*[@id="login-form"]/fieldset/div[3]', pw)

    ActionChains(d).key_down(Keys.ENTER).key_up(Keys.ENTER).perform()
    
    # Check if URL has changed
    i = 0
    try:
        while True:
            sys.stdout.write(f"Waiting for login progress to be finished{'.' * (i % 3 + 1)} \r")
            if d.current_url == cafe_link:
                sys.stdout.flush()
                sys.stdout.write("Waiting for login progress to be finished... Done.\n")
                return True

            if i > 300:
                sys.stdout.flush()
                sys.stdout.write("Waiting for login progress to be finished... Failed.\n")
                return False
            time.sleep(1)
            sys.stdout.flush()
            sys.stdout.write("                                                              \r")
            sys.stdout.flush()
            i += 1
    except Exception as e:
        print(e)
        return False
    

def generate_comment(name: str, birthday: str, phone_number: str) -> str:
    return f"[ {name} / {birthday} / {phone_number} ]"

if __name__ == '__main__':
    update_time()