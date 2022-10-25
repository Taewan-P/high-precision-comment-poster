from bs4 import BeautifulSoup
import ntplib
import os
import sys
import time
import requests

from datetime import datetime

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



if __name__ == '__main__':
    update_time()