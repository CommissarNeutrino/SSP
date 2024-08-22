import requests
import time
from typing import Dict, Any, Literal

class Base_handler():

    def __init__(self, request_url: str, **kwargs):
        self.request_url=request_url
        for key, value in kwargs.items():
            setattr(self, key, value)

    def request(self, content: Dict[str, Any], retries_number: int = 10, sleeping_time: int = 5, requests_func: Literal["post", "get"] = "post") -> Dict|str:
        """
        Отправляет запрос на указанный url
        """
        for i in range(retries_number):
            try:
                method = getattr(requests, requests_func)
                response = method(self.request_url, **content)
                if response.status_code == 200:
                    data = response.json()
                    return data
                elif response.status_code == 429:
                    print(f"Rate limit exceeded. Retrying after {sleeping_time} seconds...")
                    time.sleep(sleeping_time)
                    continue
                else:
                    return f"Непредвиденная ошибка при выполнении запроса ({response.status_code}): {response.raise_for_status()}.\nБыл получен ответ {response.json()}"
            except Exception as e:
                print(f"There were a mistake. {e}. Retrying in {sleeping_time} seconds")
                time.sleep(sleeping_time)
