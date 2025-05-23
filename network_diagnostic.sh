#!/bin/bash

echo "=== Aruba AP 網絡診斷工具 ==="
echo ""

# 讀取AP配置
if [ ! -f "ap_config.json" ]; then
    echo "❌ 找不到 ap_config.json 文件"
    exit 1
fi

echo "🔍 診斷結果："
echo ""

# 使用Python解析JSON並進行詳細測試
python3 -c "
import json
import subprocess
import socket
import sys

def test_port(ip, port, timeout=5):
    try:
        socket.setdefaulttimeout(timeout)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((ip, port))
        sock.close()
        return result == 0
    except:
        return False

try:
    with open('ap_config.json', 'r') as f:
        config = json.load(f)
    
    for ap in config:
        name = ap['name']
        ip = ap['ip']
        
        print(f'📡 測試 {name} ({ip}):')
        
        # 1. Ping 測試
        ping_result = subprocess.run(['ping', '-c', '1', '-W', '3', ip], 
                                   capture_output=True, text=True)
        if ping_result.returncode == 0:
            print(f'  ✅ Ping: 成功')
        else:
            print(f'  ❌ Ping: 失敗')
            
        # 2. SSH 端口測試  
        ssh_open = test_port(ip, 22, 5)
        if ssh_open:
            print(f'  ✅ SSH端口(22): 開放')
        else:
            print(f'  ❌ SSH端口(22): 關閉或不可達')
            
        # 3. 路由測試
        route_result = subprocess.run(['ip', 'route', 'get', ip], 
                                    capture_output=True, text=True)
        if route_result.returncode == 0:
            print(f'  ✅ 路由: 可達')
            print(f'     路徑: {route_result.stdout.strip()}')
        else:
            print(f'  ❌ 路由: 無法到達')
            
        print()
        
except Exception as e:
    print(f'❌ 診斷過程出錯: {e}')
    sys.exit(1)
"

echo ""
echo "🔧 建議解決方案："
echo ""
echo "如果所有AP都無法連接，可能的原因："
echo "1. **網段衝突**: 172.17.x.x 與 Docker 網段衝突"
echo "   解決方案: 請確認AP的真實IP地址是否正確"
echo ""
echo "2. **防火牆阻擋**: 系統防火牆可能阻擋連接"
echo "   檢查命令: sudo iptables -L"
echo ""
echo "3. **AP離線**: 設備可能未開機或網絡斷開"
echo "   解決方案: 檢查設備電源和網線連接"
echo ""
echo "4. **網絡配置**: 本機無法路由到AP網段"
echo "   檢查命令: ip route show"
echo ""
echo "5. **SSH服務**: AP的SSH服務可能被禁用"
echo "   解決方案: 通過AP管理界面啟用SSH"
echo ""
echo "📝 要修改AP IP地址，請運行: ./setup_real_aps.sh" 