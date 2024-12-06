class MyClass:
    # 허용된 값의 집합
    ALLOWED_VALUES = {"apple", "banana", "cherry"}

    def __init__(self):
        self._value = None  # 내부 변수
        self.value = "apple"  # 초기값 설정 시 유효성 검사

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if new_value not in MyClass.ALLOWED_VALUES:
            raise ValueError(f"{new_value} is not an allowed value. Allowed values are: {MyClass.ALLOWED_VALUES}")
        self._value = new_value

    def sosadankj(self):
        self.value="asd"

# 사용 예제
try:
    obj = MyClass()
    print(obj.value)  # "apple"
    obj.sosadankj()   # "asd is not an allowed value. Allowed values are: {'cherry', 'banana', 'apple'}""
except ValueError as e:
    print(e)