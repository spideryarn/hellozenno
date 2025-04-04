# Frontend Debugging

This document covers debugging techniques for the SvelteKit frontend architecture. For a detailed overview of the SvelteKit structure, see [Frontend SvelteKit Architecture](./FRONTEND_SVELTEKIT_ARCHITECTURE.md).

See `DEBUGGING.md` for general debugging information.

## Browser Automation with Playwright MCP

For frontend debugging, we primarily use Playwright Model Context Protocol (MCP) for browser automation. Playwright provides robust testing and debugging capabilities for our SvelteKit frontend.


### Debugging Workflow

1. Start your local development server (typically on port 5173, see `scripts/local/run_sveltekit.sh`)
2. Use Playwright to interact with and analyze your frontend
3. Review the test results, screenshots, and debug information
4. Fix issues and repeat

## Alternative: Cursor Tools for Browser Automation

As a backup option, cursor-tools can also be used for browser debugging:

```bash
# Open a URL and capture logs/network activity
cursor-tools browser open "http://localhost:5173" --screenshot=debug.png

# Execute actions on a webpage
cursor-tools browser act "Click the login button" --url="http://localhost:5173"
```

## Additional Resources

- See `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md` for details on our SvelteKit architecture
- See `.cursor/rules/cursor-tools.mdc` for complete cursor-tools documentation
- See Playwright documentation at https://playwright.dev/
