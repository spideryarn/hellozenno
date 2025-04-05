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

see `.cursor/rules/cursor-tools.mdc`

As a backup option, cursor-tools can also be used for browser debugging:

```bash
# Open a URL and capture logs/network activity
cursor-tools browser open "http://localhost:5173" --screenshot=debug.png

# Execute actions on a webpage
cursor-tools browser act "Click the login button" --url="http://localhost:5173"

**Browser Automation (Stateless):**
`cursor-tools browser open <url> [options]` - Open a URL and capture page content, console logs, and network activity (e.g., `cursor-tools browser open "https://example.com" --html`)
`cursor-tools browser act "<instruction>" --url=<url> [options]` - Execute actions on a webpage using natural language instructions (e.g., `cursor-tools browser act "Click Login" --url=https://example.com`)
`cursor-tools browser observe "<instruction>" --url=<url> [options]` - Observe interactive elements on a webpage and suggest possible actions (e.g., `cursor-tools browser observe "interactive elements" --url=https://example.com`)
`cursor-tools browser extract "<instruction>" --url=<url> [options]` - Extract data from a webpage based on natural language instructions (e.g., `cursor-tools browser extract "product names" --url=https://example.com/products`)

**Browser Command Options (for 'open', 'act', 'observe', 'extract'):**
--console: Capture browser console logs (enabled by default, use --no-console to disable)
--html: Capture page HTML content
--network: Capture network activity (enabled by default, use --no-network to disable)
--screenshot=<file path>: Save a screenshot of the page (e.g., `--screenshot=screenshots/example.png` to save in the `screenshots/` directory)
--timeout=<milliseconds>: Set navigation timeout (default: 30000ms)
--viewport=<width>x<height>: Set viewport size (e.g., 1280x720). When using --connect-to, viewport is only changed if this option is explicitly provided
--headless: Run browser in headless mode (default: true)
--no-headless: Show browser UI (non-headless mode) for debugging
--connect-to=<port>: Connect to existing Chrome instance
--wait=<duration or selector>: Wait after page load (e.g., '5s', '#element-id', 'selector:.my-class')
--video=<directory>: Save a video recording of the browser interaction to the specified directory (1280x720 resolution). Not available when using --connect-to

**Notes on Browser Commands:**
- All browser commands are stateless: each command starts with a fresh browser instance and closes it when done.
- When using `--connect-to`, special URL values are supported:
  - `current`: Use the existing page without reloading
  - `reload-current`: Use the existing page and refresh it (useful in development)
- Multi step workflows involving state or combining multiple actions are supported in the `act` command using the pipe (|) separator (e.g., `cursor-tools browser act "Click Login | Type 'user@example.com' into email | Click Submit" --url=https://example.com`)
- Video recording is available for all browser commands using the `--video=<directory>` option. This will save a video of the entire browser interaction at 1280x720 resolution. The video file will be saved in the specified directory with a timestamp.
- DO NOT ask browser act to "wait" for anything, the wait command is currently disabled in Stagehand.
```

## Additional Resources

- See `frontend/docs/FRONTEND_SVELTEKIT_ARCHITECTURE.md` for details on our SvelteKit architecture
- See `.cursor/rules/cursor-tools.mdc` for complete cursor-tools documentation
- See Playwright documentation at https://playwright.dev/
