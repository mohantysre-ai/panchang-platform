/**
 * WhatsApp / social share card for classic UI
 */
window.generateAndSharePanchangCard = async function generateAndSharePanchangCard(data) {
  const canvas = document.createElement("canvas");
  canvas.width = 1080;
  canvas.height = 1350;
  const ctx = canvas.getContext("2d");
  if (!ctx) return;

  const gradient = ctx.createLinearGradient(0, 0, 0, 1350);
  gradient.addColorStop(0, "#1A0B2E");
  gradient.addColorStop(0.5, "#2D124D");
  gradient.addColorStop(1, "#0F051D");
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 1080, 1350);

  ctx.strokeStyle = "#D4AF37";
  ctx.lineWidth = 12;
  ctx.strokeRect(40, 40, 1000, 1270);
  ctx.lineWidth = 2;
  ctx.strokeRect(55, 55, 970, 1240);

  ctx.textAlign = "center";
  ctx.fillStyle = "#FFD700";
  ctx.font = "bold 52px sans-serif";
  ctx.fillText("DAINIK PANCHANG", 540, 140);

  ctx.fillStyle = "#E0E0E0";
  ctx.font = "32px sans-serif";
  ctx.fillText(`Region: ${data.stateName} | ${data.date}`, 540, 200);

  ctx.beginPath();
  ctx.moveTo(200, 240);
  ctx.lineTo(880, 240);
  ctx.strokeStyle = "#D4AF37";
  ctx.stroke();

  ctx.fillStyle = "rgba(255, 255, 255, 0.07)";
  if (ctx.roundRect) {
    ctx.beginPath();
    ctx.roundRect(100, 280, 880, 780, 24);
    ctx.fill();
  } else {
    ctx.fillRect(100, 280, 880, 780);
  }

  ctx.textAlign = "left";
  let yPos = 370;
  const items = [
    { label: "Sunrise / Sunset", value: data.sunrise },
    { label: "Tithi", value: data.tithi },
    { label: "Nakshatra", value: data.nakshatra },
    { label: "Rahu Kalam", value: data.rahuKalam },
  ];
  if (data.festivalToday) {
    items.unshift({ label: "Festival", value: data.festivalToday });
  }
  items.forEach((item) => {
    ctx.fillStyle = "#FFC107";
    ctx.font = "bold 36px sans-serif";
    ctx.fillText(item.label, 150, yPos);
    ctx.fillStyle = "#FFFFFF";
    ctx.font = "36px sans-serif";
    ctx.fillText(String(item.value || "—"), 150, yPos + 48);
    yPos += 120;
  });

  ctx.textAlign = "center";
  ctx.fillStyle = "#FFD700";
  ctx.font = "bold 38px sans-serif";
  ctx.fillText("Regional Panchang App", 540, 1150);
  ctx.fillStyle = "#B0BEC5";
  ctx.font = "28px sans-serif";
  ctx.fillText("Daily Muhurat, Rashifal & Regional Panji", 540, 1200);

  await new Promise((resolve) => {
    canvas.toBlob(async (blob) => {
      if (!blob) {
        resolve();
        return;
      }
      const file = new File([blob], `Panchang_${String(data.date).replace(/\s+/g, "_")}.png`, {
        type: "image/png",
      });
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        try {
          await navigator.share({
            title: `Daily Panchang - ${data.date}`,
            text: `Today's Panchang for ${data.stateName}: ${data.tithi}`,
            files: [file],
          });
        } catch (_) {
          /* canceled */
        }
      } else {
        const link = document.createElement("a");
        link.download = file.name;
        link.href = canvas.toDataURL("image/png");
        link.click();
      }
      resolve();
    }, "image/png");
  });
};
