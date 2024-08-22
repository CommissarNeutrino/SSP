from typing import Dict
class Paper:
    def __init__(self, data_dict: Dict ={}):
        for key, value in data_dict.items():
            setattr(self, key, value)