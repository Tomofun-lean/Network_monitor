"""
Aruba CLI 匯出器
透過 SSH 連接到 Aruba 接入點，解析客戶端數量並以 Prometheus 指標格式匯出。

使用方式：python aruba_cli_exporter.py
配置位置：/config/ap_config.json
"""

import json
import re
import signal
import time
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, REGISTRY
import paramiko

app = Flask(__name__)

# 常數設定
CONFIG_PATH = "/config/ap_config.json"
TIMEOUT = 120  # 秒
CLIENT_REGEX = r"Num Clients:(\d+)"

# 定義指標
clients_gauge = Gauge('aruba_ap_clients_total', '接入點的客戶端數量', ['ap', 'ip'])

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutException("SSH 連接超時")

def get_ap_config():
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        app.logger.error(f"讀取配置文件錯誤: {e}")
        return []

def get_client_count(ap_info):
    """從 Aruba AP 獲取客戶端數量"""
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(TIMEOUT)
        
        ssh.connect(
            ap_info['ip'],
            username=ap_info['username'],
            password=ap_info['password'],
            timeout=TIMEOUT
        )
        
        stdin, stdout, stderr = ssh.exec_command("show ap association")
        output = stdout.read().decode('utf-8')
        
        match = re.search(CLIENT_REGEX, output)
        if match:
            return int(match.group(1))
        else:
            app.logger.warning(f"無法解析客戶端數量: {ap_info['name']}")
            return 0
            
    except Exception as e:
        app.logger.error(f"連接到 {ap_info['name']} 時出錯: {e}")
        return 0
    finally:
        signal.alarm(0)  # 取消計時器
        ssh.close()

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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Aruba CLI 匯出器</h1>
                <p>這是一個 Prometheus 匯出器，通過 SSH 連接到 Aruba 接入點獲取客戶端數量。</p>
                <p>正在重定向到 <a href="/metrics">/metrics</a> 頁面...</p>
                <p>如果未自動跳轉，請點擊上方鏈接。</p>
            </div>
        </body>
    </html>
    '''

@app.route('/metrics')
def metrics():
    ap_list = get_ap_config()
    
    # 更新每個接入點的指標
    for ap in ap_list:
        client_count = get_client_count(ap)
        clients_gauge.labels(ap=ap['name'], ip=ap['ip']).set(client_count)
    
    return Response(generate_latest(REGISTRY), mimetype="text/plain")

if __name__ == "__main__":
    print("啟動 Aruba CLI 匯出器...")
    print("請訪問 http://localhost:9130/metrics 查看指標數據")
    app.run(host="0.0.0.0", port=9130) 