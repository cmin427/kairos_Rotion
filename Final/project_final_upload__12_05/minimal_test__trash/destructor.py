class Example:
    def __init__(self):
        print("__init__")
        
    def __del__(self):
        print("__del__")

# init
ex = Example()

print("------------")

# del
del ex
