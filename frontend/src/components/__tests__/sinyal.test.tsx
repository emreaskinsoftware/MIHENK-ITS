/**
 * Ön yüz ilke testleri (spec 8).
 *
 * Arka uçtaki testler "servis doğru veriyi üretiyor mu" sorusunu yanıtlıyor.
 * Buradakiler farklı bir soruyu yanıtlar: "arayüz, servisin sustuğu yerde
 * gerçekten susuyor mu?" Çekimserlik servis katmanında doğru çalışsa bile,
 * arayüz `label === null` durumunda bir "bilinmiyor" rozeti çizerse İlke 2
 * ürün yüzeyinde çiğnenmiş olur.
 */
import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { KokenGostergesi } from "../KokenGostergesi";
import { YzSinyali } from "../YzSinyali";
import type { KokenSonucu, TespitSonucu } from "../../lib/api";

const cekimser: TespitSonucu = {
  label: null,
  confidence: null,
  abstained: true,
  reason: "metin_cok_kisa",
  token_count: 8,
  length_bucket: "K1",
};

const yzEtiketi: TespitSonucu = {
  label: "yz_olasi",
  confidence: 0.91,
  abstained: false,
  reason: null,
  token_count: 120,
  length_bucket: "K3",
};

describe("YzSinyali — çekimserlik", () => {
  it("çekimser sonuçta hiçbir rozet çizmez", () => {
    const { container } = render(
      <YzSinyali postId="p1" tespit={cekimser} itirazVar={false} onItiraz={vi.fn()} />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("tespit sonucu hiç yoksa da boş kalır", () => {
    const { container } = render(
      <YzSinyali postId="p1" tespit={null} itirazVar={false} onItiraz={vi.fn()} />,
    );
    expect(container.innerHTML).toBe("");
  });

  it("etiket varsa rozeti ve itiraz düğmesini gösterir", () => {
    render(<YzSinyali postId="p1" tespit={yzEtiketi} itirazVar={false} onItiraz={vi.fn()} />);
    expect(screen.getByText(/Yapay zekâ üretimi olabilir/)).toBeDefined();
    expect(screen.getByRole("button", { name: /itiraz et/i })).toBeDefined();
  });

  it("rozet dili kesin hüküm kurmaz ('olabilir' der)", () => {
    render(<YzSinyali postId="p1" tespit={yzEtiketi} itirazVar={false} onItiraz={vi.fn()} />);
    const metin = screen.getByText(/Yapay zekâ üretimi olabilir/).textContent ?? "";
    expect(metin).toContain("olabilir");
    expect(metin).not.toMatch(/^Yapay zekâ üretimi$/);
  });

  it("itiraz edilmiş gönderide sinyali gizler", () => {
    render(<YzSinyali postId="p1" tespit={yzEtiketi} itirazVar={true} onItiraz={vi.fn()} />);
    expect(screen.queryByText(/Yapay zekâ üretimi olabilir/)).toBeNull();
    expect(screen.getByRole("status").textContent).toMatch(/incelemede/i);
  });
});

describe("KokenGostergesi — çekimserlik", () => {
  const belirsiz: KokenSonucu = {
    media_id: "m1",
    status: "belirsiz",
    display: false,
    evidence: null,
    label: null,
  };

  it("üst veri yoksa hiçbir gösterge çizmez", () => {
    const { container } = render(<KokenGostergesi koken={belirsiz} />);
    expect(container.innerHTML).toBe("");
  });

  it("manifest varsa etiketi ve kanıt kaynağını duyurur", () => {
    const kesin: KokenSonucu = {
      media_id: "m2",
      status: "yz_uretimi",
      display: true,
      evidence: "c2pa",
      label: "Yapay zekâ ile üretildi (üretici beyanı)",
    };
    render(<KokenGostergesi koken={kesin} />);
    // Bilgi yalnızca renkle değil, metin ve aria-label ile de aktarılır.
    const oge = screen.getByLabelText(/Kanıt kaynağı: c2pa/);
    expect(oge.textContent).toContain("Yapay zekâ ile üretildi");
  });
});
