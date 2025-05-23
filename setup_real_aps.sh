#!/bin/bash

echo "=== Aruba AP 真實監控環境設置 ==="
echo ""

# 檢查是否存在配置文件
if [ -f "ap_config.json" ]; then
    echo "發現現有的 ap_config.json 文件"
    echo "內容："
    cat ap_config.json
    echo ""
    read -p "是否要重新配置？(y/n): " reconfigure
    if [ "$reconfigure" != "y" ]; then
        echo "保持現有配置"
        exit 0
    fi
fi

echo "請提供您的 Aruba AP 連接資訊："
echo ""

# 初始化 JSON 數組
echo "[" > ap_config.json

# 詢問 AP 數量
read -p "請輸入要監控的 AP 數量: " ap_count

for ((i=1; i<=ap_count; i++)); do
    echo ""
    echo "=== 設置第 $i 個 AP ==="
    read -p "AP 名稱: " ap_name
    read -p "AP IP 地址: " ap_ip
    read -p "SSH 用戶名: " ap_username
    read -s -p "SSH 密碼: " ap_password
    echo ""
    
    # 添加 JSON 對象
    if [ $i -gt 1 ]; then
        echo "  ," >> ap_config.json
    fi
    
    echo "  {" >> ap_config.json
    echo "    \"name\": \"$ap_name\"," >> ap_config.json
    echo "    \"ip\": \"$ap_ip\"," >> ap_config.json
    echo "    \"username\": \"$ap_username\"," >> ap_config.json
    echo "    \"password\": \"$ap_password\"" >> ap_config.json
    echo "  }" >> ap_config.json
done

# 結束 JSON 數組
echo "]" >> ap_config.json

echo ""
echo "✅ AP 配置已保存到 ap_config.json"
echo ""
echo "配置內容（隱藏密碼）："
sed 's/"password": "[^"]*"/"password": "***"/' ap_config.json

echo ""
echo "下一步：運行 'make down && make up' 來啟動監控服務" 