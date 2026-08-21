/**
 * Tailwind yapılandırması.
 *
 * RENK PALETİ ERİŞİLEBİLİRLİK İÇİN SEÇİLDİ (spec 6.9, WCAG 2.2 AA):
 * Metin renkleri arka planlarına karşı en az 4.5:1 karşıtlık sağlar.
 * `mihenk.metin` (#1a1a1a) beyaz üzerinde ~16.9:1, `mihenk.ikincil` (#4a4a4a)
 * ~8.6:1, vurgu rengi `mihenk.vurgu` (#0b5c4a) beyaz üzerinde ~6.6:1 verir.
 *
 * ÖNEMLİ KURAL: Bilgi yalnızca renkle aktarılmaz. Her renkli durumun yanında
 * simge ve metin bulunur (bkz. components/KokenGostergesi.tsx).
 */
export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        mihenk: {
          metin: "#1a1a1a",
          ikincil: "#4a4a4a",
          vurgu: "#0b5c4a",
          "vurgu-acik": "#e6f2ef",
          uyari: "#8a4b00",
          "uyari-acik": "#fdf1e3",
          cizgi: "#d9d9d9",
          zemin: "#fbfbfa",
        },
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", "Segoe UI", "Roboto", "Arial", "sans-serif"],
      },
      minHeight: {
        // Dokunma hedefi alt sınırı (spec 6.9): 44x44 px
        dokunma: "44px",
      },
      minWidth: {
        dokunma: "44px",
      },
    },
  },
  plugins: [],
};
