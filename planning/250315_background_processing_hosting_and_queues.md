# Background Processing Options for Language Learning Application

## Overview

This document outlines various approaches to implementing asynchronous background processing for our language learning application. The primary goal is to handle multi-step LLM pipelines (image transcription, translation, word extraction, etc.) without blocking the UI.

## Current Architecture

- **Web Framework**: Flask running on Fly.io
- **Database**: PostgreSQL via Supabase
- **Frontend**: Gradually moving to more Svelte components
- **Processing Pipeline**: Multi-step sequence for processing language content
  - Image OCR/transcription
  - Translation
  - Word form extraction
  - Lemma identification
  - Sentence generation
  - Audio generation

## Key Requirements

- Asynchronous processing to avoid blocking the UI
- Simple architecture that's easy to understand and maintain
- Support for long-running tasks that may take several minutes
- Real-time updates to show progress in the UI
- Reliability - tasks should complete even if interrupted

## Background Processing Options

### Option 1: Flask with Fire-and-Forget Pattern

**Description**: Enhance the current Flask application with a fire-and-forget pattern using threads.

**How it works**:
1. User uploads content to a Flask endpoint
2. Flask makes a fire-and-forget API call to trigger processing
3. Processing function updates the database as it progresses
4. Frontend polls or subscribes to database changes

**Pros**:
- Minimal changes to existing codebase
- No need to migrate from Flask
- Simple implementation
- Can chain multiple steps for long-running processes

**Cons**:
- Less elegant than built-in background task systems
- No built-in retries or monitoring
- Tasks not durable if server restarts

**Implementation Example**:
```python
@app.route('/upload', methods=['POST'])
def upload_file():
    # Save the file
    file_id = save_file(request.files['file'])
    
    # Trigger long-running process without waiting for response
    import threading
    import requests
    
    def trigger_processing():
        try:
            requests.post(
                f"http://localhost:5000/api/process/{file_id}",
                timeout=0.1  # Very short timeout - we don't care about the response
            )
        except requests.exceptions.Timeout:
            # This is expected and fine!
            pass
    
    # Start the request in a separate thread
    thread = threading.Thread(target=trigger_processing)
    thread.daemon = True  # This makes the thread exit when the main program exits
    thread.start()
    
    # Return response to the user immediately
    return {'status': 'processing', 'file_id': file_id}

@app.route('/api/process/<file_id>', methods=['POST'])
def process_file(file_id):
    # Process step 1
    update_status(file_id, "transcribing")
    text = perform_ocr(get_image(file_id))
    update_sourcefile(file_id, {"text_target": text, "status": "transcribed"})
    
    # Trigger next step as another fire-and-forget request
    import threading
    import requests
    
    def trigger_next_step():
        try:
            requests.post(
                f"http://localhost:5000/api/translate/{file_id}",
                timeout=0.1
            )
        except requests.exceptions.Timeout:
            pass
    
    thread = threading.Thread(target=trigger_next_step)
    thread.daemon = True
    thread.start()
    
    return {'status': 'processing_started'}

### Option 2: Supabase Queues + External Workers

**Description**: Use Supabase's built-in queue system with Python workers running on your application server.

**How it works**:
1. User uploads content which adds a message to a Supabase queue
2. Python workers poll the queue and process items
3. Workers update the database as processing progresses
4. Frontend subscribes to database changes via Supabase Realtime

**Pros**:
- Postgres-native solution that fits with existing stack
- Durable message queue with guaranteed delivery
- Dashboard for monitoring queues and messages
- Workers can run on same server as web application

**Cons**:
- Requires setting up worker processes
- Need to manage worker processes separately

**Implementation Example**:
```python
# In your upload handler
@app.route('/upload', methods=['POST'])
def upload_file():
    # Save the file
    file_id = save_file(request.files['file'])
    
    # Add to Supabase queue
    supabase.from_('pgmq_public.send_message').insert({
        'queue_name': 'image_processing',
        'message_body': {'file_id': file_id}
    }).execute()
    
    return {'status': 'processing', 'file_id': file_id}

# In your worker process
def process_queue():
    while True:
        # Poll the queue
        result = supabase.from_('pgmq_public.get_message').select('*').eq('queue_name', 'image_processing').execute()
        if result.data:
            message = result.data[0]
            try:
                # Process the message
                file_id = message['message_body']['file_id']
                process_file(file_id)
                
                # Mark as processed
                supabase.from_('pgmq_public.ack_message').insert({
                    'queue_name': 'image_processing',
                    'message_id': message['message_id']
                }).execute()
            except Exception as e:
                # Log error, message will be retried later
                print(f"Error processing message: {e}")
        
        time.sleep(5)  # Poll every 5 seconds
