-- Offset Pagination (simple but inefficient for large datasets)
-- Example: Fetch 10 records starting from offset 0
WITH paginated_data AS (
  SELECT id, name, created_at
  FROM users
  ORDER BY created_at DESC
  LIMIT 10 OFFSET 0
)
SELECT * FROM paginated_data;

-- Keyset Pagination (efficient, uses a key to avoid scanning)
-- Example: Fetch 10 records after a specific key (e.g., user_id = 123)
WITH keyset_data AS (
  SELECT id, name, created_at
  FROM users
  WHERE created_at < (SELECT created_at FROM users WHERE id = 123)
  ORDER BY created_at DESC
  LIMIT 10
)
SELECT * FROM keyset_data;

-- Note: In real use, keyset uses a stable key (e.g., user_id or created_at)
-- This avoids the performance issues of offset pagination when data grows.
