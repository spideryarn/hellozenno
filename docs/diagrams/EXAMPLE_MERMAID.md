## Mermaid Diagram Example

This file demonstrates a minimal Mermaid diagram inside Markdown. You can preview it on GitHub or with the Mermaid Live Editor ([link](https://mermaid.live/)).

### Flowchart: HelloZenno Architecture (Simplified)

```mermaid
flowchart TD
    A[User] -->|Login| B[Supabase Auth]
    B -->|JWT| C[Frontend (SvelteKit)]
    C -->|API request| D[Backend (Flask API)]
    D -->|SQL| E[(Supabase Postgres)]
    E -->|Data| D
    D -->|JSON| C
```

Notes:
- The diagram mirrors the high-level data flow described in `docs/reference/ARCHITECTURE.md`.
- Edit the nodes/edges to match specific features (e.g., audio variants flow).


