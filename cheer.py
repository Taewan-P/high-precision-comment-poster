import requests
import sys

from post import get_grp_id


def get_cheer_id(cafe_link: str) -> int:
    cafe_id = get_grp_id(cafe_link)
    req_url = f"https://fancafe-external-api.cafe.daum.net/fancafe/{cafe_id}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/104.0.5112.81 Safari/537.36 ',
        'sec-ch-ua-platform': 'Windows',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'referer': 'https://cafe.daum.net/',
        'origin': 'https://cafe.daum.net',
        'dnt': '1',
        'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
        'accept-enconding': 'gzip, deflate, br',
        'accept': '*/*'
    }

    r = requests.get(req_url, headers=headers)

    if r.status_code == 200:
        return r.json()['cafe']['cheerWidgetId']


def cheer_fan(cafe_id: str, cheer_id: int, count: int) -> bool:
    req_url = f"https://fancafe-external-api.cafe.daum.net/fancafe/widget/cheer/{cafe_id}/{cheer_id}?count={count}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/104.0.5112.81 Safari/537.36 ',
        'sec-ch-ua-platform': 'Windows',
        'sec-ch-ua-mobile': '?0',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'referer': 'https://cafe.daum.net/',
        'origin': 'https://cafe.daum.net',
        'dnt': '1',
        'accept-language': 'ko,en-US;q=0.9,en;q=0.8',
        'accept-enconding': 'gzip, deflate, br',
        'accept': '*/*'
    }

    r = requests.post(req_url, headers=headers)
    
    if r.status_code == 200:
        return True
    else:
        print(f"Cheer Failed! - Status Code: {r.status_code}")
        return False

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Invalid parameter')
        sys.exit(1)
    
    cafe_link = sys.argv[1]
    cafe_id = get_grp_id(cafe_link)
    cheer_id = get_cheer_id(cafe_link)
    result = cheer_fan(cafe_id, cheer_id, 1)

    if result is True:
        print("Cheer Success!")