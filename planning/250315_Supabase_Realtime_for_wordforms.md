# Implementing Supabase Realtime for Wordforms

## Status: Draft

## Summary
This document outlines a plan to implement real-time updates for wordforms using Supabase's Realtime feature. The goal is to create a parallel implementation that doesn't disrupt existing functionality, allowing us to explore Supabase Realtime while keeping things simple. The implementation will be broken down into stages, starting with the simplest possible approach.

## Context and Problem Statement
Currently, the wordforms list for a sourcefile is rendered from backend data and requires a page refresh to see updates. We want to explore how Supabase Realtime can be used to automatically update the list when changes occur in the database.

## Decision Drivers
- Keep implementation simple (prototype/exploratory)
- Minimal disruption to existing functionality
- No authentication requirements at this stage
- Prefer frontend-only solution if possible
- Implement in stages, from simplest to more complex

## Considered Options
1. Modify existing components to add Realtime capability
2. Create a parallel implementation with a new route/component
3. Set up a backend event system that pushes updates to the frontend

## Decision
**Option 2: Create a parallel implementation with a new route/component**

This allows us to explore the technology without risking the existing functionality. It also provides a clear comparison between the current approach and the Realtime approach.

## Implementation Stages

### Stage 1: Minimal Viable Implementation
In this stage, we create the simplest possible implementation to demonstrate Supabase Realtime functionality.

#### 1.1 Create a Basic Route and Template
Add a new route `/el/{sourcedir_slug}/{sourcefile_slug}/words2` with a simplified template:

```python
@sourcefile_views_bp.route(
    "/<target_language_code>/<sourcedir_slug>/<sourcefile_slug>/words2"
)
def inspect_sourcefile_words_realtime(
    target_language_code: str, sourcedir_slug: str, sourcefile_slug: str
):
    """Display the words of a source file with real-time updates."""
    target_language_name = get_language_name(target_language_code)

    try:
        # Get the sourcefile entry
        sourcefile_entry = _get_sourcefile_entry(
            target_language_code, sourcedir_slug, sourcefile_slug
        )
        
        # Get common template parameters (similar to existing view)
        template_params = _get_common_template_params(
            target_language_code, 
            target_language_name, 
            sourcefile_entry, 
            sourcedir_slug, 
            sourcefile_slug,
            # Other parameters...
        )

        # Add specific parameters for Realtime
        template_params.update({
            "active_tab": "words2",
            "sourcefile_id": sourcefile_entry.id,
            "supabase_url": current_app.config["SUPABASE_URL"],
            "supabase_anon_key": current_app.config["SUPABASE_ANON_KEY"],
        })

        return render_template("sourcefile_words_realtime.jinja", **template_params)
    except DoesNotExist:
        abort(404, description="File not found")
```

Create a simple template:

```jinja
{% extends "base.jinja" %}
{% from "_sourcefile_icon.jinja" import sourcefile_icon %}

{% block breadcrumbs %}
    » <a href="{{ url_for('views.languages') }}">Languages</a>
    » <a href="{{ url_for('sourcedir_views.sourcedirs_for_language', target_language_code=target_language_code) }}">{{ target_language_name }}</a>
    » <a href="{{ url_for('sourcedir_views.sourcefiles_for_sourcedir', target_language_code=target_language_code, sourcedir_slug=sourcedir_slug) }}">{{ sourcedir }}</a>
    » {{ sourcefile }}
{% endblock breadcrumbs %}

{% block content %}
<div class="container">
    {% include '_sourcefile_header.jinja' %}

    <div class="tab-content">
        <h2>Words (Realtime) <small id="wordforms-count"></small></h2>
        
        <div id="wordforms-list"></div>
        
        <script>
            // Make Supabase config available to the frontend
            window.SUPABASE_CONFIG = {
                url: "{{ supabase_url }}",
                anonKey: "{{ supabase_anon_key }}",
                sourcefileId: {{ sourcefile_id }}
            };
            
            document.addEventListener('DOMContentLoaded', function() {
                initRealtimeWordforms();
            });
        </script>
        <script src="{{ url_for('static', filename='js/realtime-wordforms.js') }}"></script>
    </div>
</div>
{% endblock content %}
```

