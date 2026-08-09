import React, { useEffect, useMemo, useState } from 'react';
import { CelestialHeader } from '../components/CelestialHeader';
import { updatePanchangLockScreen } from '../services/liveActivityService';
import {
  fetchPanchang,
  fetchStates,
  formatDisplayDate,
  rashiFromLongitude,
  tithiPhaseFromIndex,
  type PanchangResponse,
} from '../services/panchangApi';
import { STATE_LABELS, themeForState } from '../styles/themeConfig';
import { generateAndSharePanchangCard } from '../utils/shareCardGenerator';

const FEATURED_STATES = ['OD', 'TN', 'MH', 'KL', 'WB', 'GJ', 'KA'] as const;

function todayIso(): string {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

export const PanchangDashboard: React.FC = () => {
  const [selectedState, setSelectedState] = useState<string>('OD');
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);
  const [dateStr, setDateStr] = useState<string>(todayIso());
  const [stateCodes, setStateCodes] = useState<string[]>([...FEATURED_STATES]);
  const [data, setData] = useState<PanchangResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [sharing, setSharing] = useState<boolean>(false);

  const currentTheme = useMemo(() => themeForState(selectedState), [selectedState]);

  const backgroundColor = isDarkMode ? currentTheme.darkBg : currentTheme.lightBg;
  const textColor = isDarkMode ? currentTheme.darkText : currentTheme.lightText;
  const cardBackgroundColor = isDarkMode ? currentTheme.darkCardBg : currentTheme.lightCardBg;

  useEffect(() => {
    let cancelled = false;
    fetchStates()
      .then((res) => {
        if (cancelled) return;
        const codes = Object.keys(res.states).sort();
        setStateCodes([...new Set([...FEATURED_STATES, ...codes])]);
      })
      .catch(() => {
        /* keep featured fallback */
      });
    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchPanchang({ stateCode: selectedState, dateStr })
      .then((payload) => {
        if (cancelled) return;
        setData(payload);
      })
      .catch((err: unknown) => {
        if (cancelled) return;
        setError(err instanceof Error ? err.message : 'Failed to load panchang');
        setData(null);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [selectedState, dateStr]);

  useEffect(() => {
    if (!data) return;
    const slots = data.regional.gowri_panchangam ?? data.regional.choghadiya_day ?? [];
    const active = slots[0];
    if (!active) return;
    const endTime = active.time.split(' - ')[1] ?? active.time;
    void updatePanchangLockScreen({
      currentMuhurat: active.name,
      endTime,
      progressPercent: Math.round(data.panchang.tithi.progress_percent),
    });
  }, [data]);

  const tithiPhase = data
    ? tithiPhaseFromIndex(data.panchang.tithi.index, data.panchang.tithi.progress_percent)
    : 0.5;
  const moonSign = data ? rashiFromLongitude(data.astronomy.moon_sidereal_longitude) : '—';
  const sunSign = data ? rashiFromLongitude(data.astronomy.sun_sidereal_longitude) : '—';
  const regionTitle =
    STATE_LABELS[selectedState] ??
    (data ? `${data.state_code} · ${data.regional.system}` : currentTheme.regionName);
  const subtitle = data
    ? `${formatDisplayDate(data.date)} | ${data.panchang.tithi.name} · ${data.panchang.vaar.name}`
    : 'Loading regional panchang…';

  const muhuratSlots =
    data?.regional.gowri_panchangam ?? data?.regional.choghadiya_day ?? [];

  async function handleShare() {
    if (!data || sharing) return;
    setSharing(true);
    try {
      await generateAndSharePanchangCard({
        date: formatDisplayDate(data.date),
        tithi: data.panchang.tithi.name,
        nakshatra: data.panchang.nakshatra.name,
        sunrise: `${data.panchang.sunrise} / ${data.panchang.sunset}`,
        rahuKalam: data.inauspicious_timings.rahu_kalam,
        stateName: STATE_LABELS[selectedState] ?? selectedState,
      });
    } finally {
      setSharing(false);
    }
  }

  return (
    <div
      className="min-h-screen transition-colors duration-300 p-4 pb-10"
      style={{ backgroundColor, color: textColor }}
    >
      <div className="flex flex-wrap justify-between items-center gap-3 max-w-xl mx-auto mb-6">
        <select
          value={selectedState}
          onChange={(e) => setSelectedState(e.target.value)}
          className="p-2 rounded-lg font-semibold border shadow-sm min-w-[12rem]"
          style={{
            backgroundColor: cardBackgroundColor,
            color: textColor,
            borderColor: currentTheme.accentGold,
          }}
          aria-label="Select region"
        >
          {stateCodes.map((code) => (
            <option key={code} value={code}>
              {STATE_LABELS[code] ?? code}
            </option>
          ))}
        </select>

        <div className="flex items-center gap-2">
          <input
            type="date"
            value={dateStr}
            onChange={(e) => setDateStr(e.target.value)}
            className="p-2 rounded-lg border text-sm"
            style={{
              backgroundColor: cardBackgroundColor,
              color: textColor,
              borderColor: currentTheme.accentGold,
            }}
            aria-label="Select date"
          />
          <button
            type="button"
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="p-2 px-4 rounded-lg font-bold border"
            style={{ borderColor: currentTheme.accentGold }}
          >
            {isDarkMode ? '☀️ Light' : '🌙 Dark'}
          </button>
        </div>
      </div>

      <div
        className="max-w-xl mx-auto rounded-2xl p-6 shadow-xl border"
        style={{ backgroundColor: cardBackgroundColor, borderColor: currentTheme.accentGold }}
      >
        <div className="text-center mb-2">
          <span className="text-3xl" aria-hidden>
            {currentTheme.headerGraphic}
          </span>
          <h1 className="text-2xl font-bold mt-1 tracking-tight">{regionTitle}</h1>
          <p className="text-xs opacity-75 mt-1">{subtitle}</p>
          {data && (
            <p className="text-[0.7rem] opacity-60 mt-1">
              {data.regional.system} · {data.regional.muhurat_system} · {data.regional.calendar_style}
            </p>
          )}
        </div>

        {loading && (
          <p className="text-center text-sm opacity-70 py-8">Calculating celestial timings…</p>
        )}
        {error && <p className="text-center text-sm text-rose-400 py-4">{error}</p>}

        {!loading && !error && data && (
          <>
            <CelestialHeader
              tithiPhase={tithiPhase}
              moonSign={moonSign}
              sunSign={sunSign}
              isDark={isDarkMode}
            />

            <div className="grid grid-cols-2 gap-4 mt-6">
              <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
                <p className="text-xs uppercase font-bold" style={{ color: currentTheme.accentGold }}>
                  Sunrise / Sunset
                </p>
                <p className="text-lg font-semibold leading-snug">
                  {data.panchang.sunrise} / {data.panchang.sunset}
                </p>
              </div>
              <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
                <p className="text-xs uppercase font-bold" style={{ color: currentTheme.accentGold }}>
                  Nakshatra
                </p>
                <p className="text-lg font-semibold leading-snug">
                  {data.panchang.nakshatra.name} (Pada {data.panchang.nakshatra.pada})
                </p>
              </div>
              <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
                <p className="text-xs uppercase font-bold" style={{ color: currentTheme.accentGold }}>
                  Rahu Kalam
                </p>
                <p className="text-lg font-semibold text-rose-500 leading-snug">
                  {data.inauspicious_timings.rahu_kalam}
                </p>
              </div>
              <div className="p-3 rounded-lg border" style={{ borderColor: 'rgba(212,175,55,0.3)' }}>
                <p className="text-xs uppercase font-bold" style={{ color: currentTheme.accentGold }}>
                  Abhijit Muhurat
                </p>
                <p className="text-lg font-semibold text-emerald-500 leading-snug">
                  {data.auspicious_timings.abhijit_muhurat}
                </p>
              </div>
            </div>

            {muhuratSlots.length > 0 && (
              <div className="mt-6">
                <p
                  className="text-xs uppercase font-bold mb-2"
                  style={{ color: currentTheme.accentGold }}
                >
                  {data.regional.gowri_panchangam ? 'Gowri Panchangam' : 'Choghadiya'}
                </p>
                <div className="grid gap-2 max-h-56 overflow-auto pr-1">
                  {muhuratSlots.map((slot) => (
                    <div
                      key={`${slot.slot}-${slot.name}`}
                      className="flex justify-between gap-3 text-sm px-3 py-2 rounded-lg border"
                      style={{ borderColor: 'rgba(212,175,55,0.2)' }}
                    >
                      <span
                        className={
                          slot.nature === 'Good'
                            ? 'text-emerald-500 font-semibold'
                            : 'text-rose-400 font-semibold'
                        }
                      >
                        {slot.name}
                      </span>
                      <span className="opacity-75 text-right">{slot.time}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <button
              type="button"
              onClick={() => void handleShare()}
              disabled={sharing}
              className="mt-6 w-full p-3 rounded-xl font-bold border"
              style={{
                borderColor: currentTheme.accentGold,
                backgroundColor: isDarkMode ? 'rgba(212,175,55,0.12)' : 'rgba(212,175,55,0.15)',
              }}
            >
              {sharing ? 'Preparing card…' : 'Share Panchang Card'}
            </button>
          </>
        )}
      </div>

      <p className="text-center text-xs opacity-50 mt-6">
        <a href="/classic" className="underline underline-offset-2">
          Open classic calendar UI
        </a>
      </p>
    </div>
  );
};
