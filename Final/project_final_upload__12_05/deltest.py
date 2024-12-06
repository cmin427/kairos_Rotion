class MyClass:
    def __init__(self, name):
        self.name = name
        print(f"객체 '{self.name}'가 생성되었습니다.")

    def __del__(self):
        print(f"객체 '{self.name}'가 삭제됩니다.")

# 객체 생성
obj = MyClass("TestObject")

# 명시적으로 객체 삭제
del obj
