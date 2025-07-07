# Dynamic Pricing Agent System - Agent Implementation

This document describes the implementation of the three core agents in the Dynamic Pricing Agent System: **Web Scraping Agent**, **Competitor Monitoring Agent**, and **Supervisor Agent**.

## Overview

The system implements a multi-agent architecture using CrewAI for coordination, LangChain for memory management, Redis for inter-agent communication, and Pinecone for vector storage. Each agent has specific responsibilities and communicates with others through well-defined interfaces.

## Architecture

```
┌─────────────────┐    ┌─────────────────────┐    ┌─────────────────┐
│  Web Scraping   │───▶│ Competitor Monitoring│───▶│   Supervisor    │
│     Agent       │    │      Agent          │    │     Agent       │
└─────────────────┘    └─────────────────────┘    └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
    ┌─────────┐            ┌─────────┐              ┌─────────┐
    │  Redis  │            │Pinecone │              │PostgreSQL│
    │ Pub/Sub │            │ Vector  │              │ Database │
    └─────────┘            │  Store  │              └─────────┘
```

## Agents Implementation

### 1. Web Scraping Agent (`src/agents/web_scraping_agent.py`)

**Purpose**: Scrapes competitor product data from e-commerce platforms and publishes it to Redis for other agents to consume.

**Key Features**:
- Uses LangChain tools for web scraping
- Integrates with existing search and scrape tools
- Publishes scraped data to Redis Pub/Sub channel `scraped_data`
- Stores backup data in Redis list `pending_competitor_data`
- Handles multiple e-commerce platforms (Amazon, etc.)

**API Endpoint**: `POST /agents/web-scraping`

**Example Usage**:
```python
from agents import run_web_scraping_agent

result = run_web_scraping_agent({
    "domain": "amazon.com",
    "category": "electronics",
    "product_name": "iPhone 15"
})
```

### 2. Competitor Monitoring Agent (`src/agents/competitor_monitoring_agent.py`)

**Purpose**: Monitors competitor data, creates embeddings using Sentence Transformers, and stores them in Pinecone for similarity search.

**Key Features**:
- Uses Sentence Transformers (`all-MiniLM-L6-v2`) for embeddings
- Stores embeddings in Pinecone vector database
- Subscribes to Redis Pub/Sub for real-time updates
- Provides similarity search functionality
- Maintains price history in PostgreSQL
- Handles vector similarity search for finding similar products

**API Endpoints**:
- `POST /agents/competitor-monitoring`
- `GET /agents/competitor-monitoring/similar/{product_name}`

**Example Usage**:
```python
from agents import run_competitor_monitoring_agent, competitor_monitoring_agent

# Process new data
result = run_competitor_monitoring_agent(product_data)

# Find similar products
similar_products = competitor_monitoring_agent.get_similar_products(
    "iPhone 15", "electronics", limit=5
)
```

### 3. Supervisor Agent (`src/agents/supervisor_agent.py`)

**Purpose**: Orchestrates the entire pricing cycle, coordinates all sub-agents using CrewAI, and maintains context using LangChain memory.

**Key Features**:
- Uses CrewAI for multi-agent coordination
- Implements LangChain memory for context retention
- Manages pricing cycles with configurable intervals
- Coordinates all sub-agents in a workflow
- Provides pricing history and analysis
- Supports continuous monitoring mode

**API Endpoints**:
- `POST /agents/supervisor`
- `GET /agents/supervisor/history/{product_id}`

**Example Usage**:
```python
from agents import run_supervisor_agent

products = [
    {
        "product_id": "prod_001",
        "product_name": "iPhone 15",
        "domain": "amazon.com",
        "category": "electronics"
    }
]

result = run_supervisor_agent({"products": products})
```

## Installation and Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `config.env.example` to `.env` and configure:

```bash
cp config.env.example .env
```

Required environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `OPENROUTER_API_KEY` or `GROQ_API_KEY`: LLM API key
- `REDIS_HOST`, `REDIS_PORT`: Redis configuration
- `PINECONE_API_KEY`: Pinecone API key (optional but recommended)

