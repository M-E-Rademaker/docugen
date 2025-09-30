-- # Get Active Users
--
-- ## Description
-- Returns active users

SELECT user_id, username, last_login
FROM users
WHERE is_active = 1;