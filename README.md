# Aruba AP 企業級監控系統

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)

一個基於 Docker 的企業級 Aruba 無線接入點監控解決方案，提供實時監控、指標收集和可視化儀表板。

## 📋 目錄

- [功能特色](#-功能特色)
- [系統架構](#-系統架構)
- [技術棧](#-技術棧)
- [快速開始](#-快速開始)
- [詳細安裝](#-詳細安裝)
- [配置說明](#-配置說明)
- [使用指南](#-使用指南)
- [監控指標](#-監控指標)
- [故障排除](#-故障排除)
- [性能優化](#-性能優化)
- [開發指南](#-開發指南)
- [貢獻指南](#-貢獻指南)

## 🌟 功能特色

- **🔄 實時監控**: 通過 SSH 連接實時收集 Aruba AP 數據
- **📊 多維度指標**: 客戶端數量、連接狀態、設備健康度
- **🐳 容器化部署**: 完整的 Docker Compose 解決方案
- **📈 可視化儀表板**: 基於 Grafana 的專業監控界面
- **⚡ 高性能**: 並行數據收集，快速響應（<50ms）
- **🔧 企業級**: 支援多 AP 環境，可擴展架構
- **🛡️ 安全性**: SSH 密鑰認證，配置文件隔離
- **📱 響應式**: 支援桌面和移動設備訪問

## 🏗️ 系統架構

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

## 💻 技術棧

### 核心技術
- **Python 3.12**: 主要開發語言
- **Flask**: Web 框架
- **Paramiko**: SSH 連接庫
- **Prometheus Client**: 指標收集

### 基礎設施
- **Docker & Docker Compose**: 容器化部署
- **Prometheus**: 時間序列數據庫
- **Grafana**: 監控儀表板
- **SNMP Exporter**: SNMP 協議支援

### 開發工具
- **Conda**: 環境管理
- **Make**: 構建自動化
- **Git**: 版本控制

## 🚀 快速開始

### 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- Git
- 網絡連接到 Aruba APs

### 一鍵部署

```bash
# 1. 克隆項目
git clone https://github.com/your-username/aruba_monitor.git
cd aruba_monitor

# 2. 配置 AP 連接信息
cp ap_config.example.json ap_config.json
vim ap_config.json  # 編輯您的 AP 配置

# 3. 啟動監控系統
make up

# 4. 檢查服務狀態
make test
```

### 訪問界面

- **Grafana 監控儀表板**: http://localhost:3001 (admin/admin)
- **Prometheus 數據庫**: http://localhost:9090
- **CLI 匯出器狀態**: http://localhost:9130

## 📦 詳細安裝

### 方法 1: Docker Compose (推薦)

```bash
# 克隆項目
git clone https://github.com/your-username/aruba_monitor.git
cd aruba_monitor

# 配置環境
cp ap_config.example.json ap_config.json

# 編輯 AP 配置
{
  "name": "AP名稱",
  "ip": "AP_IP_地址", 
  "username": "SSH用戶名",
  "password": "SSH密碼"
}

# 啟動服務
docker-compose up -d

# 檢查服務狀態
docker-compose ps
```

### 方法 2: 本地開發環境

```bash
# 創建 Conda 環境
conda env create -f environment.yml
conda activate aruba_monitor

# 安裝依賴
pip install -r requirements.txt

# 運行 CLI 匯出器
cd exporter
python aruba_cli_exporter.py

# 運行 Prometheus (另一個終端)
prometheus --config.file=grafana_prom/prometheus.yml

# 運行 Grafana (另一個終端)
grafana-server --config=grafana_prom/grafana.ini
```

## ⚙️ 配置說明

### AP 配置文件 (ap_config.json)

```json
[
  {
    "name": "AP_名稱",
    "ip": "192.168.1.100", 
    "username": "admin",
    "password": "your_password"
  }
]
```

### 環境變量

```bash
# Docker Compose 環境變量
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION=15d
CLI_EXPORTER_PORT=9130
```

### 網絡配置

如果 AP 網段與 Docker 默認網段衝突：

```bash
# 創建自定義 Docker 網絡
docker network create --subnet=192.168.100.0/24 monitoring_net

# 或修改 Docker daemon 配置
sudo vim /etc/docker/daemon.json
{
  "bip": "192.168.100.1/24"
}
```

## 📖 使用指南

### 基本操作

```bash
# 服務管理
make up          # 啟動所有服務
make down        # 停止所有服務
make restart     # 重啟服務
make logs        # 查看日誌

# 測試和診斷
make test        # 測試匯出器
./network_diagnostic.sh    # 網絡診斷
./verify_setup.sh         # 環境驗證
```

### Grafana 儀表板配置

1. **訪問 Grafana**: http://localhost:3001
2. **登入**: admin / admin
3. **添加數據源**:
   - Type: Prometheus
   - URL: http://prometheus:9090
4. **導入儀表板**:
   - 上傳: `grafana_prom/dashboards/aruba_overview.json`

### 查詢範例

```promql
# AP 客戶端總數
sum(aruba_ap_clients_total)

# 按 AP 分組的客戶端數量
sum by (ap) (aruba_ap_clients_total)

# AP 連接狀態
aruba_ap_connection_status

# 連接失敗的 AP
aruba_ap_connection_status == 0
```

## 📊 監控指標

### 主要指標

| 指標名稱 | 類型 | 描述 | 標籤 |
|---------|------|------|------|
| `aruba_ap_clients_total` | Gauge | AP 客戶端數量 | ap, ip |
| `aruba_ap_connection_status` | Gauge | AP 連接狀態 (1=成功, 0=失敗) | ap, ip |

### 系統指標

- `python_*`: Python 運行時指標
- `process_*`: 進程相關指標
- `http_*`: HTTP 請求指標

### 指標示例

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

## 🔧 故障排除

### 常見問題

#### 1. AP 連接失敗

**症狀**: `aruba_ap_connection_status = 0`

**解決方案**:
```bash
# 檢查網絡連通性
ping AP_IP_ADDRESS

# 檢查 SSH 連接
ssh username@AP_IP_ADDRESS

# 檢查路由配置
ip route | grep AP_NETWORK

# 診斷工具
./network_diagnostic.sh
```

#### 2. Prometheus 抓取超時

**症狀**: `context deadline exceeded`

**解決方案**:
```bash
# 檢查匯出器響應時間
time curl http://localhost:9130/metrics

# 重新構建容器
docker-compose build --no-cache
docker-compose up -d
```

#### 3. Grafana 顯示 "No data"

**解決方案**:
```bash
# 檢查數據源配置
curl http://localhost:9090/api/v1/query?query=aruba_ap_clients_total

# 運行修復工具  
./fix_grafana_datasource.sh
```

#### 4. Docker 網絡衝突

**症狀**: AP 在 172.17.x.x 無法連接

**解決方案**:
```bash
# 方案 1: 修改 Docker 網段
sudo vim /etc/docker/daemon.json
{
  "bip": "192.168.100.1/24",
  "default-address-pools": [
    {"base": "192.168.100.0/16", "size": 24}
  ]
}

sudo systemctl restart docker

# 方案 2: 使用正確的 AP IP
# 更新 ap_config.json 中的 IP 地址
```

### 日誌查看

```bash
# 查看所有服務日誌
docker-compose logs

# 查看特定服務日誌
docker-compose logs aruba_cli_exporter
docker-compose logs prometheus  
docker-compose logs grafana

# 實時日誌
docker-compose logs -f aruba_cli_exporter
```

### 性能監控

```bash
# 容器資源使用
docker stats

# 網絡連接
netstat -tlnp | grep -E "(9090|9130|3001)"

# 磁盤使用
docker system df
```

## ⚡ 性能優化

### 系統優化

```bash
# 調整抓取間隔 (prometheus.yml)
scrape_interval: 30s     # 全局間隔
scrape_timeout: 15s      # 超時設置

# 調整 CLI 匯出器超時
CONNECT_TIMEOUT = 3      # SSH 連接超時
CMD_TIMEOUT = 5          # 命令執行超時
```

### 資源配置

```yaml
# docker-compose.yml 資源限制
services:
  aruba_cli_exporter:
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

### 緩存策略

- **指標緩存**: 30秒內重複請求使用緩存
- **並行處理**: 多 AP 同時收集數據
- **快速失敗**: 網絡不可達時立即返回

## 👨‍💻 開發指南

### 本地開發環境

```bash
# 創建開發環境
conda env create -f environment.yml
conda activate aruba_monitor

# 安裝開發依賴
pip install -r requirements-dev.txt

# 代碼格式化
black src/
flake8 src/

# 運行測試
pytest tests/
```

### 項目結構

```
aruba_monitor/
├── exporter/                   # CLI 匯出器
│   ├── aruba_cli_exporter.py  # 主程序
│   └── Dockerfile             # 容器配置
├── grafana_prom/              # 監控配置
│   ├── prometheus.yml         # Prometheus 配置
│   ├── snmp.yml              # SNMP 配置
│   └── dashboards/           # Grafana 儀表板
├── docker-compose.yml         # 服務編排
├── ap_config.json            # AP 配置
├── Makefile                  # 構建腳本
└── README.md                 # 說明文件
```

### 添加新指標

```python
# 1. 定義指標
new_metric = Gauge('aruba_ap_new_metric', '新指標描述', ['ap', 'ip'])

# 2. 收集數據
def collect_new_metric(ap_info):
    # 實現數據收集邏輯
    return metric_value

# 3. 更新指標
new_metric.labels(ap=ap_name, ip=ap_ip).set(metric_value)
```

### API 文檔

```bash
# CLI 匯出器端點
GET /               # 狀態頁面
GET /metrics        # Prometheus 指標

# Prometheus API
GET /api/v1/query?query=PROMQL     # 查詢指標
GET /api/v1/targets                # 目標狀態
```

## 🤝 貢獻指南

### 貢獻流程

1. **Fork 項目**
2. **創建功能分支**: `git checkout -b feature/amazing-feature`
3. **提交更改**: `git commit -m 'Add amazing feature'`
4. **推送分支**: `git push origin feature/amazing-feature`
5. **創建 Pull Request**

### 代碼規範

- **Python**: 遵循 PEP 8
- **Docker**: 使用多階段構建
- **文檔**: 包含完整的 docstring
- **測試**: 覆蓋率 > 80%

### 開發工作流

```bash
# 1. 環境準備
conda activate aruba_monitor
pre-commit install

# 2. 開發調試
docker-compose up -d prometheus grafana
python exporter/aruba_cli_exporter.py

# 3. 測試驗證
pytest tests/
./verify_setup.sh

# 4. 提交代碼
git add .
git commit -m "feat: add new feature"
git push origin feature-branch
```

## 📝 版本更新

### v1.0.0 (最新)
- ✅ 基於 SSH 的實時數據收集
- ✅ 完整的 Docker Compose 部署
- ✅ Grafana 監控儀表板
- ✅ 並行數據收集優化
- ✅ 企業級錯誤處理
- ✅ 完整的文檔和故障排除指南

### 路線圖
- 🔄 SNMP 協議支援
- 📱 移動端適配
- 🔔 告警功能
- 📊 歷史數據分析
- 🔐 RBAC 權限控制

## 📄 許可證

本項目採用 [MIT 許可證](LICENSE)。

## 📞 支援與聯繫

- **問題報告**: [GitHub Issues](https://github.com/your-username/aruba_monitor/issues)
- **功能請求**: [GitHub Discussions](https://github.com/your-username/aruba_monitor/discussions)
- **安全問題**: security@your-domain.com

---

## 🙏 致謝

感謝所有貢獻者和開源社區的支持！

**Made with ❤️ for Enterprise Network Monitoring** 