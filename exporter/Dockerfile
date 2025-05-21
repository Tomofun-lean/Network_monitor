FROM python:3.12-slim

WORKDIR /srv

# 安裝依賴
RUN pip install --no-cache-dir paramiko flask prometheus_client

# 複製匯出器代碼
COPY aruba_cli_exporter.py /srv/
COPY fake_aruba_exporter.py /srv/

# 模式選擇參數 (real 或 fake)
ARG MODE=real

# 根據模式設置入口點
CMD ["sh", "-c", "if [ \"$MODE\" = \"real\" ]; then python /srv/aruba_cli_exporter.py; else python /srv/fake_aruba_exporter.py; fi"] 