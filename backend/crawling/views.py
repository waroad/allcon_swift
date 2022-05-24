import json
import time

from django.utils.decorators import method_decorator

from .models import SearchResult
from rest_framework import viewsets
from .serializer import SearchResultSerializer
from django.views.generic import View
from django.http import HttpResponse

from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait as wait
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

class SearchResultViewSet(viewsets.ModelViewSet):
    queryset = SearchResult.objects.all()
    serializer_class = SearchResultSerializer

class Search(View):
    s = Service('chromedriver')
    driver = webdriver.Chrome(service=s)

    def get(self, request):
        open_or_close = request.GET['state']
        if open_or_close == 'open':
            return HttpResponse('web opened...')
        else:
            self.driver.close()
            return HttpResponse('web closed...')

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
                result['title'] = content_name
                print(content_link)
                result['url'] = content_link
                print(content_href)
                result['href'] = content_href
                is_content_title = False
        else:
            content_sites = content.find_elements(By.CLASS_NAME, 'price-comparison__grid__row__icon')
            for site in content_sites:
                sites.add(site.get_attribute('alt'))
            print(sites)
            site_list = list(sites)
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

    categories_content = driver.find_element(By.XPATH,
                                             '//*[@id="base"]/div[2]/div/div[2]/div[6]/div[1]/div[1]/div[2]/div[2]')
    categories = categories_content.find_elements(By.TAG_NAME, 'span')
    category = []
    for i in categories:
        category.append(i.get_attribute('innerHTML').strip("<span>"","" </span>""<!---->"))
    category = list(filter(None, category))

    director = ""
    try:
        director = driver.find_element(By.XPATH,
                                       '//*[@id="base"]/div[2]/div/div[2]/div[6]/div[1]/div[1]/div[4]/div[2]/span/a').get_attribute(
            'innerHTML')
    except:
        print("no director")

    rating = driver.find_element(By.XPATH,
                                 '//*[@id="base"]/div[2]/div/div[2]/div[6]/div[1]/div[1]/div[1]/div[2]/div/div[2]/a')
    rating = rating.get_attribute('innerHTML').replace('>', '(')
    rating = rating.split('(')

    year = driver.find_element(By.XPATH,
                               '//*[@id="base"]/div[2]/div/div[2]/div[2]/div[1]/div[1]/div/span').text
    year = year.strip("("")")
    sites = set()
    content_sites = driver.find_elements(By.CLASS_NAME, 'price-comparison__grid__row__icon')
    for site in content_sites:
        sites.add(site.get_attribute('alt'))
    synopsis = driver.find_element(By.XPATH, '//*[@id="base"]/div[2]/div/div[2]/div[6]/div[1]/div[3]/p/span').text

    print(title)
    res['title'] = title
    print(year)
    res['year'] = year
    print(sites)
    res['sites'] = list(sites)
    print(director.strip())
    res['director'] = director.strip()
    print(rating[1].strip())
    res['rating'] = rating[1].strip()
    print(category)
    res['category'] = category
    print(synopsis)
    res['synopsis'] = synopsis

    return res
