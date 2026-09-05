/** Tailwind config for the Mizan site. Colors are CSS variables (see input.css) so the
 *  light/dark theme is one class swap on <html>, and every utility is written once. */
module.exports = {
  content: ["./site/**/*.html", "./site/assets/site.js"],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        bg: "rgb(var(--c-bg) / <alpha-value>)",
        surface: "rgb(var(--c-surface) / <alpha-value>)",
        line: "rgb(var(--c-line) / <alpha-value>)",
        fg: "rgb(var(--c-fg) / <alpha-value>)",
        muted: "rgb(var(--c-muted) / <alpha-value>)",
        primary: {
          DEFAULT: "rgb(var(--c-primary) / <alpha-value>)",   // links, icons (AA on bg)
          strong: "rgb(var(--c-primary-strong) / <alpha-value>)", // button fill (AA with white text)
          hover: "rgb(var(--c-primary-hover) / <alpha-value>)",
        },
        accent: "rgb(var(--c-accent) / <alpha-value>)",
      },
      fontFamily: {
        sans: [
          "system-ui", "-apple-system", "Segoe UI", "Roboto", "Helvetica Neue", "Arial",
          "Noto Sans", "Noto Sans Arabic", "Noto Naskh Arabic", "Segoe UI Arabic", "Tahoma",
          "sans-serif",
        ],
      },
    },
  },
  plugins: [],
};
