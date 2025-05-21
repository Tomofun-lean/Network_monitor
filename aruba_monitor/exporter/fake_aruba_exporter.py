"""
啟動方式：
1. 建立並啟用 conda 環境：
   conda env create -f environment.yml
   conda activate aruba-monitor
2. 執行程式：python fake_aruba_exporter.py (在 exporter 目錄下)
3. 訪問 http://localhost:9131/metrics 查看指標
"""
from flask import Flask, Response, redirect, url_for
from prometheus_client import Counter, Gauge, generate_latest, REGISTRY
import random

app = Flask(__name__)

# 模擬的 Aruba 接入點清單
APS = [
    {"name": "BA535", "ip": "172.17.1.6"},
    {"name": "FW535", "ip": "172.17.1.7"},
    {"name": "LN535", "ip": "172.17.1.8"},
    {"name": "kiki",  "ip": "172.17.1.11"}
]

# 定義指標
clients = Gauge('aruba_ap_clients_total', '接入點的客戶端數量', ['ap', 'ip'])
radio_util = Gauge('aruba_radio_util_percent', '無線電使用率百分比', ['ap', 'ip'])
noise_floor = Gauge('aruba_noise_floor_dbm', '噪聲底限 (dBm)', ['ap', 'ip'])

@app.route('/')
def index():
    """根路徑，提供友好的提示訊息和自動重定向"""
    return '''
    <html>
        <head>
            <meta http-equiv="refresh" content="3;url=/metrics">
            <title>Aruba AP 模擬匯出器</title>
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
                <h1>Aruba AP 模擬匯出器</h1>
                <p>這是一個 Prometheus 匯出器，用於模擬 Aruba 接入點的指標數據。</p>
                <p>正在重定向到 <a href="/metrics">/metrics</a> 頁面...</p>
                <p>如果未自動跳轉，請點擊上方鏈接。</p>
            </div>
        </body>
    </html>
    '''

@app.route('/metrics')
def metrics():
    # 為每個接入點更新指標
    for ap in APS:
        clients.labels(ap=ap["name"], ip=ap["ip"]).set(random.randint(0, 50))
        radio_util.labels(ap=ap["name"], ip=ap["ip"]).set(round(random.uniform(10, 90), 1))
        noise_floor.labels(ap=ap["name"], ip=ap["ip"]).set(random.randint(-95, -80))
    
    # 生成指標輸出
    return Response(generate_latest(REGISTRY), mimetype="text/plain")

if __name__ == "__main__":
    print("啟動 Aruba AP 模擬匯出器...")
    print("請確保您在 'aruba_monitor/exporter' 目錄下執行此腳本。")
    print("請訪問 http://localhost:9131/metrics 查看指標數據")
    print("或訪問 http://localhost:9131/ 進行自動重定向到指標頁面")
    app.run(host="0.0.0.0", port=9131) 