import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv
import time


file_with_urls = 'urls.txt'
file_result = 'products.csv'
available_all = False


def kupi_vorota(urls, filename, available_all=False):
    # Настройка опций для запуска Firefox в режиме без GUI (необязательно)
    options = Options()
    # options.headless = True  # Uncomment для запуска в фоновом режиме
    # Создание драйвера
    driver = webdriver.Firefox(options=options)
    for url in urls:
        parse_url(driver, url, filename, available_all)
    # Закрытие драйвера
    driver.quit()


def parse_url(driver, url, filename, available_all=False):
    # Открытие страницы
    driver.get(url)
    # Переключение фильтра на "В наличии и под заказ"
    if available_all:
        time.sleep(2)
        filter = driver.find_element(By.ID, 'AVAILABLE_ALL')
        filter.click()
        time.sleep(2)

    while True:
        # Пролистывание страницы до самого низа
        # Это делается для того, чтобы все товары были загружены
        # Получение текущей высоты страницы
        last_height = driver.execute_script("return document.body.scrollHeight")
        # Пролистывание страницы до низа
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Пауза для загрузки контента
        time.sleep(2)
        # Получение новой высоты страницы
        new_height = driver.execute_script("return document.body.scrollHeight")
        # Если высота не изменилась, значит страница полностью загружена
        if new_height == last_height:
            break
    # Парсинг артикулов, наименований и цен
    try:
        # Ожидание загрузки элементов
        products = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".product-item"))
        )
        # Создание файла CSV для записи результатов
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['Артикул', 'Наименование', 'Цена']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for product in products:
                # Парсинг артикула
                article = product.find_element(By.CSS_SELECTOR, ".product-item-properties").text.split()[-1]
                # Парсинг наименования
                name = product.find_element(By.CSS_SELECTOR, ".product-item-title").text
                # Парсинг цены
                price = product.find_element(By.CSS_SELECTOR, ".product-item-price-current").text
                if price.endswith('руб.'):
                    price = ''.join(price[:-4].split())
                writer.writerow({'Артикул': article, 'Наименование': name, 'Цена': price})
                print(f"Артикул: {article}, Наименование: {name}, Цена: {price}")
    except TimeoutException:
        print("Товары не загрузились")


def read_file_to_list(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file]
        return lines
    except FileNotFoundError:
        print(f"Файл {filename} не найден.")
        return []
    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return []


def main():
    args = sys.argv
    if len(args) > 1:
        file_result = args[1]
    if len(args) > 2 and args[2]=='all':
        available_all = True
    urls = read_file_to_list(file_with_urls)
    kupi_vorota(urls, file_result, available_all)


if __name__ == '__main__':
    main()
