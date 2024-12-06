import os

def create_file_if_not_exists(file_path):
    """
    지정된 파일이 없으면 새로 생성하는 함수

    Args:
        file_path (str): 생성할 파일의 경로

    Returns:
        None
    """

    if not os.path.exists(file_path):
        with open(file_path, 'w') as f:
            # 파일 생성 후 필요한 초기화 작업 (선택 사항)
            pass  # 여기에 파일 생성 후 실행할 코드를 작성

# 파일 생성
file_path = "my_file.txt"
create_file_if_not_exists(file_path)