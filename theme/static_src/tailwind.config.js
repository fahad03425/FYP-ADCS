// Import the default Tailwind color palette
const colors = require('tailwindcss/colors');

module.exports = {
    content: [
        '../templates/**/*.html',
        '../../templates/**/*.html',
        './static/**/*.js',
        '../../**/templates/**/*.html',
    ],
    theme: {
        extend: {
            colors: {
                ...colors, // Spread all default Tailwind colors as custom colors
                'bluish': '#4266b0',
                'redish': '#fe0000',
            },
            spacing: {
                'custom-margin': '297px',
                '120': "120%",
            },
            screens: {
                '3xl': '1501px',
            },
        },
    },
    plugins: [
        require('@tailwindcss/forms'),
        require('@tailwindcss/typography'),
        require('@tailwindcss/aspect-ratio'),
    ],
};

