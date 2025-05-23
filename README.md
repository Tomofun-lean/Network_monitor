# Aruba AP 企業級監控系統

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

這是一個基於 Docker 的 Aruba 無線接入點監控解決方案，專為企業環境設計。系統透過 SSH 連接收集 AP 數據，並提供實時監控與可視化儀表板。

## 目錄

- [主要功能](#主要功能)
- [系統架構](#系統架構)
- [技術棧](#技術棧)
- [快速開始](#快速開始)
- [安裝說明](#安裝說明)
- [配置設定](#配置設定)
- [使用方法](#使用方法)
- [監控指標](#監控指標)
- [故障排除](#故障排除)
- [性能調優](#性能調優)
- [開發說明](#開發說明)
- [貢獻指南](#貢獻指南)

## 主要功能

- **實時監控**：透過 SSH 連接持續收集 Aruba AP 運行數據
- **多維度指標**：監控客戶端數量、連接狀態及設備健康度
- **容器化部署**：使用 Docker Compose 簡化部署流程
- **視覺化儀表板**：整合 Grafana 提供專業監控介面
- **高效能設計**：採用並行數據收集，響應時間低於 50 毫秒
- **企業級架構**：支援多 AP 環境，具備良好擴展性
- **安全考量**：採用 SSH 認證，配置檔案獨立管理
- **跨平台支援**：支援桌面與行動裝置瀏覽

## 系統架構

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Aruba APs     │    │  CLI Exporter   │    │   Prometheus    │
│  172.17.1.x     │◄───┤    (SSH)        │◄───┤   (TSDB)        │
│                 │    │   Port: 9130    │    │   Port: 9090    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  SNMP Exporter  │    │    Grafana      │    │   Web UI        │
│   (Optional)    │    │   Port: 3001    │◄───┤   Dashboard     │
│   Port: 9116    │    │   admin/admin   │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 技術棧

### 核心技術
- **Python 3.12**：主要開發語言
- **Flask**：輕量級 Web 框架
- **Paramiko**：SSH 連接處理
- **Prometheus Client**：指標收集與匯出

### 基礎設施
- **Docker & Docker Compose**：容器化部署方案
- **Prometheus**：時間序列資料庫
- **Grafana**：監控儀表板系統
- **SNMP Exporter**：SNMP 協議支援（可選）

### 開發工具
- **Conda**：Python 環境管理
- **Make**：自動化建置工具
- **Git**：版本控制系統

## 快速開始

### 系統需求

- Docker 20.10 或更新版本
- Docker Compose 2.0 或更新版本
- Git 版本控制工具
- 能夠連接到 Aruba AP 的網路環境

### 一鍵部署

```bash
# 1. 下載專案原始碼
git clone https://github.com/your-username/aruba_monitor.git
cd aruba_monitor

# 2. 設定 AP 連接資訊
cp ap_config.example.json ap_config.json
vim ap_config.json  # 編輯您的 AP 設定

# 3. 啟動監控系統
make up

# 4. 檢查系統狀態
make test
```

### 存取介面

- **Grafana 監控儀表板**：http://localhost:3001 (帳號：admin，密碼：admin)
- **Prometheus 資料庫**：http://localhost:9090
- **CLI 匯出器狀態**：http://localhost:9130

## 安裝說明

### 方法一：Docker Compose 部署（建議）

```bash
# 取得專案程式碼
git clone https://github.com/your-username/aruba_monitor.git
cd aruba_monitor

# 準備設定檔
cp ap_config.example.json ap_config.json

# 編輯 AP 設定資訊
{
  "name": "AP名稱",
  "ip": "AP_IP_位址", 
  "username": "SSH使用者名稱",
  "password": "SSH密碼"
}

# 啟動所有服務
docker-compose up -d

# 確認服務運行狀態
docker-compose ps
```

### 方法二：本地開發環境

```bash
# 建立 Conda 環境
conda env create -f environment.yml
conda activate aruba_monitor

# 安裝相依套件
pip install -r requirements.txt

# 執行 CLI 匯出器
cd exporter
python aruba_cli_exporter.py

# 在其他終端視窗執行 Prometheus
prometheus --config.file=grafana_prom/prometheus.yml

# 在其他終端視窗執行 Grafana
grafana-server --config=grafana_prom/grafana.ini
```

## 配置設定

### AP 設定檔案 (ap_config.json)

```json
[
  {
    "name": "AP設備名稱",
    "ip": "192.168.1.100", 
    "username": "admin",
    "password": "your_password"
  }
]
```

### 環境變數設定

```bash
# Docker Compose 環境變數
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION=15d
CLI_EXPORTER_PORT=9130
```

### 網路設定

如果 AP 網段與 Docker 預設網段發生衝突：

```bash
# 建立自訂 Docker 網路
docker network create --subnet=192.168.100.0/24 monitoring_net

# 或者修改 Docker daemon 設定
sudo vim /etc/docker/daemon.json
{
  "bip": "192.168.100.1/24"
}
```

## 使用方法

### 基本操作指令

```bash
# 服務管理
make up          # 啟動所有服務
make down        # 停止所有服務
make restart     # 重新啟動服務
make logs        # 查看服務日誌

# 測試與診斷
make test        # 測試匯出器功能
./network_diagnostic.sh    # 執行網路診斷
./verify_setup.sh         # 驗證環境設定
```

### Grafana 儀表板設定

1. **存取 Grafana**：開啟瀏覽器前往 http://localhost:3001
2. **登入系統**：使用預設帳號 admin，密碼 admin
3. **新增資料源**：
   - 類型：Prometheus
   - URL：http://prometheus:9090
4. **匯入儀表板**：
   - 上傳檔案：`grafana_prom/dashboards/aruba_overview.json`

### 查詢範例

```promql
# AP 客戶端總數
sum(aruba_ap_clients_total)

# 依 AP 分組的客戶端數量
sum by (ap) (aruba_ap_clients_total)

# AP 連接狀態
aruba_ap_connection_status

# 找出連接失敗的 AP
aruba_ap_connection_status == 0
```

## 監控指標

### 主要指標說明

| 指標名稱 | 資料類型 | 說明 | 標籤 |
|---------|---------|------|------|
| `aruba_ap_clients_total` | Gauge | AP 連接的客戶端數量 | ap, ip |
| `aruba_ap_connection_status` | Gauge | AP 連接狀態（1=成功，0=失敗） | ap, ip |

### 系統層級指標

- `python_*`：Python 執行時期相關指標
- `process_*`：系統程序相關指標
- `http_*`：HTTP 請求相關指標

### 指標資料範例

```
# HELP aruba_ap_clients_total 接入點的客戶端數量
# TYPE aruba_ap_clients_total gauge
aruba_ap_clients_total{ap="AP001",ip="192.168.1.10"} 15.0
aruba_ap_clients_total{ap="AP002",ip="192.168.1.11"} 8.0

# HELP aruba_ap_connection_status AP連接狀態
# TYPE aruba_ap_connection_status gauge  
aruba_ap_connection_status{ap="AP001",ip="192.168.1.10"} 1.0
aruba_ap_connection_status{ap="AP002",ip="192.168.1.11"} 0.0
```

## 故障排除

### 常見問題與解決方案

#### 問題 1：AP 連接失敗

**現象**：`aruba_ap_connection_status = 0`

**解決步驟**：
```bash
# 測試網路連通性
ping AP_IP_ADDRESS

# 確認 SSH 連接
ssh username@AP_IP_ADDRESS

# 檢查路由設定
ip route | grep AP_NETWORK

# 執行診斷工具
./network_diagnostic.sh
```

#### 問題 2：Prometheus 抓取逾時

**現象**：出現 `context deadline exceeded` 錯誤

**解決步驟**：
```bash
# 檢查匯出器回應時間
time curl http://localhost:9130/metrics

# 重新建置容器
docker-compose build --no-cache
docker-compose up -d
```

#### 問題 3：Grafana 顯示無資料

**解決步驟**：
```bash
# 驗證資料源設定
curl http://localhost:9090/api/v1/query?query=aruba_ap_clients_total

# 執行修復工具  
./fix_grafana_datasource.sh
```

#### 問題 4：Docker 網路衝突

**現象**：AP 位於 172.17.x.x 但無法連接

**解決方案**：
```bash
# 方案一：修改 Docker 網段
sudo vim /etc/docker/daemon.json
{
  "bip": "192.168.100.1/24",
  "default-address-pools": [
    {"base": "192.168.100.0/16", "size": 24}
  ]
}

sudo systemctl restart docker

# 方案二：使用正確的 AP IP 位址
# 更新 ap_config.json 中的 IP 設定
```

### 日誌檢視

```bash
# 查看所有服務日誌
docker-compose logs

# 查看特定服務日誌
docker-compose logs aruba_cli_exporter
docker-compose logs prometheus  
docker-compose logs grafana

# 即時監控日誌
docker-compose logs -f aruba_cli_exporter
```

### 效能監控

```bash
# 檢視容器資源使用情況
docker stats

# 檢查網路連接狀態
netstat -tlnp | grep -E "(9090|9130|3001)"

# 檢視磁碟使用情況
docker system df
```

## 性能調優

### 系統最佳化設定

```bash
# 調整 Prometheus 抓取設定 (prometheus.yml)
scrape_interval: 30s     # 全域抓取間隔
scrape_timeout: 15s      # 逾時設定

# 調整 CLI 匯出器逾時設定
CONNECT_TIMEOUT = 3      # SSH 連接逾時
CMD_TIMEOUT = 5          # 指令執行逾時
```

### 資源配置建議

```yaml
# docker-compose.yml 資源限制設定
services:
  aruba_cli_exporter:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

### 快取策略

- **指標快取**：30 秒內的重複請求會使用快取資料
- **並行處理**：同時收集多個 AP 的資料
- **快速失敗**：網路不可達時立即回傳結果

## 開發說明

### 本地開發環境設定

```bash
# 建立開發環境
conda env create -f environment.yml
conda activate aruba_monitor

# 安裝開發相依套件
pip install -r requirements-dev.txt

# 程式碼格式化
black src/
flake8 src/

# 執行測試
pytest tests/
```

### 專案架構

```
aruba_monitor/
├── exporter/                   # CLI 匯出器
│   ├── aruba_cli_exporter.py  # 主要程式
│   └── Dockerfile             # 容器設定
├── grafana_prom/              # 監控設定
│   ├── prometheus.yml         # Prometheus 設定
│   ├── snmp.yml              # SNMP 設定
│   └── dashboards/           # Grafana 儀表板
├── docker-compose.yml         # 服務編排
├── ap_config.json            # AP 設定
├── Makefile                  # 建置腳本
└── README.md                 # 專案說明
```

### 新增監控指標

```python
# 1. 定義新指標
new_metric = Gauge('aruba_ap_new_metric', '新指標說明', ['ap', 'ip'])

# 2. 實作資料收集
def collect_new_metric(ap_info):
    # 在此實作資料收集邏輯
    return metric_value

# 3. 更新指標數值
new_metric.labels(ap=ap_name, ip=ap_ip).set(metric_value)
```

### API 說明

```bash
# CLI 匯出器端點
GET /               # 狀態頁面
GET /metrics        # Prometheus 指標

# Prometheus API
GET /api/v1/query?query=PROMQL     # 查詢指標
GET /api/v1/targets                # 目標狀態
```

## 貢獻指南

### 參與貢獻的流程

1. **Fork 專案**到您的 GitHub 帳號
2. **建立功能分支**：`git checkout -b feature/amazing-feature`
3. **提交變更**：`git commit -m 'Add amazing feature'`
4. **推送分支**：`git push origin feature/amazing-feature`
5. **建立 Pull Request**

### 程式碼規範

- **Python**：遵循 PEP 8 編碼規範
- **Docker**：使用多階段建置最佳化
- **文件**：撰寫完整的 docstring
- **測試**：維持 80% 以上的測試覆蓋率

### 開發工作流程

```bash
# 1. 環境準備
conda activate aruba_monitor
pre-commit install

# 2. 開發除錯
docker-compose up -d prometheus grafana
python exporter/aruba_cli_exporter.py

# 3. 測試驗證
pytest tests/
./verify_setup.sh

# 4. 提交程式碼
git add .
git commit -m "feat: add new feature"
git push origin feature-branch
```

## 版本歷史

### v1.0.0（目前版本）
- 基於 SSH 的即時資料收集功能
- 完整的 Docker Compose 部署方案
- Grafana 監控儀表板整合
- 並行資料收集效能最佳化
- 企業級錯誤處理機制
- 完整的說明文件與故障排除指南

### 未來規劃
- SNMP 協議支援
- 行動裝置介面最佳化
- 告警通知功能
- 歷史資料分析
- 角色權限控制系統

## 授權條款

本專案採用 [MIT 授權條款](LICENSE)。

## 支援與聯絡

- **問題回報**：[GitHub Issues](https://github.com/your-username/aruba_monitor/issues)
- **功能建議**：[GitHub Discussions](https://github.com/your-username/aruba_monitor/discussions)
- **安全性問題**：security@your-domain.com

---

## 致謝

感謝所有參與貢獻的開發者與開源社群的支持。

**專為企業網路監控而生** 