import requests
from bs4 import BeautifulSoup as BS
import re

# import Levenshtein
# import difflib

headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

brands = ["adidas", "Arkk Copenhagen", "Asics", "BIRKENSTOCK", "CHAMPION", "Chinatown Market", "CLARKS", "CONVERSE",
          "Crep Protect", "DIADORA", "DR.MARTENS", "EDWIN", "FILA", "First WS2", "Happy Socks", "HERMETIC SQUARE",
          "HUF", "HYDRO FLASK", "Inne", "Jordan", "Jordan Brand", "KangaROOS", "Mizuno", "NAPAPIJRI", "New Balance",
          "NEW ERA", "Nike", "NOVESTA", "Patagonia", "Puma", "RAINS", "Reebok", "SECRID", "Stussy", "SUPERGA", "TEALER",
          "TEVA", "The North Face", "Vans"]


colors_pl = ["Czerwony", "Różowy", "Pomarańczowy", "Żółty", "Brązowy", "Niebieski", "Fioletowy", "Zielony", "Biały",
          "Czarny", "Szary", "Granatowy"]


class Item:

    def __init__(self, link, full_name, brand, model, index, color, normal_price, sale_price, sizes):
        self.link = link
        self.full_name = full_name
        self.brand = brand
        self.model = model
        self.index = index
        self.color = color
        self.normal_price = normal_price
        self.sale_price = sale_price
        self.sizes = sizes


def create_url(search_request):
    reg = re.compile('[^a-zA-Z0-9 ]')
    reg_2 = re.compile('[^a-zA-Z0-9.\- ]')

    url_1 = reg.sub(' ', search_request)
    url_1 = re.sub(' +', ' ', url_1)
    url_1 = re.sub(' ', '-', url_1)
    print(url_1)

    url_2 = reg_2.sub('', search_request)
    url_2 = re.sub(' +', ' ', url_2)
    url_2 = re.sub(' ', '%20', url_2)
    print(url_2)

    url = 'https://chmielna20.pl/products/{0}/keyword,{1}?keyword={2}'.format(url_1, url_2, url_2)
    return url


def parse_item(item):
    link = item.find('a')
    if link is not None:
        link = link['href']
        name_str = item.find('h2', class_='products__item-name')
        full_name = name_str.text.strip()
        for brand_name in brands:

            if full_name.find(brand_name) != -1:
                brand = brand_name
                brand_pos = full_name.find(brand_name)

                break
        brand_len = brand_pos + len(brand)
        last_right_bracket = full_name.rfind('(')
        model = full_name[brand_len:last_right_bracket].strip()

        index = full_name[last_right_bracket:].strip()
        index = index[1:-1]  # убираем скобки

        price_div = item.find('p', class_='products__item-price')
        # стандартно два потомка, если с акцией - три
        if len(price_div.findChildren()) == 3:
            normal_price = price_div.findChildren()[0].text
            sale_price = price_div.findChildren()[1].text
        elif len(price_div.findChildren()) == 2:
            normal_price = price_div.findChildren()[0].text
            sale_price = '0'

        # оставляем в строке только вещественное число
        nums = re.findall(r'\d*\.\d+|\d+', normal_price)
        normal_price = [float(i) for i in nums][0]
        nums = re.findall(r'\d*\.\d+|\d+', sale_price)
        sale_price = [float(i) for i in nums][0]

        sizes_ul = item.find('div', class_='sizes').find('ul')
        sizes = ''

        for li in sizes_ul.findAll('li'):
            # у некоторых товаров нет размеров
            if 'data-sizeeu' in li:
                sizes += li['data-sizeeu'] + ', '

        sizes = sizes[:-2]  # удаляем пробел и лишнюю запятую

        # узнаем цвет
        # идем в карточку товара
        raw = requests.get(link, headers=headers)
        html = BS(raw.text, 'html.parser')

        description_div = html.find('div', class_='col-md-6 col-sm-12 col-xs-12 description')

        # тег p с цветом на разных товарах может быть разным по счету. поэтому проверяем каждый p на наличие там цвета
        for p in description_div.findAll('p'):
            if (p.text[2:] in colors_pl) is True:
                color = p.text[2:]
                break
            else:
                color = ''
        create_object(link, full_name, brand, model, index, color, normal_price, sale_price, sizes)


def create_object(link, full_name, brand, model, index, color, normal_price, sale_price, sizes):

    item = Item(link, full_name, brand, model, index, color, normal_price, sale_price, sizes)
    print(vars(item))


def parse(search_request):
    url = create_url(search_request)
    raw = requests.get(url, headers=headers)
    html = BS(raw.text, 'html.parser')

    objects_arr = []

    container = html.find('div', class_='product__container')
    ul = container.find('ul', class_='col-md-12')
    for li in ul.findAll('li'):
        parse_item(li)


# str_search = input('search for...')
# str_search = 'nike,./-air max 270 react'
str_search = 'adidas backpack'

# в строке search ищет по рег.выр-ю сверху и заменяет на ''

parse(str_search)





