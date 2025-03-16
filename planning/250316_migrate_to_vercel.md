# Migrating from Fly.io to Vercel Serverless Python

## Goal and Context

Migrate the HelloZenno web application from Fly.io to Vercel serverless Python while keeping Supabase as the database provider. This migration will allow us to leverage Vercel's serverless architecture for better scalability and simpler deployment.

The current application is a Flask-based web app deployed on Fly.io with a Supabase PostgreSQL database. We need to adapt the application architecture to work with Vercel's serverless model, which has different constraints and requirements compared to the current containerized deployment on Fly.io.

## Principles and Key Decisions

- Keep the Supabase PostgreSQL database as is
- Adapt the Flask application to work with Vercel's serverless functions
- Maintain all existing functionality and routes
- Keep implementation simple and straightforward - focus on getting a working prototype
- Break the migration into small, incremental steps with working code at each stage
- Reuse code from the `hellozenno-vercel` experiment where appropriate
- Delete the `hellozenno-vercel` directory after successful migration
- Use the existing Git branch `250316_Vercel` for all changes

## Actions

- [x] **Initial Setup and Project Structure**
  - [x] Set up the basic project structure with `api/` directory for serverless functions
  - [x] Create a `vercel.json` configuration file with appropriate routing rules
  - [x] Update `requirements.txt` for Vercel deployment

- [x] **Environment Configuration**
  - [x] Adapt environment variable handling for Vercel
  - [x] Update `utils/env_config.py` to detect Vercel environment

- [x] **Basic Flask App Adaptation**
  - [x] Modify Flask application to work as both a traditional Flask app and a Vercel serverless function
  - [x] Create a handler function for Vercel serverless execution
  - [x] Test with a simple route to verify the setup works
  - [x] Consolidate app.py into api/index.py

- [x] **Database Connection Configuration**
  - [x] Update `.env.prod` to use Supabase's connection pooling port (6543)
  - [x] Ensure database connections are properly closed after each request

- [x] **Route Migration Investigation**
  - [x] Analyze existing routes and identify any potential challenges for serverless migration
  - [x] Document any routes that might need special handling

- [x] **Database Connection Investigation**
  - [x] Research best practices for database connections in serverless environments
  - [x] Plan appropriate modifications to connection handling

- [x] **Deployment Preparation**
  - [x] Create a new Vercel project
  - [ ] Configure environment variables in Vercel dashboard
  - [ ] Deploy to Vercel preview environment

- [ ] **Testing and Validation**
  - [ ] Test basic functionality (vercel-test route)
  - [ ] Test database connectivity
  - [ ] Test all routes and functionality
  - [ ] Verify database operations work correctly

- [x] **Health Check Adaptation**
  - [x] Modify system_views.py to remove system metrics not available in serverless
  - [x] Focus health check on database connectivity

- [ ] **Production Deployment**
  - [ ] Deploy to production
  - [ ] Update documentation

- [ ] **Future Enhancements**
  - [ ] Implement static file serving with WhiteNoise
  - [ ] Optimize long-running operations for serverless environment
  - [ ] Implement file storage solution for serverless environment

- [ ] **Cleanup**
  - [ ] Remove Fly.io specific configuration files
  - [ ] Delete `hellozenno-vercel` directory
  - [ ] Update deployment documentation

## Detailed Implementation Plan

### Initial Setup and Project Structure

- [x] **Set Up Project Structure**
  - [x] Create `api/` directory for serverless functions
  - [x] Create main entry point at `api/index.py`
  - [x] Create `vercel.json` with routing configuration:
    ```json
    {
      "rewrites": [
        { "source": "/(.*)", "destination": "/api/index" }
      ]
    }
    ```

- [x] **Adapt Flask Application**
  - [x] Modify Flask application to work as both a traditional Flask app and a Vercel serverless function
  - [x] Create a handler function for Vercel serverless execution
  - [x] Test with a simple "Hello World" route
  - [x] Consolidate app.py into api/index.py

### Database Connection Configuration

- [x] **Update Database Connection**
  - [x] Update `.env.prod` to use Supabase's connection pooling port (6543)
  - [x] Ensure database connections are properly closed after each request

### Route Migration Investigation

- [x] **Analyze Routes**
  - [x] Review all blueprints and their routes
  - [x] Identify any routes with special requirements (file uploads, long-running operations, etc.)
  - [x] Document findings and plan adaptations

### Database Connection Research

- [x] **Research Best Practices**
  - [x] Investigate connection handling in serverless environments
  - [x] Consider connection pooling alternatives for serverless
  - [x] Plan appropriate modifications to `utils/db_connection.py`

### Deployment Preparation

- [x] **Create Vercel Project**
  - [x] Install Vercel CLI: `npm i -g vercel`
  - [x] Login to Vercel: `vercel login`
  - [x] Link to existing Vercel account: `vercel link`

