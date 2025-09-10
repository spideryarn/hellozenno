# Adding Private Flag to Sourcedir

## Overview
Add a private boolean field to the Sourcedir model that allows users to mark source directories as private. Private directories will only be visible to their owners, adding a layer of privacy control to the HelloZenno application. This feature will help users separate their personal learning materials from publicly visible content.

## Requirements

1. Add a `private` boolean field to the `Sourcedir` model, defaulting to `false`
2. Create a database migration to add this field
3. Add an API endpoint to set the private status of a sourcedir
4. Update the frontend to display and toggle the private status
5. Modify the sourcedir listing to display private status indicators
6. Filter sourcedirs in listing views to respect privacy settings (only show private dirs to their owners)

## Implementation Details

### 1. Database Model Changes

Add a private boolean field to the Sourcedir model in `db_models.py`:

```python
class Sourcedir(BaseModel):
    path = CharField()  # the directory path
    target_language_code = CharField()  # 2-letter language code (e.g. "el" for Greek)
    slug = CharField(max_length=SOURCEDIR_SLUG_MAX_LENGTH)
    description = TextField(null=True)  # description of the directory content
    created_by = ForeignKeyField(
        AuthUser, backref="sourcedirs", null=True, on_delete="CASCADE"
    )
    private = BooleanField(default=False)  # if True, dir is only visible to owner
```

### 2. Database Migration

Create migration file `037_add_sourcedir_private.py` to add the private field:

```python
def migrate(migrator: Migrator, database: pw.Database, *, fake=False):
    """Add private boolean field to Sourcedir with default False."""
    # Define Sourcedir model class for the migration
    class Sourcedir(pw.Model):
        private = pw.BooleanField(default=False)
        
        class Meta:
            table_name = 'sourcedir'
    
    # Add the private field with a default value of False
    with database.atomic():
        migrator.add_fields(
            Sourcedir,
            private=pw.BooleanField(default=False),
        )
```

### 3. API Endpoint for Setting Privacy

Add a new endpoint to `sourcedir_api.py` for setting the private flag:

```python
@sourcedir_api_bp.route(
    "/<target_language_code>/<sourcedir_slug>/set_private",
    methods=["PUT"],
)
@api_auth_required
def set_sourcedir_private_api(
    target_language_code: str, sourcedir_slug: str
):
    """Set the private flag of a sourcedir to a specific value."""
    try:
        # Get the sourcedir entry
        sourcedir_entry = _get_sourcedir_entry(
            target_language_code, sourcedir_slug
        )
        
        # Verify ownership
        if sourcedir_entry.created_by_id != g.user_id:
            return jsonify({"error": "You don't have permission to modify this directory's privacy settings"}), 403

        # Get the new value from the request
        data = request.get_json() or {}
        if "private" not in data:
            return jsonify({"error": "Missing 'private' parameter"}), 400
            
        # Use the provided value
        new_private_value = bool(data["private"])

        # Update the private flag
        sourcedir_entry.private = new_private_value
        sourcedir_entry.save()

        return jsonify({"private": new_private_value}), 200

    except DoesNotExist:
        return jsonify({"error": "Directory not found"}), 404
    except Exception as e:
        current_app.logger.error(f"Error setting privacy status: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

### 4. Frontend Changes

#### 4.1 JavaScript for Sourcedir Privacy Toggle

Update `sourcedirs.js` to include a function for setting privacy:

```javascript
// Set private flag
function setSourcedirPrivate(sourcedirSlug, isPrivate) {
    const url = resolveRoute('SOURCEDIR_API_SET_SOURCEDIR_PRIVATE_API', {
        target_language_code: window.target_language_code,
        sourcedir_slug: sourcedirSlug
    });

    return fetch(url, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ private: isPrivate })
    }).then(async response => {
        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Failed to set privacy status');
        }
        
        return response.json();
    });
}
```

#### 4.2 Update SourcedirHeader.svelte Component

Add a private toggle to the `SourcedirHeader.svelte` component:

```svelte
<!-- Private toggle section -->
{#if data.session}
  <div class="private-toggle-section">
    <div class="d-flex align-items-center">
      <span class="me-2">Private:</span>
      <div class="form-check form-switch">
        <input 
          class="form-check-input" 
          type="checkbox" 
          role="switch" 
          id="privateSwitch"
          checked={sourcedir.private ?? false}
          on:change={() => togglePrivate()}
        >
        <label class="form-check-label" for="privateSwitch">
          {sourcedir.private ? 'Private' : 'Public'}
        </label>
      </div>
    </div>
    <small class="text-muted">
      {sourcedir.private 
        ? 'This directory is private and only visible to you' 
        : 'This directory is public and visible to everyone'}
    </small>
  </div>
{/if}
```

With the corresponding toggle function:

```javascript
async function togglePrivate() {
  try {
    const response = await fetch(
      getApiUrl(
        RouteName.SOURCEDIR_API_SET_SOURCEDIR_PRIVATE_API,
        {
          target_language_code,
          sourcedir_slug
        }
      ),
      {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ private: !sourcedir.private })
      }
    );
    
    if (!response.ok) {
      throw new Error(`Failed to toggle private flag: ${response.statusText}`);
    }
    
    const result = await response.json();
    
    // Update the local state to reflect the change
    sourcedir.private = result.private;
  } catch (error) {
    console.error('Error toggling private flag:', error);
    alert('Failed to update private status. Please try again.');
  }
}
```

### 5. Update Sourcedir Listing

Modify `sourcedirs.jinja` to show privacy status indicators:

```html
<li>
    <a href="{{ url_for('sourcedir_views.sourcefiles_for_sourcedir_vw', target_language_code=target_language_code, sourcedir_slug=dir.slug) }}">
        {{ dir.path }}
    </a>
    {% if dir.private %}
        <span title="Private - only visible to you">
            <i class="ph-fill ph-lock" style="color: #f59e0b;"></i>
        </span>
    {% endif %}
    {% if dir.slug in empty_sourcedirs %}
        <button class="button delete-btn" onclick="confirmDelete('{{ dir.slug }}')">Delete</button>
    {% endif %}
