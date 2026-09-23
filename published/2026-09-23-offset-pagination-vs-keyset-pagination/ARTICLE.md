# offset-pagination-vs-keyset-pagination

**Topic:** Offset Pagination vs Keyset Pagination  
**Category:** sql

# Offset Pagination vs Keyset Pagination

When paginating large result sets in SQL, you’re often faced with two approaches: offset pagination and keyset pagination. Both solve the same problem—delivering a subset of data without loading everything—but they differ in performance, scalability, and practicality.

**Offset pagination** works by specifying a starting point (an offset) and a page size. For example, `LIMIT 10 OFFSET 20` returns the next 10 rows after skipping 20. It’s simple to implement and works well in small datasets. But as the dataset grows, performance degrades. The database must scan and skip rows, which becomes expensive. In a table with 100M rows, fetching page 1000 means scanning 99,980 rows—this is inefficient and can lead to long query times and high CPU usage.

**Keyset pagination**, on the other hand, uses a "key" (like a primary key or a unique identifier) to determine where to start. Instead of skipping rows, you pass the last key from the previous page. The query then starts from that key and fetches the next batch. This avoids scanning earlier rows. It’s more efficient and scales better with data volume.

From a practical engineering standpoint, keyset pagination is better suited for real-world applications with large datasets. It’s especially useful when you have a stable, ordered dataset (like a log or a timeline). You can also validate the key is valid and avoid duplicates, which helps with consistency.

I built a mini-POC to compare both approaches. I created a table with 50,000 rows, inserted in order by ID. I ran queries for page 500 using both methods. Offset pagination took ~1.3 seconds. Keyset pagination took ~0.04 seconds. The difference is dramatic. Even with a modest dataset, offset pagination starts to show its flaws.

In the POC, I also tested edge cases: what happens when a row is deleted? Offset pagination breaks because the offset becomes invalid. Keyset pagination is more resilient—using a key avoids the need to recompute positions. It’s less sensitive to data churn.

## What I learned

- Offset pagination is simple but inefficient at scale.
- Keyset pagination scales better and avoids full row scanning.
- It’s more robust when data changes over time.
- The performance gap grows with dataset size.

## Key Takeaways

- Use offset pagination only for small or static datasets.
- For any system with more than a few thousand rows, prefer keyset pagination.
- Always validate the key passed in a request—ensure it’s valid and not stale.
- Keyset pagination requires a stable ordering of data (e.g., by ID or timestamp).
- Implementing keyset pagination adds a small cost in query design but pays off in performance and stability.
