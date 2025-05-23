.PHONY: up down test help

help:
	@echo "使用方法:"
	@echo "  make up     - 啟動所有服務 (docker-compose up -d)"
	@echo "  make down   - 停止所有服務 (docker-compose down)"
	@echo "  make test   - 測試真實 CLI 匯出器端點是否正常工作"
	@echo "  make help   - 顯示此幫助訊息"

up:
	docker-compose up -d

down:
	docker-compose down

test:
	@echo "測試 Aruba CLI 匯出器 (真實模式)..."
	@curl -s http://localhost:9130/metrics | head -n 15
	@echo ""
	@echo "檢查 AP 客戶端指標:"
	@curl -s http://localhost:9130/metrics | grep "aruba_ap_clients_total" 