</li>
```

### 6. Backend Privacy Filtering

Modify `get_sourcedirs_for_language()` in `sourcedir_utils.py` to filter private sourcedirs:

```python
def get_sourcedirs_for_language(target_language_code: str, sort_by: str = "date", current_user_id=None):
    """
    Get all sourcedirs for a specific language with metadata.
    
    Args:
        target_language_code: Language code to filter by
        sort_by: Sorting method ("date" or "alpha")
        current_user_id: Optional ID of the current user for filtering private dirs
        
    Returns:
        A dictionary with sourcedir data and metadata
    """
    from utils.lang_utils import get_language_name
    from db_models import Sourcedir, Sourcefile
    from peewee import fn, SQL
    from flask import g
    
    # Get the current user ID from g if not provided
    if current_user_id is None and hasattr(g, 'user') and g.user:
        current_user_id = g.user.get('id')
    
    # Base query
    query = Sourcedir.select().where(Sourcedir.target_language_code == target_language_code)
    
    # Add privacy filtering
    if current_user_id:
        # If user is logged in, show public dirs plus their own private dirs
        query = query.where(
            (Sourcedir.private == False) | 
            ((Sourcedir.private == True) & (Sourcedir.created_by == current_user_id))
        )
    else:
        # If no user is logged in, only show public dirs
        query = query.where(Sourcedir.private == False)
    
    # Apply sorting
    if sort_by == "date":
        query = query.order_by(fn.COALESCE(Sourcedir.updated_at, Sourcedir.created_at).desc())
    else:
        query = query.order_by(fn.LOWER(Sourcedir.path))
    
    # Build response
    sourcedirs = []
    empty_sourcedirs = []
    
    for sourcedir_entry in query:
        # Check if sourcedir is empty
        if sourcedir_entry.sourcefiles.count() == 0:
            empty_sourcedirs.append(sourcedir_entry.slug)
            
        sourcedirs.append({
            "id": sourcedir_entry.id,
            "path": sourcedir_entry.path,
            "slug": sourcedir_entry.slug,
            "target_language_code": sourcedir_entry.target_language_code,
            "description": sourcedir_entry.description,
            "private": sourcedir_entry.private,
            "created_at": sourcedir_entry.created_at,
            "updated_at": sourcedir_entry.updated_at,
        })
    
    return {
        "sourcedirs": sourcedirs,
        "empty_sourcedirs": empty_sourcedirs,
        "target_language_name": get_language_name(target_language_code),
    }
```

Also update related views in `sourcedir_views.py` to pass the current user ID.

## Testing Plan

1. Verify database migration adds the private field correctly
2. Test setting a sourcedir to private via the API 
3. Verify private sourcedirs are only visible to their owners in listings
4. Test the UI toggle functionality for changing privacy settings
5. Ensure private indicators appear correctly in the sourcedir listing
6. Test that anonymous users cannot see private sourcedirs
7. Verify that the API enforces ownership checks when setting privacy

## Implementation Steps

1. Create the database migration
2. Update the Sourcedir model
3. Implement the API endpoint
4. Update the sourcedir listing to show private status
5. Update sourcedir_utils.py to filter private sourcedirs
6. Add private toggle to the SourcedirHeader component
7. Run the migration
8. Test functionality