#!/usr/bin/python
# -*- coding: Shift-JIS -*-

from bs4 import BeautifulSoup
from itertools import zip_longest
#from retry import retry
import matplotlib.pyplot as plt
import re
import requests
#import pandas as pd 
import time
import webbrowser


def get_html(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def get_next_url(soup):
    next_button = soup.find("button", class_="btnFunc pager__btn__next")
    try:
        onclock_element = next_button.get("onclick")
        next_url = onclock_element.split("'")[1]
    except:
        next_url = "none"
    return next_url

def get_data(soup, data_list):

    items1 = soup.findAll("p", attrs={"class": "casetMedia__body__maker"})
    items2 = soup.findAll("h3", attrs={"class": "casetMedia__body__title"})
    items3 = soup.findAll("span", attrs={"class": "basePrice__price__main"})
    items4 = soup.findAll("span", attrs={"class": "basePrice__price__sub"})
    #items5 = soup.findAll("p", attrs={"class": "specWrap__box__title"}, text=["年式", "走行距離", "排気量"])
    items6 = soup.findAll("p", attrs={"class": "specWrap__box__num"})
    items7 = soup.findAll("h3", attrs={"class": "casetMedia__body__title"})

    count = 0
    
    # get car year, mileage and displacement
    car_year_list = []
    mileage_list = []
    displacement_list = []
    
    for value6 in items6:
        values = value6.contents[0]
        
        if count % 3 == 0:
            car_year_list.append(values)
        if count % 3 == 1:
            mileage_list.append(values)
        if count % 3 == 2:
            displacement_list.append(values)
        #print(values)
        count += 1
    
    count = 0
    for value1, value2, value3, value4, value7 in zip_longest(items1, items2, items3, items4, items7):
        data_dict = {"car_maker": "", "car_name": "", "price": "", "car_year": "", "mileage": "", "displacement": "" , "car_url": "" }
        
        # get car maker
        data_dict["car_maker"] = value1.contents[0].replace(" ", "") # remove single-byte spaces
        
        # get car name
        value2_1 = value2.findAll("a")
        value2_2 = value2_1[0].contents[0].replace("\xa0", "  ") # fixed garbled spaces
        data_dict["car_name"] = value2_2.replace(" ", "") # remove single-byte spaces
        
        # get price
        price = int(value3.contents[0]) # get intefer
        str_decimal = value4.contents[0] # get decimal
        decimal = int(re.sub(r"\D", "", str_decimal)) # remove a dot
        while decimal > 1:
            decimal *= 0.1
        price += decimal
        data_dict["price"] = price
        
        # insert car year, mileage and displacement to data_dict
        data_dict["car_year"] = car_year_list[count]
        data_dict["mileage"] = mileage_list[count]
        data_dict["displacement"] = displacement_list[count]
        
        # get car_url
        value7_1 = value7.contents[1]
        data_dict["car_url"] = "https://www.carsensor.net" + value7_1.get("href")
        
        count += 1
        data_list.append(data_dict)
    return data_list

def draw_graph(data_list):
    prices = [item['price'] for item in data_list]
    car_years = [int(item['displacement']) for item in data_list]
    urls = [item['car_url'] for item in data_list]

    fig, ax = plt.subplots()
    scatter = ax.scatter(prices, car_years)
    plt.xlabel('Price')
    plt.ylabel('displacement')
    plt.title('Price vs displacement')

    def on_click(event):
        if event.inaxes == ax:
            cont, ind = scatter.contains(event)
            if cont:
                url = urls[ind['ind'][0]]
                webbrowser.open(url)

    cid = fig.canvas.mpl_connect('button_press_event', on_click)

    plt.show()


def main():
    data_list = []
    # コード実行時はカーセンサー在庫一覧のページURLを指定してください！
    #  例）url = "https://www.carsensor.net/shop/都道府県/000000000/stocklist/"
    url = ""
    
    while True:
        if url.startswith("https://"):
            soup = get_html(url)
            data_list = get_data(soup, data_list)
            time.sleep(3)
            url = get_next_url(soup)
        else:
            break
    print(data_list)
    draw_graph(data_list)
        
if __name__ == '__main__':
    main()