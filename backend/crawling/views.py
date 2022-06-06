import datetime
import json
import random
import re
import time
import requests

from django.utils.decorators import method_decorator

from .models import SearchResult
from rest_framework import viewsets
from .serializer import SearchResultSerializer
from django.views.generic import View
from django.http import HttpResponse

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from django.views.decorators.csrf import csrf_exempt

from bs4 import BeautifulSoup as bs


# Create your views here.

class SearchResultViewSet(viewsets.ModelViewSet):
    queryset = SearchResult.objects.all()
    serializer_class = SearchResultSerializer


class Search(View):
    option = Options()
    # 알림창 끄기
    option.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 1
    })
    s = Service(executable_path="C:/Users/pc/PycharmProjects/allcon_swift/backend/chromedriver.exe")
    driver = webdriver.Chrome(options=option, service=s)

    base_url = "https://watcha.com/sign_in"
    driver.get(base_url)
    id_element = driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/main/div[1]/main/div/form/div[1]/input')
    pswd_element = driver.find_element(By.XPATH,
                                       '//*[@id="root"]/div[1]/main/div[1]/main/div/form/div[2]/input')

    id_element.send_keys('teamprojten@gmail.com')
    pswd_element.send_keys('teamteam1010')

    driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/main/div[1]/main/div/form/div[3]/button').click()

    def get(self, request):
        open_or_close = request.GET.get('state', False)
        recommend_category = request.GET.get('fav', False)
        print(recommend_category)
        if open_or_close and not recommend_category:
            if open_or_close == 'open':
                self.driver.find_element(By.XPATH, '//*[@id="root"]/div[1]/main/div[1]/section/ul/li[1]/button').click()
                return HttpResponse('web opened...')
            else:
                self.driver.close()
                return HttpResponse('web closed...')
        elif not open_or_close:
            res = {
                'netflix': get_recommend_netflix_content(),
                'watcha': get_recommend_watcha_content(self.driver),
                'recommend': get_category_content(recommend_category, self.driver)
            }
            return HttpResponse(json.dumps(res), content_type='application/json')

    @method_decorator(csrf_exempt)
    def post(self, request):
        keyword = request.GET.get('keyword', False)
        url = request.GET.get('url', False)
        if keyword and not url:
            res = get_justwatch_contents(keyword, self.driver)
        elif url and not keyword:
            res = get_justwatch_detail_contents(url, self.driver)
        else:
            res = 'null'
        return HttpResponse(json.dumps(res), content_type='application/json')


def get_wavve_contents(keyword, driver):
    res = {}
    base_url = "https://www.wavve.com/index.html"
    driver.get(base_url)

    driver.find_element(By.XPATH, '//*[@id="contents"]/div[1]/section/div[1]/a/img').click()

    x_path = '//*[@id="app"]/div[1]/div[2]/header/div[2]/div/button/span'
    driver.find_element(By.XPATH, x_path).click()

    element = driver.find_element(By.XPATH, '//*[@id="search-ip"]')
    element.send_keys(keyword)
    element.send_keys(Keys.RETURN)

    wait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//*[@id="contents"]/div[1]/div/a/img'))).click()

    driver.find_element(By.XPATH, '//*[@id="contents"]/div[2]/div/ul/li[5]/button').click()

    wait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME, 'thumb-img')))
    movie_list = driver.find_elements(By.TAG_NAME, 'img')

    for movie in movie_list:
        movie_name = movie.get_attribute('alt')
        is_there_movie_name = keyword in movie_name
        is_there_paren = "(" in movie_name
        if is_there_movie_name and not is_there_paren:
            movie_link = movie.get_attribute('src')
            res["title"] = movie_name
            res["url"] = movie_link

    return res


