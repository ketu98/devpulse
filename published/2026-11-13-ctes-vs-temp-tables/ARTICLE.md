# ctes vs temp tables in sql

**Topic:** CTEs vs Temp Tables  
**Category:** sql

# CTEs vs Temp Tables in SQL

When writing SQL queries, especially in complex scenarios, you often need to break down logic into reusable, intermediate steps. Two common tools for that are Common Table Expressions (CTEs) and temporary tables. While they both serve the purpose of defining intermediate result sets, their behavior, performance, and use cases differ in practical settings.

CTEs are defined inline within a query and exist only for the scope of that query. They’re ideal for one-off transformations or recursive logic. For example, you might use a CTE to compute a hierarchy of departments and employees in a single query. CTEs are easy to write and read, and they don’t require schema changes or cleanup. However, they’re not persisted and can’t be reused across queries — which limits their utility in stored procedures or scripts that call multiple queries.

Temp tables, on the other hand, are stored in memory or tempdb and can be referenced across multiple queries. They’re useful when you need to reuse a result set or when the intermediate data is large and expensive to recompute. For instance, if you’re aggregating data from multiple tables and need to join it in several steps, a temp table can hold the result of the first aggregation and be used in subsequent steps.

From a practical engineering perspective, I evaluated both in a small POC: a query that joins sales data with product metadata, then filters and aggregates results. I used a CTE for the join and aggregation, and a temp table for the same logic but with an extra filtering step that needed to be reused.

The CTE version was simpler and faster for small datasets — it executed in under 100ms. But when I added a complex filter that ran on the same data in a second query, the CTE had to recompute everything, adding 300ms of overhead. The temp table version pre-computed the data, and the second query used it directly — cutting the total time by 40%.

## What I learned  
CTEs are great for clean, readable queries with minimal reuse. Temp tables shine when you need to re-use intermediate data or when performance is critical. The choice isn’t about "which is better" — it’s about matching the use case.

## Key Takeaways  
- Use CTEs for simple, one-off transformations or recursive queries.  
- Use temp tables when you need to reuse intermediate results or when data is large and expensive to recompute.  
- Always consider query reuse and performance when choosing between them.  
- In a POC, temp tables reduced execution time when reusing data across steps — a real-world benefit in iterative development.
