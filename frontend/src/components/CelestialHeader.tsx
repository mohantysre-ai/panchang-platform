import React, { useEffect, useRef } from 'react';

interface CelestialHeaderProps {
  tithiPhase: number; // 0 (New Moon / Amavasya) to 1 (Full Moon / Purnima)
  moonSign: string;   // e.g. "Vrishabha (Taurus)"
  sunSign: string;    // e.g. "Karka (Cancer)"
  isDark: boolean;
}

export const CelestialHeader: React.FC<CelestialHeaderProps> = ({
  tithiPhase,
  moonSign,
  sunSign,
  isDark,
}) => {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    let animationFrameId: number;
    let angle = 0;

    const render = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const centerX = canvas.width / 2;
      const centerY = canvas.height / 2;
      const radius = 60;

      // 1. Draw Orbit Ring
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius + 35, 0, Math.PI * 2);
      ctx.strokeStyle = isDark ? 'rgba(255, 215, 0, 0.25)' : 'rgba(180, 83, 9, 0.25)';
      ctx.lineWidth = 1.5;
      ctx.setLineDash([4, 4]);
      ctx.stroke();
      ctx.setLineDash([]);

      // 2. Render Moon Sphere with Tithi Shadow
      ctx.save();
      ctx.beginPath();
      ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
      ctx.fillStyle = '#E2E8F0';
      ctx.fill();

      // Shadow overlay for moon phase rendering
      ctx.beginPath();
      const shadowWidth = radius * (1 - 2 * Math.abs(tithiPhase - 0.5));
      ctx.ellipse(
        centerX,
        centerY,
        Math.max(0.1, shadowWidth),
        radius,
        0,
        0,
        Math.PI * 2
      );
      ctx.fillStyle = tithiPhase > 0.5 ? '#1E293B' : '#0F172A';
      ctx.fill();
      ctx.restore();

      // 3. Orbiting Planets (Sun & Moon Indicators)
      angle += 0.01;
      const planetX = centerX + (radius + 35) * Math.cos(angle);
      const planetY = centerY + (radius + 35) * Math.sin(angle);

      // Sun / Planet Node
      ctx.beginPath();
      ctx.arc(planetX, planetY, 8, 0, Math.PI * 2);
      ctx.fillStyle = '#F59E0B'; // Sun Amber
      ctx.shadowColor = '#F59E0B';
      ctx.shadowBlur = 10;
      ctx.fill();
      ctx.shadowBlur = 0;

      animationFrameId = requestAnimationFrame(render);
    };

    render();

    return () => cancelAnimationFrame(animationFrameId);
  }, [tithiPhase, isDark]);

  return (
    <div className="relative flex flex-col items-center justify-center p-4">
      <canvas ref={canvasRef} width={300} height={200} className="w-full max-w-[300px]" />
      <div className="flex gap-6 mt-2 text-sm font-semibold">
        <span style={{ color: isDark ? '#FDE68A' : '#7C2D12' }}>☀️ Sun: {sunSign}</span>
        <span style={{ color: isDark ? '#E2E8F0' : '#1E293B' }}>🌙 Moon: {moonSign}</span>
      </div>
    </div>
  );
};
