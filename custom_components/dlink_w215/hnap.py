"""Minimal HNAP client for D-Link DSP-W215, working on firmware 2.2x."""
import hashlib
import hmac
import re
import time
import urllib.request

NS = "http://purenetworks.com/HNAP1/"


def _md5(key: str, msg: str) -> str:
    return hmac.new(key.encode(), msg.encode(), hashlib.md5).hexdigest().upper()


def _tag(tag: str, text: str):
    m = re.search(f"<{tag}>(.*?)</{tag}>", text, re.S)
    return m.group(1) if m else None


class W215:
    def __init__(self, host: str, pin: str, user: str = "admin", timeout: int = 8):
        self.url = f"http://{host}/HNAP1/"
        self.pin, self.user, self.timeout = pin, user, timeout
        self._priv = self._cookie = None

    def _post(self, action: str, body: str, auth: bool = True) -> str:
        soap = f'"{NS}{action}"'
        xml = (
            '<?xml version="1.0" encoding="utf-8"?><soap:Envelope '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            'xmlns:xsd="http://www.w3.org/2001/XMLSchema" '
            'xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/"><soap:Body>'
            f'<{action} xmlns="{NS}">{body}</{action}></soap:Body></soap:Envelope>'
        )
        headers = {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": soap}
        if self._cookie:
            headers["Cookie"] = f"uid={self._cookie}"
        if auth and self._priv:
            ts = str(int(time.time() * 1000) % 2000000000000)
            headers["HNAP_AUTH"] = f"{_md5(self._priv, ts + soap)} {ts}"
        req = urllib.request.Request(self.url, xml.encode(), headers)
        return urllib.request.urlopen(req, timeout=self.timeout).read().decode()

    def login(self) -> None:
        self._priv = self._cookie = None
        r = self._post("Login", f"<Action>request</Action><Username>{self.user}</Username>"
                       "<LoginPassword></LoginPassword><Captcha></Captcha>", auth=False)
        ch, self._cookie, pk = _tag("Challenge", r), _tag("Cookie", r), _tag("PublicKey", r)
        if not ch:
            raise ConnectionError("HNAP login request failed")
        self._priv = _md5(pk + self.pin, ch)
        r = self._post("Login", f"<Action>login</Action><Username>{self.user}</Username>"
                       f"<LoginPassword>{_md5(self._priv, ch)}</LoginPassword><Captcha></Captcha>",
                       auth=False)
        if _tag("LoginResult", r) != "success":
            raise PermissionError("HNAP login rejected (check PIN)")

    def call(self, action: str, body: str, result: str | None = None) -> str:
        """Call with one automatic re-login if the session expired."""
        for attempt in (0, 1):
            if not self._priv:
                self.login()
            r = self._post(action, body)
            ok = _tag(f"{action}Result", r)
            if ok in ("OK", None) or attempt:
                return r
            self._priv = None  # session likely expired; retry once
        return r

    def is_on(self) -> bool:
        r = self.call("GetSocketSettings", "<ModuleID>1</ModuleID>")
        return _tag("OPStatus", r) == "true"

    def set_state(self, on: bool) -> None:
        # fw 2.2x rejects SetSocketSettings; SetModuleEnabled switches the relay.
        v = "true" if on else "false"
        r = self.call("SetModuleEnabled", "<ModuleEnabledList><ModuleEnabled><ModuleID>1</ModuleID>"
                      f"<OPStatus>{v}</OPStatus></ModuleEnabled></ModuleEnabledList>")
        if _tag("SetModuleEnabledResult", r) != "OK":
            raise RuntimeError(f"Switch command failed: {r[-300:]}")

    def power(self):
        r = self.call("GetCurrentPowerConsumption", "<ModuleID>2</ModuleID>")
        v = _tag("CurrentConsumption", r)
        return float(v) if v not in (None, "") else None

    def temperature(self):
        r = self.call("GetCurrentTemperature", "<ModuleID>3</ModuleID>")
        v = _tag("CurrentTemperature", r)
        return float(v) if v not in (None, "") else None
