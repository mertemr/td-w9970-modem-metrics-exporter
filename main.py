import os
import re
from base64 import b64encode
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import load_dotenv

load_dotenv()

MODEM_IP = os.getenv("MODEM_IP")
MODEM_USERNAME = os.getenv("MODEM_USERNAME")
MODEM_PASSWORD = os.getenv("MODEM_PASSWORD")

ENDPOINT = "/cgi?1=null&5=null"

SERVER_PORT = int(os.getenv("PORT", 8000))


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path == "/metrics":
            self.send_response(404)
            self.end_headers()
            return

        try:
            metrics = fetch_dsl_metrics()
            prometheus_output = prometheus_format(metrics)
        except Exception as e:
            print(e)
            self.send_response(500)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(prometheus_output.encode("utf-8"))


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


def prometheus_format(metrics: dict[str, str]) -> str:
    output = ""
    output += "# HELP dsl_modem_metrics DSL metrics from the modem\n"
    output += "# TYPE dsl_modem_metrics gauge\n"

    for key, value in metrics.items():
        key = key.strip().replace(".", "_").replace("-", "_")
        output += f"dsl_modem_{key} {value}\n"

    return output


if __name__ == "__main__":
    # fetch_dsl_metrics()
    server_address = ("127.0.0.1", SERVER_PORT)
    httpd = HTTPServer(server_address, MetricsHandler)
    print(f"Access the metrics at http://127.0.0.1:{SERVER_PORT}/metrics")

    try:
        httpd.serve_forever()
    except Exception as e:
        print(e)
    finally:
        httpd.server_close()