#### 1.2 Create a Vanilla JS Implementation

Create a simple JavaScript file for realtime updates:

```javascript
// static/js/realtime-wordforms.js
async function initRealtimeWordforms() {
    const config = window.SUPABASE_CONFIG || {};
    const { createClient } = supabase;
    
    // Check if Supabase script is loaded
    if (!createClient) {
        console.error('Supabase client not found. Make sure to include the Supabase script.');
        return;
    }
    
    // Create Supabase client
    const supabase = createClient(config.url, config.anonKey);
    const sourcefileId = config.sourcefileId;
    const wordformsList = document.getElementById('wordforms-list');
    const wordformsCount = document.getElementById('wordforms-count');
    
    // Add loading indicator
    wordformsList.innerHTML = '<p>Loading wordforms...</p>';
    
    // Fetch initial data
    await fetchWordforms();
    
    // Set up realtime subscription
    const channel = supabase
        .channel('wordforms-changes')
        .on('postgres_changes', 
            {
                event: '*', 
                schema: 'public',
                table: 'sourcefilewordform',
                filter: `sourcefile_id=eq.${sourcefileId}`
            }, 
            (payload) => {
                console.log('Realtime update received:', payload);
                
                // Show update notification
                showUpdateNotification();
                
                // Refresh data
                fetchWordforms();
            }
        )
        .subscribe((status) => {
            console.log('Subscription status:', status);
            
            if (status === 'SUBSCRIBED') {
                console.log('Successfully subscribed to changes');
            } else if (status === 'CHANNEL_ERROR') {
                console.error('Failed to subscribe to changes');
                wordformsList.innerHTML = '<p class="error">Error subscribing to real-time updates</p>';
            }
        });
    
    // Fetch wordforms from Supabase
    async function fetchWordforms() {
        try {
            wordformsList.classList.add('loading');
            
            const { data, error } = await supabase
                .from('sourcefilewordform')
                .select(`
                    id,
                    centrality,
                    ordering,
                    wordform:wordform_id(
                        id,
                        wordform,
                        translations,
                        part_of_speech,
                        lemma_entry:lemma_entry_id(
                            id,
                            lemma
                        )
                    )
                `)
                .eq('sourcefile_id', sourcefileId)
                .order('ordering');
            
            if (error) throw error;
            
            // Update UI
            renderWordforms(data);
            
            // Update count
            if (wordformsCount) {
                wordformsCount.textContent = `(${data.length})`;
            }
            
        } catch (err) {
            console.error('Error fetching wordforms:', err);
            wordformsList.innerHTML = `<p class="error">Error loading wordforms: ${err.message}</p>`;
        } finally {
            wordformsList.classList.remove('loading');
        }
    }
    
    // Render wordforms to the UI
    function renderWordforms(data) {
        if (!data || data.length === 0) {
            wordformsList.innerHTML = '<p class="no-entries"><em>No words found in this source file</em></p>';
            return;
        }
        
        const items = data.map(item => {
            const wordform = item.wordform;
            const translation = wordform.translations && wordform.translations.length > 0 
                ? wordform.translations[0] : '';
            
            return `
                <div class="wordform-item" data-id="${item.id}">
                    <a href="/${window.target_language_code}/wordform/${encodeURIComponent(wordform.wordform)}" 
                       class="wordform-link">
                        <span class="wordform">${wordform.wordform}</span>
                        ${translation ? `<span class="translation">${translation}</span>` : ''}
                    </a>
                </div>
            `;
        }).join('');
        
        wordformsList.innerHTML = `<div class="wordforms-list">${items}</div>`;
    }
    
    // Show update notification
    function showUpdateNotification() {
        const notification = document.createElement('div');
        notification.className = 'update-notification';
        notification.textContent = 'Wordforms updated!';
        
        document.body.appendChild(notification);
        
        // Make element visible with CSS animation
        setTimeout(() => {
            notification.classList.add('visible');
        }, 10);
        
        // Remove after 3 seconds
        setTimeout(() => {
            notification.classList.remove('visible');
            setTimeout(() => {
                notification.remove();
            }, 300); // matches CSS transition duration
        }, 3000);
    }
    
    // Clean up on page unload
    window.addEventListener('beforeunload', () => {
        if (channel) {
            supabase.removeChannel(channel);
        }
    });
}
```

