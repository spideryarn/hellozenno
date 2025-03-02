/** @type {import('tailwindcss').Config} */
export default {
    content: [
        './src/**/*.{html,js,svelte,ts}',
        '../templates/**/*.jinja',  // Include Jinja templates
    ],
    // Use a prefix to avoid conflicts with existing CSS
    prefix: 'tw-',
    theme: {
        extend: {
            colors: {
                // Match existing color scheme
                primary: '#2563eb',
                secondary: '#1d4ed8',
                danger: '#dc2626',
                success: '#16a34a',
            },
        },
    },
    plugins: [],
} 