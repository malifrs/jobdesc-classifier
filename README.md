# JobDesc Classifier

Aplikasi web untuk menganalisis teks lowongan pekerjaan bidang TI. Aplikasi
melakukan tiga hal sekaligus atas satu masukan teks:

1. Klasifikasi peran utama ke dalam enam kategori memakai model SVM dengan
   representasi TF-IDF.
2. Penetapan sub-role berdasarkan cosine similarity terhadap profil okupasi
   O*NET Bright Outlook di dalam peran hasil prediksi.
3. Ekstraksi keterampilan melalui pencocokan kamus keterampilan O*NET yang
   sudah diberi bobot.

Aplikasi tidak menyimpan data. Setiap masukan diproses di memori lalu hasilnya
langsung ditampilkan.

## Isi berkas

| Berkas | Keterangan |
| --- | --- |
| `app.py` | Antarmuka Streamlit, berkas utama yang dijalankan |
| `analisis.py` | Lapisan analisis: pemuatan bundel, klasifikasi, sub-role, keterampilan |
| `job_role_onet_complete.joblib` | Bundel komponen terlatih hasil notebook eksperimen |
| `requirements.txt` | Daftar pustaka beserta versinya |

## Menjalankan secara lokal

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

Aplikasi terbuka di `http://localhost:8501`.

## Catatan versi

Bundel model disimpan dengan joblib, sehingga versi scikit-learn saat memuat
harus sama dengan versi saat melatih. Karena itu semua versi di
`requirements.txt` dikunci dan aplikasi perlu dijalankan pada Python 3.12.
