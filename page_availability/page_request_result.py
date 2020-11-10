

class PageRequestResult:
    def __init__(self, url, status=0, text_regex = None, text_matched=None, request_time=None, request_duration=0., error=None):
        self.url = url
        self.status = status
        self.text_regex = text_regex
        self.text_matched = text_matched
        self.request_time = request_time
        self.request_duration = request_duration
        self.error = error
