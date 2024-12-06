import threading

def math(thname,v):
    sum=0
    
    for i in range(0,v):
        sum+=i
        print(thname," ",sum)
        
th1=threading.Thread(target=math,args=("스래드1",10))
th2=threading.Thread(target=math,args=("스레드2",10))

th1.daemon=True