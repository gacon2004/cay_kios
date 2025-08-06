/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './app/**/*.{js,ts,jsx,tsx}', // Chỉ định các file để Tailwind quét
        './components/**/*.{js,ts,jsx,tsx}',
    ],
    theme: {
        extend: {
            animation: {
                'slide-in-from-top': 'slideInFromTop 0.3s ease-out',
                'slide-in-from-bottom': 'slideInFromBottom 0.3s ease-out',
                'slide-out-to-right': 'slideOutToRight 0.3s ease-in',
            },
            keyframes: {
                slideInFromTop: {
                    '0%': { transform: 'translateY(-100%)' },
                    '100%': { transform: 'translateY(0)' },
                },
                slideInFromBottom: {
                    '0%': { transform: 'translateY(100%)' },
                    '100%': { transform: 'translateY(0)' },
                },
                slideOutToRight: {
                    '0%': { transform: 'translateX(0)', opacity: 1 },
                    '100%': { transform: 'translateX(100%)', opacity: 0 },
                },
            },
        },
    },
    plugins: [],
};
