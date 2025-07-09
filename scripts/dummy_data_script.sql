INSERT INTO products (id, name, category, base_price, current_price, cost_price, stock_level, demand_score, sales_velocity, price_elasticity, market_position, is_active, last_updated) VALUES
('P1001', 'Wireless Mouse', 'Electronics', 15.99, 17.99, 10.00, 120, 0.85, 8.5, -1.2, 'mid-range', true, '2024-06-01 10:00:00'),
('P1002', 'Bluetooth Headphones', 'Electronics', 45.00, 49.99, 30.00, 80, 0.92, 12.3, -0.8, 'premium', true, '2024-06-01 10:05:00'),
('P1003', 'Yoga Mat', 'Sports', 20.00, 22.50, 12.00, 200, 0.78, 15.7, -1.5, 'budget', true, '2024-06-01 10:10:00'),
('P1004', 'Stainless Steel Water Bottle', 'Home & Kitchen', 12.00, 13.50, 7.00, 150, 0.81, 6.2, -1.1, 'mid-range', true, '2024-06-01 10:15:00'),
('P1005', 'Desk Lamp', 'Home & Office', 25.00, 27.99, 15.00, 60, 0.74, 4.8, -0.9, 'premium', true, '2024-06-01 10:20:00'),
('P1006', 'Smartphone Case', 'Electronics', 8.99, 9.99, 5.00, 300, 0.88, 25.1, -1.8, 'budget', true, '2024-06-01 10:25:00'),
('P1007', 'Coffee Maker', 'Home & Kitchen', 89.99, 99.99, 60.00, 45, 0.69, 2.1, -0.6, 'premium', true, '2024-06-01 10:30:00'),
('P1008', 'Running Shoes', 'Sports', 65.00, 72.99, 40.00, 75, 0.83, 7.4, -1.3, 'mid-range', true, '2024-06-01 10:35:00');

INSERT INTO agent_decisions (product_id, agent_name, decision_type, input_data, output_data, confidence_score, explanation, reflection, reasoning_chain, timestamp) VALUES
('P1001', 'PricingDecisionAgent', 'price_increase', '{"demand_score": 0.85, "inventory_level": 120, "competitor_prices": [18.99, 19.99], "base_price": 15.99}', '{"new_price": 17.99, "change_percentage": 12.5}', 0.95, 'Increased price due to high demand and competitive positioning', 'The decision to increase price was justified by strong demand signals and competitor pricing. However, I should monitor if this affects sales velocity.', '{"step1": "Analyzed demand score of 0.85", "step2": "Checked inventory level of 120 units", "step3": "Compared with competitor prices", "step4": "Applied pricing strategy", "step5": "Finalized new price"}', '2024-06-01 10:00:00'),
('P1002', 'PricingDecisionAgent', 'price_increase', '{"demand_score": 0.92, "inventory_level": 80, "competitor_prices": [52.99, 48.99], "base_price": 45.00}', '{"new_price": 49.99, "change_percentage": 11.1}', 0.98, 'Premium product with excellent demand justifies price increase', 'The premium positioning and high demand score support this price increase. The product maintains competitive advantage while maximizing profit margins.', '{"step1": "Evaluated premium market position", "step2": "Assessed high demand score of 0.92", "step3": "Analyzed competitor premium pricing", "step4": "Calculated optimal price point", "step5": "Applied premium pricing strategy"}', '2024-06-01 10:05:00'),
('P1003', 'DemandAnalysisAgent', 'demand_assessment', '{"sales_velocity": 15.7, "price_elasticity": -1.5, "stock_level": 200}', '{"demand_score": 0.78, "trend": "stable", "recommendation": "maintain_price"}', 0.87, 'High sales velocity indicates strong demand despite budget positioning', 'The high sales velocity suggests the product is performing well in its budget segment. The negative price elasticity indicates price sensitivity.', '{"step1": "Calculated sales velocity from recent data", "step2": "Analyzed price elasticity impact", "step3": "Assessed market segment performance", "step4": "Determined demand score", "step5": "Generated recommendations"}', '2024-06-01 10:10:00'),
('P1004', 'InventoryTrackingAgent', 'stock_assessment', '{"current_stock": 150, "reorder_point": 40, "max_stock": 250}', '{"status": "healthy", "recommendation": "no_action", "days_until_reorder": 15}', 0.92, 'Stock levels are healthy and above reorder point', 'Current inventory levels are optimal. The system predicts 15 days until reorder point is reached based on current sales velocity.', '{"step1": "Checked current stock level", "step2": "Compared with reorder point", "step3": "Calculated days until reorder", "step4": "Assessed inventory health", "step5": "Generated recommendations"}', '2024-06-01 10:15:00'),
('P1005', 'CompetitorMonitoringAgent', 'price_analysis', '{"competitor_prices": [29.99], "our_price": 27.99, "market_position": "premium"}', '{"price_advantage": 2.00, "recommendation": "maintain_position", "confidence": 0.89}', 0.89, 'Maintaining competitive advantage in premium segment', 'Our price is competitive in the premium segment. The $2 advantage provides good margin while maintaining market position.', '{"step1": "Gathered competitor price data", "step2": "Calculated price advantage", "step3": "Assessed market positioning", "step4": "Evaluated competitive landscape", "step5": "Generated strategic recommendations"}', '2024-06-01 10:20:00');

-- Dummy data for feedback_log table
INSERT INTO feedback_log (agent_name, feedback_type, message, related_product_id, timestamp)
VALUES
  ('PricingDecisionAgent', 'reflection', 'Price was set too high, consider lowering next cycle.', 'P1001', '2024-07-02T12:00:00Z'),
  ('SupervisorAgent', 'manual_review', 'Manual override required for product P1001.', 'P1001', '2024-07-02T13:00:00Z'); 
  
