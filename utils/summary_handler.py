import requests
import fitz
import os
from typing import List, Dict
from utils.api_handler import GPT_Summarizer
from utils.func import get_LLM_call_function


class Summary_Handler():

    """
    TODO: Убрать RAI.TextSummarizer в process_pdf_files (DONE) 
    + Добавить обработку нижних рангов PDF от Semantic Scholar
    """

    summarizer_prompt = """
Create a concise and comprehensive summary of the provided text, which is an article. The summary should:
* Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects
* Rely strictly on the provided text, without including any external information
* Be formatted in paragraph form for easy understanding 
* Not include any follow-up text
* Be unified and coherent
* Be around {} symbols (characters) long
* Be written in Russian language
>>> Text:
{}
"""

    summaries_merger_prompt = """
Create a concise and comprehensive article, based of the provided texts, which are summaries of articles. Your article should:
* Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects
* Rely strictly on the provided text, without including any external information
* Be formatted in paragraph form for easy understanding * Not include any follow-up text
* Be unified and coherent.
* Do not say about provided texts
* Be around 1000 symbols (characters) long
* Be written in Russian language
>>> Texts to summarize:
{}
"""

    def create_summary(self, query: str, LLM_name: str, LLM_settings: Dict[str, str]) -> str:
        prompt_request = self.summaries_merger_prompt.format(query)
        call_function = get_LLM_call_function(LLM_name)
        if call_function:
            output = call_function(model=LLM_settings[f"{LLM_name}_model"], api_key=LLM_settings[f"{LLM_name}_api_key"], prompt=prompt_request)
            return output
        else:
            print("Возникла ошибка в разбиении запроса пользователя на темы - проблема с вызовом LLM")

    def download_pdf(self, url: str, dest_path: str) -> None:
        """
        TODO: Добавить raise_for_status-механику
        Скачивает PDF-файлы и сохраняет в систему
        """
        response = requests.get(url)
        with open(dest_path, 'wb') as f:
            f.write(response.content)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Получает текст из pdf-файла
        """
        document = fitz.open(pdf_path)
        text = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text()
        return text

    def process_pdf_files(self, urls: List[str], summarizer_word_limit: int, global_settings: Dict[str, str]) -> dict:
        """
        Обрабатывает список URL PDF-файлов и создает их краткое изложение, отправляя каждый из них GPT.
        """
        summaries = {}
        for counter, url in enumerate(urls):
            try:
                pdf_path = f"/tmp/{counter}.pdf"
                self.download_pdf(url, pdf_path)
                text = self.extract_text_from_pdf(pdf_path)
                # summaries[counter] = f"Error processing file: {str(e)}. Broken url: {url}"
                summarizer = GPT_Summarizer(base_prompt=self.summarizer_prompt,
                                        summarizer_word_limit=summarizer_word_limit,
                                        model=global_settings["LLM_settings"][f"{global_settings['LLM_name']}_model"],
                                        api_key=global_settings["LLM_settings"][f"{global_settings['LLM_name']}_api_key"]
                                    )
                summary = summarizer.summarize(text)
                # summaries[counter] = f"Error processing file: {str(e)}. Broken url: {url}"
                summaries[counter] = summary
                os.remove(pdf_path)
            except requests.exceptions.ConnectionError as e:
                print("Trouble with pdf download")
                print(f"Error: {e}")
                continue
            except fitz.FileDataError as e:
                print("Trouble with pdf opening")
                print(f"Error: {e}")
                continue

        return summaries
    
    def merge_summaries(self, summaries: dict, global_settings: Dict[str, str]) -> str:
        """Объединяет краткие изложения статей в одно"""
        prompt_base = self.summaries_merger_prompt
        summary_to_prompt = [f"<{key} ARTICLE START>{item}<{key} ARTICLE END>\n" for key, item in summaries.items()]
        prompt_merge_summaries = prompt_base.format(summary_to_prompt)
        output = self.create_summary(prompt_merge_summaries, global_settings["LLM_name"], global_settings["LLM_settings"])
        return output

    def main_frame(self, pdf_urls: List[str], summarizer_word_limit: int, global_settings: Dict[str, str]) -> str:
        """
        Парсит pdf-файлы и создает из них одно краткое изложение.
        """
        summaries = self.process_pdf_files(pdf_urls, summarizer_word_limit, global_settings)
        whole_summary = self.merge_summaries(summaries, global_settings)
        return whole_summary