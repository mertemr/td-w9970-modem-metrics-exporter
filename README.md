# Modem Metrics Exporter

## Contents
- [Overview](#overview)
- [Features](#features)
- [Metrics](#metrics)
- [Installation](#installation)
  - [Running in local environment](#running-in-local-environment)
  - [Running with Docker](#running-with-docker)
- [Grafana Dashboard](#grafana-dashboard)
- [License](#license)
- [Contributing](#contributing)

## Overview
This project is a Prometheus exporter for TP-Link TD-W9970 modem. It fetches modem metrics from the modem's web interface and exposes them as Prometheus metrics. 

Only tested with TD-W9970 modem, but may work with other TP-Link Wxxx modems as well.

## Features
Prometheus-compatible metric output
* Modem connection status
* Active modulation type (VDSL2, ADSL, etc.)
* Upload and download speeds
* Noise margins
* Attenuation information

## Metrics
| Metric Name | Description |
| ----------- | ----------- |
| dsl_modem_status | Modem connection status (1 if up, 0 if down) |
| dsl_modem_upstreamCurrRate | Current upstream rate in kbps |
| dsl_modem_downstreamCurrRate | Current downstream rate in kbps |
| dsl_modem_upstreamMaxRate | Maximum achievable upstream rate in kbps |
| dsl_modem_downstreamMaxRate | Maximum achievable downstream rate in kbps |
| dsl_modem_upstreamNoiseMargin | Upstream noise margin in dB |
| dsl_modem_downstreamNoiseMargin | Downstream noise margin in dB |
| dsl_modem_upstreamAttenuation | Upstream attenuation in dB |
| dsl_modem_downstreamAttenuation | Downstream attenuation in dB |

## Installation
### Running in local environment
You can run this project in your local environment by following the steps below.

1. Clone the repository  
`git clone https://github.com/mertemr/td-w9970-modem-metrics-exporter.git`

2. Install dependencies  
`pip install -r requirements.txt`

3. Set the environment variables in .env file (rename .env.example to .env)
  - `MODEM_USERNAME`: Modem admin username
  - `MODEM_PASSWORD`: Modem admin password
  - `MODEM_IP`: Modem IP address

    3.1 Alternatively, you can set the environment variables directly in your shell
    ```bash
    export MODEM_USERNAME=<your_modem_username>
    export MODEM_PASSWORD=<your_modem_password>
    export MODEM_IP=<your_modem_ip>
    ```

4. Run the exporter  
`python main.py`

5. Access the metrics at http://localhost:8000/metrics

### Running with Docker
You can run this project with Docker by following the steps below.

```bash
docker run \
    --restart unless-stopped \
    -p 8000:8000 \
    -e MODEM_USERNAME=<your_modem_username> \
    -e MODEM_PASSWORD=<your_modem_password> \
    -e MODEM_IP=<your_modem_ip> \
    -d mactorient/td-w9970-modem-metrics-exporter:latest
```
or you can build the Docker image yourself
```bash
docker build -t td-w9970-modem-metrics-exporter .
```
```bash	
docker run \
    --restart unless-stopped \
    -p 8000:8000 \
    -e MODEM_USERNAME=<your_modem_username> \
    -e MODEM_PASSWORD=<your_modem_password> \
    -e MODEM_IP=<your_modem_ip> \
    -d td-w9970-modem-metrics-exporter:latest
```

Access the metrics at http://localhost:8000/metrics

## Grafana Dashboard
I'll be adding a sample Grafana dashboard soon.  
    TODO: Create a Grafana dashboard and provide the JSON file

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please feel free to open a pull request.  
If you have any questions or issues, please open an issue.