### 3. Database Setup

```bash
# Run database migrations
alembic upgrade head
```

### 4. Start Services

```bash
# Start Redis (if not already running)
redis-server

# Start PostgreSQL (if not already running)
# Follow your system's PostgreSQL setup instructions

# Start the application
python src/main.py
```

## API Usage Examples

### 1. Run Web Scraping

```bash
curl -X POST "http://localhost:8000/agents/web-scraping" \
  -H "Content-Type: application/json" \
  -d '{
    "domain": "amazon.com",
    "category": "electronics",
    "product_name": "iPhone 15"
  }'
```

### 2. Run Competitor Monitoring

```bash
curl -X POST "http://localhost:8000/agents/competitor-monitoring" \
  -H "Content-Type: application/json" \
  -d '{
    "product_data": {
      "product_id": "prod_001",
      "product_name": "iPhone 15",
      "competitor_name": "amazon.com",
      "competitor_price": 999.99,
      "category": "electronics",
      "scraped_at": "2024-01-01T12:00:00Z"
    }
  }'
```

### 3. Run Supervisor Agent

```bash
curl -X POST "http://localhost:8000/agents/supervisor" \
  -H "Content-Type: application/json" \
  -d '{
    "products": [
      {
        "product_id": "prod_001",
        "product_name": "iPhone 15",
        "domain": "amazon.com",
        "category": "electronics"
      }
    ]
  }'
```

### 4. Get Similar Products

```bash
curl "http://localhost:8000/agents/competitor-monitoring/similar/iPhone%2015?category=electronics&limit=5"
```

### 5. Get Pricing History

```bash
curl "http://localhost:8000/agents/supervisor/history/prod_001?days=30"
```

## Agent Communication Flow

1. **Web Scraping Agent** scrapes competitor data and publishes to Redis
2. **Competitor Monitoring Agent** subscribes to Redis, processes data, creates embeddings, and stores in Pinecone
3. **Supervisor Agent** orchestrates the entire cycle, coordinates all agents, and maintains context

## Key Features

### Redis Pub/Sub Integration
- Real-time communication between agents
- Backup data storage in Redis lists
- Fault-tolerant message processing

### Vector Similarity Search
- Sentence Transformers for embedding generation
- Pinecone for efficient similarity search
- Product matching and comparison

### CrewAI Coordination
- Multi-agent workflow management
- Task delegation and coordination
- Sequential and parallel processing support

### LangChain Memory
- Context retention across pricing cycles
- Conversation history management
- Learning from previous decisions

## Error Handling

All agents include comprehensive error handling:
- Graceful degradation when services are unavailable
- Retry mechanisms for transient failures
- Detailed logging for debugging
- Fallback strategies for missing data

## Monitoring and Logging

- Structured logging with different levels
- Health check endpoints
- Performance metrics tracking
- Error reporting and alerting

## Future Enhancements

1. **Demand Analysis Agent**: Implement sales data analysis and demand prediction
2. **Inventory Tracking Agent**: Add real-time inventory monitoring
3. **Pricing Decision Agent**: Implement advanced pricing algorithms
4. **Dashboard**: Add Grafana integration for monitoring
5. **Retraining**: Implement LLM retraining based on feedback

## Troubleshooting

### Common Issues

1. **Redis Connection Error**: Ensure Redis is running and accessible
2. **Pinecone API Error**: Check API key and index configuration
3. **Database Connection Error**: Verify PostgreSQL connection string
4. **LLM API Error**: Ensure valid API key is configured

### Debug Mode

Enable debug logging by setting:
```bash
export LOG_LEVEL=DEBUG
```

## Contributing

When adding new agents or modifying existing ones:
1. Follow the established patterns for agent implementation
2. Add comprehensive error handling
3. Include API endpoints for testing
4. Update documentation
5. Add unit tests

## License

This implementation is part of the Dynamic Pricing Agentic System and follows the project's licensing terms. 