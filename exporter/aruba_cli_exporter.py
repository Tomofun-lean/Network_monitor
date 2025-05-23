"""
Aruba CLI 匯出器
透過 SSH 連接到 Aruba 接入點，解析客戶端數量並以 Prometheus 指標格式匯出。

使用方式：python aruba_cli_exporter.py
配置位置：/config/ap_config.json
"""

import json
import re
import time
import socket
import threading
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, REGISTRY
import paramiko

app = Flask(__name__)

# 常數設定 - 調整為更快的超時
CONFIG_PATH = "/config/ap_config.json"
CONNECT_TIMEOUT = 3   # 連接超時（秒）- 縮短
CMD_TIMEOUT = 5       # 命令執行超時（秒）- 縮短
CLIENT_REGEX = r"Num Clients:(\d+)"
MAX_COLLECTION_TIME = 8  # 整體收集超時（秒）

# 定義指標
clients_gauge = Gauge('aruba_ap_clients_total', '接入點的客戶端數量', ['ap', 'ip'])
connection_status_gauge = Gauge('aruba_ap_connection_status', 'AP連接狀態 (1=成功, 0=失敗)', ['ap', 'ip'])

# 緩存機制
last_update_time = 0
update_interval = 30  # 30秒更新一次
cached_ap_list = []
is_collecting = False  # 防止並發收集

def initialize_default_metrics():
    """初始化默認指標值"""
    ap_list = get_ap_config()
    for ap in ap_list:
        clients_gauge.labels(ap=ap['name'], ip=ap['ip']).set(0)
        connection_status_gauge.labels(ap=ap['name'], ip=ap['ip']).set(0)
    app.logger.info(f"初始化 {len(ap_list)} 個 AP 的默認指標")

def get_ap_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        app.logger.error(f"讀取配置文件錯誤: {e}")
        return []

def test_network_connectivity(ip, port=22):
    """快速測試網絡連通性"""
    try:
        socket.setdefaulttimeout(1)  # 1秒快速測試
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except Exception:
        return False

def get_client_count_with_timeout(ap_info, result_dict, index):
    """在單獨線程中執行，支援超時控制"""
    ap_name = ap_info['name']
    ap_ip = ap_info['ip']
    
    try:
        # 快速網絡測試
        if not test_network_connectivity(ap_ip):
            app.logger.debug(f"{ap_name}: 網絡不可達")
            result_dict[index] = {'clients': 0, 'status': 0}
            return
        
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        # SSH 連接
        ssh.connect(
            ap_ip,
            username=ap_info['username'],
            password=ap_info['password'],
            timeout=CONNECT_TIMEOUT
        )
        
        # 執行命令
        stdin, stdout, stderr = ssh.exec_command("show ap association", timeout=CMD_TIMEOUT)
        output = stdout.read().decode('utf-8')
        ssh.close()
        
        # 解析結果
        match = re.search(CLIENT_REGEX, output)
        if match:
            client_count = int(match.group(1))
            result_dict[index] = {'clients': client_count, 'status': 1}
            app.logger.info(f"{ap_name}: {client_count} 客戶端")
        else:
            # 嘗試替代模式
            alternative_patterns = [
                r"Total\s+:\s*(\d+)",
                r"(\d+)\s+clients?\s+connected",
                r"Clients:\s*(\d+)"
            ]
            
            for pattern in alternative_patterns:
                match = re.search(pattern, output, re.IGNORECASE)
                if match:
                    client_count = int(match.group(1))
                    result_dict[index] = {'clients': client_count, 'status': 1}
                    app.logger.info(f"{ap_name}: {client_count} 客戶端（替代模式）")
                    return
            
            result_dict[index] = {'clients': 0, 'status': 1}
            app.logger.debug(f"{ap_name}: 無法解析客戶端數量")
        
    except Exception as e:
        app.logger.debug(f"{ap_name}: 連接失敗 - {str(e)[:50]}")
        result_dict[index] = {'clients': 0, 'status': 0}

