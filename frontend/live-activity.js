/**
 * Lock Screen Live Activity stub for classic UI
 */
window.updatePanchangLockScreen = async function updatePanchangLockScreen(params) {
  try {
    const p = params || {};
    console.log(
      `[LockScreen Activity] ${p.currentMuhurat || "—"} active until ${p.endTime || "—"} (${p.progressPercent ?? 0}%)`
    );
  } catch (err) {
    console.warn("Live Activities update failed:", err);
  }
};
