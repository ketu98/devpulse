## What this demonstrates

This POC compares offset pagination and keyset pagination in SQL, showing how each handles large datasets and avoids performance degradation from large offset values.

## How it works

Offset pagination uses a `LIMIT` and `OFFSET` clause to skip rows. Keyset pagination uses a specific value (e.g., `id`) from the last returned row to fetch the next batch, avoiding large offsets.

## How to run

1. Create a table:  
   ```sql
   CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(50), created_at TIMESTAMP);
   ```

2. Insert sample data:  
   ```sql
   INSERT INTO users (id, name, created_at) VALUES 
   (1, 'Alice', '2023-01-01'), (2, 'Bob', '2023-01-02'), (3, 'Charlie', '2023-01-03');
   ```

3. Test offset pagination:  
   ```sql
   SELECT * FROM users ORDER BY id LIMIT 2 OFFSET 0;
   ```

4. Test keyset pagination:  
   ```sql
   SELECT * FROM users WHERE id > 1 ORDER BY id LIMIT 2;
   ```

## Things to try

- Add 1000 rows and test offset with offset=999.  
- Compare query performance with `EXPLAIN`.  
- Modify the table to include a `last_id` column to simulate keyset state.
