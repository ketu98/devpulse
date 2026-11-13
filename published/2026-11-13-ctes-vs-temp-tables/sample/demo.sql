WITH cte_data AS (
    SELECT 1 AS id, 'A' AS value
    UNION ALL
    SELECT 2, 'B'
    UNION ALL
    SELECT 3, 'C'
)
SELECT id, value
FROM cte_data;

-- Create a temp table
CREATE TEMPORARY TABLE temp_data (
    id INT,
    value VARCHAR(10)
);

INSERT INTO temp_data (id, value)
VALUES (1, 'A'), (2, 'B'), (3, 'C');

SELECT id, value
FROM temp_data;
