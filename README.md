# FlyConnectome Compare

5 FlyWire Codex Drosophila connectome dataset'ini (FAFB, BANC, MANC, MAOL, MCNS) birbiriyle
kıyaslayan bir çalışma. Üç eksen:

1. **Erkek vs dişi tüm-CNS ağ istatistikleri** (BANC vs MCNS) — birincil odak.
2. **Rekonstrüksiyon tutarlılığı**: FAFB'nin görsel lob kısmı vs MAOL (dedike optik lob rekonstrüksiyonu).
3. **VNC cinsiyet karşılaştırması** (MANC vs BANC'ın sinir-kordonu kısmı) — Stürner et al. 2024'ün
   tamamlayıcısı, tüm-ağ istatistiği katmanında.

Notlar/tasarım kararları: `D:\obsidianVault\FlyConnectome_Compare\` (`00_Genel_Bakis.md`, `DURUM.md`).

## Veri

`data/<dataset>/` altında (git'e alınmıyor, codex.flywire.ai'den manuel indirilir):
- `connections_princeton.csv.gz` — tüm dataset'lerde aynı şema: `pre_root_id, post_root_id, neuropil, syn_count, nt_type`
- BANC/MANC/MAOL/MCNS: `neurons.csv.gz` (aynı şema, `Root ID`, `Super Class`, `Class`, `Sub Class`, `Primary Cell Type`, `Soma side`, `Nerve`, ...)
- FAFB: `classification.csv.gz` + `consolidated_cell_types.csv.gz` + `names.csv.gz` + `processed_labels.csv.gz` + `visual_neuron_types.csv.gz` (aynı bilgi, ayrı dosyalarda, snake_case kolonlarla)

`flyconnectome_compare.io.loaders` bu farkı gizleyip her dataset için birleşik bir `neurons`
şeması (`root_id, super_class, class, sub_class, cell_type, side, nerve`) döndürür.

## Kurulum

```
pip install -e ".[dev]"
pytest
```

## Durum

İskelet kuruldu (2026-09-23) — yükleyiciler çalışıyor, metrik/karşılaştırma mantığı henüz
tasarlanmadı (`compare/` altındaki modüller placeholder).
