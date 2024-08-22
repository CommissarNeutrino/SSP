import os
from easydict import EasyDict as edict
from utils.paper import Paper
from typing import Tuple, Optional, List, Callable
from utils.api_handler import GPT_Handler, Semantic_Scholar_Handler

def get_pdf_links(list_papers: List[Paper], pdf_amount_needed: int = 5) -> Tuple[List[str], Optional[str]]:
    """
    Ищет в списке статей те, что имеют PDF-флаг со статусом "GOLD". В базе данных Semantic Scholar есть несколько уровней качества pdf, "GOLD" наилучший.
    Получив pdf_amount_needed ссылок на статьи останавливает работу.
    Если было найдено недостаточно статей, вывод сообщение об этом
    """
    dict_pdf_links = {}
    for paper in list_papers:
        if len(dict_pdf_links)>=pdf_amount_needed:
            break
        if paper.isOpenAccess:
            result = paper.openAccessPdf
            if result and result.get('status') == 'GOLD':
                dict_pdf_links[paper] = result.get("url")
    if len(dict_pdf_links)<pdf_amount_needed:
        error_string = f"Полученный список ссылок оказался меньше, чем ожидалось. Нашлось {len(dict_pdf_links)} ссылок. Расширьте список статей, если вам нужно найти больше ссылок."
        return dict_pdf_links, error_string
    return dict_pdf_links, None


def semantic_scholar_call(theme_list: List[str], request_attrs: edict, api_key: str) -> (List[Paper] | str):
    client = Semantic_Scholar_Handler()
    return client.semantic_scholar_request(theme_list, request_attrs, api_key)

def get_LLM_call_function(LLM_name: str) -> Optional[Callable]:
    function_name = next((method for method in dir(LLM_call_functions) if method.startswith(LLM_name)), None)
    if function_name:
        return getattr(LLM_call_functions(), function_name)


class LLM_call_functions():

    def gpt_call(self, model: str, api_key: str, prompt: str) -> Optional[str]:
        client = GPT_Handler(model=model, api_key=api_key)
        return client.gpt_request(prompt)
