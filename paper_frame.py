from easydict import EasyDict as edict
from typing import List, Tuple, Dict
from Relevance_search import Paper_Relevance_search
from utils.paper import Paper
from utils.summary_handler import Summary_Handler
from utils.func import get_pdf_links

class Paper_Frame():
    
    # request_attrs - Доступные настройки запроса в Semantic Scholar 
    request_attrs: edict = edict({
        "fields": {
            "paperId": True, #Always included. A unique (string) identifier for this paper
            "corpusId": False, #A second unique (numeric) identifier for this paper
            "url": False, #URL on the Semantic Scholar website
            "title": False, #Included if no fields are specified
            "venue": False, #Normalized venue name
            "publicationVenue": False, #Publication venue meta-data for the paper
            "year": False, #Year of publication
            "authors": False, #Up to 500 will be returned. Will include: authorId & name
            "externalIdsIDs": False, #from external sources #Supports ArXiv, MAG, ACL, PubMed, Medline, PubMedCentral, DBLP, DOI
            "abstract": False, #The paper's abstract. Note that due to legal reasons, this may be missing even if we display an abstract on the website
            "referenceCount": False, #Total number of papers referenced by this paper
            "citationCount": False, #Total number of citations S2 has found for this paper
            "influentialCitationCount": False, #More information here
            "isOpenAccess": False, #More information here
            "openAccessPdf": False, #A link to the paper if it is open access, and we have a direct link to the pdf
            "fieldsOfStudy": False, #A list of high-level academic categories from external sources
            "s2FieldsOfStudy": False, #A list of academic categories, sourced from either external sources or our internally developed classifier
            "publicationTypes": False, #Journal Article, Conference, Review, etc
            "publicationDate": False, #YYYY-MM-DD, if available
            "journal": False, #Journal name, volume, and pages, if available
            "citationStyles": False, #Generates bibliographical citation of paper. Currently supported styles: BibTeX
            "embedding": {
                "embedding.specter_v1": False,
                "embedding.specter_v2": False,
            }, #Vector embedding of paper content. Use an optional suffix to specify the model version:
            "tldr": False, #Auto-generated short summary of the paper from the SciTLDR model
            "authors_specific": {
                "authorId": False, #S2 unique ID for this author
                "externalIds": False, #ORCID/DBLP IDs for this author, if known
                "url": False, #URL on the Semantic Scholar website
                "name": False, #Author's name to users. WARNING: this list may be out of date or contain deadnames of authors who have changed their name. (see https://en.wikipedia.org/wiki/Deadnaming)
                "affiliations": False, #Author's affiliations #sourced from claimed authors who have set affiliation on their S2 author page.
                "homepage": False, #Author's homepage
                "paperCount": False, #Author's total publications count
                "citationCount": False, #Author's total citations count
                "hIndex": False, #See the S2 FAQ on h-index            
            }, #Up to 500 will be returned
            "citations": {
                "paperId": False, #Always included. A unique (string) identifier for this paper
                "corpusId": False, #A second unique (numeric) identifier for this paper
                "url": False, #URL on the Semantic Scholar website
                "title": False, #Included if no fields are specified
                "venue": False, #Normalized venue name
                "publicationVenue": False, #Publication venue meta-data for the paper
                "year": False, #Year of publication
                "authors": False, #Up to 500 will be returned. Will include: authorId & name
                "externalIdsIDs": False, #from external sources #Supports ArXiv, MAG, ACL, PubMed, Medline, PubMedCentral, DBLP, DOI
                "abstract": False, #The paper's abstract. Note that due to legal reasons, this may be missing even if we display an abstract on the website
                "referenceCount": False, #Total number of papers referenced by this paper
                "citationCount": False, #Total number of citations S2 has found for this paper
                "influentialCitationCount": False, #More information here
                "isOpenAccess": False, #More information here
                "openAccessPdf": False, #A link to the paper if it is open access, and we have a direct link to the pdf
                "fieldsOfStudy": False, #A list of high-level academic categories from external sources
                "s2FieldsOfStudy": False, #A list of academic categories, sourced from either external sources or our internally developed classifier
                "publicationTypes": False, #Journal Article, Conference, Review, etc
                "publicationDate": False, #YYYY-MM-DD, if available
                "journal": False, #Journal name, volume, and pages, if available
                "citationStyles": False, #Generates bibliographical citation of paper. Currently supported styles: BibTeX
            }, #Up to 1000 will be returned
            "references": {
                "paperId": False, #Always included. A unique (string) identifier for this paper
                "corpusId": False, #A second unique (numeric) identifier for this paper
                "url": False, #URL on the Semantic Scholar website
                "title": False, #Included if no fields are specified
                "venue": False, #Normalized venue name
                "publicationVenue": False, #Publication venue meta-data for the paper
                "year": False, #Year of publication
                "authors": False, #Up to 500 will be returned. Will include: authorId & name
                "externalIdsIDs": False, #from external sources #Supports ArXiv, MAG, ACL, PubMed, Medline, PubMedCentral, DBLP, DOI
                "abstract": False, #The paper's abstract. Note that due to legal reasons, this may be missing even if we display an abstract on the website
                "referenceCount": False, #Total number of papers referenced by this paper
                "citationCount": False, #Total number of citations S2 has found for this paper
                "influentialCitationCount": False, #More information here
                "isOpenAccess": False, #More information here
                "openAccessPdf": False, #A link to the paper if it is open access, and we have a direct link to the pdf
                "fieldsOfStudy": False, #A list of high-level academic categories from external sources
                "s2FieldsOfStudy": False, #A list of academic categories, sourced from either external sources or our internally developed classifier
                "publicationTypes": False, #Journal Article, Conference, Review, etc
                "publicationDate": False, #YYYY-MM-DD, if available
                "journal": False, #Journal name, volume, and pages, if available
                "citationStyles": False, #Generates bibliographical citation of paper. Currently supported styles: BibTeX
            }, #Up to 1000 will be returned
        },
        "publicationTypes": {
            'Review': False,
            'JournalArticle': False,
            'CaseReport': False,
            'ClinicalTrial': False,
            'Dataset': False,
            'Editorial': False,
            'LettersAndComments': False,
            'MetaAnalysis': False,
            'News': False,
            'Study': False,
            'Book': False,
            'BookSection': False,
        }, #Use a comma-separated list to include papers with more than one publication types. Example: Review,JournalArticle will return papers with publication types Review and JournalArticle.
        "fieldsOfStudy": {
            'Computer Science': False,
            'Medicine': False,
            'Chemistry': False,
            'Biology': False,
            'Materials Science': False,
            'Physics': False,
            'Geology': False,
            'Psychology': False,
            'Art': False,
            'History': False,
            'Geography': False,
            'Sociology': False,
            'Business': False,
            'Political Science': False,
            'Economics': False,
            'Philosophy': False,
            'Mathematics': False,
            'Engineering': False,
            'Environmental Science': False,
            'Agricultural and Food Sciences': False,
            'Education': False,
            'Law': False,
            'Linguistics': False,
        }, #Restrict results to given field-of-study, using the s2FieldsOfStudy paper field.
        # Use a comma-separated list to include papers from any of the listed fields
        # Example: Physics,Mathematics will return papers with either Physics or
        # Mathematics in their list of fields-of-study.
        "publicationDateOrYear": '', # Restrict results to the given range of publication dates or years (inclusive). Accepts the format <startDate>:<endDate>. Each term is optional, allowing for specific dates, fixed ranges, or open-ended ranges. In addition, prefixes are suported as a shorthand, e.g. 2020-06 matches all dates in June 2020. Specific dates are not known for all papers, so some records returned with this filter will have a null value for publicationDate. year, however, will always be present. For records where a specific publication date is not known, they will be treated as if published on January 1st of their publication year.
        # Examples:
        # 2016-03-05:2020-06-06 as early as March 5th, 2016 or as late as June 6th, 2020
        # 1981-08-25: on or after August 25th, 1981
        # :2015-01 before or on January 31st, 2015
        # 2015:2020 between January 1st, 2015 and December 31st, 2020
        "year": '', #Restrict results to the given range of publication year (inclusive)
        # Examples:
        # 2019 in 2019
        # 2016-2020 as early as 2016 or as late as 2020
        # 2010- during or after 2010
        # -2015 before or during 2015
        "venue": '', #Restrict results by venue.
        # Input could also be an ISO4 abbreviation. Examples include:
        # Nature
        # New England Journal of Medicine
        # Radiology
        # N. Engl. J. Med.
        # Use a comma-separated list to include papers from more than one venue.
        # Example: Nature,Radiology will return papers from venues Nature and Radiology.
        "openAccessPdf": False, #Restrict results to only include papers with a public PDF
        "minCitationCount": 0, #Restrict results to only include papers with the minimum number of citations, inclusive.
        "offset": 0, #Default: 0. When returning a list of results, start with the element at this position in the list.
        "limit": 100, #Default: 100 The maximum number of results to return. Must be <= 100
    })

    # Базовые настройки запроса в Sematic Scholar
    default_filter_settings: edict = edict({
        "request_fields_settings": {
            "title": True,
            "year": True,
            "citationCount": True,
            "externalIds": True,
            "isOpenAccess": True,
            "openAccessPdf": True,
            "authors": True,
            "tldr": True,
            "abstract": True,
        },
        "request_non_fields_settings": {},
    })
    
    def get_papers(self, query: str, filter_settings: Dict[str, str|int], global_settings: Dict[str, str]) -> List[Paper]|str:
        """
        Получение статей из базы данных Semantic Scholar.
        query - запрос пользователя
        filter_settings - фильтры, установленные пользователем
        request_fields_settings - настройки для "fields" в request_attrs
        request_non_fields_settings - настройки для остальных ключей в request_attrs
        """
        self.default_filter_settings["request_fields_settings"].update(filter_settings["request_fields_settings"])
        self.default_filter_settings["request_non_fields_settings"].update(filter_settings["request_non_fields_settings"])
        self.request_attrs.fields.update(self.default_filter_settings["request_fields_settings"])
        self.request_attrs.update(self.default_filter_settings["request_non_fields_settings"])
        return Paper_Relevance_search().get_list_of_papers(query, self.request_attrs, global_settings)

    def get_summaries(self, papers_list: List[Paper], summaries_settings: Dict[str, str|int], global_settings: Dict[str, str]) -> Tuple[str, str]:
        """
        Статьи, получаемые из базы данных Semantic Scholar опционально имеют ссылки на pdf-версии
        Мы получаем заданное пользователем число этих ссылок и обрабатываем документы, на них находящиеся.
        В дальнейшем происходит суммирование этих статей и последующее объединение их в одно краткое изложение
        """
        dict_pdf_links, error = get_pdf_links(papers_list, summaries_settings["paper_amount"])
        summary = Summary_Handler().main_frame(list(dict_pdf_links.values()),
                                               summaries_settings["word_amount"],
                                               global_settings
                                            )
        return summary, error