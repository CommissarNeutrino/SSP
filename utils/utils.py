from utils.paper import Paper
from typing import Tuple, Optional, List
from RAI import QAGPT

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
    return dict_pdf_links

def gpt_call(gpt_model: str, gpt_api_key: str, prompt: str) -> Optional[str]:
    client = QAGPT(model=gpt_model, key=gpt_api_key)
    gpt_request = client.form_message(prompt)
    output = client.ask([gpt_request])
    try:
        return output
    except Exception as e:
        print(e)
        print(output)