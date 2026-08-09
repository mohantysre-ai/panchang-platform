import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { PanchangDashboard } from './pages/PanchangDashboard';
import './index.css';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <PanchangDashboard />
  </StrictMode>,
);
