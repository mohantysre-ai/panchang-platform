import React, { useState } from 'react';
import { CelestialHeader } from '../components/CelestialHeader';
import { REGIONAL_THEMES } from '../styles/themeConfig';

export const PanchangDashboard: React.FC = () => {
  const [selectedRegion, setSelectedRegion] = useState<string>('Odisha');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);

  const currentTheme = REGIONAL_THEMES[selectedRegion] || REGIONAL_THEMES['Odisha'];

  // Contrast Resolution Rules
  const backgroundColor = isDarkMode ? currentTheme.darkBg : currentTheme.lightBg;
  const textColor = isDarkMode ? currentTheme.darkText : currentTheme.lightText;
  const cardBackgroundColor = isDarkMode ? currentTheme.darkCardBg : currentTheme.lightCardBg;

  return (
    <div
      className="min-h-screen transition-colors duration-300 p-4 font-sans"
      style={{ backgroundColor, color: textColor }}
    >
      {/* Top Bar: Regional Switcher & Theme Mode Toggle */}
      <div className="flex justify-between items-center max-w-xl mx-auto mb-6">
        <select
          value={selectedRegion}
          onChange={(e) => setSelectedRegion(e.target.value)}
          className="p-2 rounded-lg font-semibold border shadow-sm"
          style={{
            backgroundColor: cardBackgroundColor,
            color: textColor,
            borderColor: currentTheme.accentGold,
          }}
        >
          <option value="Odisha">Odisha (Panji)</option>
          <option value="TamilNadu">Tamil Nadu (Thirukanidha)</option>
          <option value="Maharashtra">Maharashtra (Amanta)</option>
        </select>

        <button
          onClick={() => setIsDarkMode(!isDarkMode)}
          className="p-2 px-4 rounded-lg font-bold border"
          style={{ borderColor: currentTheme.accentGold }}
        >
          {isDarkMode ? '☀️ Light' : '🌙 Dark'}
        </button>
      </div>

      {/* Regional Card Frame */}
      <div className="max-w-xl mx-auto rounded-2xl p-6 shadow-xl border" style={{ backgroundColor: cardBackgroundColor, borderColor: currentTheme.accentGold }}>
        <div className="text-center mb-2">
          <span className="text-3xl">{currentTheme.headerGraphic}</span>
          <h1 className="text-2xl font-bold mt-1">{currentTheme.regionName}</h1>
          <p className="text-xs opacity-75">10 August 2026 | Sravana Sukla Dwadashi</p>
        </div>

        {/* Dynamic Celestial Header Component */}
        <CelestialHeader
          tithiPhase={0.78}
          moonSign="Vrishabha (Taurus)"
          sunSign="Karka (Cancer)"
          isDark={isDarkMode}
        />

        {/* Panchang Timings Table with Contrast Controls */}
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
            <p className="text-xs uppercase font-bold text-amber-500">Sunrise / Sunset</p>
            <p className="text-lg font-semibold">05:48 AM / 06:42 PM</p>
          </div>
          <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
            <p className="text-xs uppercase font-bold text-amber-500">Nakshatra</p>
            <p className="text-lg font-semibold">Rohini (until 04:12 PM)</p>
          </div>
          <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
            <p className="text-xs uppercase font-bold text-amber-500">Rahu Kalam</p>
            <p className="text-lg font-semibold text-rose-500">07:24 AM - 09:01 AM</p>
          </div>
          <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
            <p className="text-xs uppercase font-bold text-amber-500">Abhijit Muhurat</p>
            <p className="text-lg font-semibold text-emerald-500">11:52 AM - 12:44 PM</p>
          </div>
        </div>
      </div>
    </div>
  );
};
