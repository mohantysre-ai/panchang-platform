export interface RegionTheme {
  regionName: string;
  lightBg: string;
  lightText: string;
  lightCardBg: string;
  darkBg: string;
  darkText: string;
  darkCardBg: string;
  accentGold: string;
  headerGraphic: string;
}

export const REGIONAL_THEMES: Record<string, RegionTheme> = {
  Odisha: {
    regionName: 'Odisha (Puri Panji)',
    lightBg: '#FFF8F0',
    lightText: '#4A154B',
    lightCardBg: '#FFFFFF',
    darkBg: '#120309',
    darkText: '#FDE68A',
    darkCardBg: 'rgba(255, 255, 255, 0.06)',
    accentGold: '#D97706',
    headerGraphic: '🛕',
  },
  TamilNadu: {
    regionName: 'Tamil Nadu (Thirukanidha)',
    lightBg: '#FFFDF0',
    lightText: '#78350F',
    lightCardBg: '#FFFFFF',
    darkBg: '#0B1325',
    darkText: '#F3F4F6',
    darkCardBg: 'rgba(255, 255, 255, 0.07)',
    accentGold: '#EAB308',
    headerGraphic: '🪔',
  },
  Maharashtra: {
    regionName: 'Maharashtra (Amanta Panchang)',
    lightBg: '#FEFCE8',
    lightText: '#1E293B',
    lightCardBg: '#FFFFFF',
    darkBg: '#1C1917',
    darkText: '#FEF08A',
    darkCardBg: 'rgba(255, 255, 255, 0.05)',
    accentGold: '#F59E0B',
    headerGraphic: '🌸',
  },
  Bengal: {
    regionName: 'West Bengal (Bengali Panjika)',
    lightBg: '#FFF5F7',
    lightText: '#4A0E1C',
    lightCardBg: '#FFFFFF',
    darkBg: '#14060B',
    darkText: '#FECACA',
    darkCardBg: 'rgba(255, 255, 255, 0.06)',
    accentGold: '#BE123C',
    headerGraphic: '🪷',
  },
  Kerala: {
    regionName: 'Kerala (Malayalam Panchanam)',
    lightBg: '#F0FDF6',
    lightText: '#14532D',
    lightCardBg: '#FFFFFF',
    darkBg: '#04150D',
    darkText: '#BBF7D0',
    darkCardBg: 'rgba(255, 255, 255, 0.06)',
    accentGold: '#CA8A04',
    headerGraphic: '🪔',
  },
  Default: {
    regionName: 'Regional Panchang',
    lightBg: '#FFFDF8',
    lightText: '#1C1917',
    lightCardBg: '#FFFFFF',
    darkBg: '#0C0A09',
    darkText: '#FAFAF9',
    darkCardBg: 'rgba(255, 255, 255, 0.06)',
    accentGold: '#D4AF37',
    headerGraphic: '🕉',
  },
};

/** Map API state codes → cultural theme keys */
export const STATE_THEME_KEY: Record<string, keyof typeof REGIONAL_THEMES> = {
  OD: 'Odisha',
  WB: 'Bengal',
  TN: 'TamilNadu',
  PY: 'TamilNadu',
  KL: 'Kerala',
  LD: 'Kerala',
  MH: 'Maharashtra',
  GJ: 'Maharashtra',
  GA: 'Maharashtra',
  DN: 'Maharashtra',
};

export const STATE_LABELS: Record<string, string> = {
  OD: 'Odisha (Panji)',
  WB: 'West Bengal (Panjika)',
  TN: 'Tamil Nadu (Thirukanidha)',
  KL: 'Kerala (Panchanam)',
  MH: 'Maharashtra (Amanta)',
  GJ: 'Gujarat (Amanta)',
  KA: 'Karnataka',
  AP: 'Andhra Pradesh',
  TS: 'Telangana',
  UP: 'Uttar Pradesh',
  RJ: 'Rajasthan',
  PB: 'Punjab',
  DL: 'Delhi',
  AS: 'Assam',
  BR: 'Bihar',
  MP: 'Madhya Pradesh',
  GA: 'Goa',
  PY: 'Puducherry',
};

export function themeForState(stateCode: string): RegionTheme {
  const key = STATE_THEME_KEY[stateCode.toUpperCase()] ?? 'Default';
  return REGIONAL_THEMES[key] ?? REGIONAL_THEMES.Default;
}
