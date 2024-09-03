from bs4 import BeautifulSoup
from urllib import request
import requests
import time

def scrape_pages(base_url, starting_page, ending_page):
    product_list = []
    for page_num in range(starting_page,(ending_page+1)):
        url = base_url.format(page_num)
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            items = soup.find_all('article', attrs={'class':'prd _fb col c-prd'})
            print('Page scraped successfully!')
            for item in items:
                item_name = item.find('h3').text
                current_price = item.find('div', attrs={'class': 'prc'}).text
                old_price_element = item.find('div', attrs={'class' : 'old'})
                discount_element = item.find('div', attrs={'class' : 'bdg _dsct _sm'})
                link = item.find('a', attrs={'class':'core'}).get('href')
                old_price =None
                discount =None
                # only appending products with discount
                if discount_element:
                    old_price = old_price_element.text
                    discount = discount_element.text
                    product_list.append((item_name,current_price,old_price,discount,link))
            print(f'{len(items)} items were scraped!')
        else:
            print('Failed to retrieve page')
        print(f'Page {page_num} scraped successfully!')
        time.sleep(5)
    return product_list

# base_url= 'https://www.jumia.co.ke/all-products/?page={}#catalog-listing'
# starting_page =1
# ending_page = 5
# scrape_pages(base_url,starting_page,ending_page)