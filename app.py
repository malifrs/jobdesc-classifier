"""Antarmuka web JobDesc Classifier.

Aplikasi berjalan tanpa penyimpanan data. Setiap permintaan diproses di memori
lalu hasilnya langsung ditampilkan, tanpa disimpan ke basis data maupun berkas.
"""

import time
from html import escape

import streamlit as st

from analisis import MIN_KARAKTER, muat_penganalisis

st.set_page_config(page_title="JobDesc Classifier", layout="wide")

WARNA = """
<style>
    :root {
        --hijau: #0A6B4E;
        --hijau-tua: #0F4A38;
        --latar: #F1F6F3;
        --panel: #E7F0EA;
        --chip: #CDE7D8;
        --abu: #5B6B63;
    }
    .stApp { background: var(--latar); }
    header[data-testid="stHeader"], #MainMenu, footer { display: none; }
    .block-container { padding: 2.5rem 4rem 4rem; max-width: 1500px; }

    .bilah { display: flex; align-items: center; gap: 3rem; margin-bottom: 3.5rem; }
    .merek { font-size: 1.25rem; font-weight: 700; color: var(--hijau); }
    .menu {
        font-size: .95rem; font-weight: 600; color: var(--hijau);
        border-bottom: 2px solid var(--hijau); padding-bottom: .25rem;
    }

    .judul { font-size: 2rem; font-weight: 600; color: #1B2A22; margin-bottom: .75rem; }
    .keterangan { font-size: 1rem; color: var(--abu); line-height: 1.6; margin-bottom: 2rem; }

    /* Panel masukan */
    div[data-testid="stTextArea"] textarea {
        background: var(--panel); border: none; border-radius: 12px;
        min-height: 320px; font-size: 1rem; color: #1B2A22; padding: 1.25rem;
    }
    div[data-testid="stTextArea"] textarea::placeholder { color: #7C8C84; }
    div[data-testid="stTextArea"] label { display: none; }

    /* Selector memakai keturunan, bukan anak langsung, karena Streamlit
       membungkus tombol di dalam div tambahan. */
    div[data-testid="stButton"] button, .stButton button {
        background: var(--hijau); color: #fff; border: none; border-radius: 10px;
        padding: .85rem 1rem; font-size: 1.05rem; font-weight: 600; min-height: 3rem;
    }
    div[data-testid="stButton"] button:hover, .stButton button:hover {
        background: var(--hijau-tua); color: #fff; border: none;
    }
    div[data-testid="stButton"] button p, .stButton button p {
        font-size: 1.05rem; font-weight: 600;
    }

    /* Kartu keluaran */
    .kartu-utama {
        background: #fff; border-radius: 14px; padding: 2rem 2.25rem; margin-bottom: 1.5rem;
    }
    .label-kecil {
        font-size: .75rem; letter-spacing: .12em; text-transform: uppercase;
        color: var(--abu); margin-bottom: .6rem;
    }
    .peran { font-size: 2.5rem; font-weight: 700; color: var(--hijau); line-height: 1.1; }
    .durasi { margin-top: .9rem; font-size: .8rem; color: var(--abu); }

    .kartu { background: var(--panel); border-radius: 14px; padding: 1.5rem 1.75rem; margin-bottom: 1.25rem; }
    .kartu-judul { font-size: 1rem; font-weight: 700; color: #1B2A22; margin-bottom: 1rem; }
    .isi { font-size: 1.05rem; color: #1B2A22; }

    .chip {
        display: inline-block; background: var(--chip); color: var(--hijau-tua);
        border-radius: 999px; padding: .35rem .8rem; margin: 0 .4rem .5rem 0; font-size: .85rem;
    }
    .kosong { color: var(--abu); font-style: italic; }
</style>
"""
st.markdown(WARNA, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading model...")
def ambil_penganalisis():
    """Bundel dimuat sekali lalu dipakai ulang untuk seluruh permintaan."""
    return muat_penganalisis()


st.markdown(
    '<div class="bilah"><span class="merek">JobDesc Classifier</span>'
    '<span class="menu">Dashboard</span></div>',
    unsafe_allow_html=True,
)

kiri, kanan = st.columns(2, gap="large")

with kiri:
    st.markdown('<div class="judul">Job description classifier</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="keterangan">Paste your raw job description text below. Our model will '
        "decompose the requirements and classify the career archetype.</div>",
        unsafe_allow_html=True,
    )
    teks = st.text_area(
        "Job description",
        placeholder="Input your job description here...",
        key="masukan",
    )
    # width="stretch" perlu disebut eksplisit; bawaan Streamlit adalah "content"
    # sehingga tombol menyusut mengikuti panjang teksnya.
    ditekan = st.button("Predict", width="stretch")

if ditekan:
    bersih = teks.strip()
    if not bersih:
        st.session_state["hasil"] = None
        st.session_state["pesan"] = "The input field is empty. Please enter a job description first."
    elif len(bersih) < MIN_KARAKTER:
        st.session_state["hasil"] = None
        st.session_state["pesan"] = (
            f"The job description is too short. Please enter at least {MIN_KARAKTER} characters "
            f"(currently {len(bersih)})."
        )
    else:
        # Waktu diukur hanya pada proses analisis, setelah model berada di memori,
        # agar angka yang ditampilkan mencerminkan beban komputasi per lowongan.
        mulai = time.perf_counter()
        st.session_state["hasil"] = ambil_penganalisis().analisis(bersih)
        st.session_state["durasi"] = time.perf_counter() - mulai
        st.session_state["pesan"] = None

with kanan:
    pesan = st.session_state.get("pesan")
    hasil = st.session_state.get("hasil")

    if pesan:
        st.warning(pesan)
    elif hasil:
        durasi = st.session_state.get("durasi")
        catatan = (
            f'<div class="durasi">Processed in {durasi:.2f} seconds</div>'
            if durasi is not None
            else ""
        )
        st.markdown(
            '<div class="kartu-utama">'
            '<div class="label-kecil">Predicted job category</div>'
            f'<div class="peran">{escape(hasil["role_utama"])}</div>'
            f"{catatan}"
            "</div>",
            unsafe_allow_html=True,
        )

        subrole = hasil["sub_role"] or "Not available"
        st.markdown(
            '<div class="kartu"><div class="kartu-judul">Sub-role</div>'
            f'<div class="isi">{escape(subrole)}</div></div>',
            unsafe_allow_html=True,
        )

        # Keterampilan sudah terurut menurut bobot; angka bobotnya tidak ditampilkan.
        if hasil["keterampilan"]:
            chip = "".join(
                f'<span class="chip">{escape(k["skill"])}</span>' for k in hasil["keterampilan"]
            )
        else:
            chip = '<span class="kosong">No O*NET skills were recognised in this text.</span>'
        st.markdown(
            f'<div class="kartu"><div class="kartu-judul">Skills</div>{chip}</div>',
            unsafe_allow_html=True,
        )