Add CSS for the notification:

```css
/* Add to base.css or include in the template */
.update-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s ease-out;
    z-index: 1000;
}

.update-notification.visible {
    opacity: 1;
    transform: translateY(0);
}

.wordforms-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
}

.wordform-item {
    padding: 0.5rem;
    border-radius: 4px;
    background-color: #f8f9fa;
}

.wordform-link {
    display: flex;
    flex-direction: column;
    text-decoration: none;
    color: inherit;
}

.wordform {
    font-weight: bold;
}

.translation {
    color: #666;
    font-size: 0.9em;
    font-style: italic;
}

.loading {
    opacity: 0.7;
}

.error {
    color: #d9534f;
    font-style: italic;
}
```

#### 1.3 Add the Supabase Script

Update the base template to include the Supabase JS library:

```jinja
<!-- In base.jinja, before the closing </head> tag -->
<script src="{{ url_for('static', filename='js/extern/supabase.js') }}"></script>
```

Download the Supabase JS client and save it to static/js/extern:

```bash
curl https://cdn.jsdelivr.net/npm/@supabase/supabase-js/dist/umd/supabase.js -o static/js/extern/supabase.js
```

#### 1.4 Update Backend Configuration
Add Supabase configuration:

```python
# In app.py or config.py
from utils.env_config import SUPABASE_URL, SUPABASE_ANON_KEY

app.config['SUPABASE_URL'] = SUPABASE_URL.get_secret_value()
app.config['SUPABASE_ANON_KEY'] = SUPABASE_ANON_KEY.get_secret_value()
```

And update env_config.py:

```python
from pydantic import SecretStr, Field
# Add to existing environment variables
SUPABASE_URL: SecretStr = Field("", env="SUPABASE_URL")
SUPABASE_ANON_KEY: SecretStr = Field("", env="SUPABASE_ANON_KEY")
```

Update .env.example and your local .env file with Supabase settings.

#### 1.5 Update Navigation
Add a link to the new view in the sourcefile header:

```jinja
<!-- In _sourcefile_header.jinja -->
<div class="tab-navigation">
    <!-- Existing tabs -->
    <a href="{{ url_for('sourcefile_views.inspect_sourcefile_text', target_language_code=target_language_code, sourcedir_slug=sourcedir_slug, sourcefile_slug=sourcefile_slug) }}" class="tab-link{% if active_tab == 'text' %} active{% endif %}">Text</a>
    <a href="{{ url_for('sourcefile_views.inspect_sourcefile_words', target_language_code=target_language_code, sourcedir_slug=sourcedir_slug, sourcefile_slug=sourcefile_slug) }}" class="tab-link{% if active_tab == 'words' %} active{% endif %}">Words</a>
    <!-- New tab -->
    <a href="{{ url_for('sourcefile_views.inspect_sourcefile_words_realtime', target_language_code=target_language_code, sourcedir_slug=sourcedir_slug, sourcefile_slug=sourcefile_slug) }}" class="tab-link{% if active_tab == 'words2' %} active{% endif %}">Words (RT)</a>
    <!-- Other tabs -->
</div>
```

### Stage 2: Svelte Component Implementation
Once Stage 1 is working, we can enhance the implementation with Svelte components for better maintainability and reactivity.

#### 2.1 Create Supabase Client (frontend/src/lib/supabase.ts)
```typescript
import { createClient } from '@supabase/supabase-js';

// Get config from window object
const config = window.SUPABASE_CONFIG || {};

// Create a single supabase client for the entire app
export const supabase = createClient(
  config.url || '',
  config.anonKey || ''
);
```

