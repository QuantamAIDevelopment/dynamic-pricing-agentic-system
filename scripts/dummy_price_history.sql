-- Dummy data for price_history table
INSERT INTO price_history (product_id, old_price, new_price, change_reason, agent_name, confidence_score, timestamp)
VALUES
  ('P12345', 19.99, 21.99, 'Automated pricing decision', 'PricingDecisionAgent', 0.95, '2024-07-01T10:00:00Z'),
  ('P12345', 21.99, 20.99, 'Manual override', 'SupervisorAgent', 0.90, '2024-07-02T10:00:00Z'); 