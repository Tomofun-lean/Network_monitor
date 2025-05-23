#!/bin/bash

echo "=== Grafana 數據源配置修復工具 ==="
echo ""

# 等待 Grafana 服務啟動
echo "🔍 等待 Grafana 服務啟動..."
for i in {1..30}; do
    if curl -s http://localhost:3001/api/health >/dev/null 2>&1; then
        echo "✅ Grafana 服務已啟動"
        break
    fi
    echo "   等待中... ($i/30)"
    sleep 2
done

# 檢查 Prometheus 可用性
echo ""
echo "🔍 檢查 Prometheus 服務..."
if curl -s http://localhost:9090/-/ready >/dev/null 2>&1; then
    echo "✅ Prometheus 服務正常"
else
    echo "❌ Prometheus 服務不可用"
    exit 1
fi

echo ""
echo "📝 Grafana 數據源配置說明："
echo ""
echo "1. 打開瀏覽器訪問: http://localhost:3001"
echo "2. 使用帳號密碼登入: admin / admin"
echo "3. 點擊左側齒輪圖標 → Data Sources"
echo "4. 點擊 'Add data source'"
echo "5. 選擇 'Prometheus'"
echo "6. 在 URL 欄位填入: http://prometheus:9090"
echo "7. 點擊 'Save & Test'"
echo ""
echo "🎯 數據查詢範例："
echo "   - aruba_ap_clients_total"
echo "   - aruba_ap_connection_status"
echo ""
echo "📊 導入儀表板："
echo "   1. 點擊左側 + 號 → Import"
echo "   2. 上傳文件: grafana_prom/dashboards/aruba_overview.json"
echo "   3. 選擇剛建立的 Prometheus 數據源"
echo ""

# 測試數據可用性
echo "🧪 測試數據可用性:"
prometheus_query="http://localhost:9090/api/v1/query?query=aruba_ap_clients_total"
if curl -s "$prometheus_query" | grep -q "aruba_ap_clients_total"; then
    echo "✅ AP 客戶端指標數據可用"
else
    echo "⚠️  AP 客戶端指標數據暫不可用（AP 連接問題）"
fi

echo ""
echo "🚀 現在您可以在 Grafana 中看到監控數據了！" 