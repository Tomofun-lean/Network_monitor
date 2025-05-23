#!/bin/bash

echo "=== Aruba AP 監控環境驗證 ==="
echo ""

# 檢查必要文件
echo "🔍 檢查必要文件..."

if [ ! -f "ap_config.json" ]; then
    echo "❌ 缺少 ap_config.json 文件"
    echo "請先運行 ./setup_real_aps.sh 來配置 AP 連接信息"
    exit 1
fi

if [ ! -f "docker-compose.yml" ]; then
    echo "❌ 缺少 docker-compose.yml 文件"
    exit 1
fi

echo "✅ 所有必要文件都存在"
echo ""

# 檢查 Docker 服務
echo "🔍 檢查 Docker 服務狀態..."
if ! docker --version >/dev/null 2>&1; then
    echo "❌ Docker 未安裝或未運行"
    exit 1
fi

if ! docker-compose --version >/dev/null 2>&1; then
    echo "❌ Docker Compose 未安裝"
    exit 1
fi

echo "✅ Docker 和 Docker Compose 可用"
echo ""

# 檢查端口是否被佔用
echo "🔍 檢查端口佔用情況..."
check_port() {
    port=$1
    service_name=$2
    if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
        echo "⚠️  端口 $port ($service_name) 已被佔用"
        echo "   請停止相關服務或修改 docker-compose.yml 中的端口配置"
        return 1
    else
        echo "✅ 端口 $port ($service_name) 可用"
        return 0
    fi
}

ports_ok=true
check_port 9090 "Prometheus" || ports_ok=false
check_port 3001 "Grafana" || ports_ok=false
check_port 9115 "SNMP Exporter" || ports_ok=false
check_port 9131 "Fake Exporter" || ports_ok=false

if [ "$ports_ok" = false ]; then
    echo ""
    echo "❌ 有端口衝突，請解決後再重試"
    exit 1
fi

echo ""

# 顯示配置信息
echo "🔍 當前 AP 配置："
sed 's/"password": "[^"]*"/"password": "***"/' ap_config.json
echo ""

# 檢查網絡連通性
echo "🔍 測試 AP 網絡連通性..."

# 使用 Python 解析 JSON 配置
python3 -c "
import json
import subprocess
import sys

try:
    with open('ap_config.json', 'r') as f:
        config = json.load(f)
    
    unconfigured = False
    for ap in config:
        ap_name = ap['name']
        ap_ip = ap['ip']
        
        if ap_ip == '請填入您的AP IP地址':
            print(f'⚠️  {ap_name}: 尚未配置真實 IP 地址')
            unconfigured = True
            continue
        
        # 測試網絡連通性
        result = subprocess.run(['ping', '-c', '1', '-W', '3', ap_ip], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f'✅ {ap_name} ({ap_ip}): 網絡可達')
        else:
            print(f'❌ {ap_name} ({ap_ip}): 網絡不可達')
    
    if unconfigured:
        sys.exit(1)
        
except Exception as e:
    print(f'❌ 解析配置文件時出錯: {e}')
    sys.exit(1)
"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 請先完成 AP 配置："
    echo "   ./setup_real_aps.sh"
    echo ""
    exit 1
fi

echo ""
echo "=== 部署建議 ==="
echo "✅ 環境檢查完成，建議的部署步驟："
echo ""
echo "1. 停止現有服務（如果有）："
echo "   make down"
echo ""
echo "2. 啟動監控服務："
echo "   make up"
echo ""
echo "3. 檢查服務狀態："
echo "   make test"
echo ""
echo "4. 訪問監控界面："
echo "   - Grafana: http://localhost:3001 (admin/admin)"
echo "   - Prometheus: http://localhost:9090"
echo "   - AP 指標: http://localhost:9130/metrics"
echo ""
echo "5. 驗證指標收集："
echo "   curl http://localhost:9130/metrics" 