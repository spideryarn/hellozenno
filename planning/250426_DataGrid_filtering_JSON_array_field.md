# DataGrid Filtering Issues & Plans

## Short-term Fix: Hide Filter Inputs

As of April 26, 2025, we've temporarily hidden the filter input boxes in DataGrid.svelte because:

1. The filtering functionality isn't working correctly in all cases
2. It's confusing users who expect the filters to behave in a standard way
3. A proper fix requires more development time than currently available

The change adds a `showFilters = false` flag to the component, which can be easily re-enabled when the filtering functionality is properly fixed. All the filtering logic remains intact for future improvements.

## Future Plans

We need to revisit the entire filtering system to:
1. Make it more consistent and intuitive
2. Address performance issues with various column types
3. Properly handle special cases (JSON arrays, date fields, etc.)
4. Add visual feedback when filters are applied

## Appendix: JSON Array Filtering

When filtering on columns that store JSON arrays like `translations` we evaluated several approaches and have now standardised on **Option A – a generated text column**.

### Option A (chosen): generated column + trigram index

1.  Add a **generated column** which flattens the JSON array into a single lower-cased, comma-separated string:

    ```sql
    alter table public.wordform
      add column translations_flat text
      generated always as (lower(array_to_string(translations, ','))) stored;
    ```

2.  Create a `GIN … gin_trgm_ops` index on the new column for fast substring search:

    ```sql
    create index on public.wordform using gin (translations_flat gin_trgm_ops);
    ```

3.  In the DataGrid provider we simply apply `ilike('%foo%')` against `translations_flat`.

Advantages
*   Keeps UI logic simple – behaves like any other text column
*   No complex casts in the URL and no PostgREST limitations
*   Index gives good performance even with large tables
*   Automatically stays in sync because it's a stored generated column

### Option 1 (rejected): provider-side JSON query transformation
Attempted to cast `translations::text` and apply `ilike`, but PostgREST strips the cast, causing 404 / 42883 errors. Work-arounds became brittle and type-unsafe.

### Option 3 (rejected): column definition enhancement (`filterType: 'json_array'`)
Provided explicit marking in DataGrid but still required awkward server-side query logic. Added complexity without solving performance or URL-filter constraints.

With Option A in place the grid can now filter `translations` reliably with no extra per-page configuration.