INSERT INTO competitor_prices (product_id, product_name, category, competitor_name, competitor_price, competitor_url, availability, shipping_cost, rating, review_count, scraped_at, confidence_score) VALUES
('P1001', 'Wireless Mouse', 'Electronics', 'Amazon', 18.99, 'https://amazon.com/wireless-mouse', true, 0.00, 4.5, 1250, '2024-06-01 10:00:00', 0.95),
('P1001', 'Wireless Mouse', 'Electronics', 'Best Buy', 19.99, 'https://bestbuy.com/wireless-mouse', true, 5.99, 4.3, 890, '2024-06-01 10:00:00', 0.92),
('P1002', 'Bluetooth Headphones', 'Electronics', 'Amazon', 52.99, 'https://amazon.com/bluetooth-headphones', true, 0.00, 4.7, 2100, '2024-06-01 10:05:00', 0.98),
('P1002', 'Bluetooth Headphones', 'Electronics', 'Walmart', 48.99, 'https://walmart.com/bluetooth-headphones', true, 0.00, 4.4, 1560, '2024-06-01 10:05:00', 0.94),
('P1003', 'Yoga Mat', 'Sports', 'Amazon', 21.99, 'https://amazon.com/yoga-mat', true, 0.00, 4.6, 3200, '2024-06-01 10:10:00', 0.96),
('P1003', 'Yoga Mat', 'Sports', 'Target', 23.50, 'https://target.com/yoga-mat', true, 0.00, 4.2, 1800, '2024-06-01 10:10:00', 0.91),
('P1004', 'Stainless Steel Water Bottle', 'Home & Kitchen', 'Amazon', 14.99, 'https://amazon.com/water-bottle', true, 0.00, 4.8, 4500, '2024-06-01 10:15:00', 0.97),
('P1005', 'Desk Lamp', 'Home & Office', 'Amazon', 29.99, 'https://amazon.com/desk-lamp', true, 0.00, 4.4, 980, '2024-06-01 10:20:00', 0.93); 

-- Dummy data for price_history table
INSERT INTO price_history (product_id, old_price, new_price, change_reason, agent_name, confidence_score, timestamp)
VALUES
  ('P1001', 19.99, 21.99, 'Automated pricing decision', 'PricingDecisionAgent', 0.95, '2024-07-01T10:00:00Z'),
  ('P1001', 21.99, 20.99, 'Manual override', 'SupervisorAgent', 0.90, '2024-07-02T10:00:00Z'); 
  

-- Dummy data for demand_scores table
INSERT INTO demand_scores (product_id, demand_score, sales_velocity, price_advantage_pct, stock_level, llm_explanation, calculated_at)
VALUES
  ('P1001', 0.85, 8.5, 5.0, 120, 'High demand due to competitor price advantage and good product reviews. Sales velocity indicates strong market acceptance.', '2024-07-01T09:00:00Z'),
  ('P1002', 0.92, 12.3, 8.2, 80, 'Premium product with excellent demand. High sales velocity suggests strong brand recognition and quality perception.', '2024-07-01T09:00:00Z'),
  ('P1003', 0.78, 15.7, 3.1, 200, 'Budget-friendly product with good demand. High sales velocity indicates price sensitivity and volume-driven sales.', '2024-07-01T09:00:00Z'),
  ('P1004', 0.81, 6.2, 4.5, 150, 'Steady demand with moderate sales velocity. Product appeals to health-conscious consumers.', '2024-07-01T09:00:00Z'),
  ('P1005', 0.74, 4.8, 2.8, 60, 'Lower demand for premium desk lamp. Sales velocity suggests niche market appeal.', '2024-07-01T09:00:00Z');

-- Dummy data for inventory_levels table
INSERT INTO inventory_levels (product_id, stock_level, reorder_point, max_stock, last_updated)
VALUES
  ('P1001', 120, 30, 200, '2024-07-01T08:00:00Z'),
  ('P1002', 80, 20, 150, '2024-07-01T08:00:00Z'),
  ('P1003', 200, 50, 300, '2024-07-01T08:00:00Z'),
  ('P1004', 150, 40, 250, '2024-07-01T08:00:00Z'),
  ('P1005', 60, 15, 100, '2024-07-01T08:00:00Z'); 
  
INSERT INTO sales_data (product_id, quantity_sold, sale_price, sale_date, demand_signal, customer_segment, sales_channel, discount_applied, transaction_id) VALUES
('P1001', 2, 17.99, '2024-06-01 09:00:00', 0.85, 'tech-savvy', 'online', 0.00, 'TXN001'),
('P1001', 1, 17.99, '2024-06-01 10:30:00', 0.85, 'general', 'online', 0.00, 'TXN002'),
('P1002', 1, 49.99, '2024-06-01 11:15:00', 0.92, 'premium', 'online', 0.00, 'TXN003'),
('P1003', 3, 22.50, '2024-06-01 12:00:00', 0.78, 'fitness', 'online', 5.00, 'TXN004'),
('P1004', 1, 13.50, '2024-06-01 13:45:00', 0.81, 'health-conscious', 'online', 0.00, 'TXN005'),
('P1005', 1, 27.99, '2024-06-01 14:20:00', 0.74, 'professional', 'online', 0.00, 'TXN006'),
('P1006', 5, 9.99, '2024-06-01 15:10:00', 0.88, 'budget-conscious', 'online', 0.00, 'TXN007'),
('P1007', 1, 99.99, '2024-06-01 16:00:00', 0.69, 'premium', 'online', 0.00, 'TXN008'); 

