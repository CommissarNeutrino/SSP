from .base_handler import Base_handler
import time
from typing import Union, List, Dict
from easydict import EasyDict as edict
from utils.paper import Paper

class Semantic_Scholar_Handler(Base_handler):
    sleep_time: int = 5

    def __init__(self, **kwargs) -> None:
        super().__init__(request_url="https://api.semanticscholar.org/graph/v1/paper/search", **kwargs)
    
    def semantic_scholar_request(self, user_input):
        content = self.construct_content(user_input)
        while True:
            try:
                return self.request(content)
            except Exception as e:
                print(f"There were a mistake. {e}. Retrying in {self.sleep_time} seconds")
                time.sleep(self.sleep_time)

    def parse_dict_filter_params(self, dict_in_question: Dict, return_dict: Dict = {}, recursion_key: str = '') -> Dict[str, Union[int, str]]:
        """
        Транскрипция параметров из вводного формата в нужный для создания http запроса.
        str-параметр - добавляем str под соответствующем ключом
        int-параметр - добавляем int под соответствующем ключом
        bool-параметр и нулевой уровень рекурсии - добавляем пустую строку под соответствующем ключом
        bool-параметр и ненулевой уровень рекурсии - добавляем название ключа последнего уровня под соответствующем ключом нижнего уровня
        dict-параметр - запускаем функцию на найденном словаре с повышением уровня рекурсии
        """
        for key, item in dict_in_question.items():
            if key == "fields": continue
            if isinstance(item, str) and item != '':
                return_dict[key] = item
            elif isinstance(item, int) and item != 0:
                return_dict[key] = item
            elif isinstance(item, bool) and recursion_key == '' and item:
                return_dict[key] = ""
            elif isinstance(item, bool) and recursion_key != '' and item:
                if return_dict.get(recursion_key):
                    return_dict[recursion_key] += f",{key}"
                else:
                    return_dict[recursion_key] = f"{key}"
            elif isinstance(item, dict):
                return_dict = self.parse_dict_filter_params(item, return_dict, recursion_key=key)
        return return_dict
    
    def parse_dict_fields(self, dict_in_question: Dict, return_string: str = "") -> str:
        """
        Транскрипция параметров из формата dict в строку для создания http запроса.
        Случаи:
        bool-параметр - добавляем его в строку запроса
        dict-параметр - запускаем функцию на найденном словаре
        """
        for key, item in dict_in_question.items():
            if isinstance(item, bool) and item:
                return_string += f"{key},"
            elif isinstance(item, dict):
                return_string = self.parse_dict_fields(item, return_string)
        return return_string

    def form_query_params(self, request_attrs: edict) -> Dict[str, str]:
        """
        Формируем фильтрационные параметры для поиска по датабазе
        """
        fields_dict = request_attrs.fields
        fields_str = self.parse_dict_fields(fields_dict)
        if fields_str[-1] == ",":
            fields_str=fields_str[:-1]
        filter_query_params = self.parse_dict_filter_params(request_attrs)
        base_params = {
            'limit': request_attrs["limit"],
            'fields': fields_str,
        }
        base_params.update(filter_query_params)
        return base_params
    
    def semantic_scholar_request(self, theme_list: List[str], request_attrs: edict, semantic_scholar_api_key: str) -> List[Paper]|str:
        """
        Формируем и отправляем запрос к Semantic Scholar database.
        """
        query_params = self.form_query_params(request_attrs)
        query_params.update({'query': theme_list})
        content = {"params": query_params}
        if semantic_scholar_api_key:
            content["headers"] = {
                'Authorization': semantic_scholar_api_key
            }
        api_answer = self.request(content, retries_number=20, requests_func="get")
        if type(api_answer) != str:
            try:
                return [Paper(data_dict=element) for element in api_answer['data']]
            except KeyError as e:
                print(api_answer)
                print(e)
        else:
            return api_answer