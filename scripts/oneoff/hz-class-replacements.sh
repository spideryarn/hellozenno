#\!/bin/bash
# Script to update class names with hz- prefix in Hello Zenno codebase

cd /Users/greg/Dropbox/dev/experim/hellozenno

echo "Replacing button classes in HTML/Svelte files..."

# 1. Button Classes in HTML/Svelte classes
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-primary([^"]*)"/class="$1hz-btn-primary$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-secondary([^"]*)"/class="$1hz-btn-secondary$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-success([^"]*)"/class="$1hz-btn-success$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-danger([^"]*)"/class="$1hz-btn-danger$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-warning([^"]*)"/class="$1hz-btn-warning$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-info([^"]*)"/class="$1hz-btn-info$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-outline-danger([^"]*)"/class="$1hz-btn-outline-danger$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)btn-action([^"]*)"/class="$1hz-btn-action$2"/g'

echo "Replacing text/bg classes in HTML/Svelte files..."

# 2. Text and Background Classes in HTML/Svelte
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)text-primary-green([^"]*)"/class="$1hz-text-primary-green$2"/g'
find frontend -type f \( -name "*.svelte" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/class="([^"]*)bg-dark([^"]*)"/class="$1hz-bg-dark$2"/g'

echo "Replacing classes in CSS files..."

# 3. CSS class selectors
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-primary/\.hz-btn-primary/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-secondary/\.hz-btn-secondary/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-success/\.hz-btn-success/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-danger/\.hz-btn-danger/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-warning/\.hz-btn-warning/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-info/\.hz-btn-info/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-outline-danger/\.hz-btn-outline-danger/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.btn-action/\.hz-btn-action/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.text-primary-green/\.hz-text-primary-green/g'
find frontend -type f -name "*.css" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\.bg-dark/\.hz-bg-dark/g'

echo "Fixing documentation references..."

# 4. Documentation references
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-primary\`/\`\.hz-btn-primary\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-secondary\`/\`\.hz-btn-secondary\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-success\`/\`\.hz-btn-success\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-danger\`/\`\.hz-btn-danger\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-warning\`/\`\.hz-btn-warning\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-info\`/\`\.hz-btn-info\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-outline-danger\`/\`\.hz-btn-outline-danger\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.btn-action\`/\`\.hz-btn-action\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.text-primary-green\`/\`\.hz-text-primary-green\`/g'
find frontend -type f -name "*.md" -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/\`\.bg-dark\`/\`\.hz-bg-dark\`/g'

echo "Checking for any double prefixing..."

# 5. Check and fix any accidental double prefixes
find frontend -type f \( -name "*.svelte" -o -name "*.css" -o -name "*.md" -o -name "*.html" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs perl -i -pe 's/hz-hz-/hz-/g'

echo "Checking for any remaining unprefixed button classes:"
find frontend -type f \( -name "*.svelte" -o -name "*.css" \) -not -path "*/node_modules/*" -not -path "*/.svelte-kit/*" -not -path "*/extern/*" -not -path "*/.vercel/*" | xargs grep -l "\bclass=\"[^\"]*btn-" | grep -v "btn-sm" | grep -v "btn-lg" || echo "No unprefixed button classes found\!"

grep -r "hz-hz-" frontend --include="*.css" --include="*.svelte" --include="*.html" --include="*.md" || echo "No double prefixes found\!"
