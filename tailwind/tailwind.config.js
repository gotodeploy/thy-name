/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [],
    theme: {
        extend: {
            fontFamily: {
                taiwan: ['Noto Serif CJK TC', 'sans-serif'],
                nihon: ['Noto Serif CJK JP', 'sans-serif'],
            },
        },
    },
    safelist: [
        "bg-gray-100",
        "bg-green-500",
        "bg-red-500",
        "bg-white",
        "border",
        "border-b",
        "border-gray-200",
        "font-bold",
        "font-taiwan",
        "font-nihon",
        "mb-6",
        "min-w-full",
        "mx-auto",
        "p-6",
        "px-2",
        "px-4",
        "px-4",
        "py-1",
        "py-2",
        "rounded",
        "text-3xl",
        "text-white",
    ],
    plugins: [],
}

