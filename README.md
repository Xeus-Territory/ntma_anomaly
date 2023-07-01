# NTMA_Anomaly
# Network Traffic Monitor and Analysis on anomaly detection for scaling infrastructure

*This repo is creature of by [@me](https://github.com/Xeus-Territory) and [@markpage2k1](https://github.com/MarkPage2k1). This is opensource, experimental and not have limited, so if you want contributed with me and mark, contact me.*

## Purpose:
- Purpose of project is about make the ideal about the HA (High Available) system combine DevOps with automation and AI for intelligence action
- This way can be detected anomaly in network traffic by monitoring and analysis through log, metrics for deciding to make decision about automatic scaling by horizontal for demand anything work with low latency at least
- Combine AI for anomaly detection can make the system can be flexible with data and can be dynamically scaled with flex metric not like using basic metrics or log.
- Featured can be offer for detection DDos, Malware working in system. (Not now but feature this can be release)

## Project structure: <br>
- [Infrastructure](./Infrastructure/README.md):
    - Anything about the infrastructure contain from Cloud, docker, system-design and other component to deploy 
- [Script](./Script/README.md):
    - Everything about the build, setup and deployment by Bash, Python and Golang
- [ML-AI](./ML-AI/README.md)
    - Contain the ML and AI project inside to anomaly detection and make decisions
- Other:
    - Script file for building the agent and deployment agent for orchestrating and automation system

## Requirements of project
- 2 VM or more (including cadvisor, az-cli, node-exporter, docker, ...). Don't worry, Everything i relate and even have the manual in repo

## Design Infrastructure: v0.1.0 <br>
**Local Infra** <br>
![Alt text](Infrastructure/design/LocalInfra.drawio.png) <br>
**Cloud Infra** <br>
![Alt text](Infrastructure/design/CloudInfra.drawio.png)

# NTMA_Anomaly V0.2.0
![Update](https://gifdb.com/images/high/colorful-bouncing-update-text-3rtmoubg4wfovqho.gif)
- Have a new module for setup project with bash script `setup-all-ai.sh` or `setup-all-metric.sh`
- Have a new script file for building a new image with bash script `docker-build-image.sh`

## Design Infrastructure: v0.2.0 (Nothing have a bit changed since v0.1.0) <br>