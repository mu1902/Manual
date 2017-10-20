try:
    file_object = open('stock.txt', mode='r', encoding='UTF-8')
    stocks = file_object.readlines()
finally:
    file_object.close()

for stock in stocks:
    print(stock)