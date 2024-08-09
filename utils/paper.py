class Paper:
    def __init__(self, data_dict=None, **kwargs):
        if data_dict != None:
            for key, value in data_dict.items():
                setattr(self, key, value)
        else:
            self.title = kwargs.get('title')
            self.authors = kwargs.get('authors')
            self.journal = kwargs.get('journal')
            self.year = kwargs.get('year')
            self.url = kwargs.get('url')
            self.paper_id = kwargs.get('paperId')
            self.open_access = kwargs.get('isOpenAccess')
        self.mark = None