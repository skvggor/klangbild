// Site color tokens for consistent theming
// Use these instead of inline hex codes

export const colors = {
  // Primary brand colors
  primary: {
    DEFAULT: "#7C3AED",
    light: "#8B5CF6",
    dark: "#6D28D9",
  },

  // Secondary accent
  secondary: {
    DEFAULT: "#06B6D4",
    light: "#22D3EE",
    dark: "#0891B2",
  },

  // Background colors
  background: {
    DEFAULT: "#0a0a0f",
    light: "#0f0f1a",
    lighter: "#1a1a2e",
  },

  // Text colors
  text: {
    primary: "#ffffff",
    secondary: "#9CA3AF", // gray-400
    muted: "#6B7280", // gray-500
  },

  // Semantic colors
  success: "#4ade80",
  warning: "#fbbf24",
  error: "#f87171",
  info: "#22d3ee",
};

// Tailwind classes mapping for common use cases
export const theme = {
  // Background gradients
  gradients: {
    hero: "bg-gradient-to-b from-[#0f0f1a] via-[#0a0a0f] to-[#0a0a0f]",
    primary: "bg-gradient-to-r from-[#7C3AED] via-[#06B6D4] to-[#7C3AED]",
    card: "bg-gradient-to-br from-[#0f0f1a] to-[#1a1a2e]",
  },

  // Border colors
  borders: {
    subtle: "border-[#7C3AED]/10",
    hover: "border-[#7C3AED]/30",
    DEFAULT: "border-[#7C3AED]/20",
  },

  // Shadow colors
  shadows: {
    primary: "shadow-[#7C3AED]/10",
    hover: "shadow-[#7C3AED]/40",
    DEFAULT: "shadow-[#7C3AED]/20",
  },

  // Text colors
  text: {
    primary: "text-[#7C3AED]",
    secondary: "text-[#06B6D4]",
    success: "text-[#4ade80]",
  },

  // Background colors with opacity
  bg: {
    card: "bg-[#0f0f1a]/80",
    hover: "bg-[#0f0f1a]/50",
    icon: "bg-[#7C3AED]/10",
  },
};
