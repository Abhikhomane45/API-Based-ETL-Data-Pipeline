
-- 1. Check the number of cryptocurrency records
SELECT COUNT(*) AS total_coins
FROM `promising-node-513006-f9.ecommerce.crypto_market`;


-- 2. Find the 10 largest cryptocurrencies by market cap
SELECT
    coin_name,
    price_usd,
    market_cap_usd,
    market_cap_rank
FROM `promising-node-513006-f9.ecommerce.crypto_market`
ORDER BY market_cap_rank
LIMIT 10;


-- 3. Find cryptocurrencies with a positive 24-hour price change
SELECT
    coin_name,
    price_usd,
    price_change_24h_pct
FROM `promising-node-513006-f9.ecommerce.crypto_market`
WHERE price_change_24h_pct > 0
ORDER BY price_change_24h_pct DESC;


-- 4. Check for duplicate cryptocurrency IDs
SELECT
    coin_id,
    COUNT(*) AS record_count
FROM `promising-node-513006-f9.ecommerce.crypto_market`
GROUP BY coin_id
HAVING COUNT(*) > 1;


-- 5. Analyze products by category
SELECT
    category,
    COUNT(*) AS total_products,
    ROUND(AVG(price), 2) AS average_price
FROM `promising-node-513006-f9.ecommerce.products`
GROUP BY category
ORDER BY total_products DESC;