#### 2.2 Create WordformsRealtime Component (frontend/src/components/WordformsRealtime.svelte)
```svelte
<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { writable } from 'svelte/store';
  import { supabase } from '../lib/supabase';
  import MiniWordform from './MiniWordform.svelte';
  
  // Props
  export let sourcefileId: number;
  export let targetLanguageCode: string;
  
  // Store for wordforms
  const wordforms = writable<any[]>([]);
  let loading = true;
  let error = null;
  let subscription: any;
  let wordformsCount = 0;
  let showUpdateNotification = false;
  
  // Helper to get URL for wordform
  function getWordformUrl(wordform: string): string {
    return `/${targetLanguageCode}/wordform/${encodeURIComponent(wordform)}`;
  }
  
  // Fetch wordforms from Supabase
  async function fetchWordforms() {
    try {
      loading = true;
      
      // Query the sourcefilewordform table with appropriate joins
      const { data, error: queryError } = await supabase
        .from('sourcefilewordform')
        .select(`
          id,
          centrality,
          ordering,
          wordform:wordform_id(
            id,
            wordform,
            translations,
            lemma_entry:lemma_entry_id(
              id,
              lemma
            )
          )
        `)
        .eq('sourcefile_id', sourcefileId)
        .order('ordering');
      
      if (queryError) throw queryError;
      
      // Transform data for component
      const transformedData = data.map(item => ({
        id: item.id,
        wordform: item.wordform.wordform,
        translation: item.wordform.translations && item.wordform.translations.length > 0 
          ? item.wordform.translations[0] 
          : null,
        href: getWordformUrl(item.wordform.wordform),
        ordering: item.ordering,
        lemma: item.wordform.lemma_entry ? item.wordform.lemma_entry.lemma : null
      }));
      
      wordforms.set(transformedData);
      wordformsCount = transformedData.length;
      
      // Update count in the UI
      const countEl = document.getElementById('wordforms-count');
      if (countEl) countEl.textContent = `(${wordformsCount})`;
      
    } catch (err) {
      console.error('Error fetching wordforms:', err);
      error = err;
    } finally {
      loading = false;
    }
  }

  // Display update notification
  function displayUpdateNotification() {
    showUpdateNotification = true;
    setTimeout(() => {
      showUpdateNotification = false;
    }, 3000);
  }

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
          else if (payload.eventType === 'UPDATE') {
            // For UPDATE, update the specific record
            wordforms.update(items => {
              const index = items.findIndex(item => item.id === payload.new.id);
              if (index !== -1) {
                // Just update ordering/centrality, as those are the most likely to change
                items[index] = { 
                  ...items[index], 
                  ordering: payload.new.ordering,
                  centrality: payload.new.centrality
                };
              }
              return [...items].sort((a, b) => a.ordering - b.ordering);
            });
          } 
          else if (payload.eventType === 'DELETE') {
            // For DELETE, remove the item
            wordforms.update(items => 
              items.filter(item => item.id !== payload.old.id)
            );
            
            // Update count
            wordformsCount--;
            const countEl = document.getElementById('wordforms-count');
            if (countEl) countEl.textContent = `(${wordformsCount})`;
          }
        }
      )
      .subscribe((status) => {
        console.log('Subscription status:', status);
        
        if (status === 'CHANNEL_ERROR') {
          console.error('Failed to subscribe to changes');
          error = new Error('Failed to subscribe to real-time updates');
        }
      });
  }
  
  onMount(() => {
    console.log('WordformsRealtime mounted, fetching data for sourcefile:', sourcefileId);
    fetchWordforms();
    setupRealtimeSubscription();
  });
  
  onDestroy(() => {
    if (subscription) {
      supabase.removeChannel(subscription);
    }
  });
</script>

<div class="wordforms-realtime">
  {#if loading}
    <p>Loading wordforms...</p>
  {:else if error}
    <p class="error">Error loading wordforms: {error.message}</p>
  {:else if $wordforms.length === 0}
    <p class="no-entries"><em>No words found in this source file</em></p>
  {:else}
    <div class="wordforms-list">
      {#each $wordforms as wordform (wordform.id)}
        <MiniWordform 
          wordform={wordform.wordform} 
          translation={wordform.translation} 
          href={wordform.href} 
        />
      {/each}
    </div>
  {/if}
  
  {#if showUpdateNotification}
    <div class="update-notification visible">
      Wordforms updated!
    </div>
  {/if}
</div>

<style>
  .wordforms-realtime {
    margin-top: 1rem;
  }
  
  .wordforms-list {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .no-entries, .error {
    color: #666;
    font-style: italic;
  }
  
  .error {
    color: #d9534f;
  }
  
  .update-notification {
    position: fixed;
    bottom: 20px;
    right: 20px;
    background-color: #4CAF50;
    color: white;
    padding: 10px 20px;
    border-radius: 4px;
    opacity: 0;
    transform: translateY(20px);
    transition: all 0.3s ease-out;
    z-index: 1000;
  }
  
  .update-notification.visible {
    opacity: 1;
    transform: translateY(0);
  }
</style>
```

