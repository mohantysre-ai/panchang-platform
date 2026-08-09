(() => {
  const SHELL_FONT =
    'NotoSansDevanagari, NotoSansKannada, NotoSansTamil, NotoSansTelugu, NotoSansMalayalam, NotoSansOriya, NotoSansBengali, NotoSansGujarati, NotoSansGurmukhi, "Segoe UI", system-ui, sans-serif';

  const esc = (s) =>
    String(s ?? "").replace(/[&<>"']/g, (c) =>
      ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c])
    );

  function currentLang() {
    const code = document.getElementById("state")?.value;
    return (
      window.I18N?.stateLang?.[code] ||
      document.getElementById("lang")?.value ||
      "hi"
    );
  }

  function t(key) {
    const L = currentLang();
    const ui = window.I18N?.ui || {};
    return (ui[L] && ui[L][key]) || (ui.mr && ui.mr[key]) || (ui.hi && ui.hi[key]) || key;
  }

  function go(id) {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth", block: "start" });
    close();
  }
  function close() {
    document.querySelector(".shell-menu")?.classList.remove("open");
    document.body.style.overflow = "";
  }
  function open() {
    localizeShell();
    document.querySelector(".shell-menu")?.classList.add("open");
    document.body.style.overflow = "hidden";
  }

  function isDark() {
    return !document.body.classList.contains("theme-light");
  }

  function applyTheme(dark) {
    document.body.classList.toggle("theme-light", !dark);
    localStorage.setItem("panchang-theme", dark ? "dark" : "light");
    document.querySelector('meta[name="theme-color"]')?.setAttribute("content", dark ? "#1a4a8a" : "#FFFDF5");
    if (typeof window.applyInk === "function") {
      window.applyInk(window.skyTone || "day");
    } else if (!dark) {
      document.documentElement.style.setProperty("--text", "#1A1208");
      document.documentElement.style.setProperty("--panel-bg", "rgba(255,253,248,.96)");
      document.documentElement.style.setProperty("--state-accent", "#9c3d24");
    } else {
      document.documentElement.style.setProperty("--text", "#ffffff");
      document.documentElement.style.setProperty("--panel-bg", "rgba(8,22,48,.82)");
      document.documentElement.style.setProperty("--state-accent", "#ffc978");
    }
    localizeShell();
  }

  async function shareCard() {
    close();
    const p = window.__lastPanchang;
    if (!p || !window.generateAndSharePanchangCard) {
      alert(t("loading_panchang"));
      return;
    }
    const stateEl = document.getElementById("state");
    const L = currentLang();
    const stateName =
      window.NATIVE_STATE_NAMES?.[stateEl?.value] ||
      (window.I18N?.states?.[L] || {})[stateEl?.value] ||
      stateEl?.value ||
      "";
    await window.generateAndSharePanchangCard({
      date: document.getElementById("heroDate")?.textContent || p.date,
      tithi: document.getElementById("heroMain")?.textContent || p.panchang?.tithi?.name || "—",
      nakshatra: p.panchang?.nakshatra?.name || "—",
      sunrise: `${p.panchang?.sunrise || "—"} / ${p.panchang?.sunset || "—"}`,
      rahuKalam: p.inauspicious_timings?.rahu_kalam || "—",
      stateName,
    });
  }

  function navItems() {
    return [
      ["📅", t("nav_panchang"), "calendarPanel"],
      ["🪔", t("nav_today"), "hero"],
      ["🕉", t("nav_rashifal"), "h"],
      ["🎉", t("nav_festivals"), "r"],
    ];
  }

  function toolItems() {
    return [
      ["state", "📍", t("change_region")],
      ["date", "📆", t("pick_date")],
      ["theme", "☀️", t(isDark() ? "light_mode" : "dark_mode")],
      ["share", "↗", t("share_card")],
      ["live", "🔒", t("lock_activity")],
      ["a11y", "Aa", t("text_size")],
      ["react", "✦", t("celestial_dash")],
      ["install", "⬇", t("install_app")],
    ];
  }

  function localizeShell() {
    const root = document.querySelector("[data-shell-root]");
    if (!root) return;

    const brand = t("brand");
    const tag = t("brand_tag");
    root.querySelectorAll(".shell-brand strong, #shellSplash strong").forEach((el) => {
      el.textContent = brand;
    });
    root.querySelectorAll(".shell-brand span, #shellSplash span").forEach((el) => {
      if (el.classList.contains("icon") || el.classList.contains("bi")) return;
      el.textContent = tag;
    });

    const sections = root.querySelectorAll(".shell-section");
    if (sections[0]) sections[0].textContent = t("explore");
    if (sections[1]) sections[1].textContent = t("tools");

    const nav = navItems();
    root.querySelectorAll(".shell-nav [data-target], .shell-bottom [data-target]").forEach((btn) => {
      const item = nav.find((x) => x[2] === btn.dataset.target);
      if (!item) return;
      const isBottom = btn.closest(".shell-bottom");
      btn.innerHTML = isBottom
        ? `<span class="bi">${item[0]}</span>${esc(item[1])}`
        : `<span class="icon">${item[0]}</span>${esc(item[1])}`;
    });

    toolItems().forEach(([action, icon, label]) => {
      const btn = root.querySelector(`[data-action="${action}"]`);
      if (!btn) return;
      btn.innerHTML = `<span class="icon">${icon}</span>${esc(label)}`;
    });

    root.querySelectorAll(".shell-drawer, .shell-bottom, .shell-brand, .shell-nav button").forEach((el) => {
      el.style.setProperty("font-family", SHELL_FONT, "important");
    });
  }

  function wire(root) {
    root.querySelector("#shellMenuBtn").onclick = open;
    root.querySelector(".shell-scrim").onclick = close;
    root.querySelector(".shell-close").onclick = close;
    root.querySelectorAll("[data-target]").forEach((b) => {
      b.onclick = () => go(b.dataset.target);
    });
    root.querySelector('[data-action="state"]').onclick = () => {
      close();
      document.getElementById("state")?.focus();
    };
    root.querySelector('[data-action="date"]').onclick = () => {
      close();
      const el = document.getElementById("date");
      el?.focus();
      el?.showPicker?.();
    };
    root.querySelector('[data-action="theme"]').onclick = () => applyTheme(!isDark());
    root.querySelector('[data-action="share"]').onclick = () => void shareCard();
    root.querySelector('[data-action="live"]').onclick = () => {
      close();
      const p = window.__lastPanchang;
      const slots = p?.regional?.gowri_panchangam || p?.regional?.choghadiya_day || [];
      const active = slots[0];
      window.updatePanchangLockScreen?.({
        currentMuhurat: active?.name || "Muhurat",
        endTime: (active?.time || "").split(" - ")[1] || "—",
        progressPercent: Math.round(p?.panchang?.tithi?.progress_percent || 0),
      });
    };
    root.querySelector('[data-action="a11y"]').onclick = () => {
      close();
      document.getElementById("fontUp")?.focus();
    };
    root.querySelector('[data-action="react"]').onclick = () => {
      window.location.href = "/app";
    };
    root.querySelector('[data-action="install"]').onclick = async () => {
      if (window.__pwaInstall) {
        window.__pwaInstall.prompt();
        await window.__pwaInstall.userChoice;
        window.__pwaInstall = null;
      }
      close();
    };
  }

  function add() {
    if (document.querySelector("[data-shell-root]")) {
      localizeShell();
      return;
    }
    const d = document.createElement("div");
    d.setAttribute("data-shell-root", "1");
    d.innerHTML = `<div class="shell-splash" id="shellSplash"><div><div class="mark">ॐ</div><strong></strong><span></span></div></div>
<div class="shell-topbar"><button class="shell-fab" id="shellMenuBtn" type="button" aria-label="menu">☰</button></div>
<div class="shell-menu" aria-hidden="true">
  <div class="shell-scrim"></div>
  <aside class="shell-drawer">
    <button class="shell-close" type="button" aria-label="close">×</button>
    <div class="shell-brand"><div class="shell-logo">ॐ</div><div><strong></strong><span></span></div></div>
    <div class="shell-section"></div>
    <nav class="shell-nav">
      <button type="button" data-target="calendarPanel" class="active"></button>
      <button type="button" data-target="hero"></button>
      <button type="button" data-target="h"></button>
      <button type="button" data-target="r"></button>
    </nav>
    <div class="shell-section"></div>
    <nav class="shell-nav">
      <button type="button" data-action="state"></button>
      <button type="button" data-action="date"></button>
      <button type="button" data-action="theme"></button>
      <button type="button" data-action="share"></button>
      <button type="button" data-action="live"></button>
      <button type="button" data-action="a11y"></button>
      <button type="button" data-action="react"></button>
      <button type="button" data-action="install"></button>
    </nav>
  </aside>
</div>
<nav class="shell-bottom">
  <button type="button" data-target="calendarPanel" class="active"></button>
  <button type="button" data-target="hero"></button>
  <button type="button" data-target="h"></button>
  <button type="button" data-target="r"></button>
</nav>`;

    document.body.appendChild(d);
    wire(d);
    localizeShell();

    window.addEventListener("beforeinstallprompt", (e) => {
      e.preventDefault();
      window.__pwaInstall = e;
    });

    // Kill stale English shell / Kannada-only state list from old SW caches
    if ("serviceWorker" in navigator) {
      caches.keys().then((keys) => Promise.all(keys.map((k) => caches.delete(k)))).catch(() => {});
      navigator.serviceWorker.getRegistrations?.().then((regs) => {
        regs.forEach((r) => r.update());
      });
      navigator.serviceWorker.register("/sw.js?v=7").catch(() => {});
    }

    const saved = localStorage.getItem("panchang-theme");
    applyTheme(saved !== "light");

    document.getElementById("state")?.addEventListener("change", () => {
      setTimeout(localizeShell, 30);
    });
    window.addEventListener("panchang:loaded", localizeShell);
    // Late pass after i18n + state options settle
    setTimeout(localizeShell, 200);
    setTimeout(localizeShell, 800);

    setTimeout(() => document.getElementById("shellSplash")?.classList.add("hide"), 900);
    setTimeout(() => document.getElementById("shellSplash")?.remove(), 1400);
  }

  document.addEventListener("DOMContentLoaded", add);
  window.__localizeShell = localizeShell;
})();
