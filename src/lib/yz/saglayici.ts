/**
 * MİHENK — Yapay zekâ sağlayıcı soyutlaması.
 *
 * Mimari karar (bkz. rapor 3.1): sistem iki katmanlı çalışır.
 *   A) YEREL katman — özetleme, kümeleme, görsel denetim.
 *      Dış servise ihtiyaç duymaz, düşük maliyetlidir, yerlidir.
 *   B) UZAK katman — doğrulama ve asistan. Güncel dünya bilgisi ve web
 *      araması gerektirdiği için dış model üzerinden yürütülür.
 *
 * Anahtar tanımlı değilse sistem SESSİZCE yerel katmana düşer; prototip
 * her koşulda çalışır durumda kalır. Bu, jüri demosunda ağ/anahtar
 * sorununun gösterimi kesmemesi için bilinçli bir tasarım kararıdır.
 */

export type SaglayiciAdi = "claude" | "openai" | "gemini" | "yerel";

export interface UretimIstegi {
  sistem: string;
  kullanici: string;
  enFazlaJeton?: number;
  webAramasi?: boolean;
}

export interface UretimYaniti {
  metin: string;
  saglayici: SaglayiciAdi;
  kaynaklar?: { baslik: string; url: string }[];
  jetonKullanimi?: { girdi: number; cikti: number };
}

const VARSAYILAN_MODEL: Record<Exclude<SaglayiciAdi, "yerel">, string> = {
  claude: "claude-sonnet-5",
  openai: "gpt-4o",
  gemini: "gemini-2.0-flash",
};

export function etkinSaglayici(): SaglayiciAdi {
  const tercih = process.env.YZ_SAGLAYICI as SaglayiciAdi | undefined;
  if (tercih === "claude" && process.env.ANTHROPIC_API_KEY) return "claude";
  if (tercih === "openai" && process.env.OPENAI_API_KEY) return "openai";
  if (tercih === "gemini" && process.env.GEMINI_API_KEY) return "gemini";
  // Tercih belirtilmemişse tanımlı olan ilk anahtarı kullan
  if (process.env.ANTHROPIC_API_KEY) return "claude";
  if (process.env.OPENAI_API_KEY) return "openai";
  if (process.env.GEMINI_API_KEY) return "gemini";
  return "yerel";
}

export async function uret(istek: UretimIstegi): Promise<UretimYaniti> {
  const saglayici = etkinSaglayici();
  try {
    switch (saglayici) {
      case "claude": return await claudeIle(istek);
      case "openai": return await openaiIle(istek);
      case "gemini": return await geminiIle(istek);
      default: return { metin: "", saglayici: "yerel" };
    }
  } catch (hata) {
    // Ağ/kota hatasında gösterimi kesmemek için yerel katmana düş
    console.error("[yz] sağlayıcı hatası, yerel katmana düşülüyor:", hata);
    return { metin: "", saglayici: "yerel" };
  }
}

async function claudeIle(istek: UretimIstegi): Promise<UretimYaniti> {
  const govde: Record<string, unknown> = {
    model: process.env.YZ_MODEL || VARSAYILAN_MODEL.claude,
    max_tokens: istek.enFazlaJeton ?? 1024,
    system: istek.sistem,
    messages: [{ role: "user", content: istek.kullanici }],
  };
  if (istek.webAramasi) {
    govde.tools = [{ type: "web_search_20250305", name: "web_search", max_uses: 5 }];
  }

  const yanit = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      "x-api-key": process.env.ANTHROPIC_API_KEY!,
      "anthropic-version": "2023-06-01",
    },
    body: JSON.stringify(govde),
  });
  if (!yanit.ok) throw new Error(`Claude ${yanit.status}: ${await yanit.text()}`);

  const veri = await yanit.json();
  const metin = (veri.content ?? [])
    .filter((p: { type: string }) => p.type === "text")
    .map((p: { text: string }) => p.text)
    .join("\n");

  const kaynaklar = kaynaklariTopla(veri.content);
  return {
    metin,
    saglayici: "claude",
    kaynaklar,
    jetonKullanimi: veri.usage
      ? { girdi: veri.usage.input_tokens, cikti: veri.usage.output_tokens }
      : undefined,
  };
}

/** Claude web arama sonuçlarından kaynak listesi çıkarır */
function kaynaklariTopla(icerik: unknown[]): { baslik: string; url: string }[] {
  const bulunan: { baslik: string; url: string }[] = [];
  const gez = (dugum: unknown) => {
    if (!dugum || typeof dugum !== "object") return;
    const d = dugum as Record<string, unknown>;
    if (typeof d.url === "string" && typeof d.title === "string") {
      bulunan.push({ baslik: d.title, url: d.url });
    }
    for (const deger of Object.values(d)) {
      if (Array.isArray(deger)) deger.forEach(gez);
      else if (deger && typeof deger === "object") gez(deger);
    }
  };
  (icerik ?? []).forEach(gez);
  // Yinelenen URL'leri ele
  const gorulen = new Set<string>();
  return bulunan.filter((k) => !gorulen.has(k.url) && gorulen.add(k.url));
}

async function openaiIle(istek: UretimIstegi): Promise<UretimYaniti> {
  const yanit = await fetch("https://api.openai.com/v1/chat/completions", {
    method: "POST",
    headers: {
      "content-type": "application/json",
      authorization: `Bearer ${process.env.OPENAI_API_KEY}`,
    },
    body: JSON.stringify({
      model: process.env.YZ_MODEL || VARSAYILAN_MODEL.openai,
      max_tokens: istek.enFazlaJeton ?? 1024,
      messages: [
        { role: "system", content: istek.sistem },
        { role: "user", content: istek.kullanici },
      ],
    }),
  });
  if (!yanit.ok) throw new Error(`OpenAI ${yanit.status}: ${await yanit.text()}`);
  const veri = await yanit.json();
  return { metin: veri.choices?.[0]?.message?.content ?? "", saglayici: "openai" };
}

async function geminiIle(istek: UretimIstegi): Promise<UretimYaniti> {
  const model = process.env.YZ_MODEL || VARSAYILAN_MODEL.gemini;
  const yanit = await fetch(
    `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent?key=${process.env.GEMINI_API_KEY}`,
    {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify({
        systemInstruction: { parts: [{ text: istek.sistem }] },
        contents: [{ role: "user", parts: [{ text: istek.kullanici }] }],
        generationConfig: { maxOutputTokens: istek.enFazlaJeton ?? 1024 },
      }),
    },
  );
  if (!yanit.ok) throw new Error(`Gemini ${yanit.status}: ${await yanit.text()}`);
  const veri = await yanit.json();
  const metin = (veri.candidates?.[0]?.content?.parts ?? [])
    .map((p: { text?: string }) => p.text ?? "")
    .join("");
  return { metin, saglayici: "gemini" };
}
