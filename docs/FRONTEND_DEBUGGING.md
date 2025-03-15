# Frontend Debugging

## Browser Automation with cursor-tools

For frontend debugging, we use cursor-tools browser automation features. These provide powerful AI-assisted debugging capabilities.

### Key Commands

```bash
# Open a URL and capture logs/network activity
cursor-tools browser open "http://localhost:3000" --screenshot=debug.png

# Execute actions on a webpage
cursor-tools browser act "Click the login button" --url="http://localhost:3000"

# Observe interactive elements
cursor-tools browser observe "What can I interact with?" --url="http://localhost:3000"

# Extract data from a webpage
cursor-tools browser extract "Get all error messages" --url="http://localhost:3000"
```

### Debugging Workflow

1. Start your local development server
2. Use browser commands to interact with and analyze your frontend
3. Check console logs, network activity, and screenshots
4. Fix issues and repeat

## Additional Resources

- See `.cursorrules` for complete cursor-tools documentation
- See `docs/FRONTEND_INFRASTRUCTURE.md` for details on our frontend architecture
