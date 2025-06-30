CREATE TABLE products (
    id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(200),
    category VARCHAR(100),
    base_price DECIMAL(10,2),
    current_price DECIMAL(10,2),
    cost_price DECIMAL(10,2),
    stock_level INTEGER,
    demand_score DECIMAL(3,2),
    last_updated DATETIME
);

CREATE TABLE price_history (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(20),
    old_price DECIMAL(10,2),
    new_price DECIMAL(10,2),
    change_reason TEXT,
    agent_name VARCHAR(100),
    confidence_score DECIMAL(3,2),
    timestamp DATETIME
);

CREATE TABLE competitor_prices (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(20),
    competitor_name VARCHAR(100),
    competitor_price DECIMAL(10,2),
    scraped_at DATETIME
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
    timestamp DATETIME
);

CREATE TABLE sales_data (
    id INTEGER PRIMARY KEY,
    product_id VARCHAR(20),
    quantity_sold INTEGER,
    sale_price DECIMAL(10,2),
    sale_date DATE,
    demand_signal DECIMAL(3,2)
);