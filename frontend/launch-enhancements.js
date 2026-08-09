(() => {
  const $ = (s) => document.querySelector(s);
  const state = () => $("#state")?.value || "KA";
  const date = () => $("#date")?.value || new Date().toISOString().slice(0, 10);
  const lat = () => $("#lat")?.value || "12.9716";
  const lon = () => $("#lon")?.value || "77.5946";

  function lang() {
    return window.I18N?.stateLang?.[state()] || $("#lang")?.value || "hi";
  }

  function localizeLunarName(englishName, index) {
    const L = lang();
    const list = window.I18N?.lunarMonths?.[L] || window.I18N?.lunarMonths?.hi || [];
    if (index != null && list[index - 1]) return list[index - 1];
    const en = window.I18N?.lunarMonthEn || [];
    const i = en.findIndex((n) => n.toLowerCase() === String(englishName || "").toLowerCase());
    if (i >= 0 && list[i]) return list[i];
    return englishName || "";
  }

  function formatLunarCaption(x) {
    const L = lang();
    const ui = window.I18N?.ui?.[L] || window.I18N?.ui?.hi || {};
    const systems = window.I18N?.systems?.[L] || window.I18N?.systems?.hi || {};
    const systemLabel = systems[x.system] || x.system || "";
    const name = localizeLunarName(x.name, x.index);
    if (x.system === "Solar") {
      return (ui.solar_month || "{name}").replace("{name}", name).replace("{system}", systemLabel);
    }
    return (ui.lunar_month || "{system} · {name}")
      .replace("{system}", systemLabel)
      .replace("{name}", name);
  }

  async function lunar() {
    const q = new URLSearchParams({
      state_code: state(),
      date_str: date(),
      timezone: "Asia/Kolkata",
      lat: lat(),
      lon: lon(),
    });
    try {
      const x = await fetch("/api/v1/lunar-month?" + q).then((r) => r.json());
      const h = $("#calTitle");
      if (!h) return;
      let el = h.querySelector(".astronomical-month");
      if (!el) {
        el = document.createElement("span");
        el.className = "regional-month astronomical-month";
        h.appendChild(el);
      }
      el.textContent = formatLunarCaption(x);
    } catch (_) {}
  }

  document.addEventListener("DOMContentLoaded", () => {
    setTimeout(lunar, 1100);
    ["state", "date"].forEach((id) =>
      $("#" + id)?.addEventListener("change", () => setTimeout(lunar, 300))
    );
    ["prevMonth", "nextMonth", "btnCalLoad", "btnToday"].forEach((id) =>
      $("#" + id)?.addEventListener("click", () => setTimeout(lunar, 450))
    );
  });
})();
