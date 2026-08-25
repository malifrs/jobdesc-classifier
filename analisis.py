"""Lapisan analisis aplikasi web.

Modul ini memuat komponen terlatih dari berkas bundel joblib, lalu menjalankan
prosedur analisis yang sama persis dengan tahap eksperimen pada notebook:
klasifikasi peran (SVM), penetapan sub-role (cosine similarity), dan ekstraksi
keterampilan (pencocokan kamus O*NET).
"""

from pathlib import Path
import re

import joblib
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Panjang minimum masukan. Teks yang lebih pendek dari ini tidak memuat cukup
# informasi untuk dianalisis, jadi ditolak sebelum masuk ke model.
MIN_KARAKTER = 30


def normalize(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def contains_term(text, term):
    """Cek kemunculan istilah sebagai kata utuh (menghindari kecocokan sebagian).
    Token pendek diblokir HANYA bila alfanumerik murni (mis. "go", "ai", "os")
    yang rawan bertabrakan dengan kata umum; nama simbolik seperti "c#" atau
    "c++" tetap diizinkan karena cukup khas."""
    term = normalize(term)
    if not term:
        return False
    if len(term) < 3 and term.isalnum():
        return False
    return re.search(r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])", text) is not None


class Penganalisis:
    """Pembungkus komponen terlatih beserta prosedur analisisnya."""

    def __init__(self, komponen):
        self.model = komponen["role_model"]
        self.profiles = komponen["profiles"]
        self.subrole_vectorizer = komponen["subrole_vectorizer"]
        self.profile_matrix = komponen["profile_matrix"]
        self.skill_weight_by_code = komponen["skill_weight_by_code"]
        self.all_skill_names = komponen["all_skill_names"]
        self.skill_aliases = komponen["skill_aliases"]
        self.acronym_to_skill = komponen["acronym_to_skill"]
        self.metadata = komponen.get("metadata", {})

    def tentukan_subrole(self, teks, peran):
        """Pilih sub-role dengan cosine similarity tertinggi, dibatasi pada
        okupasi yang berada di dalam peran hasil prediksi."""
        mask = (self.profiles["role_category"] == peran).values
        if not mask.any():
            return {"sub_role": None, "onet_code": None, "cosine_similarity": 0.0, "ranking": []}

        kemiripan = cosine_similarity(
            self.subrole_vectorizer.transform([teks]), self.profile_matrix[mask]
        ).ravel()

        kandidat = self.profiles[mask].reset_index(drop=True)
        urutan = np.argsort(-kemiripan)
        ranking = [
            {
                "sub_role": kandidat.iloc[i]["sub_role"],
                "onet_code": kandidat.iloc[i]["onet_code"],
                "cosine_similarity": round(float(kemiripan[i]), 4),
            }
            for i in urutan
        ]
        terbaik = ranking[0]
        return {
            "sub_role": terbaik["sub_role"],
            "onet_code": terbaik["onet_code"],
            "cosine_similarity": terbaik["cosine_similarity"],
            "ranking": ranking,
        }

    def ekstraksi_keterampilan(self, teks, onet_code=None):
        """Ambil keterampilan dari teks dengan mencocokkan kamus O*NET beserta
        aliasnya. Bobot diambil dari okupasi sub-role terpilih; keterampilan di
        luar daftar okupasi tersebut tetap ditampilkan dengan bobot dasar 1."""
        teks = normalize(teks)
        bobot_okupasi = self.skill_weight_by_code.get(onet_code, {})

        def bobot(skill):
            return int(bobot_okupasi.get(skill, 1))

        ditemukan = {}
        for skill in self.all_skill_names:
            alias = [skill] + self.skill_aliases.get(skill, [])
            if any(contains_term(teks, a) for a in alias):
                ditemukan[skill] = bobot(skill)

        for akronim, skill in self.acronym_to_skill.items():
            if contains_term(teks, akronim):
                ditemukan.setdefault(skill, bobot(skill))

        hasil = [{"skill": s, "bobot": w} for s, w in ditemukan.items()]
        hasil.sort(key=lambda item: (-item["bobot"], item["skill"].lower()))
        return hasil

    def analisis(self, deskripsi):
        """Analisis satu deskripsi pekerjaan secara utuh."""
        teks = str(deskripsi).strip()
        if len(teks) < MIN_KARAKTER:
            raise ValueError(f"Deskripsi pekerjaan minimal {MIN_KARAKTER} karakter.")

        peran = str(self.model.predict([teks])[0])

        # Margin keputusan dipakai untuk mengurutkan kandidat peran. Nilainya
        # bukan probabilitas, jadi tidak ditampilkan ke pengguna.
        margin = np.asarray(self.model.decision_function([teks])).ravel()
        peringkat_peran = sorted(
            (
                {"role": str(label), "margin": round(float(skor), 4)}
                for label, skor in zip(self.model.classes_, margin)
            ),
            key=lambda item: item["margin"],
            reverse=True,
        )

        subrole = self.tentukan_subrole(teks, peran)
        keterampilan = self.ekstraksi_keterampilan(teks, subrole["onet_code"])

        return {
            "role_utama": peran,
            "sub_role": subrole["sub_role"],
            "onet_code": subrole["onet_code"],
            "cosine_similarity": subrole["cosine_similarity"],
            "keterampilan": keterampilan,
            "top_3_sub_role": subrole["ranking"][:3],
            "top_3_margin_peran": peringkat_peran[:3],
        }


def cari_bundel(path_bundel=None):
    """Cari berkas bundel di lokasi yang lazim relatif terhadap berkas ini."""
    if path_bundel:
        return Path(path_bundel)

    dasar = Path(__file__).resolve().parent
    kandidat = [
        dasar / "job_role_onet_complete.joblib",
        dasar.parent / "svm_onet_bright_outlook_output" / "job_role_onet_complete.joblib",
        dasar / "svm_onet_bright_outlook_output" / "job_role_onet_complete.joblib",
    ]
    for berkas in kandidat:
        if berkas.exists():
            return berkas
    raise FileNotFoundError(
        "Berkas job_role_onet_complete.joblib tidak ditemukan. "
        "Jalankan notebook terlebih dahulu atau salin berkas tersebut ke folder aplikasi."
    )


def muat_penganalisis(path_bundel=None):
    """Muat bundel dari disk dan bungkus menjadi objek Penganalisis."""
    return Penganalisis(joblib.load(cari_bundel(path_bundel)))
