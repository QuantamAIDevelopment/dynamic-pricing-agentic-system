# Dynamic Pricing Agentic AI System

A comprehensive, multi-agent AI system for dynamic pricing optimization in e-commerce, featuring advanced tools, memory, reflection, and reasoning capabilities.

## 🚀 Features

### **Agentic AI Components**
- **Tools**: Specialized tools for pricing analysis, demand forecasting, and inventory management
- **Memory**: Persistent context retention across pricing cycles
- **Reflection**: Agents reflect on their decisions and learn from feedback
- **Reasoning**: Step-by-step reasoning chains for transparent decision-making

### **Multi-Agent Architecture**
- **Supervisor Agent**: Orchestrates the entire pricing workflow
- **Pricing Decision Agent**: Makes optimal pricing decisions using comprehensive analysis
- **Demand Analysis Agent**: Analyzes demand patterns and forecasts future demand
- **Inventory Tracking Agent**: Monitors inventory levels and optimizes stock management
- **Competitor Monitoring Agent**: Tracks competitor prices and market positioning
- **Web Scraping Agent**: Gathers real-time data from e-commerce platforms

### **Advanced Analytics**
- Price elasticity calculations
- Sales velocity analysis
- Demand forecasting
- Inventory optimization
- Competitor price analysis
- Market sentiment assessment

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Supervisor    │    │   Pricing       │    │   Demand        │
│     Agent       │    │   Decision      │    │     Agent       │
│                 │    │     Agent       │    │     Agent       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Inventory     │    │   Competitor    │    │   Web Scraping  │
│   Tracking      │    │   Monitoring    │    │     Agent       │
│     Agent       │    │     Agent       │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         └───────────────────────┼───────────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Tools Layer   │
                    │                 │
                    │ • Pricing Tools │
                    │ • Demand Tools  │
                    │ • Inventory     │
                    │   Tools         │
                    │ • Scraping      │
                    │   Tools         │
                    └─────────────────┘
                                 │
                    ┌─────────────────┐
                    │   Database      │
                    │                 │
                    │ • Products      │
                    │ • Sales Data    │
                    │ • Price History │
                    │ • Agent         │
                    │   Decisions     │
                    └─────────────────┘
```

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd dynamic-pricing-agentic-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Initialize the database**
   ```bash
   # Run the schema and dummy data scripts
   psql -d your_database -f scripts/schema.sql
   psql -d your_database -f scripts/dummy_products.sql
   psql -d your_database -f scripts/dummy_competitor_prices.sql
   psql -d your_database -f scripts/dummy_sales_data.sql
   psql -d your_database -f scripts/dummy_agent_decisions.sql
   ```

5. **Start the API server**
   ```bash
   python src/main.py
   ```

## 📊 API Endpoints

### **Supervisor Agent**
- `POST /agents/supervisor` - Run complete pricing cycle
- `GET /agents/supervisor/history/{product_id}` - Get pricing history

### **Pricing Decision Agent**
- `POST /agents/pricing/analyze` - Run comprehensive pricing analysis
- `GET /agents/pricing/recommendations/{product_id}` - Get pricing recommendations
- `GET /agents/pricing/optimal-price/{product_id}` - Calculate optimal price

### **Demand Analysis Agent**
- `POST /agents/demand/analyze` - Run demand analysis
- `GET /agents/demand/score/{product_id}` - Get demand score

### **Inventory Tracking Agent**
- `POST /agents/inventory/analyze` - Run inventory analysis
- `GET /agents/inventory/health/{product_id}` - Get inventory health
- `GET /agents/inventory/optimize/{product_id}` - Get inventory optimization

### **Competitor Monitoring Agent**
- `POST /agents/competitor/monitor` - Monitor competitor prices
- `GET /agents/competitor-monitoring/similar/{product_name}` - Find similar products

### **Comprehensive Analysis**
- `POST /agents/comprehensive-analysis` - Run all analyses for a product

## 🔧 Tools

### **Pricing Tools**
- `calculate_price_elasticity()` - Calculate price sensitivity
- `analyze_competitor_pricing()` - Analyze competitor price positioning
- `calculate_optimal_price()` - Determine optimal price point
- `get_pricing_recommendations()` - Get comprehensive pricing advice

### **Demand Tools**
- `calculate_sales_velocity()` - Calculate units sold per day
- `calculate_demand_score()` - Compute demand score from multiple factors
- `forecast_demand()` - Predict future demand
- `analyze_demand_signals()` - Analyze demand patterns

### **Inventory Tools**
- `calculate_reorder_point()` - Calculate optimal reorder point
- `analyze_inventory_health()` - Assess inventory status
- `forecast_inventory_needs()` - Predict inventory requirements
- `optimize_inventory_levels()` - Get inventory optimization recommendations

## 🧠 Agentic AI Features

### **Memory & Context**
- Agents maintain conversation history and context
- Previous decisions influence future recommendations
- Learning from historical pricing cycles

### **Reflection & Reasoning**
- Agents reflect on their decisions and outcomes
- Step-by-step reasoning chains for transparency
- Confidence scores for all recommendations

### **Feedback Integration**
- Agents listen for feedback and adjust behavior
- Continuous improvement through feedback loops
- Adaptive decision-making based on outcomes

## 📈 Usage Examples

### **Run Comprehensive Analysis**
```python
import requests

