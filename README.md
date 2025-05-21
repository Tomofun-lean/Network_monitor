# Aruba AP 監控工具包

## 系統概述

這是一個完整的 Aruba 無線網路監控解決方案，能夠收集和視覺化 Aruba 接入點的各種性能指標。系統由以下主要組件組成：

1. **指標收集器（Exporters）**：
   - **Aruba CLI Exporter**：透過 SSH 連接到真實的 Aruba 接入點，收集客戶端數量等指標。
   - **Fake Aruba Exporter**：模擬 Aruba 接入點產生隨機指標數據，適合測試和開發。
   - **SNMP Exporter**：透過 SNMP 協議收集更多詳細的設備指標。

2. **監控與視覺化平台**：
   - **Prometheus**：時間序列數據庫，負責存儲和查詢所有指標數據。
   - **Grafana**：提供美觀的儀表板介面，用於視覺化顯示監控數據。

3. **部署方式**：
   - 支援單獨運行匯出器（適合開發測試）
   - 支援完整的 Docker Compose 環境（適合生產部署）

## 系統需求

- **Python 3.12**（獨立運行匯出器時需要）
- **Docker** 和 **Docker Compose**（推薦部署方式）
- 網路連接可達的 Aruba 接入點（真實模式需要）
- 至少 1GB 可用記憶體
- 50MB 可用磁碟空間（不含長期指標存儲）

## 快速入門指南

### 方式一：使用 Docker Compose（推薦）

這是部署完整監控系統的最簡單方法，包括所有組件：Prometheus、Grafana 和指標收集器。

#### 步驟 1：準備環境

1. 確認您已安裝 Docker 和 Docker Compose：
   ```bash
   docker --version
   docker-compose --version
   ```

2. 克隆或下載本專案：
   ```bash
   git clone <專案倉庫URL>
   cd Network_Monitor  # 根目錄
   cd aruba_monitor    # 進入專案目錄
   ```

#### 步驟 2：配置系統（使用模擬數據）

首次使用建議先使用模擬數據測試系統功能：

1. 修改 `docker-compose.yml` 檔案，將 `aruba_cli_exporter` 服務的 MODE 參數改為 `fake`：
   ```yaml
   aruba_cli_exporter:
     build:
       context: ./exporter
       args:
         MODE: fake  # 從 real 改為 fake
   ```

2. 註釋掉 `aruba_cli_exporter` 服務中的 volumes 配置：
   ```yaml
   # volumes:
   #   - ./ap_config.json:/config/ap_config.json:ro
   ```

#### 步驟 3：啟動系統

1. 關閉可能正在運行的服務（避免端口衝突）：
   ```bash
   make down  # 或 docker-compose down --remove-orphans
   ```

2. 啟動所有服務：
   ```bash
   make up    # 或 docker-compose up -d
   ```

3. 檢查服務是否正常運行：
   ```bash
   make test  # 或 docker-compose ps
   ```

#### 步驟 4：訪問監控界面

1. **訪問 Grafana 儀表板**：
   - 開啟瀏覽器，訪問：http://localhost:3001
   - 使用預設帳號：**admin** / 密碼：**admin**
   - 首次登入會提示修改密碼，可以選擇「略過」保持原密碼

2. **配置 Prometheus 數據源**：
   - 在 Grafana 左側導航欄，點擊「⚙️ 設定」→「Data Sources」
   - 點擊「Add data source」→ 選擇「Prometheus」
   - URL 欄位填入：`http://prometheus:9090`（注意：這是 Docker 網路內的地址）
   - 點擊「Save & Test」，確認連接成功

3. **導入預配置儀表板**：
   - 在 Grafana 左側導航欄，點擊「+」→「Import」
   - 點擊「Upload JSON file」按鈕
   - 選擇 `aruba_monitor/grafana_prom/dashboards/aruba_overview.json` 檔案
   - 選擇 Prometheus 數據源後點擊「Import」

4. **其他監控界面**：
   - **Prometheus**：http://localhost:9090
   - **Fake Exporter 指標**：http://localhost:9131/metrics

恭喜！您現在應該能看到 Aruba AP 概覽儀表板，顯示由模擬匯出器產生的隨機數據。

### 方式二：使用真實 Aruba AP（生產環境）

當您準備好監控真實的 Aruba 接入點時，請按照以下步驟操作：

1. **配置 AP 連接資訊**：
   ```bash
   cp ap_config.example.json ap_config.json
   # 使用編輯器打開 ap_config.json
   vim ap_config.json  # 或使用其他編輯器
   ```

2. 在 `ap_config.json` 中填入您的 AP 連接資訊：
   ```json
   [
     {
       "name": "AP名稱",
       "ip": "192.168.1.x",
       "username": "管理員帳號",
       "password": "管理員密碼"
     },
     // 可以添加多個 AP
   ]
   ```

3. 修改 `docker-compose.yml` 將 `aruba_cli_exporter` 模式改為真實模式：
   ```yaml
   aruba_cli_exporter:
     build:
       context: ./exporter
       args:
         MODE: real  # 改回 real
     volumes:
       - ./ap_config.json:/config/ap_config.json:ro  # 取消註釋
   ```

