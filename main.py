import os
import re
from base64 import b64encode
from http.server import BaseHTTPRequestHandler, HTTPServer
from socket import gethostbyname_ex, gethostname
from dotenv import load_dotenv
from httpx import Client

load_dotenv()

MODEM_IP = os.getenv("MODEM_IP")
MODEM_USERNAME = os.getenv("MODEM_USERNAME")
MODEM_PASSWORD = os.getenv("MODEM_PASSWORD")

ENDPOINT = "/cgi?1=null&5=null"

SERVER_PORT = int(os.getenv("PORT", 8000))
METRICS_ENDPOINT = "/metrics"

auth_b64 = b64encode(f"{MODEM_USERNAME}:{MODEM_PASSWORD}".encode()).decode()
headers = {
    "Content-Type": "text/plain",
    "Referer": f"http://{MODEM_IP}/",
    "Origin": f"http://{MODEM_IP}",
    "Sec-GPC": "1"
}

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

client = Client(
    base_url=f"http://{MODEM_IP}", headers=headers, cookies={"Authorization": f"Basic {auth_b64}"}, timeout=10
)


class MetricsHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if not self.path == METRICS_ENDPOINT:
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


def fetch_dsl_metrics():
    response = client.post(ENDPOINT, data=payload)
    response.raise_for_status()
    data = response.text

    pattern = re.compile(r"^.*\=.*$", re.MULTILINE)

    matches = dict(
        map(
            lambda x: x.split("="),
            filter(lambda x: x.strip() != "", pattern.findall(data)),
        )
    )

    return matches


def prometheus_format(metrics: dict[str, str]) -> str:
    output = "# HELP dsl_modem_metrics DSL metrics from the modem\n" \
             "# TYPE dsl_modem_metrics gauge\n"

    for key, value in metrics.items():
        key = key.strip().replace(".", "_").replace("-", "_")
        
        try:
            output += f"dsl_modem_{key} {float(value)}\n"
        except ValueError:
            value_lower = value.strip().lower()
            if value_lower == "up":
                output += f"dsl_modem_{key} 1\n"
            elif value_lower == "down":
                output += f"dsl_modem_{key} 0\n"

    return output


def get_host_ips():
    hostname = gethostname()
    yield from gethostbyname_ex(hostname)[2]

def main():
    server_address = ("", SERVER_PORT)
    httpd = HTTPServer(server_address, MetricsHandler)
    print("Access the metrics at:")
    for i in get_host_ips():
        print(f"  http://{i}:{SERVER_PORT}{METRICS_ENDPOINT}")

    try:
        httpd.serve_forever()
    except Exception as e:
        print(e)
    except KeyboardInterrupt:
        pass

    httpd.server_close()
    client.close()


if __name__ == "__main__":
    main()
