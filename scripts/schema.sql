CREATE TABLE products (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(100),
    base_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    stock_level INTEGER,
    demand_score DECIMAL(3,2),
    sales_velocity DECIMAL(10,2),
    price_elasticity DECIMAL(5,2),
    market_position VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    last_updated DATETIME
);

CREATE TABLE IF NOT EXISTS price_history (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) REFERENCES products(id),
    old_price NUMERIC(10, 2),
    new_price NUMERIC(10, 2),
    change_reason VARCHAR(255),
    agent_name VARCHAR(100),
    confidence_score NUMERIC(3, 2),
    timestamp TIMESTAMP
);

CREATE TABLE competitor_prices (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(20),
    product_name VARCHAR(255),
    category VARCHAR(100),
    competitor_name VARCHAR(100),
    competitor_price DECIMAL(10,2),
    competitor_url VARCHAR(500),
    availability BOOLEAN DEFAULT TRUE,
    shipping_cost DECIMAL(10,2),
    rating DECIMAL(3,2),
    review_count INTEGER,
    scraped_at DATETIME,
    confidence_score DECIMAL(3,2) DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS feedback_log (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    feedback_type VARCHAR(100),
    message TEXT,
    related_product_id VARCHAR(20) REFERENCES products(id),
    severity VARCHAR(20),
    action_taken TEXT,
    timestamp TIMESTAMP
);

CREATE TABLE IF NOT EXISTS demand_scores (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) REFERENCES products(id),
    demand_score NUMERIC(3, 2),
    sales_velocity NUMERIC(10, 2),
    price_advantage_pct NUMERIC(10, 2),
    stock_level INTEGER,
    llm_explanation TEXT,
    calculated_at TIMESTAMP
);

CREATE TABLE IF NOT EXISTS inventory_levels (
    id SERIAL PRIMARY KEY,
    product_id VARCHAR(20) REFERENCES products(id),
    stock_level INTEGER,
    reorder_point INTEGER,
    max_stock INTEGER,
    last_updated TIMESTAMP
);

CREATE TABLE agent_decisions (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(20),
    agent_name VARCHAR(100),
    decision_type VARCHAR(100),
    input_data TEXT,
    output_data TEXT,
    confidence_score DECIMAL(3,2),
    explanation TEXT,
    reflection TEXT,
    reasoning_chain JSON,
    timestamp DATETIME
);

CREATE TABLE sales_data (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(20) REFERENCES products(id),
    quantity_sold INTEGER,
    sale_price DECIMAL(10,2),
    sale_date DATETIME,
    demand_signal DECIMAL(3,2),
    customer_segment VARCHAR(50),
    sales_channel VARCHAR(50),
    discount_applied DECIMAL(5,2),
    transaction_id VARCHAR(100)
);