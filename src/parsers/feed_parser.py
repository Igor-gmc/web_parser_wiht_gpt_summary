 # извлекает из страницы список превью (дата/заголовок/ссылка/текст)

import json

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from src.settings.config import settings
from src.storage.json_store import write_json_result_parse

def get_driver() -> Chrome:
    options = Options()
    options.add_argument(f"user-agent={settings.USER_AGENT}")
    driver = webdriver.Chrome(options=options)
    driver.get(settings.FEED_URL)
    return driver

def parse_data_from_post(post: WebElement) -> dict:
    """Функция парсит данные с одного поста

    Args:
        post (WebElement): Получаем WebElement

    Returns:
        dict: Отдаем словарь с заголовком и текстом статьи
    """
    date = ''
    title = ''
    text = ''
    url = ''

    try:
        # Ищем дату публикации из атрибута datetime тега time
        time_element = post.find_element(By.CSS_SELECTOR, 'a.tm-article-datetime-published time')
        date = time_element.get_attribute('datetime')
    except Exception as e:
        print(f"  [ОШИБКА] Не найдена дата: {e}")

    try:
        # Ищем заголовок (текст внутри span в ссылке)
        title_span = post.find_element(By.CSS_SELECTOR, 'a[data-test-id="article-snippet-title-link"] span')
        title = title_span.text.strip()
    except Exception as e:
        print(f"  [ОШИБКА] Не найден заголовок: {e}")

    try:
        # Ищем превью текст статьи
        text_container = post.find_element(By.CSS_SELECTOR, '.article-formatted-body_version-2')
        ps = text_container.find_elements(By.TAG_NAME, 'p')
        text = ''.join(p.text.strip() for p in ps)
    except Exception as e:
        print(f"  [ОШИБКА] Не найден текст: {e}")

    try:
        # Ищем URL статьи из ссылки "Читать далее"
        readmore_link = post.find_element(By.CSS_SELECTOR, 'a.readmore')
        href = readmore_link.get_attribute('href')
        # Если href относительный, добавляем базовый URL
        if href.startswith('/'):
            url = f"https://habr.com{href}"
        else:
            url = href
    except Exception as e:
        print(f"  [ОШИБКА] Не найден URL: {e}")

    return {
        'date': date,
        'title': title,
        'text': text,
        'url': url
    }
    


def scroll_and_find_posts(driver: Chrome) -> list:
    """Парсит статьи с усазанного URL со скроллингом страниц

    Args:
        driver (Chrome): driver.Chrome() Silenium

    Returns:
        list: список словарей с зоголовком и текстом статьи
    """
    
    target = settings.MAX_ARTICLES # сколько статей нужно собрать

    wait = WebDriverWait(driver, settings.SELENIUM_TIMEOUT) # Ожидание загрузки страницы
    CARD = "article-snippet" # Класс превью статьи на странице

    try:
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, CARD))) # Ждем пока загрузятся превью статей
    except TimeoutException:
        print("Превышено время ожидания первичной страницы")
        driver.quit()
        exit(1)
    
    preview_count = 0 # Счетчик собранных превью статей
    no_grow_count = 0 # Счетчик итераций без прироста собранных статей

    while True:
        posts = driver.find_elements(By.CLASS_NAME, CARD) # Находим все превью статей на странице

        count = len(posts)

        if count >= target:
            print(f"Собрано нужное количество превью статей: {count}")
            break

        if count == preview_count:
            no_grow_count += 1
            if no_grow_count >= 3: # если за 3 итерации не было прироста, выходим
                print(f"Прирост превью статей отсутствует, собрано: {count}")
                break
        else:
            no_grow_count = 0
        
        preview_count = count

        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Прокручиваем страницу вниз для подгрузки новых статей

        try:
            wait.until(lambda d: len(d.find_elements(By.CLASS_NAME, CARD)) > count) # Ждем пока загрузятся новые превью статей
        except TimeoutException:
            print("Превышено время ожидания подгружаемых новых статей")
            break
    
    result = [] # тут будет список спаршенных данных

    for post in posts:
        data = parse_data_from_post(post) # Получаем данные с сайта в виде словаря
        result.append(data) # Склабываем в список словари

    return result

def habr_parser() -> list[dict]:
    driver = get_driver() # Получаем драйвер
    result = scroll_and_find_posts(driver) # Получаем результат парсинга
    write_json_result_parse(str(settings.DATA_PAGES_PATH), result)
    driver.quit()
    return result

if __name__ == "__main__":
    data = habr_parser()
    print(f"Собрано статей: {len(data)}")
    for i, d in enumerate(data, 1):
        # Безопасный вывод для консоли Windows
        title = d['title'].encode('cp1251', errors='replace').decode('cp1251')
        text = d['text'].encode('cp1251', errors='replace').decode('cp1251')
        print(f"\n{'='*50}")
        print(f"Статья {i}:")
        print(f"Заголовок: {title}")
        print(f"Текст: {text}")
        print('='*50)


