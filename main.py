import os
import re
from base64 import b64encode
from http.client import HTTPConnection

from dotenv import load_dotenv

load_dotenv()

MODEM_IP = os.getenv("MODEM_IP")
MODEM_USERNAME = os.getenv("MODEM_USERNAME")
MODEM_PASSWORD = os.getenv("MODEM_PASSWORD")

ENDPOINT = "/cgi?1=null&5=null"

payload = (
    "[WAN_DSL_INTF_CFG#1,0,0,0,0,0#0,0,0,0,0,0]0,12\r\n"
    "status\r\n"
    "modulationType\r\n"
    "X_TP_AdslModulationCfg\r\n"
    "upstreamCurrRate\r\n"
    "downstreamCurrRate\r\n"
    "X_TP_AnnexType\r\n"
    "upstreamMaxRate\r\n"
    "downstreamMaxRate\r\n"
    "upstreamNoiseMargin\r\n"
    "downstreamNoiseMargin\r\n"
    "upstreamAttenuation\r\n"
    "downstreamAttenuation\r\n"
)

auth_b64 = b64encode(f"{MODEM_USERNAME}:{MODEM_PASSWORD}".encode()).decode()


def fetch_dsl_metrics():
    conn = HTTPConnection(MODEM_IP)

    headers = {
        "Cookie": f"Authorization=Basic {auth_b64}",
        "Content-Type": "text/plain",
        "Referer": f"http://{MODEM_IP}/",
        "Origin": f"http://{MODEM_IP}",
        "Sec-GPC": "1",
    }

    conn.request("POST", ENDPOINT, payload, headers)
    res = conn.getresponse()
    data = res.read().decode("utf-8")
    conn.close()

    pattern = re.compile(r"^.*\=.*$", re.MULTILINE)

    matches = dict(
        map(
            lambda x: x.split("="),
            filter(lambda x: x.strip() != "", pattern.findall(data)),
        )
    )

    return matches


if __name__ == "__main__":
    print(fetch_dsl_metrics())
