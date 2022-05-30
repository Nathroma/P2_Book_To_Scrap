# Importation des packages utile au progamme
#
import csv
import requests
import re
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Creation des variables


url_site = 'https://books.toscrape.com'
infolist = {}
urls_book = []
listOfPages = []
list_url_category = []


def main():
    """
    Toutes les boucles de programmes, à chaques boucles FOR une page differente
    La premiere boucle analyse categorie et creer un fichier portant son nom
    le deuxieme boucle repete les pages de la categorie si il y en a plusieurs
    La troisieme répète pour chaque livre present sur la page en question
    """
    fieldnames = ['product_page_url', 'universal_product_code', 'title',
                  'price_including_tax', 'price_excluding_tax',
                  'number_available', 'product_description',
                  'category', 'review_rating']
    get_all_category(url_site)
    current_category = 1
    for i in list_url_category:  # Chaque categorie
        currentPage = 0
        response = requests.get(list_url_category[current_category])
        actual_category_url = list_url_category[current_category]
        current_category += 1
        listOfPages = []
        category_name = list_url_category[current_category].replace\
            ('https://books.toscrape.com/catalogue/category/books/', '')\
            .replace('/index.html', '')
        with open('books/' + category_name, 'w', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            if response.ok:
                count_pages(listOfPages, actual_category_url)
                for pages in listOfPages:   # Chaque page
                    response = requests.get(listOfPages[currentPage])
                    soup = BeautifulSoup(response.text, 'html.parser')
                    currentPage += 1
                    for url_book in soup.findAll('h3'):    # chaque livre
                        if url_book.find('a'):
                            url_book = url_site + '/' + url_book.find('a')\
                                ['href'].replace('../../../', 'catalogue/')
                            urls_book.append(url_book)
                            get_book_values(url_book)
                            writer.writerow(infolist)


def create_folder():
    """
    Creation des dossiers pour recevoir images et info des livres
    """
    try:
        os.mkdir('books/')
        os.mkdir('images/')
    except OSError:
        pass
    else:
        pass
    main()


def count_pages(listOfPages, actual_category_url):
    """
    compte le nombre de page par categorie :
    Si il existe plusieurs page alors, les ajouters dans une liste 
    sinon garder l'unique page dans la liste 
    """
    response = requests.get(actual_category_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    next_page = soup.find('li', {"class": "current"})
    listOfPages.append(actual_category_url)
    if next_page:
        pages = int(next_page.text.strip().split(' ')[3])-1
        actual_category_url = actual_category_url.replace('index.html', '')
        for i in range(pages):
            listOfPages.append(actual_category_url + 'page-' + str(i + 2) + '.html')
    return listOfPages


def get_book_values(url_book):
    """
    ecriture de la totalité des données propre au livre 
    td 0 = UPC
    td 2 et 3 = prix avec et sans taxe
    td 5 = nombre dispo
    td 6 = Note de revue
    Title = titre du livre
    image du livre recuperer dans une def 

    toutes les infos sont rangées dans le dictionnaire "infolist"
    """
    response = requests.get(url_book)
    soup = BeautifulSoup(response.text, 'html.parser')
    tds = soup.findAll('td')  #demande a beatifulsoup de recuperer toutes les valeurs avec une balise "td"
    infolist['product_page_url'] = url_book
    infolist['universal_product_code'] = tds[0].text
    title = soup.find('li', {"class": "active"}).text
    infolist['title'] = title
    infolist['price_including_tax'] = tds[2].text.replace('£', '')
    infolist['price_excluding_tax'] = tds[3].text.replace('£', '')
    infolist['number_available'] = tds[5].text.split('(')[1].split(' ')[0]
    infolist['product_description'] = soup.find("meta",
        {"name": "description"})['content'].strip()
    infolist['category'] = soup.find('a', {"href": \
        re.compile("../category/books/")}).text
    infolist['review_rating'] = tds[6].text
    upc = infolist['universal_product_code']
    image_book = soup.find('div', {'class': 'item active'}).find('img').attrs\
        ['src'].replace('../..', 'http://books.toscrape.com')
    get_image(upc, image_book)
    print(title)


def get_all_category(url_site):
    """ 
    Implémente "list_url_category" avec la liste
    de toutes les categories du site
    """
    response = requests.get(url_site)
    url_category = ''
    if response.ok:
        soup = BeautifulSoup(response.text, 'html.parser')
        all_url_category = soup.find('ul', {'class': 'nav nav-list'}).findAll('li')
        for url_category in all_url_category:
            list_url_category.append(url_site + '/' + url_category.find('a')['href'])
        return list_url_category


def get_image(upc, image_book):
    """
    Récupere les images de chaques livres
    et les telecharge dans le dossier "images"
    """
    response = requests.get(image_book)
    file = open('images/' + upc + '.jpg', "wb") 
    file.write(response.content)
    file.close()


create_folder()