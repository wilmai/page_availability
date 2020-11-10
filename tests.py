import datetime

from page_availability.conversions import page_request_result_to_json, json_to_page_request_result
from page_availability.page_request_result import PageRequestResult


def test_conversions():
    # result -> json
    request_time = datetime.datetime.fromtimestamp(0.5, tz=datetime.timezone.utc)
    result = PageRequestResult(
        url="www.google.com",
        status=200,
        text_regex="foo",
        text_matched=True,
        request_time=request_time,
        request_duration=0.5,
        error="testing"
        )
    jsonstr = page_request_result_to_json(result)
    expected = '{"url": "www.google.com", "status": 200, "text_regex": "foo", "text_matched": true, "request_time": 0.5, "request_duration": 0.5, "error": "testing"}'
    assert jsonstr == expected

    # json -> result
    new_result = json_to_page_request_result(jsonstr)
    assert new_result.__dict__ == result.__dict__
