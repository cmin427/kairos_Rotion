import msvcrt

while True:
    order_list=[]

    while True:
        str=input("order:")
        print(str)
        if str=='q':
            print(order_list)
            break
            
        else:
            str_sp=str.split()
            order_list.append(str_sp)
        