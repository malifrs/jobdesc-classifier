# Panduan Deploy ke Streamlit Community Cloud

Folder `Deploy/` ini sudah berisi semua yang dibutuhkan dan siap dijadikan repo
GitHub. Ikuti langkah di bawah secara berurutan.

## 0. Yang perlu disiapkan

- Akun GitHub.
- Akun Streamlit Community Cloud (share.streamlit.io), daftar memakai akun GitHub.
- Git terpasang di komputer. Cek dengan `git --version`.

## 1. Buat repo GitHub privat

Di github.com pilih **New repository**:

- Nama: `jobdesc-classifier` (bebas).
- Visibility: **Private**.
- Jangan centang "Add a README file", karena README sudah ada di folder ini.

## 2. Unggah folder ini ke repo

Buka terminal di dalam folder `Deploy`, lalu jalankan:

```bash
git init
git add .
git commit -m "Aplikasi klasifikasi job description"
git branch -M main
git remote add origin https://github.com/USERNAME/jobdesc-classifier.git
git push -u origin main
```

Ganti `USERNAME` dengan nama akun GitHub Anda.

Pastikan `job_role_onet_complete.joblib` ikut terunggah. Ukurannya sekitar 3 MB,
jauh di bawah batas 100 MB per berkas di GitHub, jadi tidak perlu Git LFS. Cek
di halaman repo apakah berkas tersebut muncul.

## 3. Deploy di Streamlit Community Cloud

1. Buka share.streamlit.io lalu masuk dengan akun GitHub.
2. Saat diminta otorisasi, berikan izin akses ke **private repositories**. Tanpa
   izin ini repo privat Anda tidak akan muncul di daftar.
3. Klik **Create app**, pilih **Deploy a public app from GitHub** (opsi yang sama
   dipakai untuk repo privat setelah izin diberikan).
4. Isi formulir:
   - Repository: `USERNAME/jobdesc-classifier`
   - Branch: `main`
   - Main file path: `app.py`
   - URL aplikasi: tentukan sendiri, misalnya `jobdesc-classifier`.
5. Buka **Advanced settings**, pastikan **Python version** diatur ke **3.12**.
   Ini penting. Versi pustaka yang dikunci di `requirements.txt` tidak tersedia
   untuk Python 3.10 atau 3.11, dan pemasangan akan gagal.
6. Klik **Deploy**. Proses pemasangan pustaka memakan waktu beberapa menit pada
   deploy pertama.

## 4. Jika gagal

Log tersedia di panel **Manage app** di pojok kanan bawah halaman aplikasi.
Beberapa kegagalan yang paling mungkin:

| Gejala di log | Penyebab | Tindakan |
| --- | --- | --- |
| `No matching distribution found for scikit-learn==1.9.0` | Python yang dipilih bukan 3.12 | Ubah Python version di Settings, lalu **Reboot app** |
| `InconsistentVersionWarning` atau error saat `joblib.load` | Versi scikit-learn tidak sama dengan saat pelatihan | Pastikan `requirements.txt` yang terunggah adalah yang ada di folder ini |
| `Berkas job_role_onet_complete.joblib tidak ditemukan` | Berkas model tidak ikut ter-push | Cek `.gitignore` dan pastikan berkas terlihat di repo GitHub |
| Halaman error 500 setiap kali dibuka | starlette terpasang versi 1.4.0 | Pastikan baris `starlette==1.3.1` ada di `requirements.txt` |
| `Oh no. Error running app` tanpa keterangan | Batas memori 1 GB terlampaui | Model hanya 3 MB, jadi kemungkinan kecil. Reboot app dahulu |

## 5. Atur siapa yang boleh membuka aplikasi

Aplikasi yang dideploy dari repo privat secara bawaan ikut menjadi privat, jadi
dosen tidak akan bisa membukanya begitu saja. Atur di **Settings** aplikasi,
bagian **Sharing**, pada pertanyaan "Who can view this app":

- **This app is public and searchable**: siapa pun yang punya URL bisa membuka
  tanpa login, sementara kode di GitHub tetap privat. Ini yang paling praktis
  untuk demo dan sidang, sekaligus membebaskan Anda dari batas satu aplikasi
  privat pada akun gratis.
- **Only specific people can view this app**: hanya alamat email yang Anda
  daftarkan sebagai viewer yang bisa membuka, dan mereka harus login. Batas satu
  aplikasi privat berlaku pada mode ini.

## 6. Setelah aplikasi jalan

- URL berbentuk `https://NAMA-APLIKASI.streamlit.app`.
- Aplikasi tertidur otomatis setelah 12 jam tanpa kunjungan. Ia bangun sendiri
  saat dibuka, tetapi butuh sekitar satu menit. Buka aplikasi beberapa menit
  sebelum sidang atau demo ke dosen supaya tidak menunggu di depan penguji.
- Setiap kali Anda `git push` perubahan, aplikasi otomatis dimuat ulang.

## Catatan untuk penulisan skripsi

Alamat aplikasi bisa dicantumkan di bab implementasi sebagai bukti bahwa sistem
berjalan.
