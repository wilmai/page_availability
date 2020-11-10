import re
import datetime
import asyncio
import aiohttp

from .page_request_result import PageRequestResult


class PagePoller:
    def __init__(self, request_timeout=5.0, allow_redirects=True, polling_cycle_time=10.0, urls=[], callback=None):
        self.request_timeout = request_timeout
        self.allow_redirects = allow_redirects
        self.polling_cycle_time = polling_cycle_time
        self.urls = urls
        self.callback = callback

    def run(self, once=False) -> None:
        loop = asyncio.get_event_loop()
        while True:
            loop.run_until_complete(self._poll_urls())
            if once:
                break
            loop.run_until_complete(asyncio.sleep(self.polling_cycle_time))

    def _do_callback(self, result: PageRequestResult) -> None:
        if self.callback is not None:
            self.callback(result)

    async def _request_url(self, session: aiohttp.ClientSession, url: str, regex) -> None:
        """Request a page and time it"""
        get_utc_time = lambda: datetime.datetime.now(datetime.timezone.utc)
        result = None
        matched = None
        req_time = get_utc_time()

        try:
            async with session.get(url, allow_redirects=self.allow_redirects) as response:
                text = await response.text()
                if regex is not None:
                    matched = bool(re.search(regex, text) != None)
                result = PageRequestResult(
                    url=url,
                    status=response.status,
                    text_regex=regex,
                    text_matched=matched,
                    request_time=req_time,
                    request_duration=(get_utc_time()-req_time).total_seconds()
                    )
        except asyncio.exceptions.TimeoutError:
            result = PageRequestResult(
                url=url,
                text_regex=regex,
                text_matched=matched,
                request_time=req_time,
                request_duration=(get_utc_time()-req_time).total_seconds(),
                error="client timeout"
                )
        except aiohttp.client_exceptions.ClientResponseError as e:
            result = PageRequestResult(
                url=url,
                status=e.status,
                text_regex=regex,
                text_matched=matched,
                request_time=req_time,
                request_duration=(get_utc_time()-req_time).total_seconds()
                )
        except aiohttp.client_exceptions.ClientError as e:
            result = PageRequestResult(
                url=url,
                text_regex=regex,
                text_matched=matched,
                request_time=req_time,
                request_duration=(get_utc_time()-req_time).total_seconds(),
                error=str(e)
                )
        finally:
            if result is None:
                result = PageRequestResult(
                    url=url,
                    text_regex=regex,
                    text_matched=matched,
                    request_time=req_time,
                    request_duration=(get_utc_time()-req_time).total_seconds(),
                    error="unhandled error"
                    )
            self._do_callback(result)

    async def _request_url_set(self, session: aiohttp.ClientSession) -> None:
        """Send a request out to listed sites"""
        requests = [self._request_url(session, url, rgx) for url,rgx in self.urls]
        await asyncio.gather(*requests, return_exceptions=True)

    async def _poll_urls(self) -> None:
        """Create session and poll all urls"""
        timeout = aiohttp.ClientTimeout(total=self.request_timeout)
        async with aiohttp.ClientSession(timeout=timeout, raise_for_status=True) as session:
                await self._request_url_set(session)