def get_justwatch_contents(keyword, driver):
    res = {}
    sites = set()

    base_url = "https://www.justwatch.com/kr/%EA%B2%80%EC%83%89?q="
    driver.get(base_url)

    element = driver.find_element(By.XPATH,
                                  '//*[@id="app"]/div[3]/div/div[2]/div[1]/div/ion-searchbar/div/input')
    element.send_keys(keyword)
    element.click()
    element.send_keys(Keys.RETURN)

    content_body = driver.find_element(By.TAG_NAME, 'body')

    for i in range(10):
        content_body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    wait(driver, 20).until(EC.all_of(
        EC.presence_of_all_elements_located((By.XPATH, '//*[@id="base"]/div[3]/div/div/div[2]'))
    ))

    content_list = driver.find_elements(By.TAG_NAME, 'ion-col')
    is_content_title = True

    result = {}
    result_id = 0

    for content in content_list:

        if is_content_title:
            content_a = content.find_element(By.TAG_NAME, 'a')
            content_img = content.find_element(By.TAG_NAME, 'img')
            content_href = content_a.get_attribute('href')
            content_name = content_img.get_attribute('alt')
            content_link = content_img.get_attribute('src')

            is_there_content_name = keyword in content_name
            if is_there_content_name:
                print(content_name)
                result['title'] = str(content_name)
                print(content_link)
                result['url'] = content_link
                print(content_href)
                result['href'] = content_href
                is_content_title = False
        else:
            content_sites = content.find_elements(By.CLASS_NAME, 'price-comparison__grid__row__icon')
            content_year = content.find_element(By.CLASS_NAME, 'title-list-row__row-header-year').get_attribute(
                'innerHTML')
            for site in content_sites:
                sites.add(site.get_attribute('alt'))
            print(sites)
            site_list = list(sites)
            result['title'] += content_year
            result['sites'] = site_list
            sites.clear()
            res[result_id] = result
            result = {}
            result_id += 1
            is_content_title = True

    return res


def get_justwatch_detail_contents(url, driver):
    res = {}

    base_url = url
    driver.get(base_url)

    title = driver.find_element(By.XPATH, '//*[@id="base"]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div/h1').text
    # url은 클라이언트에서 받아와야 함. get_contents함수 실행 이후 화면 구성할 때 이미지에 url정보도 담을 수 있게 (a href = "??")
    categories_content = ""
    category = []
    try:
        categories_content = driver.find_element(By.XPATH,
                                                 '//*[@id="base"]/div[2]/div/div[1]/div/aside/div[1]/div[3]/div[2]/div[2]')
        categories = categories_content.find_elements(By.TAG_NAME, 'span')
        for i in categories:
            category.append(i.get_attribute('innerHTML').strip("<span>"","" </span>""<!---->"))
        category = list(filter(None, category))
    except:
        print("no category")

    director = ""
    try:
        director = driver.find_element(By.XPATH,
                                       '//*[@id="base"]/div[2]/div/div[1]/div/aside/div[1]/div[3]/div[4]/div[2]/span/a').get_attribute(
            'innerHTML')
    except:
        print("no director")

    rating = ""
    try:
        rating = driver.find_element(By.XPATH,
                                     '//*[@id="base"]/div[2]/div/div[1]/div/aside/div[1]/div[3]/div[1]/div[2]/div/div[2]/a')
        rating = rating.get_attribute('innerHTML').replace('>', '(')
        rating = rating.split('(')
        rating = rating[1].strip()
    except:
        print("no rate")

    year = ""
    try:
        year = driver.find_element(By.XPATH,
                                   '//*[@id="base"]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div/span').text
        year = year.strip("("")")
    except:
        print("no year")

    sites = []

    content_sites_list = driver.find_elements(By.CLASS_NAME, 'price-comparison__grid__row')
    for site in content_sites_list:
        try:
            content_sort = site.find_element(By.CLASS_NAME, 'price-comparison__grid__row__title-label').text
            content_sites = site.find_elements(By.CLASS_NAME, 'price-comparison__grid__row__element__icon')
            for content_site in content_sites:
                content_icon = content_site.find_element(By.CLASS_NAME,
                                                         'price-comparison__grid__row__icon').get_attribute(
                    'alt')
            content_price = content_site.find_element(By.CLASS_NAME, 'price-comparison__grid__row__price').text.split(
                ' ')
            sites_list_item = {'sort': content_sort, 'site': content_icon, 'price': content_price[0]}
            sites.append(sites_list_item)
        except:
            print("no site")

    synopsis = ""
    try:
        synopsis = driver.find_element(By.XPATH, '//*[@id="base"]/div[2]/div/div[2]/div[5]/div[1]/div[3]/p/span').text
    except:
        print("no synopsis")

    print(title)
    res['title'] = title
    print(year)
    res['year'] = year
    print(sites)
    res['sites'] = sites
    print(director.strip())
    res['director'] = director.strip()
    print(rating)
    res['rating'] = rating
    print(category)
    res['category'] = category
    print(synopsis)
    res['synopsis'] = synopsis

    return res


