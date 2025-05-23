FROM python:3.12-slim

WORKDIR /srv

# 安裝依賴
RUN pip install --no-cache-dir paramiko flask prometheus_client

# 複製真實匯出器代碼
COPY aruba_cli_exporter.py /srv/

# 直接運行真實CLI匯出器
CMD ["python", "/srv/aruba_cli_exporter.py"] 