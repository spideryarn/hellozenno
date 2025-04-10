# Vercel Deployment Strategy for Hello Zenno: Flask API + SvelteKit Frontend

This document outlines our deployment strategy for the Hello Zenno application, which consists of:
- Flask API backend (currently deployed on Vercel as `hz_backend` project) - will move to `api.hellozenno.com`
- SvelteKit frontend (to be deployed on Vercel as `hz_frontend`) - will take over `www.hellozenno.com` and redirected from the apex domain

We have no users, so we don't care about backwards compatibility.


## Architecture Overview

We will implement a dual-deployment approach:

1. **Flask API**: Deployed as serverless functions on Vercel at `api.hellozenno.com`
2. **SvelteKit Frontend**: Deployed on Vercel at `www.hellozenno.com` (with redirect from `hellozenno.com`)

At the moment, SvelteKit talks to Flask, which talks to Supabase. In the future, maybe both services will communicate with our Supabase Postgres database.

```
┌─────────────────┐       ┌────────────────┐
│                 │       │                │
│  SvelteKit      │       │  Flask API     │
│  Frontend       │◄─────►│  Backend       │
│  www.hellozenno │       │  api.hellozenno│
│                 │       │                │
└────────┬────────┘       └────────┬───────┘
         │                         │
  FUTURE?│                         │
         ▼                         ▼
┌─────────────────────────────────────────┐
│                                         │
│          Supabase PostgreSQL            │
│                                         │
└─────────────────────────────────────────┘
```

## Project Organization

We're using two separate Vercel projects to cleanly separate the deployments:

1. **Flask API Project**
   - Code located in the `api/` directory
   - Vercel configuration files located in `api/.vercel/`
   - Configuration file: `api/vercel.json`
   - Will be deployed to `api.hellozenno.com`

2. **SvelteKit Frontend Project**
   - Code located in the `frontend/` directory
   - Vercel configuration files located in `frontend/.vercel/`
   - No `vercel.json` needed (handled by `@sveltejs/adapter-vercel`)
   - Will be deployed to `www.hellozenno.com` and `hellozenno.com`

## Deployment Stages

### Stage 1: Prepare the Flask API Project ✅

1. **Review Current Flask Deployment** ✅
   - Ensure the Flask API is properly structured for Vercel serverless deployment
   - Flask API entry point is in `api/index.py`
   - Moved `.vercel` and `vercel.json` configuration files to the `api/` directory:

2. **Update CORS Settings** ✅
   - Modified Flask CORS configuration to allow requests from SvelteKit domains:
     ```python
     # From api/index.py
     CORS(
         app,
         resources={
             r"/api/*": {
                 "origins": [
                     "https://www.hellozenno.com",
                     "https://hellozenno.com",
                     "http://localhost:5173",  # SvelteKit local dev
                     "http://localhost:3000"   # Local Flask dev
                 ]
             },
             # Additional routes with same origin configuration
         },
     )
     ```

3. **Set Environment Variables** ✅
   - Ensured all necessary environment variables are configured in Vercel Project Settings
   - Included Supabase credentials and API keys

### Stage 2: Set Up the SvelteKit Project for Vercel ✅

1. **Install Vercel Adapter** ✅
   - The SvelteKit project already has the Vercel adapter installed:
     ```json
     // From package.json
     "@sveltejs/adapter-vercel": "^5.5.2"
     ```

2. **Configure SvelteKit for Vercel** ✅
   - The project is already configured to use the Vercel adapter:
     ```javascript
     // From svelte.config.js
     import adapter from '@sveltejs/adapter-vercel';
     import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';
     
     const config = {
         preprocess: vitePreprocess(),
         kit: { adapter: adapter() }
     };
     
     export default config;
     ```

3. **Configure API URLs** ✅
   - Added to `.env.local` and `.env.prod`:
     - `.env.local`:
       ```
       VITE_API_URL=http://localhost:3000
       ```
     - `.env.prod`:
       ```
       VITE_API_URL=https://api.hellozenno.com
       ```

4. **API Integration** ✅
   - API integration utility already exists in `src/lib/api.ts`
   - Updated `src/lib/config.ts` to use environment variables:
     ```typescript
     export const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:3000";
     ```

5. **Local Testing** ✅
   - Successfully tested local API communication between Flask and SvelteKit

### Stage 3: Create New Vercel Project for SvelteKit ✅

1. **Initialize Vercel Project** ✅
   - Installed Vercel CLI:
     ```bash
     npm install -g vercel
     ```
   - Created a new Vercel project:
     ```bash
     cd frontend
     vercel
     ```

2. **Project Configuration** ✅
   - Project builds successfully in the Vercel environment
   - Auto-detected SvelteKit settings:
     - Build Command: vite build
     - Development Command: vite dev --port $PORT
     - Output Directory: public

3. **Environment Variables** ✅
   - Added production environment variable on Vercel

4. **Preview Deployment** ✅
   - Successfully deployed a preview version

### Stage 4: Configure Custom Domains ⏳

1. **Add Custom Domain to Flask API Project**
   - In Vercel dashboard, navigate to the Flask API project
   - Go to Project Settings > Domains
   - Add domain: `api.hellozenno.com`

2. **Add Custom Domains to SvelteKit Project**
   - In Vercel dashboard, navigate to the SvelteKit project
   - Add domains:
     - `www.hellozenno.com` (primary)
     - `hellozenno.com` (redirect to www)

3. **Verify Domain Configuration**
   - Verify both domains are working:
     - `https://api.hellozenno.com`
     - `https://www.hellozenno.com`
     - `https://hellozenno.com` (should redirect to www)

### Stage 5: Production Deployment ⏳

1. **Deploy SvelteKit to Production**
   - Ready to deploy to production:
     ```bash
     ./scripts/prod/deploy_frontend.sh
     ```

2. **Deploy Flask API to Production**
   - Ready to deploy to production:
     ```bash
     ./scripts/prod/deploy_backend.sh
     ```

3. **Run Final Tests**
   - Verify all routes and API interactions work on production domains
   - Ensure frontend-backend communication is working properly

4. **Setup Monitoring**
   - Enable Vercel Analytics in both projects

## Next Steps

1. **Complete Custom Domain Configuration** DONE
   - DONE Configure `api.hellozenno.com` for the Flask API project
   - DONE Configure `www.hellozenno.com` for the SvelteKit project
   - DONE Set up redirect from apex domain to www

2. **Deploy to Production**
   - Update Flask API with CORS settings
   - Deploy SvelteKit frontend to production

3. **Transition Plan**
   - Phase out the Flask/Jinja frontend gradually
   - Redirect traffic to the new SvelteKit frontend

## Considerations and Best Practices

### Troubleshooting Common Issues

- **CORS Errors**
   - Double-check CORS configuration in Flask
   - Verify the protocol (http vs https) in API URLs

- **Build Failures**
   - Check build logs in Vercel dashboard
   - Ensure all dependencies are properly declared

- **404 Errors on API Endpoints**
   - Verify API routes are correctly configured in `vercel.json`
   - Check for any path inconsistencies between frontend requests and API routes

## Future Enhancements

- Implement Edge Functions for global low-latency responses
- Explore Vercel's Incremental Static Regeneration (ISR) for SvelteKit
- Consider Vercel's Edge Middleware for advanced routing and request handling