# Run complete analysis for a product
response = requests.post("http://localhost:8000/agents/comprehensive-analysis", 
                        json={"product_id": "P1001"})
result = response.json()
print(f"Overall status: {result['data']['overall_assessment']['status']}")
```

### **Get Pricing Recommendations**
```python
# Get pricing recommendations
response = requests.get("http://localhost:8000/agents/pricing/recommendations/P1001")
recommendations = response.json()
print(f"Recommendation: {recommendations['recommendations']['overall_recommendation']}")
```

### **Analyze Demand**
```python
# Analyze demand patterns
response = requests.post("http://localhost:8000/agents/demand/analyze",
                        json={"product_id": "P1001", "days": 30})
demand_data = response.json()
print(f"Demand level: {demand_data['data']['overall_demand_assessment']['demand_level']}")
```

## 🔄 Pricing Workflow

1. **Data Collection**: Web scraping agents gather competitor data
2. **Demand Analysis**: Analyze sales velocity and demand patterns
3. **Inventory Assessment**: Check stock levels and reorder points
4. **Competitor Analysis**: Compare pricing with market competitors
5. **Pricing Decision**: Calculate optimal price using all factors
6. **Implementation**: Update prices and monitor results
7. **Reflection**: Agents reflect on outcomes and learn

## 📊 Data Models

### **Enhanced Product Model**
- Sales velocity tracking
- Price elasticity calculations
- Market positioning
- Demand scores

### **Agent Decisions**
- Reasoning chains
- Reflection on decisions
- Confidence scores
- Input/output data tracking

### **Comprehensive Analytics**
- Price history with reasons
- Sales data with demand signals
- Inventory levels with optimization
- Competitor price tracking

## 🚀 E-commerce Integration

The system is designed for easy integration with e-commerce platforms:

- **RESTful API**: Standard JSON endpoints
- **Webhook Support**: Real-time price updates
- **Batch Processing**: Bulk pricing operations
- **Monitoring**: Real-time system health checks

## 🔧 Configuration

### **Environment Variables**
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/dbname

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# LLM Configuration
OPENAI_API_KEY=your_openai_key
GROQ_API_KEY=your_groq_key

# Pricing Cycle
PRICING_CYCLE_INTERVAL_MINUTES=30

# Vector Database
PINECONE_API_KEY=your_pinecone_key
```

## 📝 Monitoring & Logging

- **Structured Logging**: All agent actions are logged
- **Performance Metrics**: Response times and success rates
- **Error Tracking**: Comprehensive error handling and reporting
- **Health Checks**: System status monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in the repository
- Check the documentation
- Review the API examples

---

**Built with ❤️ for intelligent e-commerce pricing**
