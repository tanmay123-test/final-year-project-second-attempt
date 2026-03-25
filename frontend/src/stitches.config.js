import { createStitches } from '@stitches/react';

export const {
  styled,
  css,
  globalCss,
  keyframes,
  theme,
  createTheme,
  config,
} = createStitches({
  theme: {
    colors: {
      primary: '#7c3aed',
      primaryDark: '#630ed4',
      secondary: '#005952',
      error: '#ba1a1a',
      warning: '#fd761a',
      background: '#f2f4f6',
      surface: '#ffffff',
      textPrimary: '#191c1e',
      textSecondary: '#64748b',
      textMuted: '#94a3b8',
      glassBg: 'rgba(255, 255, 255, 0.85)',
      blueGradient: 'linear-gradient(135deg, #2563eb, #1d4ed8)',
    },
    fonts: {
      sans: 'Inter, system-ui, sans-serif',
      heading: 'Space Grotesk, Inter, sans-serif',
    },
    space: {
      1: '4px',
      2: '8px',
      3: '12px',
      4: '16px',
      5: '20px',
      6: '24px',
      8: '32px',
      10: '40px',
    },
    radii: {
      sm: '4px',
      md: '8px',
      lg: '12px',
      xl: '16px',
      '2xl': '24px',
      full: '9999px',
    },
    shadows: {
      sm: '0 1px 3px rgba(0,0,0,0.08)',
      md: '0 4px 14px rgba(0,0,0,0.1)',
      lg: '0 10px 25px rgba(0,0,0,0.15)',
      violet: '0 4px 14px rgba(124, 58, 237, 0.35)',
    },
  },
  media: {
    sm: '(min-width: 640px)',
    md: '(min-width: 768px)',
    lg: '(min-width: 1024px)',
  },
  utils: {
    marginX: (value) => ({ marginLeft: value, marginRight: value }),
    marginY: (value) => ({ marginTop: value, marginBottom: value }),
    paddingX: (value) => ({ paddingLeft: value, paddingRight: value }),
    paddingY: (value) => ({ paddingTop: value, paddingBottom: value }),
  },
});
