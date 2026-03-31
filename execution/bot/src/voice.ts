import fs from 'fs';
import path from 'path';

import { GROQ_API_KEY, ELEVENLABS_API_KEY, ELEVENLABS_VOICE_ID, STORE_DIR } from './config.js';

export const UPLOADS_DIR = path.join(STORE_DIR, 'uploads');

export function voiceCapabilities(): { stt: boolean; tts: boolean } {
  return {
    stt: !!GROQ_API_KEY,
    tts: !!(ELEVENLABS_API_KEY && ELEVENLABS_VOICE_ID),
  };
}

/**
 * Download a file from Telegram's file API to a local path.
 */
export async function downloadTelegramFile(
  token: string,
  fileId: string,
  uploadsDir: string,
): Promise<string> {
  const infoUrl = `https://api.telegram.org/bot${token}/getFile?file_id=${fileId}`;
  const infoRes = await fetch(infoUrl);
  const info = await infoRes.json() as { ok: boolean; result: { file_path: string } };
  if (!info.ok) throw new Error('Failed to get file info from Telegram');

  const fileUrl = `https://api.telegram.org/file/bot${token}/${info.result.file_path}`;
  const fileRes = await fetch(fileUrl);
  const buffer = Buffer.from(await fileRes.arrayBuffer());

  fs.mkdirSync(uploadsDir, { recursive: true });
  const ext = path.extname(info.result.file_path) || '.oga';
  const localPath = path.join(uploadsDir, `voice_${Date.now()}${ext}`);
  fs.writeFileSync(localPath, buffer);
  return localPath;
}

/**
 * Transcribe an audio file using Groq Whisper.
 */
export async function transcribeAudio(filePath: string): Promise<string> {
  if (!GROQ_API_KEY) throw new Error('GROQ_API_KEY not set');

  const fileBuffer = fs.readFileSync(filePath);
  const formData = new FormData();
  formData.append('file', new Blob([fileBuffer]), path.basename(filePath));
  formData.append('model', 'whisper-large-v3');

  const res = await fetch('https://api.groq.com/openai/v1/audio/transcriptions', {
    method: 'POST',
    headers: { Authorization: `Bearer ${GROQ_API_KEY}` },
    body: formData,
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`Groq transcription failed: ${err}`);
  }

  const data = await res.json() as { text: string };
  return data.text;
}

/**
 * Synthesize speech using ElevenLabs TTS.
 */
export async function synthesizeSpeech(text: string): Promise<Buffer> {
  if (!ELEVENLABS_API_KEY || !ELEVENLABS_VOICE_ID) {
    throw new Error('ElevenLabs not configured');
  }

  const res = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${ELEVENLABS_VOICE_ID}`, {
    method: 'POST',
    headers: {
      'xi-api-key': ELEVENLABS_API_KEY,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      model_id: 'eleven_turbo_v2',
      voice_settings: { stability: 0.5, similarity_boost: 0.75 },
    }),
  });

  if (!res.ok) {
    const err = await res.text();
    throw new Error(`ElevenLabs TTS failed: ${err}`);
  }

  return Buffer.from(await res.arrayBuffer());
}
