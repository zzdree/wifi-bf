# 🔐 WiFi Security Audit & Dictionary Tool v3.0

> Tool Audit & Pengujian Keamanan Jaringan Wi-Fi Berbasis Windows (`netsh wlan`) dengan Dynamic Wordlist Detection, Vendor Router Fingerprinting, dan Auto-Resume State.

![Python](https://img.shields.io/badge/Python-3.7+-3776AB?style=flat-square&logo=python&logoColor=white)
![Platform](https://img.shields.io/badge/Platform-Windows_10%2F11-0078D6?style=flat-square&logo=windows&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero_External-brightgreen?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)

---

## ⚠️ Disclaimer & Batasan Hukum

```text
PERINGATAN PENTING:
Program ini dirancang HANYA untuk tujuan edukasi, analisis riset keamanan,
serta pengujian audit penetrasi pada jaringan Wi-Fi milik Anda sendiri
atau yang telah memiliki izin tertulis resmi dari pemilik jaringan.

Akses tanpa izin ke sistem komputer atau jaringan pihak ketiga melanggar
hukum yang berlaku (UU ITE Pasal 30 - Akses Ilegal). Penulis tidak bertanggung
jawab atas segala bentuk penyalahgunaan program ini.
```

---

## 📖 Overview

**WiFi Security Audit Tool v3.0** adalah skrip pengujian penetrasi keamanan Wi-Fi berbasis Windows native. Tool ini bekerja tanpa memerlukan library eksternal (*Zero Dependencies*) dan memanfaatkan API `netsh wlan` bawaan Windows untuk menguji ketahanan password jaringan nirkabel terhadap serangan berbasis kamus (*dictionary attack*).

---

## ✨ Fitur Unggulan

- 🔍 **Dynamic Dictionary Auto-Detection:** Secara otomatis memindai dan menghitung jumlah password valid (min. 8 karakter) serta ukuran file `.txt` apa pun yang dimasukkan ke dalam folder `dictionaries/`.
- 🏷️ **Router Vendor Fingerprinting:** Menganalisis BSSID (MAC Address OUI) dan pola penamaan SSID untuk mendeteksi pabrikan router (ZTE, Huawei, FiberHome, TP-Link, dll).
- 📶 **Interactive WLAN Scanner:** Memindai seluruh SSID di sekitar lengkap dengan indikator kekuatan sinyal (*RSSI bar*), tipe enkripsi (WPA2-PSK / WPA3 / Open), dan BSSID.
- ⚡ **Auto Profile & Cleanup:** Membuat profil jaringan sementara (`temporary.xml`) dan menghapusnya kembali secara otomatis agar sistem Windows tetap bersih tanpa meninggalkan jejak koneksi.
- 💾 **Resume Point & Logging:** Menyimpan posisi pengujian terakhir secara otomatis (`.progress`) jika dihentikan dengan `Ctrl + C`, serta mencatat hasil temuan ke `results.log`.
- 🔀 **Password Shuffling:** Opsi pengacakan urutan password untuk meningkatkan efektivitas pengujian.

---

## 📁 Struktur Repositori

```
wifi-brute-force/
├── .gitignore             ← Melindungi log dan progress lokal
├── LICENSE                ← Lisensi resmi MIT (@zzdree)
├── README.md              ← Dokumentasi lengkap & petunjuk penggunaan
├── main.py                ← Skrip utama program (eksekusi via python main.py)
└── dictionaries/          ← Folder penampung file wordlist (.txt)
    └── .gitkeep
```

---

## ⚙️ Persyaratan Sistem

| Komponen | Persyaratan |
| :--- | :--- |
| **Sistem Operasi** | Windows 10 / 11 |
| **Python** | Versi 3.7 atau lebih baru |
| **Hak Akses** | **Administrator** (Wajib, untuk kontrol `netsh wlan`) |
| **Adapter Jaringan** | Adapter Wi-Fi aktif |
| **Pustaka Eksternal** | **Tidak ada** (Menggunakan modul bawaan Python) |

---

## 🚀 Panduan Penggunaan

1. **Clone Repositori:**
   ```bash
   git clone https://github.com/zzdree/wifi-brute-force.git
   cd wifi-brute-force
   ```

2. **Tambahkan Wordlist / Dictionary:**
   Letakkan file wordlist password berformat `.txt` ke dalam folder `dictionaries/`:
   ```
   dictionaries/
   ├── wordlist_custom.txt
   └── common_passwords.txt
   ```
   *Program akan langsung mendeteksi semua file `.txt` secara otomatis saat dijalankan!*

3. **Jalankan Program (Sebagai Administrator):**
   Buka Command Prompt atau PowerShell dengan **Run as Administrator**, lalu ketik:
   ```bash
   python main.py
   ```

---

## 🎮 Menu Navigasi CLI

```text
══════════════════════════════════════════════════
  WIFI SECURITY AUDIT TOOL v3.0
══════════════════════════════════════════════════
  1. Scan & Pilih Target WiFi
  2. Masukkan SSID Manual
  3. Analisis Vendor Router & Rekomendasi
  4. Keluar
══════════════════════════════════════════════════
```

---

## 👨‍💻 Author

- **Andreas Restuawanta Christwara** ([@zzdree](https://github.com/zzdree))

---

## 📜 Lisensi

Proyek ini dilisensikan di bawah [MIT License](LICENSE).
