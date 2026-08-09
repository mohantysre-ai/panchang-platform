(() => {
  const names = {
    AP: "ఆంధ్ర ప్రదేశ్",
    AR: "अरुणाचल प्रदेश",
    AS: "অসম",
    BR: "बिहार",
    CG: "छत्तीसगढ़",
    GA: "गोवा",
    GJ: "ગુજરાત",
    HR: "हरियाणा",
    HP: "हिमाचल प्रदेश",
    JH: "झारखंड",
    KA: "ಕರ್ನಾಟಕ",
    KL: "കേരള",
    MP: "मध्य प्रदेश",
    MH: "महाराष्ट्र",
    MN: "मणिपुर",
    ML: "मेघालय",
    MZ: "मिजोरम",
    NL: "नागालैंड",
    OD: "ଓଡ଼ିଶା",
    PB: "ਪੰਜਾਬ",
    RJ: "राजस्थान",
    SK: "सिक्किम",
    TN: "தமிழ்நாடு",
    TS: "తెలంగాణ",
    TR: "ত্রিপুরা",
    UP: "उत्तर प्रदेश",
    UK: "उत्तराखंड",
    WB: "পশ্চিমবঙ্গ",
    DL: "दिल्ली",
    JK: "जम्मू और कश्मीर",
    LA: "लद्दाख",
    PY: "புதுச்சேரி",
    CH: "चंडीगढ़",
    DN: "દાદરા અને નગર હવેલી અને દમણ અને દીવ",
    LD: "ലക്ഷദ്വീപ്",
    AN: "अंडमान और निकोबार",
  };
  // Native script labels for the state picker (one language per state).
  window.NATIVE_STATE_NAMES = names;

  const fallbackLang = {
    PY: "ta",
    LD: "ml",
    DN: "gu",
    CH: "hi",
    AN: "hi",
    LA: "hi",
    SK: "hi",
    TR: "bn",
    MN: "hi",
    ML: "hi",
    MZ: "hi",
    NL: "hi",
    AR: "hi",
  };
  const I = window.I18N || {};
  I.stateLang = I.stateLang || {};
  I.states = I.states || {};
  Object.keys(names).forEach((c) => {
    if (!I.stateLang[c]) I.stateLang[c] = fallbackLang[c] || I.stateLang[c];
    const homeLang = I.stateLang[c];
    if (homeLang) {
      I.states[homeLang] = I.states[homeLang] || {};
      // Prefer authentic regional spelling for the state's own language bucket
      I.states[homeLang][c] = names[c];
    }
  });
  window.I18N = I;
})();
