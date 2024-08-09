import streamlit as st
import numpy as np
import os
from typing import Tuple, List
from paper_frame import Paper_Frame
from utils.paper import Paper


class Streamlit_Frame():

    """
    TODO: 
    - Анализ полученных статей
    - Возможность генерации суммирования и анализа после генерации списка статей. По всем статьям и по выбранным.
    - Возможность изменять промпт на суммирование статей
    - Возможность изменять промпт на анализ.
    - Возможность использовать другие LLM-api.
    """

    generate_summaries: bool = False
    generate_analyse: bool = False

    def __init__(self) -> None:
        self.pipeline_instance = Paper_Frame()
        self.client_settings = self.pipeline_instance.filter_settings.client_settings

    def main(self) -> None:
        self.page_base()
        self.search_form()

    def page_base(self) -> None:
        st.set_page_config(
            page_title = 'Изучение научных статей',
            page_icon = './assets/media/logo.png',
            layout = 'wide',
        )
        st.title("Банк научных статей")
        search_settings = self.client_settings.paper_search_settings
        with st.sidebar:
            search_settings.gpt_model = st.text_area("Введите GPT-модель", value = 'gpt-4o')
            search_settings.gpt_api_key = st.text_area("Введите ваш GPT_API-ключ", value="")
            if not search_settings.gpt_api_key:
                search_settings.gpt_api_key = os.getenv('OPENAI_API_KEY')
            search_settings.semantic_scholar_api_key = st.text_area("Введите ваш SemScholar_API-ключ", value=None)

    def summaries_form(self) -> None:
        self.generate_summaries = st.checkbox("Получить summaries", value = True)
        with st.popover("Настройка получения summaries"):
            gpt_model = st.text_input("GPT model", value='gpt-4o', key="summarizer_gpt_model_init")
            paper_amount = st.number_input("Какое количество статей хотите суммировать?", value=5, min_value=1, step=1, format='%i')
            word_amount = st.number_input("Какое количество слов должно быть в каждом кратком изложении?", value=1000, min_value=100, step=100, format='%i')
        self.client_settings.summaries_settings.update({
            "gpt_model": gpt_model,
            "paper_amount": paper_amount,
            "word_amount": word_amount,
        })

    def analyse_from(self) -> None:
        self.generate_analyse = st.checkbox("Получить анализ", value = False)
        with st.popover("Настройка анализа поиска"):
            gpt_model = st.text_input("GPT model", value='gpt-4o', key="analyzer_gpt_model_init")
            paper_amount = st.number_input("Какое количество статей хотите проанализировать?", value=5, min_value=1, step=1, format='%i')
            word_amount = st.number_input("Какое количество слов должно быть в анализе?", value=1000, min_value=100, step=100, format='%i')
        self.client_settings.analyse_settings.update({
            "gpt_model": gpt_model,
            "paper_amount": paper_amount,
            "word_amount": word_amount,
        })

    def search_form(self) -> None:
        with st.form("Запрос"):
            col1, col2 = st.columns(2)
            with col1:
                query = st.text_area("Введите ваш запрос")
                self.filter_proccessing()
            with col2:
                self.summaries_form()
                self.analyse_from()
            search_start = st.form_submit_button("Начать поиск")
        if search_start:
            self.query_proccessing(query)

    def query_proccessing(self, query: str) -> None:
        papers_list, summary = self.get_data(query)
        if self.generate_analyse: self.analyze_creation(papers_list)
        if self.generate_summaries: self.summary_creation(summary)
        self.papers_list_creation(papers_list)

    def get_data(self, query: str) -> Tuple[List[Paper], str]:
        papers_list = self.pipeline_instance.get_papers(query)
        if type(papers_list) == str:
            st.write(papers_list)
            st.stop()
        summary, summaries_search_error = self.pipeline_instance.get_summaries(papers_list)
        if summaries_search_error:
            st.write(summaries_search_error)
        return papers_list, summary

    def papers_list_creation(self, papers_list: List[Paper]) -> None:
        for paper in papers_list:
            with st.container(border=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(paper.title)
                    st.write(f"Год: {paper.year}")
                    st.write(f"Количество цитирований: {paper.citationCount}")
                    if paper.externalIds.get("DOI") != None:
                        st.write(f"DOI: {paper.externalIds['DOI']}")
                    if paper.isOpenAccess and paper.openAccessPdf != None:
                        st.link_button("Открыть PDF", paper.openAccessPdf["url"])
                        st.write(paper.openAccessPdf["url"])                            
                    st.write((',').join([author["name"] for author in paper.authors]))
                with col2:
                    if getattr(paper, "tldr", False) and paper.tldr.get("text") != None:
                        st.write(paper.tldr["text"])
                    else:
                        st.write("Краткое описание статьи недоступно")

    def filter_proccessing(self) -> None:
        with st.popover("Фильтр"):
            st.write("Задать настройки поиска")
            pdf_available_flag = st.toggle("Имеется PDF")
            paper_limit = st.number_input("Количество статей", value=100, min_value=0, max_value=1000, step=1, format="%d")
            publication_start, publication_end = st.select_slider(
                "Выберите временной диапазон поиска",
                options=np.arange(1970, 2025),
                value=(1970, 2024))
            minCitationCount = st.number_input("Минимальное количество цитирований", min_value=0, step=1, format="%d")
            self.pipeline_instance.filter_settings["request_fields_settings"].update({}) 
            self.pipeline_instance.filter_settings["request_non_fields_settings"].update({
                "year": f"{publication_start}-{publication_end}",
                "minCitationCount": minCitationCount,
                "openAccessPdf": pdf_available_flag,
                "limit": paper_limit,
            })

    def summary_creation(self, summary: str) -> None:
        with st.container(border=True):
            st.write(summary)    

    def analyze_creation(self, papers: List[Paper]) -> None:
        with st.container(border=True):
            st.write("Раздел в разработке")

if __name__ == '__main__':
    Streamlit_Frame().main()