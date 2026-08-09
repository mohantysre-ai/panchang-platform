/**
 * Classic extras: cache last panchang payload + live-activity sync
 */
(() => {
  window.addEventListener("panchang:loaded", (ev) => {
    const detail = ev.detail || {};
    const p = detail.p;
    if (!p) return;
    window.__lastPanchang = p;
    const slots = p.regional?.gowri_panchangam || p.regional?.choghadiya_day || [];
    const active = slots[0];
    if (active && window.updatePanchangLockScreen) {
      const endTime = String(active.time || "").split(" - ")[1] || active.time || "—";
      void window.updatePanchangLockScreen({
        currentMuhurat: active.name,
        endTime,
        progressPercent: Math.round(p.panchang?.tithi?.progress_percent || 0),
      });
    }
  });
})();
