# Supabase High Egress Investigation

## Goal & Context
Investigate and resolve the unusually high Supabase data egress (71GB) observed in production with just a single user. This investigation aims to identify the root causes, implement monitoring solutions, and optimize the application to reduce data transfer.

### Background
- Supabase is currently showing 71GB of data egress over the last month
- Only a single user (the developer) has been using the application
- This volume suggests serious inefficiencies in how data is being transferred
- Excessive egress could lead to unnecessary costs and performance issues

## Principles & Key Decisions
- Prioritize investigation before making changes
- Focus on high-impact optimizations first
- Add monitoring to track progress of improvements
- Ensure all optimizations maintain existing functionality
- Take incremental approach to implementing changes

## Actions

TODO: Initial Investigation
- [x] Install Supabase MCP for production
- [x] Initial database structure and content analysis
- [ ] Database API egress monitoring
  - [ ] Set up specific monitoring for binary data tables (sourcefile, sentence)
  - [ ] Track frequency and volume of binary data retrievals
  - [ ] Identify patterns in when large data transfers occur
- [ ] Realtime connection analysis
  - [ ] Check browser developer tools for WebSocket traffic volume
  - [ ] Monitor Realtime connection counts and duration
  - [ ] Instrument code to log subscription lifecycle events

TODO: Binary Data Storage Optimization (HIGH PRIORITY)
- [x] Evaluate current binary data storage approach
  - [x] Confirmed ~278MB of binary data stored in database tables
  - [x] Verified no Storage buckets in use
- [ ] Create Supabase Storage buckets
  - [ ] Create separate buckets for audio and images
  - [ ] Set appropriate security policies
- [ ] Implement migration plan
  - [ ] Create script to move data from database to storage
  - [ ] Update schema to store URLs instead of binary data
  - [ ] Add proper caching headers to Storage objects

TODO: Realtime Subscription Improvements (MEDIUM PRIORITY)
- [ ] Audit existing Realtime implementations
  - [ ] Check all components using Realtime subscriptions
  - [ ] Verify cleanup on component unmount in all cases
- [ ] Optimize subscription configuration
  - [ ] Limit event types to only what's needed (vs '*')
  - [ ] Subscribe only to specific columns instead of entire rows
  - [ ] Add de-duplication for similar subscription requests
- [ ] Implement subscription monitoring
  - [ ] Add logging for subscription creation/removal
  - [ ] Create dashboard to track active subscriptions

TODO: Query Optimization (LOWER PRIORITY)
- [ ] Identify most frequent and largest queries
  - [ ] Use Supabase logs to find high-volume queries
  - [ ] Check for repeated identical queries
- [ ] Implement query improvements
  - [ ] Add pagination to large result sets
  - [ ] Select only necessary fields
  - [ ] Add caching for frequently accessed data

TODO: Testing & Verification
- [ ] Create baseline measurements
  - [ ] Record current egress metrics before changes
  - [ ] Develop test scenarios that trigger high egress
- [ ] Implement changes incrementally
  - [ ] Binary data storage first
  - [ ] Realtime optimizations second
  - [ ] Query improvements third
- [ ] Measure impact
  - [ ] Track egress reduction after each change
  - [ ] Document improvements

TODO: Document Findings
- [ ] Create detailed report of investigation results
  - [ ] List all identified high-egress operations
  - [ ] Quantify impact of each issue (est. GB/month)
  - [ ] Prioritize issues by potential impact
- [ ] Generate optimization plan
  - [ ] List specific files and functions needing changes
  - [ ] Estimate effort and impact for each optimization
  - [ ] Create implementation timeline

TODO: Implement Caching Strategies
- [ ] Add client-side caching
  - [ ] Implement browser caching for frequently accessed resources
  - [ ] Consider using tools like supabase-cache-helpers
- [ ] Add server-side caching where appropriate
  - [ ] Identify opportunities for response caching
  - [ ] Implement TTL-based cache policies

TODO: Long-term Monitoring
- [ ] Set up ongoing egress monitoring
  - [ ] Create custom dashboard for egress metrics
  - [ ] Set up alerts for abnormal egress patterns
- [ ] Document best practices
  - [ ] Update development guidelines with learned optimizations
  - [ ] Create checklist for future feature development

## Appendix

### Potential Egress Sources

1. **Audio/Image Binary Data**
   - MP3 files (up to 60MB each) potentially stored in database
   - Images uploaded for OCR processing
   - Binary data retrieval counting as database egress

2. **Large JSON Fields**
   - Models with substantial JSON content:
     - Lemma: translations, synonyms, mnemonics, etc.
     - Wordform: translations, possible_misspellings
     - Sourcefile: metadata
     - Sentence: lemma_words
     - Phrase: raw_forms, translations, component_words

3. **Realtime Subscriptions**
   - Wordforms realtime implementation
   - Potential subscription duplication or improper cleanup
   - Continuous data streaming

4. **Inefficient Query Patterns**
   - Fetching entire tables without limits
   - Retrieving unnecessary fields
   - Lack of pagination
   - Repeated identical queries 