def get_recommend_netflix_content():
    base_url = "https://top10.netflix.com/south-korea/films"
    response = requests.get(base_url)

    res = {}
    res_film = {}
    res_tv = {}

    if response.status_code == 200:
        html = response.text
        soup = bs(html, 'html.parser')
        img_lists = soup.select('img.wh-full.banner-image')
        href_lists = soup.select('a.block.text-13px.whitespace-nowrap')
        for index in range(10):
            res_film[index] = {
                "title": img_lists[index].attrs['alt'],
                "url": href_lists[index].attrs['href'],
                "photo": img_lists[index].attrs['src']
            }
    else:
        print(response.status_code)

    base_url = "https://top10.netflix.com/south-korea/tv"
    response = requests.get(base_url)

    if response.status_code == 200:
        html = response.text
        soup = bs(html, 'html.parser')
        img_lists = soup.select('img.wh-full.banner-image')
        href_lists = soup.select('a.block.text-13px.whitespace-nowrap')
        for index in range(10):
            res_tv[index] = {
                "title": img_lists[index].attrs['alt'],
                "url": href_lists[index].attrs['href'],
                "photo": img_lists[index].attrs['src']
            }
    else:
        print(response.status_code)

    res['movie'] = res_film
    res['program'] = res_tv

    return res


def get_recommend_watcha_content(driver):
    base_url = "https://watcha.com/browse/video"
    driver.get(base_url)
    driver.maximize_window()

    res = {}
    result_id = 0

    time.sleep(3)

    content_body = driver.find_element(By.TAG_NAME, 'body')

    for i in range(2):
        content_body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.2)

    rank_list = driver.find_elements(By.CSS_SELECTOR, 'li.w_exposed_cell.css-mpj9pj')
    for element in rank_list:
        res[result_id] = {
            "title": element.find_element(By.CLASS_NAME, 'css-1i82ydo').get_attribute('aria-label'),
            "url": element.find_element(By.CLASS_NAME, 'css-1i82ydo').get_attribute('href'),
            "photo": element.find_element(By.CLASS_NAME, 'css-1cs6tj2').get_attribute('src')
        }
        result_id += 1

    return res


def get_category_content(category, driver):
    print(category)
    category_list = re.split('[\[\]\"\',]', category)
    category_list = ' '.join(category_list).split()
    print(category_list)
    category_dict = {
        '액션': 'act',
        '코미디': 'cmy',
        '다큐멘터리': 'doc',
        '판타지': 'fnt',
        '공포': 'hrr',
        '음악': 'msc',
        '로맨스': 'rma',
        '스포츠': 'spt',
        '애니메이션': 'ani',
        '드라마': 'drm',
        '역사': 'hst',
        '가족': 'fml',
        '스릴러': 'trl',
        'SF': 'scf',
        '리얼리티': 'rly'
    }

    res = {}
    user_category = ""
    user_genre = []

    if category_list is not None:
        try:
            for category in category_list:
                user_category += category_dict[category] + ','
                user_genre.append(category)
            res["genre"] = user_genre
        except:
            print("없는 장르")
            res["genre"] = ""
    else:
        user_category = category_dict[random.choice(list(category_dict.keys()))]

    base_url = "https://www.justwatch.com/kr?genres=" + user_category + "&providers=dnp,nfx,nvs,wac,wav"
    driver.get(base_url)

    time.sleep(2)

    random_content = driver.find_elements(By.CLASS_NAME, 'title-list-grid__item')
    for i in range(30):
        picture = random_content[i].find_element(By.CLASS_NAME, 'picture-comp__img')
        result = {
            "title": picture.get_attribute('alt'),
            "url": random_content[i].find_element(By.CLASS_NAME, 'title-list-grid__item--link').get_attribute('href'),
            "photo": picture.get_attribute('src')
        }
        res[i] = result

    return res
