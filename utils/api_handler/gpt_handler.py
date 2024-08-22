from .base_handler import Base_handler
from typing import Optional, Dict, Literal, List, Any
import tiktoken

class GPT_Handler(Base_handler):
    model: str
    sleep_time: int = 5
    api_key: str
    response_format_type: Optional[Dict[str, Literal["json_object", "json_lines", "text"]]]
    """
    Для того, чтобы добавить к запросу GPT указание типа данных, которые он должен вернуть, укажите словарь response_format_type. На момент написание кода он может принимать три формата:
    - {'type': 'text'}
    - {'type': 'json_object'}
    - {'type': 'json_lines'}
    """

    def __init__(self, **kwargs) -> None:
        super().__init__(request_url="https://api.openai.com/v1/chat/completions", **kwargs)

    def construct_content(self, user_input: str) -> Dict[str, Dict[str, Any]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        content = {
            "json": {
                "model": self.model,
                "messages": [{"role": "user", "content": user_input}],
                # "response_format": self.response_format_type,
            },
            "headers": headers
        }
        return content
    
    def deconstruct_gpt_answer(self, gpt_answer: Dict) -> Optional[str]:
        try:
            return gpt_answer['choices'][0]['message']['content']
        except Exception as e:
            print("Возникла ошибка в деконструкции ответа GPT")
            print(f"Ответ: {gpt_answer}")
            print(f"Ошибка: {e}")
    
    def gpt_request(self, user_input) -> Optional[str]:
        content = self.construct_content(user_input)
        gpt_answer = self.request(content)
        if not isinstance(gpt_answer, str):
            return self.deconstruct_gpt_answer(gpt_answer)
        else:
            return gpt_answer
        
class GPT_Summarizer(GPT_Handler):

    model_limits = {
        "gpt-4o": 128000,
        "gpt-4o-2024-05-13": 128000,
        "gpt-4o-2024-08-06": 128000,
        "chatgpt-4o-latest": 128000,
        "gpt-4o-mini": 128000,
        "gpt-4o-mini-2024-07-18": 128000,
        "gpt-4-turbo": 128000,
        "gpt-4-turbo-2024-04-09": 128000,
        "gpt-4-turbo-preview": 128000,
        "gpt-4-0125-preview": 128000,
        "gpt-4-1106-preview": 128000,
        "gpt-4": 8192,
        "gpt-4-0613": 8192,
        "gpt-4-0314": 8192,
        "gpt-3.5-turbo-0125": 16385,
        "gpt-3.5-turbo": 16385,
        "gpt-3.5-turbo-1106": 16385,
        "gpt-3.5-turbo-instruct": 4096,
    }

    def __init__(self, base_prompt: str, summarizer_word_limit: int, **kwargs) -> None:
        super().__init__(**kwargs)
        self.base_prompt = base_prompt
        self.summarizer_word_limit = summarizer_word_limit
    
    def count_tokens(self, text: str) -> int:
        tokens = tiktoken.encoding_for_model(self.model).encode(text)
        return len(tokens)

    def summarize(self, user_input: str) -> str:
        self.token_limit = self.model_limits[self.model]
        if self.count_tokens(user_input) > self.token_limit:
            return self.summarize_large_text(user_input)
        prompt = self.base_prompt.format(self.summarizer_word_limit, user_input)
        return self.gpt_request(prompt)

    def split_text(self, text: str) -> List[str]:
        words = text.split()
        chunks = []
        current_chunk = []
        current_tokens = 0
        for word in words:
            word_tokens = self.count_tokens(word)
            if current_tokens + word_tokens > self.token_limit:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            current_chunk.append(word)
            current_tokens += word_tokens
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        return chunks

    def summarize_large_text(self, text: str) -> str:
        chunks = self.split_text(text)
        summaries = []
        for chunk in chunks:
            prompt = self.base_prompt.format(self.summarizer_word_limit, chunk)
            summary = self.gpt_request(prompt)
            summaries.append(summary)
        final_summary = " ".join(summaries)
        return final_summary