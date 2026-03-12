'use client';
import { Cpu } from 'lucide-react';

export default function Header() {
  return (
    <div className="sticky top-0 z-20 bg-white/90 backdrop-blur border-b border-rose-200">
      <div className="mx-auto max-w-6xl px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-6 w-6 rounded-lg bg-gradient-to-br from-rose-400 to-rose-600" />
          <span className="font-semibold tracking-tight text-slate-800">Pregnancy Coach</span>
        </div>
        <div className="text-xs text-rose-600/80 flex items-center gap-1">
          <Cpu className="h-4 w-4" /> Local · Ollama + Chroma
        </div>
      </div>
    </div>
  );
}
