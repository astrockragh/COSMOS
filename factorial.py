import math
import os

import numpy as np
import requests as re
import sklearn
from bs4 import BeautifulSoup

rget = re.get('https://www.chess.com/')


def hello(a):
    print("Hello {}".format(a))


test = "hi"

print("Chess.com has a status code of:")
print(rget.status_code)
name = input("Hey, dude, what's your name? ")
hello(name)
# ban
