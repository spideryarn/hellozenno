// Modal handling
const btn = document.getElementById('newSourcedirBtn');

btn.onclick = async () => {
    try {
        const name = await showModal({
            placeholder: "Enter directory name",
            confirmText: "Create",
            cancelText: "Cancel"
        });

        const url = resolveRoute('SOURCEDIR_API_CREATE_SOURCEDIR_API', { target_language_code: window.target_language_code });
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: name })
        });

        if (!response.ok) {
            let errorMsg;
            try {
                const data = await response.json();
                errorMsg = data.error;
            } catch (e) {
                // If response isn't JSON, use status text
                errorMsg = `Server returned ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMsg || 'Failed to create directory');
        }

        const { slug } = await response.json();
        // Navigate to the new sourcedir's page using slug
        const sourcefileListUrl = resolveRoute('SOURCEDIR_VIEWS_SOURCEFILES_FOR_SOURCEDIR_VW', {
            target_language_code: window.target_language_code,
            sourcedir_slug: slug
        });
        window.location.href = sourcefileListUrl;
    } catch (error) {
        if (error.message !== 'User cancelled') {
            alert('Error creating directory: ' + error.message);
        }
    }
};

// Directory operations
const confirmDelete = async (sourcedirSlug) => {
    if (!confirm(`Are you sure you want to delete this directory?`)) {
        return;
    }

    try {
        const url = resolveRoute('SOURCEDIR_API_DELETE_SOURCEDIR_API', {
            target_language_code: window.target_language_code,
            sourcedir_slug: sourcedirSlug
        });
        const response = await fetch(url, {
            method: 'DELETE'
        });

        if (!response.ok) {
            let errorMsg;
            try {
                const data = await response.json();
                errorMsg = data.error;
            } catch (e) {
                errorMsg = `Server returned ${response.status}: ${response.statusText}`;
            }
            throw new Error(errorMsg || 'Failed to delete directory. If the directory contains files, you must delete all files first.');
        }

        // Reload the page to show updated list
        window.location.reload();
    } catch (error) {
        alert('Error deleting directory: ' + error.message);
    }
}