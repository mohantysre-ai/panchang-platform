/**
 * WhatsApp & Social Media Branded Card Generator
 * File: frontend/src/utils/shareCardGenerator.ts
 */

export interface PanchangShareData {
  date: string;            // e.g., "10 August 2026"
  tithi: string;           // e.g., "Shukla Dwadashi"
  nakshatra: string;       // e.g., "Rohini"
  sunrise: string;         // e.g., "06:12 AM"
  rahuKalam: string;       // e.g., "04:30 PM - 06:00 PM"
  stateName: string;       // e.g., "Karnataka" or "Odisha"
  festivalToday?: string;  // e.g., "Maha Shivaratri"
}

export async function generateAndSharePanchangCard(data: PanchangShareData): Promise<void> {
  const canvas = document.createElement('canvas');
  canvas.width = 1080;
  canvas.height = 1350; // Optimized for WhatsApp Status and Instagram stories
  const ctx = canvas.getContext('2d');

  if (!ctx) return;

  // 1. Background Gradient (Saffron / Gold Vedic Accent)
  const gradient = ctx.createLinearGradient(0, 0, 0, 1350);
  gradient.addColorStop(0, '#1A0B2E');  // Deep Midnight Purple
  gradient.addColorStop(0.5, '#2D124D');
  gradient.addColorStop(1, '#0F051D');
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, 1080, 1350);

  // 2. Decorative Gold Border
  ctx.strokeStyle = '#D4AF37';
  ctx.lineWidth = 12;
  ctx.strokeRect(40, 40, 1000, 1270);
  ctx.lineWidth = 2;
  ctx.strokeRect(55, 55, 970, 1240);

  // 3. Header Title & State
  ctx.textAlign = 'center';
  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 52px sans-serif';
  ctx.fillText('🕉️ DAINIK PANCHANG', 540, 140);

  ctx.fillStyle = '#E0E0E0';
  ctx.font = '32px sans-serif';
  ctx.fillText(`Region: ${data.stateName} | ${data.date}`, 540, 200);

  // Gold Divider
  ctx.beginPath();
  ctx.moveTo(200, 240);
  ctx.lineTo(880, 240);
  ctx.strokeStyle = '#D4AF37';
  ctx.stroke();

  // 4. Main Panchang Card Box
  ctx.fillStyle = 'rgba(255, 255, 255, 0.07)';
  ctx.roundRect(100, 280, 880, 780, 24);
  ctx.fill();
  ctx.strokeStyle = 'rgba(212, 175, 55, 0.3)';
  ctx.stroke();

  // 5. Data Rows
  ctx.textAlign = 'left';
  let yPos = 370;

  const items = [
    { label: '☀️ Sunrise / Sunset', value: data.sunrise },
    { label: '🌙 Tithi', value: data.tithi },
    { label: '⭐ Nakshatra', value: data.nakshatra },
    { label: '⚠️ Rahu Kalam', value: data.rahuKalam },
  ];

  if (data.festivalToday) {
    items.unshift({ label: '🎉 Today\'s Festival', value: data.festivalToday });
  }

  items.forEach((item) => {
    // Label
    ctx.fillStyle = '#FFC107';
    ctx.font = 'bold 36px sans-serif';
    ctx.fillText(item.label, 150, yPos);

    // Value
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '36px sans-serif';
    ctx.fillText(item.value, 150, yPos + 48);

    yPos += 120;
  });

  // 6. Footer Branding & Call To Action
  ctx.textAlign = 'center';
  ctx.fillStyle = '#FFD700';
  ctx.font = 'bold 38px sans-serif';
  ctx.fillText('Regional Panchang App', 540, 1150);

  ctx.fillStyle = '#B0BEC5';
  ctx.font = '28px sans-serif';
  ctx.fillText('Download for Daily Muhurat, Rashifal & Regional Panji', 540, 1200);

  // 7. Trigger Native Share or Download
  canvas.toBlob(async (blob) => {
    if (!blob) return;

    const file = new File([blob], `Panchang_${data.date.replace(/\s+/g, '_')}.png`, { type: 'image/png' });

    if (navigator.canShare && navigator.canShare({ files: [file] })) {
      try {
        await navigator.share({
          title: `Daily Panchang - ${data.date}`,
          text: `Today's Panchang for ${data.stateName} (${data.date}): Tithi: ${data.tithi}, Rahu Kalam: ${data.rahuKalam}. Generated via Regional Panchang.`,
          files: [file],
        });
      } catch (err) {
        console.log('Share canceled or failed', err);
      }
    } else {
      // Fallback: Download file directly
      const link = document.createElement('a');
      link.download = `Panchang_${data.date.replace(/\s+/g, '_')}.png`;
      link.href = canvas.toDataURL('image/png');
      link.click();
    }
  }, 'image/png');
}