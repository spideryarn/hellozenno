/** @type {import('tailwindcss').Config} */
export default {
    prefix: 'tw-',
    content: [
        "../templates/**/*.{html,jinja}",
        "./src/**/*.{js,ts,jsx,tsx,svelte}",
    ],
    theme: {
        extend: {
            fontFamily: {
                'serif': ['Times New Roman', 'Times', 'serif'],
                'mono': ['Courier New', 'Courier', 'monospace'],
            },
            colors: {
                'primary': '#2563eb',    // Blue-600
                'primary-hover': '#1d4ed8',  // Blue-700
                'danger': '#dc2626',     // Red-600
                'danger-hover': '#b91c1c',  // Red-700
                'success': '#16a34a',    // Green-600
                'success-hover': '#15803d',  // Green-700
            },
            typography: {
                DEFAULT: {
                    css: {
                        fontFamily: 'Times New Roman, Times, serif',
                        maxWidth: 'none',
                        color: '#333',
                        h1: {
                            fontWeight: '400',
                        },
                        h2: {
                            fontWeight: '400',
                        },
                        h3: {
                            fontWeight: '400',
                        },
                    },
                },
            },
            container: {
                center: true,
                padding: '1rem',
                screens: {
                    sm: '640px',
                    md: '768px',
                    lg: '1024px',
                    xl: '1280px',
                    '2xl': '1536px',
                },
            },
        },
    },
    plugins: [
        require('@tailwindcss/typography'),
    ],
} 