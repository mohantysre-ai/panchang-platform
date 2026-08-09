(() => {
  const $ = (s) => document.querySelector(s);
  const state = () => $("#state")?.value || "KA";
  const date = () => $("#date")?.value || new Date().toISOString().slice(0, 10);
  const lat = () => $("#lat")?.value || "12.9716";
  const lon = () => $("#lon")?.value || "77.5946";
  const labels = {
    hi: { chog: "चौघड़िया", gowri: "गौरी पंचांगम्", good: "शुभ", bad: "अशुभ", access: "अक्षर आकार", month: "क्षेत्रीय माह" },
    kn: { chog: "ಚೌಘಡಿಯಾ", gowri: "ಗೌರಿ ಪಂಚಾಂಗಂ", good: "ಶುಭ", bad: "ಅಶುಭ", access: "ಅಕ್ಷರ ಗಾತ್ರ", month: "ಪ್ರಾದೇಶಿಕ ತಿಂಗಳು" },
    ta: { chog: "சௌகடியா", gowri: "கௌரி பஞ்சாங்கம்", good: "நல்லது", bad: "தீயது", access: "எழுத்து அளவு", month: "பிராந்திய மாதம்" },
    te: { chog: "చౌఘడియా", gowri: "గౌరి పంచాంగం", good: "శుభం", bad: "అశుభం", access: "అక్షర పరిమాణం", month: "ప్రాంతీయ మాసం" },
    mr: { chog: "चौघडिया", gowri: "गौरी पंचांग", good: "शुभ", bad: "अशुभ", access: "अक्षर आकार", month: "प्रादेशिक महिना" },
    or: { chog: "ଚୌଘଡ଼ିଆ", gowri: "ଗୌରୀ ପଞ୍ଚାଙ୍ଗ", good: "ଶୁଭ", bad: "ଅଶୁଭ", access: "ଅକ୍ଷର ଆକାର", month: "ଆଞ୍ଚଳିକ ମାସ" },
    bn: { chog: "চৌঘড়িয়া", gowri: "গৌরী পঞ্জিকা", good: "শুভ", bad: "অশুভ", access: "অক্ষরের আকার", month: "আঞ্চলিক মাস" },
    as: { chog: "চৌঘড়িয়া", gowri: "গৌৰী পঞ্জিকা", good: "শুভ", bad: "অশুভ", access: "আখৰৰ আকাৰ", month: "আঞ্চলিক মাহ" },
    pa: { chog: "ਚੌਘੜੀਆ", gowri: "ਗੌਰੀ ਪੰਚਾਂਗ", good: "ਸ਼ੁਭ", bad: "ਅਸ਼ੁਭ", access: "ਅੱਖਰ ਆਕਾਰ", month: "ਖੇਤਰੀ ਮਹੀਨਾ" },
    gu: { chog: "ચોઘડિયા", gowri: "ગૌરી પંચાંગ", good: "શુભ", bad: "અશુભ", access: "અક્ષર કદ", month: "પ્રાદેશિક મહિનો" },
    ml: { chog: "ചൗഘഡിയ", gowri: "ഗൗരി പഞ്ചാംഗം", good: "ശുഭം", bad: "അശുഭം", access: "അക്ഷര വലുപ്പം", month: "പ്രാദേശിക മാസം" },
  };
  const lang = () => $("#lang")?.value || window.I18N?.stateLang?.[state()] || "en";
  const L = () => labels[lang()] || labels.hi;

  function regionalDigits(value) {
    const digits = window.I18N?.digits?.[lang()];
    if (!digits) return String(value);
    return String(value).replace(/[0-9]/g, (d) => digits[Number(d)]);
  }

  function applyScale() {
    const v = Number(localStorage.getItem("panchang-font-scale") || 1);
    document.documentElement.style.setProperty("--font-scale", v);
    document.body.classList.add("font-scaled");
    const o = $("#fontScale");
    if (o) o.value = `${regionalDigits(Math.round(v * 100))}%`;
  }
  function a11y() {
    if ($(".a11y-bar")) return;
    const d = document.createElement("div");
    d.className = "a11y-bar";
    d.setAttribute("role", "toolbar");
    d.setAttribute("aria-label", L().access);
    d.innerHTML =
      '<button type="button" id="fontDown" aria-label="Smaller">A−</button><output id="fontScale">100%</output><button type="button" id="fontUp" aria-label="Larger">A+</button><button type="button" id="fontReset" aria-label="Reset">↺</button>';
    document.body.appendChild(d);
    $("#fontDown").onclick = () => scale(-0.1);
    $("#fontUp").onclick = () => scale(0.1);
    $("#fontReset").onclick = () => {
      localStorage.setItem("panchang-font-scale", "1");
      applyScale();
    };
    applyScale();
  }
  function scale(delta) {
    let v = Number(localStorage.getItem("panchang-font-scale") || 1);
    v = Math.max(0.85, Math.min(1.3, Math.round((v + delta) * 10) / 10));
    localStorage.setItem("panchang-font-scale", v);
    applyScale();
  }
  async function states() {
    try {
      const d = await fetch("/api/v1/states").then((r) => r.json());
      window.__regionalStates = d.states || {};
      setAccent();
    } catch (_) {}
  }
  function setAccent() {
    const c = window.__regionalStates?.[state()];
    if (c?.accent) {
      let accent = c.accent;
      // Dark maroon accents disappear on dark glass — lift them for readability.
      if (!document.body.classList.contains("theme-light") && /^#([0-9a-f]{3}|[0-9a-f]{6})$/i.test(accent)) {
        accent = "#ffc978";
      }
      document.documentElement.style.setProperty("--state-accent", accent);
    }
    if (c?.style) document.body.dataset.stateStyle = c.style || "";
  }
  async function month() {
    const h = $("#calTitle");
    if (!h) return;
    try {
      const d = new Date(date());
      const q = new URLSearchParams({
        state_code: state(),
        year: String(d.getFullYear()),
        month: String(d.getMonth() + 1),
        timezone: "Asia/Kolkata",
      });
      const x = await fetch(`/api/v1/calendar/month?${q}`).then((r) => r.json());
      let m = h.querySelector(".regional-month");
      if (!m) {
        m = document.createElement("span");
        m.className = "regional-month";
        h.appendChild(m);
      }
      m.textContent = `${L().month}: ${x.regional_month_name || ""}`;
      document.documentElement.style.setProperty(
        "--state-accent",
        x.regional_accent ||
          getComputedStyle(document.documentElement).getPropertyValue("--state-accent")
      );
    } catch (_) {}
  }
  function refresh() {
    if (window.__regionalBusy) return;
    window.__regionalBusy = true;
    try {
      // Do not inject a second muhurat card — classic #hours / #r already render it.
      document.querySelector("#regionalMuhurat")?.remove();
      setAccent();
      month();
    } finally {
      setTimeout(() => {
        window.__regionalBusy = false;
      }, 200);
    }
  }
  document.addEventListener("DOMContentLoaded", () => {
    a11y();
    states();
    const s = $("#state");
    if (s) s.addEventListener("change", () => setTimeout(refresh, 250));
    const hours = $("#hours");
    if (hours) {
      let lastSig = "";
      const mo = new MutationObserver(() => {
        if (window.__regionalBusy || !hours.children.length) return;
        const sig = hours.innerHTML;
        if (sig === lastSig) return;
        lastSig = sig;
        clearTimeout(window.__regionalTimer);
        window.__regionalTimer = setTimeout(refresh, 120);
      });
      mo.observe(hours, { childList: true });
    }
    setTimeout(refresh, 900);
  });
})();
