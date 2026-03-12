import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const base = process.env.NEXT_PUBLIC_BACKEND_URL || "http://127.0.0.1:8001";
    const body = await req.json();

    const resp = await fetch(`${base}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: "web",
        message: body.message,
        profile: {
          weeks_pregnant: body.profile?.weeks_pregnant ?? null,
          trimester: body.profile?.trimester ?? null,
          activity_level: body.profile?.activity_level ?? null,
          dietary_pref: body.profile?.dietary_pref ?? null,
          allergies: body.profile?.allergies ?? [],
          restrictions: body.profile?.restrictions ?? [],
          conditions: body.profile?.conditions ?? [],
        },
      }),
    });

    if (!resp.ok) {
      const text = await resp.text();
      console.error("Backend error", resp.status, text);
      return NextResponse.json(
        { error: `Backend ${resp.status}: ${text}` },
        { status: 502 }
      );
    }

    const data = await resp.json();
    // backend returns { message: "...", ... }
    return NextResponse.json({ reply: data.message ?? data.reply ?? "" });
  } catch (err: any) {
    console.error("Proxy error:", err);
    return NextResponse.json({ error: err?.message || "Proxy error" }, { status: 500 });
  }
}