4. 重新啟動服務：
   ```bash
   make down
   make up
   ```

### 方式三：獨立運行匯出器（開發測試）

適合進行開發或調試單個組件：

1. **建立並啟用 Conda 環境**：
   ```bash
   # 確保您在正確的目錄中
   cd aruba_monitor
   
   # 建立環境
   conda env create -f environment.yml
   
   # 啟用環境
   conda activate aruba-monitor
   ```

2. **獨立運行模擬匯出器**：
   ```bash
   cd exporter
   python fake_aruba_exporter.py
   ```

3. **訪問服務**：
   - 指標頁面：http://localhost:9131/metrics
   - 根頁面會自動重定向至指標頁面：http://localhost:9131/

## 目錄結構說明

```
aruba_monitor/
├── README.md               # 本文檔
├── Makefile                # 運行常用命令的快捷方式
├── docker-compose.yml      # Docker 服務配置
├── environment.yml         # Conda 環境配置
├── ap_config.example.json  # AP 配置範例
├── ap_config.json          # 實際 AP 配置（需手動建立）
├── exporter/               # 指標收集器代碼
│   ├── fake_aruba_exporter.py  # 模擬數據收集器
│   ├── aruba_cli_exporter.py   # 真實 AP 數據收集器
│   └── Dockerfile          # 容器建置配置
└── grafana_prom/           # Grafana 和 Prometheus 配置
    ├── dashboards/         # Grafana 儀表板
    │   └── aruba_overview.json
    ├── prometheus.yml      # Prometheus 配置
    ├── snmp.yml            # SNMP 匯出器配置
    └── targets.json        # 監控目標配置
```

## 故障排除

### 常見問題 1：無法啟動服務 / 端口衝突

**症狀**：啟動 Docker 服務時出現 `port is already allocated` 錯誤。

**解決方法**：
1. 檢查佔用端口的程序：
   ```bash
   sudo netstat -tulnp | grep <端口號>
   # 例如：sudo netstat -tulnp | grep 9131
   ```

2. 停止佔用端口的程序：
   ```bash
   kill <進程ID>
   # 或強制終止：kill -9 <進程ID>
   ```

3. 如果仍然無法釋放端口，可以修改 `docker-compose.yml` 中的端口映射：
   ```yaml
   ports:
     - "新端口:原始端口"  # 例如 "9132:9131"
   ```

### 常見問題 2：找不到環境檔案

**症狀**：執行 `conda env create` 時出現 `EnvironmentFileNotFound` 錯誤。

**解決方法**：
確認您在正確目錄下執行命令：
```bash
cd /home/lean/Network_Monitor/aruba_monitor
conda env create -f environment.yml
```

### 常見問題 3：網頁顯示 404 錯誤

**症狀**：訪問 exporter 網頁時顯示 404 錯誤。

**解決方法**：
1. 確認您訪問的 URL 包含正確的端口和路徑：
   - 模擬匯出器：http://localhost:9131/metrics
   - 真實 CLI 匯出器：http://localhost:9130/metrics
   - 新版本已支援直接訪問根路徑，會自動重定向

2. 確認對應的服務正在運行：
   ```bash
   docker-compose ps
   # 或檢查單獨運行的 Python 進程
   ps aux | grep exporter
   ```

### 常見問題 4：Grafana 無法顯示數據

**症狀**：Grafana 儀表板無法顯示任何數據。

**解決方法**：
1. 檢查 Prometheus 數據源配置是否正確：
   - URL 必須是 `http://prometheus:9090`（Docker 內部網絡名稱）

2. 檢查 Prometheus 目標是否正常：
   - 訪問 Prometheus UI：http://localhost:9090
   - 點擊 Status → Targets
   - 檢查 `aruba-cli` 和 `aruba-fake` 目標狀態是否為 UP

3. 檢查時間範圍：
   - Grafana 右上角選擇適當時間範圍，例如 "Last 5 minutes"

## 進階配置

### 自定義監控目標

編輯 `grafana_prom/targets.json` 文件，定義要監控的設備 IP：

```json
[
  {
    "targets": ["172.17.1.6"],
    "labels": {
      "ap": "AP-Room1"
    }
  }
]
```

### SNMP 監控配置

編輯 `grafana_prom/snmp.yml` 文件，根據您的設備型號和需求調整 OID。

## 安全說明

1. **請不要在公共環境暴露此服務**：服務未實現完整的安全防護。
2. **妥善保管 AP 登入憑證**：確保 `ap_config.json` 檔案權限適當設置。
3. **生產環境建議**：
   - 修改預設的 Grafana 管理員密碼
   - 啟用 HTTPS
   - 設定適當的防火牆規則

## 技術堆疊

- **Python 3.12**：腳本語言
- **Flask**：輕量級 Web 框架
- **Prometheus**：時序數據庫
- **Grafana**：數據視覺化
- **Paramiko**：SSH 連接
- **Docker & Docker Compose**：容器化部署 