- [x] **Configure Environment Variables**
  - [x] Update deployment scripts for Vercel:
    - [x] Update `scripts/prod/set_secrets.sh` to set Vercel environment variables
    - [x] Update `scripts/prod/deploy.sh` for Vercel deployment
    - [x] Create `scripts/prod/deploy_preview.sh` for preview deployments
  - [x] Run `./scripts/prod/set_secrets.sh` to set environment variables in Vercel
  - [x] Update `deploy_preview.sh` to pass environment variables directly during deployment

- [x] **Deploy to Preview**
  - [x] Deploy to Vercel preview: `./scripts/prod/deploy_preview.sh`
  - [x] Verify deployment was successful
  - [ ] Disable authentication for preview deployment in Vercel dashboard
  - [ ] Test the `/vercel-test` route

### Testing and Validation

- [ ] **Test Basic Functionality**
  - [ ] Verify the `/vercel-test` route works
  - [ ] Test database connectivity
  - [ ] Test a simple database query

- [ ] **Test All Routes**
  - [ ] Test each blueprint's routes
  - [ ] Identify any routes that fail
  - [ ] Document issues and fix them

### Health Check Adaptation

- [x] **Modify Health Check**
  - [x] Update `system_views.py` to remove system metrics not available in serverless
  - [x] Focus health check on database connectivity
  - [x] Test the updated health check

### Future Enhancements

- [ ] **Static File Serving**
  - [ ] Implement WhiteNoise for static file serving
  - [ ] Configure static file directories

- [ ] **Long-Running Operations**
  - [ ] Optimize long-running operations for serverless environment
  - [ ] Implement background job system if needed

- [ ] **File Storage**
  - [ ] Implement file storage solution for serverless environment
  - [ ] Update file-related routes to use the new storage solution

## Appendix

### Example Vercel Serverless Function Structure

```python
# api/index.py
from flask import Flask, Request
from app import create_app

app = create_app()

# Vercel serverless handler
def handler(request: Request):
    return app(request.environ, lambda status, headers, exc_info=None: [status, headers, []])
```

### Vercel Environment Variables

Key environment variables to set in Vercel dashboard:
- `DATABASE_URL`
- `FLASK_SECRET_KEY`
- `CLAUDE_API_KEY`
- `OPENAI_API_KEY`
- `ELEVENLABS_API_KEY`

### Route Migration Findings

After analyzing the routes in the application, we've identified the following potential challenges for serverless migration:

1. **File Operations**:
   - Routes that handle file uploads and downloads (e.g., `download_sourcefile`, `create_sourcefile_from_text`)
   - These may need to be adapted to use temporary storage or cloud storage instead of local filesystem

2. **Long-Running Operations**:
   - Routes that process source files (`process_sourcefile`)
   - Audio generation routes (`generate_sourcefile_audio`)
   - These may exceed the serverless function timeout limits (10 seconds in our current configuration)

3. **Static File Serving**:
   - Routes that serve audio files (`play_sourcefile_audio`, `get_mp3`)
   - These should be handled by a static file serving solution like WhiteNoise or moved to a dedicated storage service

4. **Health Checks**:
   - The current health check (`health_check`) uses system metrics that may not be available in a serverless environment
   - Need to adapt to focus on database connectivity and application status

### Adaptation Strategy

1. **For File Operations**:
   - Use Vercel's `/tmp` directory for temporary file storage
   - Consider moving to a cloud storage solution (e.g., AWS S3, Vercel Blob Storage) for persistent files

2. **For Long-Running Operations**:
   - Break down long-running operations into smaller steps
   - Consider implementing a background job system or using a separate service for these operations
   - Increase the function timeout in `vercel.json` (currently set to 60 seconds)

3. **For Static File Serving**:
   - Implement WhiteNoise for static file serving (future enhancement)
   - Consider moving large files (audio, etc.) to a dedicated storage service

4. **For Health Checks**:
   - Simplify the health check to focus on database connectivity
   - Remove system metrics that aren't relevant in a serverless environment

### Database Connection Findings

After researching database connection best practices for serverless environments, we've identified the following key points:

1. **Connection Pooling Challenges in Serverless**:
   - Traditional connection pooling is designed for long-running servers, not ephemeral serverless functions
   - Each serverless function invocation may create a new connection, potentially exhausting database connection limits
   - Connection reuse between function invocations is not guaranteed

2. **Supabase Connection Pooling**:
   - Supabase provides a server-side connection pooler called Supavisor (previously PgBouncer)
   - Supavisor runs on a separate high-availability cluster and manages connections efficiently
   - It's specifically designed to work with serverless environments

3. **Recommended Connection Strategy**:
   - Use Supabase's connection pooling on port `6543` instead of direct connections on port `5432`
   - Set the pool mode to "Transaction" for serverless functions
   - This ensures connections are only held for the duration of a transaction

### Deployment Instructions

1. **Install Vercel CLI**:
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Initialize Vercel Project**:
   ```bash
   vercel init
   ```

4. **Link to Existing Vercel Account**:
   ```bash
   vercel link
   ```

5. **Deploy**:
   ```bash
   ./scripts/prod/deploy.sh
   ./scripts/prod/deploy_preview.sh
   ```