```

### Option 3: FastAPI with Background Tasks

**Description**: Replace Flask with FastAPI and use its built-in background tasks functionality.

**How it works**:
1. User uploads content to a FastAPI endpoint
2. FastAPI spins off a background task and returns immediately
3. Background task processes the content and updates the database
4. Frontend polls or subscribes to changes

**Pros**:
- Clean built-in API for background tasks
- Better async support than Flask
- Maintains Python codebase preference
- No additional infrastructure needed

**Cons**:
- Requires migration from Flask to FastAPI
- Tasks aren't durable (if server restarts, in-progress tasks are lost)
- Long-running CPU-intensive tasks may affect server performance

**Implementation Example**:
```python
from fastapi import FastAPI, BackgroundTasks, UploadFile
from fastapi.concurrency import run_in_threadpool

app = FastAPI()

def process_image(image_id: int):
    # Fetch image data
    image_data = get_image(image_id)
    
    # Process step 1: OCR (CPU-intensive)
    text = run_in_threadpool(lambda: perform_ocr(image_data))
    update_sourcefile(image_id, {"text_target": text, "status": "transcribed"})
    
    # Process step 2: Translation
    translation = run_in_threadpool(lambda: translate_text(text))
    update_sourcefile(image_id, {"text_english": translation, "status": "translated"})
    
    # Process step 3: Word extraction
    words = run_in_threadpool(lambda: extract_words(text))
    update_sourcefile(image_id, {"words": words, "status": "processed"})

@app.post("/upload-image/")
async def upload_image(file: UploadFile, background_tasks: BackgroundTasks):
    # Save file and create database entry
    image_id = await save_image(file)
    
    # Start background processing
    background_tasks.add_task(process_image, image_id)
    
    return {"message": "Processing started", "image_id": image_id}
```

### Option 4: Vercel Serverless with Chained Functions

**Description**: Migrate to Vercel for serverless Python hosting and break processing into smaller serverless functions.

**How it works**:
1. User uploads content to a serverless function
2. Initial function saves the file and triggers the first processing step
3. Each step triggers the next step via a "fire and forget" API call
4. Database stores state between steps
5. Frontend subscribes to database changes

**Pros**:
- Managed infrastructure (no server maintenance)
- Pay only for what you use
- Automatic scaling
- Can still use Python (Flask or FastAPI)

**Cons**:
- Function execution time limits (max 60 seconds per function on Hobby plan, 300 seconds on Pro)
- More complex implementation
- Need to break processing into smaller steps

**Implementation Example**:
```python
# api/upload.py
from http.server import BaseHTTPRequestHandler
import json
import requests

def save_file(file_data):
    # Save file to storage and return ID
    # ...
    return file_id

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Get file data from request
        content_length = int(self.headers['Content-Length'])
        file_data = self.rfile.read(content_length)
        
        # Save file
        file_id = save_file(file_data)
        
        # Trigger first processing step
        base_url = f"https://{process.env.VERCEL_URL}" if process.env.VERCEL_URL else "http://localhost:3000"
        requests.post(f"{base_url}/api/process-step1", json={"file_id": file_id}, timeout=0.1)
        
        # Return response
        self.send_response(202)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "processing", "file_id": file_id}).encode())

# api/process-step1.py
# Similar implementation for each step, with each step triggering the next
```

### Option 5: Hybrid Approach (Flask/FastAPI + Supabase Queues)

**Description**: Combine your web framework (either keeping Flask or migrating to FastAPI) with Supabase Queues for reliable background processing.

**How it works**:
1. User uploads content to a web endpoint
2. Web app adds a message to a Supabase queue and returns immediately
3. Python workers (separate processes) poll the queue and process items
4. Workers update the database as processing progresses
5. Frontend subscribes to database changes via Supabase Realtime

**Pros**:
- Reliable queue system with guaranteed message delivery
- Web server doesn't get blocked by long-running tasks
- Workers can be scaled independently of web server
- Can keep existing Flask codebase if preferred

**Cons**:
- More complex setup (multiple components)
- Need to manage worker processes

**Implementation Example**:
```python
# Flask web application
@app.route('/upload-image/', methods=['POST'])
def upload_image():
    # Save file and create database entry
    file = request.files['file']
    image_id = save_image(file)
    
    # Add to Supabase queue
    supabase.from_('pgmq_public.send_message').insert({
        'queue_name': 'image_processing',
        'message_body': {'image_id': image_id}
    }).execute()
    
    return {"message": "Processing started", "image_id": image_id}

