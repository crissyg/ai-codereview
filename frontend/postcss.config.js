module.exports = {
  plugins: {
    // Tailwind CSS - utility-first CSS framework
    tailwindcss: {},
    
    // Autoprefixer - automatically adds vendor prefixes for browser compatibility
    // Ensures CSS works across different browsers (Chrome, Firefox, Safari, etc.)
    autoprefixer: {},
    
    // CSS Nano - minifies CSS for production builds (only in production)
    ...(process.env.NODE_ENV === 'production' ? { cssnano: {} } : {})
  },
}