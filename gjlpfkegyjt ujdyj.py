print(dir())

import functions
from data import my_dict
from classes import *


print('this is main file')
new: int = 15
if __name__ == '__main__':
    print('this code doesnt work if this file will be imported as new file')
    print(functions.get_db_num(120))
    print(my_dict)
    MyClass()
    print(dir())
