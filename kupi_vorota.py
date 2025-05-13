import sys
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import csv


file_with_urls = 'urls.txt'
file_result = 'products.csv'


def kupi_vorota(urls, filename):
    # Настройка опций для запуска Firefox в режиме без GUI (необязательно)
    options = Options()
    # options.headless = True  # Uncomment для запуска в фоновом режиме
    # Создание драйвера
    driver = webdriver.Firefox(options=options)
    for url in urls:
        parse_url(driver, url, filename)
    # Закрытие драйвера
    driver.quit()


def parse_url(driver, url, filename):
    # Открытие страницы
    driver.get(url)
    # Пролистывание страницы до самого низа
    # Это делается для того, чтобы все товары были загружены
    while True:
        # Получение текущей высоты страницы
        last_height = driver.execute_script("return document.body.scrollHeight")
        # Пролистывание страницы до низа
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # Пауза для загрузки контента
        import time
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
    urls = read_file_to_list(file_with_urls)
    kupi_vorota(urls, file_result)


if __name__ == '__main__':
    main()
