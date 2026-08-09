export interface RegionTheme {
  regionName: string;
  lightBg: string;
  lightText: string;
  lightCardBg: string;
  darkBg: string;
  darkText: string;
  darkCardBg: string;
  accentGold: string;
  headerGraphic: string; // SVG or Canvas icon motif
}

export const REGIONAL_THEMES: Record<string, RegionTheme> = {
  Odisha: {
    regionName: "Odisha (Puri Panji)",
    lightBg: "#FFF8F0",        // Soft Warm Cream
    lightText: "#4A154B",      // Deep Maroone/Purple for strong contrast
    lightCardBg: "#FFFFFF",
    darkBg: "#120309",         // Deep Midnight Red/Black
    darkText: "#FDE68A",       // Light Warm Gold
    darkCardBg: "rgba(255, 255, 255, 0.06)",
    accentGold: "#D97706",
    headerGraphic: "🛕",
  },
  TamilNadu: {
    regionName: "Tamil Nadu (Thirukanidha)",
    lightBg: "#FFFDF0",
    lightText: "#78350F",      // Deep Terracotta Brown
    lightCardBg: "#FFFFFF",
    darkBg: "#0B1325",         // Deep Vedic Indigo
    darkText: "#F3F4F6",       // Crisp Off-White
    darkCardBg: "rgba(255, 255, 255, 0.07)",
    accentGold: "#EAB308",
    headerGraphic: "🪔",
  },
  Maharashtra: {
    regionName: "Maharashtra (Amanta Panchang)",
    lightBg: "#FEFCE8",        // Light Marigold Tint
    lightText: "#1E293B",      // Deep Slate
    lightCardBg: "#FFFFFF",
    darkBg: "#1C1917",         // Warm Charcoal
    darkText: "#FEF08A",
    darkCardBg: "rgba(255, 255, 255, 0.05)",
    accentGold: "#F59E0B",
    headerGraphic: "🌸",
  }
};
