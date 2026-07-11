CREATE OR REPLACE VIEW alert_delivery_health AS
SELECT
  COUNT(*) AS total_deliveries,
  COUNT(*) FILTER (WHERE ok) AS successful_deliveries,
  COUNT(*) FILTER (WHERE NOT ok) AS failed_deliveries,
  AVG(latency_ms) AS average_latency_ms
FROM delivery_log;
CREATE INDEX IF NOT EXISTS idx_dead_letters_created ON dead_letters(created_at DESC);