# Appendix - clues, data collection, information gathered

## Binary Data Analysis

Database investigation reveals significant binary data stored directly in tables:

```sql
-- Binary data summary
SELECT 
    'sourcefile.audio_data' as source,
    COUNT(*) as count,
    MIN(octet_length(audio_data)) as min_size,
    MAX(octet_length(audio_data)) as max_size,
    AVG(octet_length(audio_data)) as avg_size,
    SUM(octet_length(audio_data)) as total_size
FROM public.sourcefile
WHERE audio_data IS NOT NULL
UNION ALL
SELECT 
    'sourcefile.image_data' as source,
    COUNT(*) as count,
    MIN(octet_length(image_data)) as min_size,
    MAX(octet_length(image_data)) as max_size,
    AVG(octet_length(image_data)) as avg_size,
    SUM(octet_length(image_data)) as total_size
FROM public.sourcefile
WHERE image_data IS NOT NULL
UNION ALL
SELECT 
    'sentence.audio_data' as source,
    COUNT(*) as count,
    MIN(octet_length(audio_data)) as min_size,
    MAX(octet_length(audio_data)) as max_size,
    AVG(octet_length(audio_data)) as avg_size,
    SUM(octet_length(audio_data)) as total_size
FROM public.sentence
WHERE audio_data IS NOT NULL
ORDER BY total_size DESC;
```

Results:
| Source | Count | Min Size (bytes) | Max Size (bytes) | Avg Size (bytes) | Total Size (bytes) |
|--------|-------|-----------------|------------------|------------------|-------------------|
| sourcefile.image_data | 121 | 150,784 | 3,882,488 | 1,119,124 | 135,413,989 |
| sourcefile.audio_data | 52 | 33,436 | 4,529,423 | 1,552,088 | 80,708,574 |
| sentence.audio_data | 1,578 | 17,136 | 126,223 | 39,660 | 62,583,599 |

Total binary data: ~278MB stored directly in database

## Storage Buckets Check

```sql
SELECT * FROM storage.buckets;
```

Result: No storage buckets found. All binary data is stored directly in database tables instead of Supabase Storage.

## Realtime Implementation Evidence

Found implementation in planning/250315_Supabase_Realtime_for_wordforms.md:

```javascript
// Set up realtime subscription
function setupRealtimeSubscription() {
  subscription = supabase
    .channel('wordforms-changes')
    .on(
      'postgres_changes',
      {
        event: '*', // Listen for all events (INSERT, UPDATE, DELETE)
        schema: 'public',
        table: 'sourcefilewordform',
        filter: `sourcefile_id=eq.${sourcefileId}`
      },
      (payload) => {
        console.log('Realtime update received:', payload);
        
        // Show update notification
        displayUpdateNotification();
        
        // Use a smart update strategy based on the event type
        if (payload.eventType === 'INSERT') {
          // For INSERT, we need to fetch the full record with joins
          fetchWordforms();
        } 
        // ... other event handlers
      }
    )
    .subscribe((status) => {
      console.log('Subscription status:', status);
    });
}

// Cleanup on component unmount
onDestroy(() => {
  if (subscription) {
    supabase.removeChannel(subscription);
  }
});
```

Issues noted:
- Subscribing to ALL events (`'*'`) rather than specific changes needed
- Full record fetching on INSERT events
- Proper cleanup exists but may not be triggered in all scenarios

## JSON Field Analysis

```sql
SELECT 
    table_name, 
    column_name, 
    AVG(pg_column_size(column_name)) as avg_size_bytes,
    MAX(pg_column_size(column_name)) as max_size_bytes,
    COUNT(*) as row_count
FROM (
    -- Various JSON fields from tables
    SELECT 'lemma' as table_name, 'translations' as column_name, translations FROM public.lemma 
    UNION ALL
    SELECT 'lemma' as table_name, 'synonyms' as column_name, synonyms FROM public.lemma WHERE synonyms IS NOT NULL
    UNION ALL
    SELECT 'lemma' as table_name, 'example_usage' as column_name, example_usage FROM public.lemma WHERE example_usage IS NOT NULL
    UNION ALL
    SELECT 'sentence' as table_name, 'lemma_words' as column_name, lemma_words FROM public.sentence WHERE lemma_words IS NOT NULL
    UNION ALL
    SELECT 'sourcefile' as table_name, 'metadata' as column_name, metadata FROM public.sourcefile
) AS json_data
GROUP BY table_name, column_name
ORDER BY avg_size_bytes DESC;
```

Results:
| Table | Column | Avg Size (bytes) | Max Size (bytes) | Row Count |
|-------|--------|------------------|------------------|-----------|
| lemma | example_usage | 17 | 17 | 1,482 |
| lemma | translations | 16 | 16 | 3,702 |
| sentence | lemma_words | 15 | 15 | 184 |
| sourcefile | metadata | 12 | 12 | 146 |
| lemma | synonyms | 12 | 12 | 3,105 |

JSON fields are small and unlikely to be major egress contributors.
