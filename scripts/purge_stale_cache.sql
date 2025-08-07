-- Cache purge script for nightly cleanup
-- Moves stale cache entries to 600_archives table

-- First, insert stale entries into archives
INSERT INTO 600_archives (user_id, timestamp, command, result, cache_hit, similarity_score, last_verified, verification_frequency_hours, relationship_score)
SELECT user_id, timestamp, command, result, cache_hit, similarity_score, last_verified, verification_frequency_hours, relationship_score
FROM episodic_logs
WHERE cache_confidence_score < 0.6 
  AND cache_age_hours > verification_frequency_hours
  AND cache_hit = true;

-- Then delete the stale entries from main table
DELETE FROM episodic_logs
WHERE cache_confidence_score < 0.6 
  AND cache_age_hours > verification_frequency_hours
  AND cache_hit = true;

-- Log the purge operation
INSERT INTO episodic_logs (user_id, timestamp, command, result, cache_hit, similarity_score, last_verified, verification_frequency_hours, relationship_score)
VALUES (
    gen_random_uuid(), 
    NOW(), 
    'cache_purge', 
    'Purged stale cache entries', 
    false, 
    0.0, 
    NOW(), 
    NULL, 
    0.0
); 