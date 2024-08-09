import requests
import time
from easydict import EasyDict as edict
from typing import Union, Optional, List
from utils.paper import Paper
from utils.utils import gpt_call

class Paper_Relevance_search():
    """
    TODO: обработчик ошибок при запросе к GPT
    """

    prompt_default = """
You are a professional assistant for searching scientific articles in a database. You receive a user's query, your task is to select topics from it, which will be searched semantically in the database. Remember - you must return only the list of topics that will be searched. Maximum of three topics. Answer only in English.

>>> Examples:
[
[
'User Query': 'I'm researching the impact of climate change on marine biodiversity, particularly focusing on coral reefs and the migration patterns of fish species.',
'Output': 'Impact of climate change on marine biodiversity///Coral reefs and climate change///Migration patterns of fish species and climate change'
],
[
'User Query': 'Can you find studies on the effectiveness of mindfulness meditation in reducing anxiety and improving sleep quality in adults?'
'Output': 'Effectiveness of mindfulness meditation in reducing anxiety///Mindfulness meditation and sleep quality improvement///Mindfulness meditation in adults'
],
[
'User Query': 'I'm looking for research on the use of machine learning algorithms in healthcare, specifically for early diagnosis of diseases and personalized treatment plans.',
'Output': 'Machine learning algorithms in healthcare///Early diagnosis of diseases using machine learning///Personalized treatment plans using machine learning'
]
]
>>> Real user query:
{query}
"""

    def __init__(self, gpt_model: str = "", gpt_api_key: str = "", semantic_scholar_api_key: str = None):
        self.gpt_model = gpt_model
        self.gpt_api_key = gpt_api_key
        self.semantic_scholar_api_key = semantic_scholar_api_key

    def get_theme_list(self, query: str) -> Optional[List[str]]:
        prompt_request = self.prompt_default.format(query=query)
        output = gpt_call(self.gpt_model, self.gpt_api_key, prompt=prompt_request)
        try:
            return output.split("///")
        except Exception as e:
            print(e, output)
        
    def parse_dict_filter_params(self, dict_in_question: dict, return_dict: dict = {}, recursion_key: str = '') -> dict[str, Union[int, str]]:
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
    
    def parse_dict_fields(self, dict_in_question: dict, return_string: str = "") -> str:
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

    def form_query_params(self, request_attrs: edict) -> dict[str, str]:
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
    
    def request_to_semantic_scholar(self, theme_list: List[str], request_attrs: edict, max_retries: int = 10, sleeping_time: int = 5) -> List[Paper]|str:
        """
        Формируем и отправляем запрос к Semantic Scholar database.
        """
        base_url = 'https://api.semanticscholar.org/graph/v1/paper/search'
        query_params = self.form_query_params(request_attrs)
        query_params.update({'query': theme_list})
        if self.semantic_scholar_api_key:
            headers = {
                'Authorization': self.semantic_scholar_api_key
            }
        else:
            headers = None
        for i in range(max_retries):
            response = requests.get(base_url, params=query_params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                list_papers = [Paper(data_dict=element) for element in data['data']]
                return list_papers
            elif response.status_code == 429:
                print(f"Rate limit exceeded. Retrying after {sleeping_time} seconds...")
                time.sleep(sleeping_time)
                continue
            else:
                return f"Ошибка при выполнении запроса: {response.raise_for_status()}.\nБыл получен ответ {response.json()}"
    
    def get_list_of_papers(self, query: str, request_attrs: edict) -> List[Paper]|str:
        """
        GPT получает на вход запрос пользователя и выдает список ключевых тем поиска - от 1 до 3.
        После идет запрос непосредственно по этим топикам в Semantic Scholar database.
        """
        theme_list = self.get_theme_list(query)
        list_of_papers = self.request_to_semantic_scholar(theme_list, request_attrs)
        return list_of_papers
