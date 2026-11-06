-- @bookmark: customer_search
-- @description: Search customers by name

SELECT name, address
FROM addresses
WHERE name LIKE :customer_name;
