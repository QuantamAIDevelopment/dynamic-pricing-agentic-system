import pytest
import httpx

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_root():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/")
        assert resp.status_code == 200
        print("/ response:", resp.json())

@pytest.mark.asyncio
async def test_health():
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/health")
        assert resp.status_code == 200
        print("/health response:", resp.json())

@pytest.mark.asyncio
async def test_agents_supervisor():
    async with httpx.AsyncClient() as client:
        data = {"product_name": "Test Product"}
        resp = await client.post(f"{BASE_URL}/agents/supervisor", json=data)
        print("/agents/supervisor response:", resp.json())

@pytest.mark.asyncio
async def test_agents_supervisor_history():
    async with httpx.AsyncClient() as client:
        product_id = "1"
        resp = await client.get(f"{BASE_URL}/agents/supervisor/history/{product_id}")
        print("/agents/supervisor/history response:", resp.json())

@pytest.mark.asyncio
async def test_agents_pricing_analyze():
    async with httpx.AsyncClient() as client:
        data = {"product_id": "1", "include_forecast": True}
        resp = await client.post(f"{BASE_URL}/agents/pricing/analyze", json=data)
        print("/agents/pricing/analyze response:", resp.json())

@pytest.mark.asyncio
async def test_agents_pricing_recommendations():
    async with httpx.AsyncClient() as client:
        product_id = "1"
        resp = await client.get(f"{BASE_URL}/agents/pricing/recommendations/{product_id}")
        print("/agents/pricing/recommendations response:", resp.json())

@pytest.mark.asyncio
async def test_agents_pricing_optimal_price():
    async with httpx.AsyncClient() as client:
        product_id = "1"
        resp = await client.get(f"{BASE_URL}/agents/pricing/optimal-price/{product_id}")
        print("/agents/pricing/optimal-price response:", resp.json())

@pytest.mark.asyncio
async def test_agents_demand_analyze():
    async with httpx.AsyncClient() as client:
        data = {"product_id": "1", "days": 30}
        resp = await client.post(f"{BASE_URL}/agents/demand/analyze", json=data)
        print("/agents/demand/analyze response:", resp.json())

@pytest.mark.asyncio
async def test_agents_demand_score():
    async with httpx.AsyncClient() as client:
        product_id = "1"
        resp = await client.get(f"{BASE_URL}/agents/demand/score/{product_id}")
        print("/agents/demand/score response:", resp.json())

@pytest.mark.asyncio
async def test_agents_inventory_analyze():
    async with httpx.AsyncClient() as client:
        data = {"product_id": "1", "days_ahead": 30}
        resp = await client.post(f"{BASE_URL}/agents/inventory/analyze", json=data)
        print("/agents/inventory/analyze response:", resp.json())

@pytest.mark.asyncio
async def test_agents_inventory_health():
    async with httpx.AsyncClient() as client:
        product_id = "1"
        resp = await client.get(f"{BASE_URL}/agents/inventory/health/{product_id}")
        print("/agents/inventory/health response:", resp.json())

@pytest.mark.asyncio
async def test_agents_inventory_optimize():
    async with httpx.AsyncClient() as client:
        product_id = "1"
        resp = await client.get(f"{BASE_URL}/agents/inventory/optimize/{product_id}")
        print("/agents/inventory/optimize response:", resp.json())

@pytest.mark.asyncio
async def test_agents_inventory_tracking():
    async with httpx.AsyncClient() as client:
        data = {"product_id": "1", "stock_level": 100}
        resp = await client.post(f"{BASE_URL}/agents/inventory-tracking", json=data)
        print("/agents/inventory-tracking response:", resp.json())

@pytest.mark.asyncio
async def test_agents_competitor_monitor():
    async with httpx.AsyncClient() as client:
        data = {"product_id": "1"}
        resp = await client.post(f"{BASE_URL}/agents/competitor/monitor", json=data)
        print("/agents/competitor/monitor response:", resp.json())

@pytest.mark.asyncio
async def test_agents_competitor_monitoring_similar():
    async with httpx.AsyncClient() as client:
        product_name = "Test Product"
        category = "Test Category"
        resp = await client.get(f"{BASE_URL}/agents/competitor-monitoring/similar/{product_name}?category={category}&limit=5")
        print("/agents/competitor-monitoring/similar response:", resp.json())

@pytest.mark.asyncio
async def test_agents_comprehensive_analysis():
    async with httpx.AsyncClient() as client:
        data = {"product_id": "1"}
        resp = await client.post(f"{BASE_URL}/agents/comprehensive-analysis", json=data)
        print("/agents/comprehensive-analysis response:", resp.json())

@pytest.mark.asyncio
async def test_products():
    async with httpx.AsyncClient() as client:
        data = {
            "name": "Test Product",
            "category": "Test Category",
            "competitor": "Test Competitor",
            "price": 10.0,
            "competitor_price": 9.5,
            "competitor_url": "http://example.com"
        }
        resp = await client.post(f"{BASE_URL}/products", json=data)
        print("/products response:", resp.json()) 