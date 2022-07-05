#!/usr/bin/python

import requests
import math
import json
from string import digits, ascii_lowercase
from threading import Thread
from bs4 import BeautifulSoup

CRYPTO_URL = "https://crypto.com/price"
table_info = []
threads = []

def progress_bar(current, total, bar_length=20):
  fraction = current / total
  arrow = int(fraction * bar_length - 1) * "=" + ">"
  padding = int(bar_length - len(arrow)) * " "
  ending = "\n" if current == total else "\r"

  print(f"Progress: [{arrow}{padding}] {int(fraction*100)}%", end=ending)

def get_table(start_page, end_page, thread_number):
  for n in range(start_page, end_page):
    page = requests.get(f"{CRYPTO_URL}?page={n}")
    soup = BeautifulSoup(page.content, "html.parser")
    table = soup.find(role="table").text.split()
    if thread_number + 1 == len(threads):
      progress_bar(n, num_of_pages)
    seen = set()
    for item in table:
      if len(item) > 20 and item not in seen:
        seen.add(item)
        item = item.replace("N/A", "")
        item = item.replace("Trade", "")
        splitted_info = item.split("$")
        token_name = splitted_info[0]
        remove_digits = str.maketrans("", "", digits)
        remove_lowercase = str.maketrans("", "", ascii_lowercase)
        if token_name[0] == "B" and token_name[1].isdigit:
          token_name = "".join(token_name[1:])  
        token_name = "".join(token_name).translate(remove_digits).translate(remove_lowercase)
        token_name = "".join(token_name[1:])
        price = splitted_info[1]
        percents = splitted_info[2].split("%")
        percents = percents[0]
        percents = "".join(percents)
        percents = percents.replace(price, "")
        token_obj = {
          "token_name": token_name, 
          "price": price,
          "percent_change": percents 
        }    
        table_info.append(token_obj)
      progress_bar(n, end_page)

def get_last_page():
  page = requests.get(CRYPTO_URL)
  print(page)
  soup = BeautifulSoup(page.content, "html.parser")
  button = soup.find_all("button")
  last_page = button[-2].text
  
  return int(last_page)

def dump_to_file(table_info):
  dump = json.dumps(table_info, indent=2, sort_keys=True)
  f = open("token-info.json", "w")
  f.write(dump)
  f.close()
  print("file written")

def filter_table(table_info):
  seen = set()
  new_table = []
  for token in table_info:
    t = tuple(token.items())
    if t not in seen:
        seen.add(t)
        new_table.append(token)
  return new_table

def create_threads():
  num_of_threads = math.ceil(num_of_pages / 50)
  num_of_coins = math.ceil(50 * num_of_pages)
  num_of_coins_for_thread = math.ceil(num_of_coins / num_of_threads)
  num_of_pages_for_thread = math.ceil(num_of_coins_for_thread * 1 / 50)
  start_page = 0
  end_page = num_of_pages_for_thread
  
  print(f"num of pages: {num_of_pages}")
  print(f"num of threads: {num_of_threads}")
  print(f"num of coins: {num_of_coins}")
  print(f"num of coins for thread: {num_of_coins_for_thread}")
  print(f"num of pages for thread: {num_of_pages_for_thread}")
  
  for n in range(0, num_of_threads):
    thread = Thread(target=get_table, args=(start_page, end_page, n))
    threads.append(thread)
    thread.start()
    start_page = end_page
    end_page = end_page + num_of_pages_for_thread

  for thread in threads:
    thread.join()
    
  filtered_table_info = filter_table(table_info)
  print(filtered_table_info)
  dump_to_file(filtered_table_info)
    
num_of_pages = get_last_page()
create_threads()

