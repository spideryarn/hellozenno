# Investigation Plan: High Supabase Egress & Vercel Function Duration

**Problem:** Excessive Supabase data egress (~100GB) and high Vercel function duration (hitting free tier limits) observed in production. Login wall implemented for intensive sections, impact TBC.

**Goal:** Identify the root causes of high egress and function duration, and implement solutions to reduce them.

**Investigation Steps:**

1.  **Monitor Post-Login Wall Impact:**
    *   Track Supabase egress and Vercel function duration metrics over the next few days/week.
    *   **Hypothesis:** If crawlers were the main cause, we should see a significant drop.
    *   **Action:** Check Supabase and Vercel dashboards regularly.

2.  **Analyze Supabase Usage:**
    *   **Goal:** Pinpoint which services/queries are causing the high egress.
    *   **Actions:**
        *   Review Supabase Dashboard -> Usage -> Egress Breakdown (by service: Database, Storage, Auth, etc.).
        *   Review Supabase Dashboard -> Reports -> Query Performance: Identify most frequent queries, slow queries, and queries returning large numbers of rows.
        *   Review Supabase Dashboard -> Logs Explorer -> Edge Logs (if applicable): Check for heavily queried API endpoints.
        *   Review Storage buckets: Are there unexpectedly large files or frequently accessed large files?

3.  **Analyze Vercel Function Usage:**
    *   **Goal:** Identify which functions are consuming the most resources (GB-Hrs) and why.
    *   **Actions:**
        *   Review Vercel Dashboard -> Usage -> Function Duration: Identify top consuming functions.
        *   Review Vercel Dashboard -> Logs: Check logs for the identified functions. Look for:
            *   Long execution times (especially calls to Supabase).
            *   Timeouts (`FUNCTION_INVOCATION_TIMEOUT`).
            *   Errors or unhandled exceptions.
            *   Evidence of many repeated calls.

4.  **Code Review for Inefficiencies:**
    *   **Goal:** Find code patterns contributing to excessive data transfer or long execution times.
    *   **Actions:**
        *   **Backend/API:**
            *   Review identified high-usage Vercel functions and Supabase queries.
            *   Check for `SELECT *` queries; change to select only necessary columns.
            *   Check if large datasets are fetched without pagination.
            *   Check if data is fetched inside loops unnecessarily.
            *   Review use of `INSERT`/`UPDATE` - are they returning large objects unnecessarily?
            *   Assess caching strategies (server-side).
        *   **Frontend:**
            *   Review pages/components making calls to the identified problematic endpoints/functions.
            *   Check for excessive API calls (e.g., in loops, useEffect without proper dependencies).
            *   Assess client-side caching.
        *   **Storage:**
            *   Check how images/large files are loaded. Are they resized/optimized? Is `cache-control` set appropriately?

**Potential Solutions (Implement based on findings):**

*   **Query Optimization:**
    *   Add `SELECT col1, col2` instead of `SELECT *`.
    *   Implement pagination for large lists.
    *   Add database indexes for frequently filtered/sorted columns.
    *   Optimize RLS policies if they are slow.
*   **Function Optimization:**
    *   Increase Vercel function memory/duration if necessary (and cost-effective).
    *   Enable Vercel "Fluid Compute" (check Node.js/Python runtime compatibility).
    *   Ensure functions return responses promptly, even on error.
    *   Refactor long-running tasks (e.g., background jobs, streaming).
    *   Ensure Vercel function region matches Supabase region.
*   **Storage Optimization:**
    *   Use Supabase Image Transformations for resizing/optimizing images on the fly.
    *   Set longer `cache-control` headers for static assets.
*   **Caching:** Implement or improve caching at appropriate levels (client, edge, server, database).
*   **Rate Limiting:** Consider adding rate limiting if specific users/IPs are causing issues (more complex).
*   **Network Restrictions:** Apply Supabase Network Restrictions if access should be limited (primarily a security measure, but might deter some bots if they hit Postgres directly).

**Next Steps:**

*   Start monitoring the impact of the login wall.
*   Begin investigating Supabase and Vercel dashboards for usage patterns.
