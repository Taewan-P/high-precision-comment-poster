from bs4 import BeautifulSoup
import json
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


# Get memo page token
def get_memo_token(d: webdriver.Chrome) -> str:
    # This function must be executed in memo input page. Otherwise it will not work!
    d.switch_to.frame('down')
    html = d.page_source
    bs = BeautifulSoup(html, 'html.parser')
    scripts = bs.find_all('script')
    for script in scripts:
        if 'token' in script.text:
            token = script.text.split('token: ')[1].split(',')[0].replace("'", '')
            return token
    return ''


# Webdriver Functions
def open_browser() -> webdriver.Chrome:
    options = webdriver.ChromeOptions()
    options.add_argument('User-Agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/104.0.5112.81 Safari/537.36')
    options.add_experimental_option("detach", True)
    options.add_argument('--lang=ko_KR')
    service = ChromeService(executable_path=ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


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
    

def generate_comment(name: str, birthday: str, phone_number: str, debug=True) -> str:
    if debug is True:
        return "오늘도 화이팅!!"

    return f"[ {name} / {birthday} / {phone_number} ]"


def write_comment(d: webdriver.Chrome, cafe_id: str, board_id: str, token: str, comment: str, sec=True) -> bool:
    d.switch_to.default_content()
    memo_link = f"https://cafe.daum.net/_c21_/memo_action?act=write&grpid={cafe_id}&fldid={board_id}"

    cookies = {}
    for cookie in d.get_cookies():
        name = cookie.get('name', '')
        value = cookie.get('value', None)

        if name != "" and value is not None:
            cookies[name] = value

    headers = {
        'referer': memo_link,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                        'Chrome/104.0.5112.81 Safari/537.36 ',
        'sec-ch-ua-platform': 'Windows',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'iframe',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'origin': 'https://cafe.daum.net',
        'dnt': '1',
        'content-type': 'application/x-www-form-urlencoded',
        'accept-language': 'ko,en-US;q=0.9,en;q=0.8',
        'accept-enconding': 'gzip, deflate, br',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
    }

    form_data = {
        'token': token,
        'content': comment,
        'imageurl': None,
        'imagesize': None,
        'imagename': None,
        'hideyn': 'Y' if sec else 'N',
        'noticeyn': 'N',
        'mustreadnoti': 'N',
        'listnum': 20,
        'fontproperties': '{"bold": false, "color": ""}',
        'texticonyn': 'N'
    }

    r = requests.post(memo_link, cookies=cookies, headers=headers, data=form_data)

    if r.status_code == 200 or r.status_code == 302:
        return True
    else:
        print(f"Error code: {r.status_code}")

    return False



def main(cafe_link: str, login_info: tuple, user_info: tuple, board_id: str, debug: bool, sec: bool):
    kid, kpw = login_info
    name, birthday, phone_number = user_info
    cafe_id = get_grp_id(cafe_link)
    comment = generate_comment(name, birthday, phone_number, debug=debug)

    d = open_browser()

    login(d, cafe_link, kid, kpw)
    time.sleep(1)
    goto_url(d, f"{cafe_link}/{board_id}")
    d.implicitly_wait(3)
    token = get_memo_token(d)

    if token == '':
        raise Exception("Invalid Token Exception")
    else:
        print("Token is valid. Ready to write comment.")

    result = write_comment(d, cafe_id, board_id, token, comment, sec=sec)

    if result is True:
        print("Success. Check your comments.")
        goto_url(d, f"{cafe_link}/{board_id}")
    else:
        print("Failure!")



if __name__ == '__main__':
    update_time()