#### 2.3 Update Template for Stage 2
Update the template to use the Svelte component:

```jinja
{% extends "base.jinja" %}
{% from "_sourcefile_icon.jinja" import sourcefile_icon %}
{% from "base_svelte.jinja" import load_svelte_component %}

{# Specify the Vite entry points for components #}
{% set vite_entries = ['wordformsrealtime'] %}

{% block breadcrumbs %}
    » <a href="{{ url_for('views.languages') }}">Languages</a>
    » <a href="{{ url_for('sourcedir_views.sourcedirs_for_language', target_language_code=target_language_code) }}">{{ target_language_name }}</a>
    » <a href="{{ url_for('sourcedir_views.sourcefiles_for_sourcedir', target_language_code=target_language_code, sourcedir_slug=sourcedir_slug) }}">{{ sourcedir }}</a>
    » {{ sourcefile }}
{% endblock breadcrumbs %}

{% block content %}
<div class="container">
    {% include '_sourcefile_header.jinja' %}

    <div class="tab-content">
        <h2>Words (Realtime) <small id="wordforms-count"></small></h2>
        
        <div id="wordforms-realtime"></div>
        
        <script>
            // Make Supabase config available to the frontend
            window.SUPABASE_CONFIG = {
                url: "{{ supabase_url }}",
                anonKey: "{{ supabase_anon_key }}",
                sourcefileId: {{ sourcefile_id }}
            };
        </script>
        
        {{ load_svelte_component('WordformsRealtime', {
            'sourcefileId': sourcefile_id,
            'targetLanguageCode': target_language_code
        }, component_id='wordforms-realtime') }}
    </div>

    <script>
        window.target_language_code = "{{ target_language_code }}";
        window.sourcedir_slug = "{{ sourcedir_slug }}";
        window.sourcefile_slug = "{{ sourcefile_slug }}";
        window.sourcefile = "{{ sourcefile }}";
    </script>
</div>
{% endblock content %}
```

## Technical Details

### Supabase Realtime Throttling
Supabase automatically throttles messages to 10 messages per second (1 message every 100ms) by default, so we don't need to implement our own debouncing for this prototype. If we need to adjust this, we can use the `eventsPerSecond` parameter when creating the client.

### Error Handling
The implementation includes error handling for:
1. Failed database queries
2. Subscription status errors
3. Connection issues with clear UI feedback

### Update Notification
A simple visual notification appears when real-time updates are received, to make the feature more apparent to users.

### Environment Variables
For the prototype, we'll use the simplest approach: injecting Supabase credentials via the Flask template into window variables. This avoids setting up a complete frontend environment variable system.

### Required Supabase Configuration
Supabase Realtime must be enabled for the `sourcefilewordform` table. This is typically done in the Supabase dashboard under "Database" → "Replication".

## Advantages of Staged Implementation

1. **Start Simple**: Begin with a vanilla JS implementation that's easy to debug and doesn't introduce dependencies on Svelte or complex UI components.

2. **Iterate Incrementally**: Add more sophisticated features after confirming the basic functionality works.

3. **Minimize Risk**: Each stage has a working implementation, so if issues arise in later stages, we can fall back to earlier implementations.

4. **Educational Value**: The process demonstrates how to enhance an implementation over time, making it an informative example.

## Future Improvements

After Stage 2 is complete, possible future improvements include:

1. Add authentication and row-level security
2. Move environment variables to a more standard frontend configuration
3. Add real-time updates to other parts of the application (phrases, text, etc.)