## What this demonstrates

This proof-of-concept compares the performance and use cases of Common Table Expressions (CTEs) versus temporary tables in SQL. It shows when each is more efficient and appropriate.

## How it works

The POC creates two queries: one using a CTE to generate a sequence of numbers, and another using a temporary table. Both perform the same operation, but one uses a CTE (in-memory, scoped to a session), the other stores data in a temporary table (persistent in session, reusable).

## How to run

1. Copy the SQL into a SQL editor (e.g., SQL Server, PostgreSQL).
2. Run the script in a database with support for CTEs and temp tables.
3. Observe execution time and results.

## Things to try

- Test with larger datasets (e.g., 100,000 rows).
- Compare performance with and without indexes.
- Try using a CTE in a stored procedure vs. a temp table.
- Experiment with nested CTEs vs. multiple temp table inserts.
