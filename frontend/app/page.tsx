import Chat from './components/Chat';
import ProfileSidebar from './components/ProfileSidebar';

export default function Page() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-rose-50 via-white to-pink-50">
      <div className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-6 p-4 md:grid-cols-[340px,1fr] md:p-6">
        {/* LEFT SIDEBAR */}
        <aside className="rounded-[32px] border border-rose-200 bg-white/80 p-6 shadow-xl backdrop-blur-sm">
          <div className="mb-5">
            <p className="text-xs font-medium uppercase tracking-[0.25em] text-rose-400">
              Local RAG Assistant
            </p>
            <h1 className="mt-2 text-2xl font-semibold tracking-tight text-slate-800">
              Pregnancy Coach
            </h1>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              Personalized support for workouts, meals, hydration, and vitamins during pregnancy.
            </p>
          </div>

          <div className="rounded-[24px] bg-rose-50/80 p-4">
            <ProfileSidebar />
          </div>

          <div className="mt-5 rounded-2xl border border-rose-100 bg-rose-50/60 p-3">
            <p className="text-xs leading-5 text-rose-700">
              Educational use only. Not medical advice. Always consult your obstetric provider for care specific to you.
            </p>
          </div>
        </aside>

        {/* CHAT PANEL */}
        <section className="relative flex min-h-[78vh] overflow-hidden rounded-[32px] border border-rose-200 bg-white shadow-2xl">
          {/* background image */}
          <div className="absolute inset-0 bg-[url('/chat-bg.JPG')] bg-cover bg-center" />

          {/* soft layered overlays for readability */}
          <div className="absolute inset-0 bg-white/68" />
          <div className="absolute inset-0 bg-gradient-to-b from-white/55 via-white/35 to-white/80" />

          {/* subtle top glow */}
          <div className="absolute inset-x-0 top-0 h-28 bg-gradient-to-b from-rose-100/50 to-transparent" />

          {/* content */}
          <div className="relative flex-1">
            <Chat />
          </div>
        </section>
      </div>
    </main>
  );
}