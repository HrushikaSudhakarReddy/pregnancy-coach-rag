export const metadata = { title: 'Pregnancy Coach', description: 'Local RAG coach' };
import './global.css';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-dvh bg-white text-slate-900">{children}</body>
    </html>
  );
}
