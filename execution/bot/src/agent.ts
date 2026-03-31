import { query } from '@anthropic-ai/claude-agent-sdk';

import { PROJECT_ROOT } from './config.js';
import { readEnvFile } from './env.js';
import { logger } from './logger.js';

export interface UsageInfo {
  inputTokens: number;
  outputTokens: number;
  cacheReadInputTokens: number;
  totalCostUsd: number;
  didCompact: boolean;
  preCompactTokens: number | null;
  lastCallCacheRead: number;
}

export interface AgentResult {
  text: string | null;
  newSessionId: string | undefined;
  usage: UsageInfo | null;
}

/**
 * A minimal AsyncIterable that yields a single user message then closes.
 */
async function* singleTurn(text: string): AsyncGenerator<{
  type: 'user';
  message: { role: 'user'; content: string };
  parent_tool_use_id: null;
  session_id: string;
}> {
  yield {
    type: 'user',
    message: { role: 'user', content: text },
    parent_tool_use_id: null,
    session_id: '',
  };
}

/**
 * Run a single user message through Claude Code and return the result.
 *
 * Uses `resume` to continue the same session across Telegram messages,
 * giving Claude persistent context without re-sending history.
 *
 * The SDK spawns the `claude` CLI subprocess which reads OAuth auth
 * from ~/.claude/ automatically. No explicit token needed if you're
 * already logged in via `claude login`.
 */
export async function runAgent(
  message: string,
  sessionId: string | undefined,
  onTyping: () => void,
): Promise<AgentResult> {
  const secrets = readEnvFile(['CLAUDE_CODE_OAUTH_TOKEN', 'ANTHROPIC_API_KEY']);

  const sdkEnv: Record<string, string | undefined> = { ...process.env };
  if (secrets.CLAUDE_CODE_OAUTH_TOKEN) {
    sdkEnv.CLAUDE_CODE_OAUTH_TOKEN = secrets.CLAUDE_CODE_OAUTH_TOKEN;
  }
  if (secrets.ANTHROPIC_API_KEY) {
    sdkEnv.ANTHROPIC_API_KEY = secrets.ANTHROPIC_API_KEY;
  }

  let newSessionId: string | undefined;
  let resultText: string | null = null;
  let usage: UsageInfo | null = null;
  let didCompact = false;
  let preCompactTokens: number | null = null;
  let lastCallCacheRead = 0;

  // Refresh typing indicator on an interval while Claude works.
  const typingInterval = setInterval(onTyping, 4000);

  try {
    logger.info(
      { sessionId: sessionId ?? 'new', messageLen: message.length },
      'Starting agent query',
    );

    for await (const event of query({
      prompt: singleTurn(message),
      options: {
        // cwd = AIOS workspace root so Claude Code loads our CLAUDE.md and skills
        cwd: PROJECT_ROOT,

        // Resume the previous session for this chat (persistent context)
        resume: sessionId,

        // 'project' loads CLAUDE.md from cwd; 'user' loads ~/.claude/skills/ and user settings
        settingSources: ['project', 'user'],

        // Skip all permission prompts — trusted personal bot on your own machine
        permissionMode: 'bypassPermissions',
        allowDangerouslySkipPermissions: true,

        // Pass secrets to the subprocess without polluting our own process.env
        env: sdkEnv,
      },
    })) {
      const ev = event as Record<string, unknown>;

      if (ev['type'] === 'system' && ev['subtype'] === 'init') {
        newSessionId = ev['session_id'] as string;
        logger.info({ newSessionId }, 'Session initialized');
      }

      if (ev['type'] === 'system' && ev['subtype'] === 'compact_boundary') {
        didCompact = true;
        const meta = ev['compact_metadata'] as { trigger: string; pre_tokens: number } | undefined;
        preCompactTokens = meta?.pre_tokens ?? null;
        logger.warn({ trigger: meta?.trigger, preCompactTokens }, 'Context window compacted');
      }

      if (ev['type'] === 'assistant') {
        const msgUsage = (ev['message'] as Record<string, unknown>)?.['usage'] as Record<string, number> | undefined;
        const callCacheRead = msgUsage?.['cache_read_input_tokens'] ?? 0;
        if (callCacheRead > 0) {
          lastCallCacheRead = callCacheRead;
        }
      }

      if (ev['type'] === 'result') {
        resultText = (ev['result'] as string | null | undefined) ?? null;

        const evUsage = ev['usage'] as Record<string, number> | undefined;
        if (evUsage) {
          usage = {
            inputTokens: evUsage['input_tokens'] ?? 0,
            outputTokens: evUsage['output_tokens'] ?? 0,
            cacheReadInputTokens: evUsage['cache_read_input_tokens'] ?? 0,
            totalCostUsd: (ev['total_cost_usd'] as number) ?? 0,
            didCompact,
            preCompactTokens,
            lastCallCacheRead,
          };
          logger.info(
            {
              inputTokens: usage.inputTokens,
              cacheReadTokens: usage.cacheReadInputTokens,
              costUsd: usage.totalCostUsd,
              didCompact,
            },
            'Turn usage',
          );
        }

        logger.info({ hasResult: !!resultText }, 'Agent result received');
      }
    }
  } finally {
    clearInterval(typingInterval);
  }

  return { text: resultText, newSessionId, usage };
}
