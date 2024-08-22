import requests
import time
from easydict import EasyDict as edict
from typing import Dict, Optional, List
from utils.paper import Paper
from utils.func import get_LLM_call_function, LLM_call_functions, semantic_scholar_call

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

    def get_theme_list(self, query: str, LLM_name: str, LLM_settings: Dict[str, str]) -> Optional[List[str]]:
        prompt_request = self.prompt_default.format(query=query)
        call_function = get_LLM_call_function(LLM_name)
        if call_function:
            output = call_function(
                model=LLM_settings[f"{LLM_name}_model"],
                api_key=LLM_settings[f"{LLM_name}_api_key"],
                prompt=prompt_request
                )
            try:
                return output.split("///")
            except Exception as e:
                print("Возникла ошибка в разбиении запроса пользователя на темы")
                print(f"Ответ LLM: {output}")
                print(f"Возникшая ошибка: {e}")
        else:
            print("Возникла ошибка в разбиении запроса пользователя на темы - проблема с вызовом LLM")
    
    def get_list_of_papers(self, query: str, request_attrs: edict, global_settings: Dict[str, str]) -> List[Paper]|str:
        """
        GPT получает на вход запрос пользователя и выдает список ключевых тем поиска - от 1 до 3.
        После идет запрос непосредственно по этим топикам в Semantic Scholar database.
        """
        theme_list = self.get_theme_list(query, global_settings["LLM_name"], global_settings["LLM_settings"])
        list_of_papers = semantic_scholar_call(theme_list, request_attrs, global_settings["Semantic_Scholar_api_key"])
        return list_of_papers
