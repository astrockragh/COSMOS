import sys

ex=sys.version 

def greet(who):
    greeting='Eyo {}, my python version is {}, and Carole Baskin killed her Husband'.format(who, ex)
    print(greeting)

greet('Mads')