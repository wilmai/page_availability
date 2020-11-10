import json
import datetime
from .page_request_result import PageRequestResult


def page_request_result_to_json(request: PageRequestResult) -> str:
    def date_converter(o):
        if isinstance(o, datetime.datetime):
            return o.timestamp()
    return json.dumps(request.__dict__, default=date_converter)


def json_to_page_request_result(js: str) -> PageRequestResult:
    load = json.loads(js)
    request_time = datetime.datetime.fromtimestamp(load['request_time'], tz=datetime.timezone.utc)
    return PageRequestResult(
        url=load['url'],
        status=load['status'],
        text_regex=load['text_regex'],
        text_matched=load['text_matched'],
        request_time=request_time,
        request_duration=load['request_duration'],
        error=load['error']
        )
