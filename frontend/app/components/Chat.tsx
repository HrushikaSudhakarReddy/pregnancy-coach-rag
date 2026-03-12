'use client';

import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowUp } from 'lucide-react';

type Message = { role: 'user' | 'assistant'; content: string };

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content:
        'Hi! Tell me your goals and I’ll suggest simple, pregnancy-friendly plans for **workouts, meals, hydration, or vitamins**.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<any>({
    weeks_pregnant: 22,
    trimester: 2,
    activity_level: 'light',
    dietary_pref: 'omnivore',
    allergies: [],
    restrictions: [],
    conditions: [],
  });

  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    const s = localStorage.getItem('pc_profile');
    if (s) setProfile(JSON.parse(s));
  }, []);

  useEffect(() => {
    localStorage.setItem('pc_profile', JSON.stringify(profile));
  }, [profile]);

  const send = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setMessages((m) => [...m, { role: 'user', content: userMsg }]);
    setInput('');
    setLoading(true);

    try {
      const r = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMsg, profile }),
      });

      const data = await r.json();
      const clean = String(data.reply || 'Sorry, I could not respond.').replace(/\\n/g, '\n');

      setMessages((m) => [...m, { role: 'assistant', content: clean }]);
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: 'assistant',
          content: 'I couldn’t reach the coach API. Check the backend URL in `.env.local`.',
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {/* top bar */}
      <div className="border-b border-rose-100 bg-white/60 px-5 py-4 backdrop-blur-sm">
        <div className="mx-auto flex max-w-3xl items-center justify-between">
          <div>
            <p className="text-xs font-medium uppercase tracking-[0.24em] text-rose-400">
              Pregnancy Wellness Chat
            </p>
            <h2 className="mt-1 text-lg font-semibold text-slate-800">Your local pregnancy coach</h2>
          </div>
          <div className="rounded-full border border-rose-200 bg-white/80 px-3 py-1 text-xs text-rose-600 shadow-sm">
            Private • Local
          </div>
        </div>
      </div>

      {/* chat stream */}
      <div className="flex-1 overflow-y-auto px-4 py-6 md:px-6">
        <div className="mx-auto max-w-3xl space-y-5">
          <AnimatePresence initial={false}>
            {messages.map((m, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2 }}
                className={m.role === 'user' ? 'flex justify-end' : 'flex justify-start'}
              >
                <div
                  className={
                    m.role === 'user'
                      ? 'max-w-[82%] rounded-[24px] rounded-br-md bg-rose-500 px-4 py-3 text-white shadow-lg'
                      : 'max-w-[82%] rounded-[24px] rounded-bl-md border border-rose-100 bg-white/95 px-4 py-3 text-slate-800 shadow-md backdrop-blur-sm'
                  }
                >
                  {m.role === 'assistant' && (
                    <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-rose-400">
                      Coach
                    </div>
                  )}

                  <div
                    className={
                      m.role === 'user'
                        ? 'prose prose-sm max-w-none prose-p:my-2 prose-strong:text-white prose-li:text-white prose-headings:text-white'
                        : 'prose prose-sm max-w-none prose-p:my-2 prose-headings:text-slate-800 prose-strong:text-slate-900 prose-li:text-slate-700'
                    }
                  >
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{m.content}</ReactMarkdown>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex justify-start"
            >
              <div className="rounded-2xl border border-rose-100 bg-white/95 px-4 py-3 shadow-sm">
                <div className="mb-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-rose-400">
                  Coach
                </div>
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className="inline-block h-2 w-2 animate-pulse rounded-full bg-rose-300" />
                  Thinking...
                </div>
              </div>
            </motion.div>
          )}

          <div ref={endRef} />
        </div>
      </div>

      {/* composer */}
      <div className="border-t border-rose-100 bg-white/70 backdrop-blur-md">
        <div className="mx-auto max-w-3xl p-4">
          <div className="rounded-[28px] border border-rose-200 bg-white/95 p-2 shadow-lg">
            <div className="flex items-end gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => (e.key === 'Enter' ? send() : null)}
                placeholder="Ask about workouts, meals, hydration, or vitamins"
                className="flex-1 rounded-2xl border border-transparent bg-transparent px-4 py-3 text-slate-800 outline-none placeholder:text-slate-400"
              />
              <button
                onClick={send}
                disabled={loading || !input.trim()}
                className="grid h-12 w-12 place-items-center rounded-full bg-rose-500 text-white shadow transition hover:bg-rose-600 disabled:cursor-not-allowed disabled:opacity-50"
                aria-label="Send"
              >
                <ArrowUp className="h-5 w-5" />
              </button>
            </div>
          </div>

          <p className="mt-2 px-2 text-center text-xs text-slate-500">
            Educational support only — not medical advice.
          </p>
        </div>
      </div>
    </div>
  );
}