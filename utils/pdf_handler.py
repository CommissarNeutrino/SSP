import requests
import fitz
import os
from typing import List
from RAI.actors.text_summarizer import TextSummarizer
from utils.utils import gpt_call

class PDF_Handler():

    summarizer_prompt = """
Create a concise and comprehensive summary of the provided text, which is an article. The summary should:
* Incorporate main ideas and essential information, eliminating extraneous language and focusing on critical aspects
* Rely strictly on the provided text, without including any external information
* Be formatted in paragraph form for easy understanding * Not include any follow-up text
* Be unified and coherent
* Be around 1000 symbols (characters) long
* Be written in Russian language
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

    def download_pdf(self, url: str, dest_path: str) -> None:
        """
        Скачивает PDF-файлы и сохраняет в систему
        """
        response = requests.get(url)
        response.raise_for_status()
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

    def process_pdf_files(self, urls: List[str], gpt_model: str, summarizer_word_limit: int) -> dict:
        """
        Обрабатывает список URL PDF-файлов и создает их краткое изложение, отправляя каждый из них GPT.
        """
        summaries = {}
        for counter, url in enumerate(urls):
            try:
                pdf_path = f"/tmp/{os.path.basename(url)}"
                self.download_pdf(url, pdf_path)
                text = self.extract_text_from_pdf(pdf_path)
                text_summarizer = TextSummarizer(model=gpt_model, n_words=summarizer_word_limit)
                text_summarizer.prompt = self.summarizer_prompt
                summary = text_summarizer.run(text)
                summaries[counter] = summary
                os.remove(pdf_path)
            except Exception as e:
                summaries[counter] = f"Error processing file: {str(e)}. Broken url: {url}"
        return summaries
    
    def merge_summaries(self, summaries: dict, gpt_model: str, gpt_api_key: str) -> str:
        """Объединяет краткие изложения статей в одно"""
        prompt_base = self.summaries_merger_prompt
        summary_to_prompt = [f"<{key} ARTICLE START>{item['summary']}<{key} ARTICLE END>\n" for key, item in summaries.items()]
        prompt_merge_summaries = prompt_base.format(summary_to_prompt)
        output = gpt_call(gpt_model, gpt_api_key, prompt=prompt_merge_summaries)
        return output

    def main_frame(self, pdf_urls: List[str], gpt_model: str, summarizer_word_limit: int) -> str:
        """
        Парсит pdf-файлы и создает из них одно краткое изложение.
        """
        summaries = self.process_pdf_files(pdf_urls, gpt_model, summarizer_word_limit)
        whole_summary = self.merge_summaries(summaries, gpt_model, summarizer_word_limit)
        return whole_summary