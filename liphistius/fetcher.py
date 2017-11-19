import abc
import requests
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import platform
import os
import random
import copy

_user_agents = [
    "User-Agent,Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "User-Agent, Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11"
]

_user_agents_mobiles = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 9_2_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13D15 Safari/601.1",
    "Mozilla/5.0 (Linux; Android 5.1.1; Nexus 6 Build/LYZ28E) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Mobile Safari/537.36"
]


class Fetcher(object):
    @abc.abstractmethod
    def get(self, url, params=None, **kwargs):
        pass


class RequestFetcher(Fetcher):

    def __init__(self):
        self.cookies = {}

    def get(self, url, params=None, **kwargs):
        headers = "headers" in kwargs and kwargs["headers"] or {}
        if "mobile" in kwargs and kwargs["mobile"]:
            headers["user-agent"] = random.choice(_user_agents_mobiles)
        else:
            headers["user-agent"] = random.choice(_user_agents)
        if "timeout" in kwargs:
            timeout = kwargs["timeout"]
        else:
            timeout = None
        r = requests.get(url, params, headers=headers, cookies=self.cookies, timeout=timeout)
        if r.status_code == 200:
            self.cookies = r.cookies
            return r.content
        else:
            return None


class PhontmjsFetcher(Fetcher):

    def __init__(self):
        self.cookies = []

    def _fix_cookies(self, cookies):
        domain = cookies["domain"]
        if domain.startswith("www."):
            domain = domain[3:]
        if not domain.startswith("."):
            domain = "." + domain
        ret = copy.deepcopy(cookies)
        ret["domain"] = domain
        return ret

    def _get_exe(self):
        sysstr = platform.system()
        if sysstr == "Windows":
            p = os.path.join(os.path.dirname(__file__), "../bin/windows/phantomjs.exe")
        elif sysstr == "Linux":
            p = os.path.join(os.path.dirname(__file__), "../bin/linux/phantomjs")
        else:
            p = os.path.join(os.path.dirname(__file__), "../bin/mac/phantomjs")
        return p

    def get(self, url, params=None, **kwargs):
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        if "mobile" in kwargs and kwargs["mobile"]:
            dcap["phantomjs.page.settings.userAgent"] = random.choice(_user_agents_mobiles)
        else:
            dcap["phantomjs.page.settings.userAgent"] = random.choice(_user_agents)
        driver = webdriver.PhantomJS(executable_path=self._get_exe(), desired_capabilities=dcap)
        if "timeout" in kwargs:
            driver.set_page_load_timeout(kwargs["timeout"])
        if len(self.cookies) > 0:
            for cookie in self.cookies:
                driver.add_cookie(self._fix_cookies(cookie))
        driver.get(url)
        self.cookies = driver.get_cookies()
        source = driver.page_source
        driver.quit()
        return source

if __name__ == "__main__":
    fechter = PhontmjsFetcher()
    r = fechter.get("https://www.t66y.com", timeout=5)
    print(r)