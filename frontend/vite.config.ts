// vitest/config: `test` alanini tanimayan vite tipleri yerine bunu kullaniyoruz.
import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";

// Geliştirme sunucusu, /api isteklerini FastAPI'ye yönlendirir.
// NEDEN PROXY: Ön yüz ile arka uç aynı kaynaktan geliyormuş gibi çalışır;
// CORS ayarları yalnızca gerçek dağıtımda gerekir ve demo kurulumu sadeleşir.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      "/api": { target: "http://127.0.0.1:8000", changeOrigin: true },
    },
  },
  test: {
    environment: "jsdom",
    globals: true,
  },
});
