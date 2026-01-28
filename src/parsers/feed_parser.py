 # извлекает из страницы список превью (дата/заголовок/ссылка/текст)

import json
from math import e
from turtle import save

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import Chrome, Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from src.settings.config import settings

def get_driver() -> Chrome:
    driver = webdriver.Chrome() # Инициализация драйвера
    driver.get(settings.FEED_URL) # Открытие страницы с статьями
    return driver



def scroll_and_find_posts(driver: Chrome) -> list:
    """Парсит статьи с усазанного URL со скроллингом страниц

    Args:
        driver (Chrome): driver.Chrome() Silenium

    Returns:
        list: список превью статей
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

    return posts # Возвращаем список найденных превью статей

def save_posts_to_cache(posts: list) -> None:
    pass

def main():
    driver = get_driver()
    posts = scroll_and_find_posts(driver)
    save_posts_to_cache(posts)
    driver.quit()

if __name__ == "__main__":
    main()


