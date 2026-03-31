import fs from 'fs';
import path from 'path';

import { createBot } from './bot.js';
import { ALLOWED_CHAT_ID, TELEGRAM_BOT_TOKEN, STORE_DIR, PROJECT_ROOT } from './config.js';
import { initDatabase } from './db.js';
import { logger } from './logger.js';
import { runDecaySweep } from './memory.js';
import { initScheduler } from './scheduler.js';

const PID_FILE = path.join(STORE_DIR, 'aios.pid');

function showBanner(): void {
  const bannerPath = path.join(PROJECT_ROOT, 'execution', 'bot', 'banner.txt');
  try {
    const banner = fs.readFileSync(bannerPath, 'utf-8');
    console.log('\n' + banner);
  } catch {
    console.log('\n  AIOS Bot\n');
  }
}

function acquireLock(): void {
  fs.mkdirSync(STORE_DIR, { recursive: true });
  try {
    if (fs.existsSync(PID_FILE)) {
      const old = parseInt(fs.readFileSync(PID_FILE, 'utf8').trim(), 10);
      if (!isNaN(old) && old !== process.pid) {
        try {
          process.kill(old, 'SIGTERM');
          Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 1000);
        } catch { /* already dead */ }
      }
    }
  } catch { /* ignore */ }
  fs.writeFileSync(PID_FILE, String(process.pid));
}

function releaseLock(): void {
  try { fs.unlinkSync(PID_FILE); } catch { /* ignore */ }
}

async function main(): Promise<void> {
  showBanner();

  if (!TELEGRAM_BOT_TOKEN) {
    logger.error('TELEGRAM_BOT_TOKEN is not set. Add it to .env and restart.');
    process.exit(1);
  }

  acquireLock();

  initDatabase();
  logger.info('Database ready');

  runDecaySweep();
  setInterval(() => runDecaySweep(), 24 * 60 * 60 * 1000);

  const bot = createBot();

  if (ALLOWED_CHAT_ID) {
    initScheduler((text) => bot.api.sendMessage(ALLOWED_CHAT_ID, text, { parse_mode: 'HTML' }).then(() => {}));
  }

  const shutdown = async () => {
    logger.info('Shutting down...');
    releaseLock();
    await bot.stop();
    process.exit(0);
  };
  process.on('SIGINT', () => void shutdown());
  process.on('SIGTERM', () => void shutdown());

  logger.info({ projectRoot: PROJECT_ROOT }, 'Starting AIOS...');

  await bot.start({
    onStart: (botInfo) => {
      logger.info({ username: botInfo.username }, 'AIOS is running');
      console.log(`\n  AIOS online: @${botInfo.username}`);
      console.log(`  Send /chatid to get your chat ID for ALLOWED_CHAT_ID\n`);
    },
  });
}

main().catch((err: unknown) => {
  logger.error({ err }, 'Fatal error');
  releaseLock();
  process.exit(1);
});
