import { spawnSync } from 'node:child_process';
const origin = process.env.VITE_API_BASE_URL || 'https://calendar.sigq.in';
const url = new URL(origin);
if (url.protocol !== 'https:' || url.pathname !== '/' || url.search || url.hash || url.username || url.password) {
  throw new Error('VITE_API_BASE_URL must be an HTTPS origin without a path or credentials');
}
const result = spawnSync(process.platform === 'win32' ? 'npm.cmd' : 'npm', ['run', 'build'], {
  stdio: 'inherit', env: { ...process.env, VITE_API_BASE_URL: url.origin, VITE_MOBILE_BUILD: 'true' },
  shell: process.platform === 'win32',
});
process.exit(result.status ?? 1);
