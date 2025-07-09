INSERT INTO products (id, name, category, base_price, current_price, cost_price, stock_level, demand_score, sales_velocity, price_elasticity, market_position, is_active, last_updated) VALUES
('P1001', 'Wireless Mouse', 'Electronics', 15.99, 17.99, 10.00, 120, 0.85, 8.5, -1.2, 'mid-range', true, '2024-06-01 10:00:00'),
('P1002', 'Bluetooth Headphones', 'Electronics', 45.00, 49.99, 30.00, 80, 0.92, 12.3, -0.8, 'premium', true, '2024-06-01 10:05:00'),
('P1003', 'Yoga Mat', 'Sports', 20.00, 22.50, 12.00, 200, 0.78, 15.7, -1.5, 'budget', true, '2024-06-01 10:10:00'),
('P1004', 'Stainless Steel Water Bottle', 'Home & Kitchen', 12.00, 13.50, 7.00, 150, 0.81, 6.2, -1.1, 'mid-range', true, '2024-06-01 10:15:00'),
('P1005', 'Desk Lamp', 'Home & Office', 25.00, 27.99, 15.00, 60, 0.74, 4.8, -0.9, 'premium', true, '2024-06-01 10:20:00'),
('P1006', 'Smartphone Case', 'Electronics', 8.99, 9.99, 5.00, 300, 0.88, 25.1, -1.8, 'budget', true, '2024-06-01 10:25:00'),
('P1007', 'Coffee Maker', 'Home & Kitchen', 89.99, 99.99, 60.00, 45, 0.69, 2.1, -0.6, 'premium', true, '2024-06-01 10:30:00'),
('P1008', 'Running Shoes', 'Sports', 65.00, 72.99, 40.00, 75, 0.83, 7.4, -1.3, 'mid-range', true, '2024-06-01 10:35:00');

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