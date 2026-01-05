import type { Config } from 'tailwindcss';
import colors from 'tailwindcss/colors';

const config: Config = {
  content: [
    './pages/**/*.{js,ts,jsx,tsx,mdx}',
    './components/**/*.{js,ts,jsx,tsx,mdx}',
    './app/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class', // Enable dark mode with class strategy
  theme: {
    extend: {
      // HSL-tailored palettes: Deep Indigo & Neon Teal
      colors: {
        primary: {
          50: 'hsl(220, 100%, 97%)', // Lightest indigo
          100: 'hsl(220, 90%, 94%)',
          200: 'hsl(220, 80%, 88%)',
          300: 'hsl(220, 70%, 78%)',
          400: 'hsl(220, 60%, 65%)',
          500: 'hsl(220, 50%, 50%)', // Base Deep Indigo
          600: 'hsl(220, 60%, 40%)',
          700: 'hsl(220, 70%, 30%)',
          800: 'hsl(220, 80%, 20%)',
          900: 'hsl(220, 90%, 10%)', // Darkest indigo
          950: 'hsl(220, 95%, 5%)',
        },
        accent: {
          50: 'hsl(170, 100%, 97%)', // Lightest teal
          100: 'hsl(170, 90%, 94%)',
          200: 'hsl(170, 80%, 88%)',
          300: 'hsl(170, 70%, 78%)',
          400: 'hsl(170, 60%, 65%)',
          500: 'hsl(170, 50%, 50%)', // Base Neon Teal
          600: 'hsl(170, 60%, 40%)',
          700: 'hsl(170, 70%, 30%)',
          800: 'hsl(170, 80%, 20%)',
          900: 'hsl(170, 90%, 10%)', // Darkest teal
          950: 'hsl(170, 95%, 5%)',
        },
        gray: {
          ...colors.gray, // Use default Tailwind gray for neutrals
          50: 'hsl(220, 20%, 97%)',
          100: 'hsl(220, 15%, 90%)',
          200: 'hsl(220, 10%, 80%)',
          300: 'hsl(220, 8%, 70%)',
          400: 'hsl(220, 6%, 60%)',
          500: 'hsl(220, 5%, 50%)',
          600: 'hsl(220, 7%, 40%)',
          700: 'hsl(220, 9%, 30%)',
          800: 'hsl(220, 12%, 20%)',
          900: 'hsl(220, 15%, 10%)',
          950: 'hsl(220, 18%, 5%)',
        },
        // Semantic colors for alerts, etc.
        success: colors.emerald,
        warning: colors.amber,
        danger: colors.red,
        info: colors.sky,
      },
      // Spacing Scale (8px base) - Tailwind's default already follows this.
      // Custom font sizes using clamp for fluid typography
      fontSize: {
        'fluid-xs': 'clamp(0.75rem, 1vw + 0.5rem, 0.875rem)', // 12px -> 14px
        'fluid-sm': 'clamp(0.875rem, 1.5vw + 0.5rem, 1rem)',  // 14px -> 16px
        'fluid-base': 'clamp(1rem, 2vw + 0.5rem, 1.125rem)',  // 16px -> 18px
        'fluid-lg': 'clamp(1.125rem, 2.5vw + 0.5rem, 1.25rem)',// 18px -> 20px
        'fluid-xl': 'clamp(1.25rem, 3vw + 1rem, 1.5rem)',    // 20px -> 24px
        'fluid-2xl': 'clamp(1.5rem, 4vw + 1rem, 1.875rem)',  // 24px -> 30px
        'fluid-3xl': 'clamp(1.875rem, 5vw + 1.25rem, 2.25rem)',// 30px -> 36px
        'fluid-4xl': 'clamp(2.25rem, 6vw + 1.5rem, 3rem)',    // 36px -> 48px
        'fluid-5xl': 'clamp(2.5rem, 8vw + 2rem, 4rem)',     // 40px -> 64px
      },
      // Shadows for elevation
      boxShadow: {
        'sm': '0 1px 2px 0 var(--tw-shadow-color)',
        'md': '0 4px 6px -1px var(--tw-shadow-color), 0 2px 4px -2px var(--tw-shadow-color)',
        'lg': '0 10px 15px -3px var(--tw-shadow-color), 0 4px 6px -4px var(--tw-shadow-color)',
        'xl': '0 20px 25px -5px var(--tw-shadow-color), 0 8px 10px -6px var(--tw-shadow-color)',
        '2xl': '0 25px 50px -12px var(--tw-shadow-color)',
        'inner': 'inset 0 2px 4px 0 var(--tw-shadow-color)',
      },
      transitionTimingFunction: {
        'ease-out-cubic': 'cubic-bezier(0.25, 0.46, 0.45, 0.94)',
      },
      transitionDuration: {
        '250': '250ms', // Custom duration for smoother transitions
      },
    },
  },
  plugins: [],
};
export default config;
