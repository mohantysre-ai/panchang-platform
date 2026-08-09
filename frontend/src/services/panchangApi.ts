export interface PanchangResponse {
  date: string;
  state_code: string;
  location: {
    latitude: number;
    longitude: number;
    timezone: string;
  };
  panchang: {
    tithi: {
      index: number;
      name: string;
      paksha: string;
      progress_percent: number;
    };
    nakshatra: {
      index: number;
      name: string;
      pada: number;
    };
    yoga: { index: number; name: string };
    karana: { index: number; name: string };
    vaar: { index: number; name: string };
    sunrise: string;
    sunset: string;
  };
  auspicious_timings: {
    abhijit_muhurat: string;
  };
  inauspicious_timings: {
    rahu_kalam: string;
  };
  astronomy: {
    sun_sidereal_longitude: number;
    moon_sidereal_longitude: number;
  };
  regional: {
    system: string;
    muhurat_system: string;
    calendar_style: string;
    layout: string;
    accent?: string;
    choghadiya_day?: Array<{ slot: number; name: string; nature: string; time: string }>;
    gowri_panchangam?: Array<{ slot: number; name: string; nature: string; time: string }>;
  };
}

export interface StatesResponse {
  states: Record<
    string,
    {
      system: string;
      muhurat: string;
      style: string;
      accent: string;
      priority_fields: string[];
    }
  >;
  languages: string[];
}

const RASHI = [
  'Mesha (Aries)',
  'Vrishabha (Taurus)',
  'Mithuna (Gemini)',
  'Karka (Cancer)',
  'Simha (Leo)',
  'Kanya (Virgo)',
  'Tula (Libra)',
  'Vrischika (Scorpio)',
  'Dhanu (Sagittarius)',
  'Makara (Capricorn)',
  'Kumbha (Aquarius)',
  'Meena (Pisces)',
] as const;

export function rashiFromLongitude(lon: number): string {
  const normalized = ((lon % 360) + 360) % 360;
  return RASHI[Math.floor(normalized / 30) % 12];
}

/** 0 = Amavasya (new), 1 = Purnima (full) */
export function tithiPhaseFromIndex(index: number, progressPercent: number): number {
  const frac = (Math.max(1, index) - 1 + Math.min(100, Math.max(0, progressPercent)) / 100) / 30;
  return 1 - Math.abs(2 * frac - 1);
}

export function formatDisplayDate(iso: string): string {
  const d = new Date(`${iso}T12:00:00`);
  return d.toLocaleDateString('en-IN', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
  });
}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url);
  if (!res.ok) {
    throw new Error(`Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function fetchStates(): Promise<StatesResponse> {
  return getJson<StatesResponse>('/api/v1/states');
}

export async function fetchPanchang(params: {
  stateCode: string;
  dateStr?: string;
  lat?: number;
  lon?: number;
  timezone?: string;
}): Promise<PanchangResponse> {
  const qs = new URLSearchParams({
    state_code: params.stateCode,
    lat: String(params.lat ?? 12.9716),
    lon: String(params.lon ?? 77.5946),
    timezone: params.timezone ?? 'Asia/Kolkata',
  });
  if (params.dateStr) qs.set('date_str', params.dateStr);
  return getJson<PanchangResponse>(`/api/v1/panchang?${qs}`);
}
