"""Cihaz seçimi ve cihaza bağlı eğitim ayarları.

NEDEN AYRI MODÜL: Aynı depo iki farklı makinede koşuyor — geliştirme için
CPU'lu bir dizüstü, eğitim için CUDA'lı bir masaüstü. Cihaza bağlı ayarları
(parti boyutu, dondurulan katman, karışık hassasiyet) koda dağıtmak, iki
makinede iki farklı sürüm tutmaya götürür. Burada tek yerden çözülür ve hem
eğitim betiği hem de çıkarım katmanı aynı kararı kullanır.

CPU ve GPU profillerinin neden farklı olduğu `config.py` içinde ölçülen
sayılarla açıklanmıştır.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.config import get_settings


@dataclass(frozen=True)
class RuntimeProfile:
    """Etkin cihaz ve o cihaza uygun eğitim ayarları."""

    device: str  # "cuda" | "cpu"
    device_name: str  # insan tarafından okunabilir (rapora yazılır)
    batch_size: int
    frozen_layers: int
    amp: bool  # karışık hassasiyet kullanılsın mı

    @property
    def is_cuda(self) -> bool:
        return self.device == "cuda"

    def summary(self) -> str:
        """Eğitim/ölçüm çıktısına basılan tek satırlık özet."""
        return (
            f"cihaz={self.device} ({self.device_name}) parti={self.batch_size} "
            f"dondurulan_katman={self.frozen_layers} amp={self.amp}"
        )


def resolve_runtime() -> RuntimeProfile:
    """Etkin cihazı ve ona uygun profili döndürür.

    `torch` kurulu değilse CPU profili döner; bu durumda BERTurk zaten
    yüklenemez ve sistem TF-IDF temel çizgisine veya çekimserliğe düşer.
    """
    ayar = get_settings()

    try:
        import torch

        cuda_var = torch.cuda.is_available()
        cihaz_adi = torch.cuda.get_device_name(0) if cuda_var else "CPU"
    except Exception:  # torch yok veya sürücü sorunu
        cuda_var, cihaz_adi = False, "CPU (torch yok)"

    if ayar.detection_device == "cuda" and not cuda_var:
        # Açıkça CUDA istendi ama yok: sessizce CPU'ya düşmüyoruz. Ölçüm
        # koşusunda hangi cihazda çalıştığımızı bilmek zorundayız (spec 2).
        raise RuntimeError(
            "MIHENK_DETECTION_DEVICE=cuda verildi ancak CUDA kullanılamıyor. "
            "Sürücüyü/torch kurulumunu kontrol edin veya 'auto' kullanın."
        )

    cuda_kullan = cuda_var and ayar.detection_device in ("auto", "cuda")

    if cuda_kullan:
        return RuntimeProfile(
            device="cuda",
            device_name=cihaz_adi,
            batch_size=ayar.detection_batch_size_gpu,
            frozen_layers=ayar.detection_frozen_layers_gpu,
            amp=ayar.detection_amp,
        )
    return RuntimeProfile(
        device="cpu",
        device_name=cihaz_adi,
        batch_size=ayar.detection_batch_size,
        frozen_layers=ayar.detection_frozen_layers,
        # AMP CPU'da kazanç sağlamaz, bazı işlemlerde yavaşlatır.
        amp=False,
    )