def collect_all_ap_data():
    """並行收集所有 AP 數據，帶超時控制"""
    global last_update_time, cached_ap_list, is_collecting
    
    current_time = time.time()
    
    # 防止並發收集
    if is_collecting:
        app.logger.debug("數據收集進行中，跳過")
        return
    
    # 檢查是否需要更新（緩存機制）
    if current_time - last_update_time < update_interval:
        app.logger.debug("使用緩存數據")
        return
    
    ap_list = get_ap_config()
    if not ap_list:
        return
    
    is_collecting = True
    
    def background_collect():
        """後台數據收集"""
        global last_update_time, cached_ap_list, is_collecting
        
        try:
            # 並行收集數據
            threads = []
            results = {}
            
            for i, ap in enumerate(ap_list):
                thread = threading.Thread(
                    target=get_client_count_with_timeout,
                    args=(ap, results, i)
                )
                thread.daemon = True
                thread.start()
                threads.append(thread)
            
            # 等待所有線程完成，但不超過最大時間
            start_time = time.time()
            for thread in threads:
                remaining_time = MAX_COLLECTION_TIME - (time.time() - start_time)
                if remaining_time > 0:
                    thread.join(timeout=remaining_time)
            
            # 更新指標
            for i, ap in enumerate(ap_list):
                if i in results:
                    result = results[i]
                    clients_gauge.labels(ap=ap['name'], ip=ap['ip']).set(result['clients'])
                    connection_status_gauge.labels(ap=ap['name'], ip=ap['ip']).set(result['status'])
                else:
                    # 超時的情況，保持之前的值
                    app.logger.debug(f"{ap['name']}: 數據收集超時")
            
            last_update_time = current_time
            cached_ap_list = ap_list
            app.logger.info(f"後台數據收集完成，耗時 {time.time() - start_time:.1f}秒")
            
        finally:
            is_collecting = False
    
    # 啟動後台線程
    bg_thread = threading.Thread(target=background_collect)
    bg_thread.daemon = True
    bg_thread.start()

@app.route('/')
def index():
    """根路徑，提供友好的提示訊息和自動重定向"""
    return '''
    <html>
        <head>
            <meta http-equiv="refresh" content="3;url=/metrics">
            <title>Aruba CLI 匯出器</title>
            <style>
                body { font-family: Arial, sans-serif; padding: 20px; text-align: center; }
                .container { max-width: 800px; margin: 0 auto; }
                h1 { color: #333; }
                p { color: #666; }
                a { color: #0066cc; text-decoration: none; }
                a:hover { text-decoration: underline; }
                .status { margin: 20px 0; padding: 15px; border-radius: 5px; }
                .success { background-color: #d4edda; color: #155724; }
                .warning { background-color: #fff3cd; color: #856404; }
                .info { background-color: #d1ecf1; color: #0c5460; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🔧 Aruba CLI 匯出器</h1>
                <p>這是一個 Prometheus 匯出器，通過 SSH 連接到 Aruba 接入點獲取客戶端數量。</p>
                <div class="status success">
                    <strong>✅ 服務正常運行</strong><br>
                    正在收集真實 AP 數據...
                </div>
                <div class="status info">
                    <strong>⚡ 性能優化</strong><br>
                    快速響應模式 - 適合 Prometheus 抓取
                </div>
                <p>正在重定向到 <a href="/metrics">/metrics</a> 頁面...</p>
                <p>如果未自動跳轉，請點擊上方鏈接查看指標數據。</p>
            </div>
        </body>
    </html>
    '''

@app.route('/metrics')
def metrics():
    """提供 Prometheus 指標，快速響應"""
    try:
        # 啟動數據收集（非阻塞）
        collect_all_ap_data()
        
        # 立即返回當前指標
        return Response(generate_latest(REGISTRY), mimetype="text/plain")
    
    except Exception as e:
        app.logger.error(f"指標生成錯誤: {e}")
        return Response("# 錯誤: 無法生成指標", mimetype="text/plain", status=500)

if __name__ == "__main__":
    print("🚀 啟動 Aruba CLI 匯出器（快速響應模式）...")
    print("📡 準備收集真實 AP 數據")
    print("⚡ 優化 Prometheus 抓取性能")
    print("🌐 請訪問 http://localhost:9130/metrics 查看指標數據")
    print("🔍 或訪問 http://localhost:9130/ 查看狀態頁面")
    
    # 初始化默認指標
    initialize_default_metrics()
    
    app.run(host="0.0.0.0", port=9130, debug=False) 