# Separate worker process
def worker_main():
    while True:
        # Poll the queue
        result = supabase.from_('pgmq_public.get_message').select('*').eq('queue_name', 'image_processing').execute()
        if result.data:
            message = result.data[0]
            try:
                # Process the message
                image_id = message['message_body']['image_id']
                process_image(image_id)
                
                # Mark as processed
                supabase.from_('pgmq_public.ack_message').insert({
                    'queue_name': 'image_processing',
                    'message_id': message['message_id']
                }).execute()
            except Exception as e:
                # Log error, message will be retried later
                print(f"Error processing message: {e}")
        
        time.sleep(5)  # Poll every 5 seconds
```

## Vercel Serverless Python Limitations

Vercel imposes execution time limits on serverless functions:

- **Hobby plan**: 10s default, configurable up to 60s
- **Pro plan**: 15s default, configurable up to 300s (5 minutes)
- **Enterprise plan**: 15s default, configurable up to 900s (15 minutes)

These limits apply to the entire function execution, including any background tasks. This means:

1. If you use FastAPI's `BackgroundTasks` on Vercel, the tasks must complete within the function's execution time limit.
2. Background tasks will not continue after the response is sent if they exceed the time limit.
3. For truly long-running processes, you'll need to split the work into smaller units and chain them together.

To implement a chain of processing steps on Vercel:

1. Break your pipeline into discrete steps that can each complete within the time limit
2. Each step updates the database and triggers the next step
3. Use a "fire and forget" approach to trigger the next step via an API call
4. Store intermediate state in the database between steps

This approach works well because:
- Each function completes within the timeout
- The database maintains state between steps
- Even if one step fails, you can implement retry logic or manual intervention

## FastAPI vs. Flask for Background Processing

While FastAPI has built-in background tasks, Flask can achieve similar functionality using the fire-and-forget pattern with threading. The practical differences are:

1. **Syntax and API**: FastAPI's approach is more elegant and built into the framework
2. **Implementation**: Flask requires manual thread management
3. **Async Support**: FastAPI has better overall async support, but for this specific use case, the differences are minimal

Both frameworks can effectively implement the chained processing pattern required for long-running tasks, especially when deployed on platforms with execution time limits.

## Recommendations

Based on the requirements and current setup, we recommend the following approach:

### Immediate Solution (Minimal Changes)

1. **Implement Flask Fire-and-Forget Pattern**:
   - Add threading for fire-and-forget requests
   - Keep your existing Flask codebase
   - Chain processing steps by having each step trigger the next

2. **Implement status tracking in the database**:
   - Add status fields to track progress of each processing step
   - Frontend can poll or subscribe to these status changes

3. **Use ThreadPoolExecutor for CPU-intensive operations**:
   - Wrap CPU-intensive operations in a thread pool to avoid blocking
   - Update database as each step completes

### Medium-term Solution (More Robust)

1. **Implement Supabase Queues**:
   - Add Python worker processes to handle queued tasks
   - More reliable processing with guaranteed delivery
   - Better isolation between web server and processing

2. **Enhance real-time updates with Supabase Realtime**:
   - Frontend subscribes to database changes
   - UI updates automatically as processing progresses

3. **Consider FastAPI Migration** (optional, based on other needs):
   - If other FastAPI features would benefit your application
   - Built-in async support and background tasks
   - Can still host on Fly.io

### Long-term Considerations

If the application grows more complex or needs higher reliability:

1. **Consider a dedicated task queue system**:
   - Options include Celery, RQ, or Dramatiq
   - Provides better monitoring, retries, and scheduling

2. **Evaluate serverless options**:
   - Vercel can work with either Flask or FastAPI, using the chained function approach
   - AWS Lambda with Step Functions for complex workflows

## Conclusion

For a prototype application prioritizing simplicity and rapid development, enhancing the current Flask application with the fire-and-forget pattern offers the path of least resistance. This approach allows you to:

1. Keep your existing codebase
2. Implement background processing with minimal changes
3. Chain multiple steps for long-running processes
4. Avoid UI blocking during processing

For increased reliability, adding Supabase Queues later provides a good upgrade path without requiring a full framework migration. The key is implementing a state machine in the database to track processing status and breaking the pipeline into discrete steps that can be processed independently. 