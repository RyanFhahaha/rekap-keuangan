import streamlit as st
import pandas as pd
from io import BytesIO
import os

st.set_page_config(page_title="Rekap Keuangan Event", layout="wide")
st.title("📊 Rekap Keuangan Event — JIExpo")

tab1, tab2, tab3 = st.tabs(["✏️ Input Manual", "📁 Upload CSV", "🔴 Live Google Sheets"])

with tab1:
    st.subheader("Input Transaksi Manual")
    CSV_FILE = "transaksi.csv"
    if not os.path.exists(CSV_FILE):
        pd.DataFrame(columns=["tanggal","kategori","keterangan","jumlah","nama"]).to_csv(CSV_FILE, index=False)
    with st.form("form_input"):
        col1, col2 = st.columns(2)
        with col1:
            tanggal    = st.date_input("Tanggal")
            kategori   = st.selectbox("Kategori", ["Catering","Dekorasi","Transportasi","Vendor","Lainnya"])
            keterangan = st.text_input("Keterangan")
        with col2:
            jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=10000)
            nama   = st.text_input("Nama Pencatat")
        submit = st.form_submit_button("💾 Simpan Transaksi")
        if submit:
            baru = pd.DataFrame([[tanggal, kategori, keterangan, jumlah, nama]], columns=["tanggal","kategori","keterangan","jumlah","nama"])
            baru.to_csv(CSV_FILE, mode="a", header=False, index=False)
            st.success("✅ Transaksi tersimpan!")
    st.divider()
    st.subheader("Data Tersimpan")
    if os.path.exists(CSV_FILE):
        df_lokal = pd.read_csv(CSV_FILE)
        if not df_lokal.empty:
            df_lokal["jumlah"] = pd.to_numeric(df_lokal["jumlah"], errors="coerce").fillna(0)
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Transaksi", len(df_lokal))
            col2.metric("Total Pengeluaran", f"Rp {df_lokal['jumlah'].sum():,.0f}")
            col3.metric("Rata-rata", f"Rp {df_lokal['jumlah'].mean():,.0f}")
            rekap = df_lokal.groupby("kategori")["jumlah"].sum().reset_index()
            rekap.columns = ["Kategori", "Total (Rp)"]
            st.dataframe(rekap, use_container_width=True)
            st.bar_chart(rekap.set_index("Kategori"))
            st.dataframe(df_lokal, use_container_width=True)
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                df_lokal.to_excel(writer, sheet_name="Detail", index=False)
                rekap.to_excel(writer, sheet_name="Rekap", index=False)
            st.download_button("📥 Download Excel", output.getvalue(), "laporan_manual.xlsx")
        else:
            st.info("Belum ada transaksi tersimpan.")

with tab2:
    st.subheader("Upload CSV dari Google Sheets")
    st.caption("Cara export: Google Sheets → File → Download → CSV")
    file = st.file_uploader("Upload file CSV", type=["csv"])
    if file:
        df = pd.read_csv(file)
        if list(df.columns) != ["tanggal","kategori","keterangan","jumlah","nama"]:
            try:
                df.columns = ["tanggal","kategori","keterangan","jumlah","nama"]
            except:
                st.error("Format kolom tidak cocok.")
                st.stop()
        df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce").fillna(0)
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Transaksi", len(df))
        col2.metric("Total Pengeluaran", f"Rp {df['jumlah'].sum():,.0f}")
        col3.metric("Rata-rata", f"Rp {df['jumlah'].mean():,.0f}")
        rekap = df.groupby("kategori")["jumlah"].sum().reset_index()
        rekap.columns = ["Kategori", "Total (Rp)"]
        st.dataframe(rekap, use_container_width=True)
        st.bar_chart(rekap.set_index("Kategori"))
        st.dataframe(df, use_container_width=True)
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name="Detail", index=False)
            rekap.to_excel(writer, sheet_name="Rekap", index=False)
        st.download_button("📥 Download Laporan Excel", output.getvalue(), "laporan_csv.xlsx")

with tab3:
    st.subheader("Live dari Google Sheets (Otomatis)")
    st.caption("Data refresh otomatis tiap 60 detik.")
    SHEET_NAME = "transaksi-jiexpo"
    if "gcp_service_account" not in st.secrets:
        st.warning("⚠️ Google credentials belum dikonfigurasi di Streamlit Secrets.")
        st.markdown("""
**Cara setup Streamlit Secrets:**
1. Buka [share.streamlit.io](https://share.streamlit.io) → pilih app kamu
2. Klik **Settings** → **Secrets**
3. Paste isi file `credentials.json` dalam format ini:

```toml
[gcp_service_account]
type = "service_account"
project_id = "your-project-id"
private_key_id = "your-key-id"
private_key = "-----BEGIN RSA PRIVATE KEY-----\\\\n...\\\\n-----END RSA PRIVATE KEY-----\\\\n"
client_email = "rekap-keuangan-sa@your-project.iam.gserviceaccount.com"
client_id = "your-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account"
```

4. Klik **Save** → app restart otomatis
        """)
    else:
        import gspread
        from google.oauth2.service_account import Credentials

        @st.cache_resource
        def connect_sheets():
            scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(dict(st.secrets["gcp_service_account"]), scopes=scopes)
            return gspread.authorize(creds)

        @st.cache_data(ttl=60)
        def load_data():
            client = connect_sheets()
            sheet = client.open(transaksi-jiexpo).sheet1
            return pd.DataFrame(sheet.get_all_records())

        if st.button("🔄 Refresh Data Sekarang"):
            st.cache_data.clear()

        try:
            df = load_data()
            if df.empty:
                st.info("Sheet masih kosong.")
            else:
                df.columns = ["tanggal","kategori","keterangan","jumlah","nama"]
                df["jumlah"] = pd.to_numeric(df["jumlah"], errors="coerce").fillna(0)
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Transaksi", len(df))
                col2.metric("Total Pengeluaran", f"Rp {df['jumlah'].sum():,.0f}")
                col3.metric("Rata-rata", f"Rp {df['jumlah'].mean():,.0f}")
                kategori_filter = st.multiselect("Filter Kategori", df["kategori"].unique(), default=list(df["kategori"].unique()))
                df_filtered = df[df["kategori"].isin(kategori_filter)]
                rekap = df_filtered.groupby("kategori")["jumlah"].sum().reset_index()
                rekap.columns = ["Kategori", "Total (Rp)"]
                st.dataframe(rekap, use_container_width=True)
                st.bar_chart(rekap.set_index("Kategori"))
                st.dataframe(df_filtered, use_container_width=True)
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df_filtered.to_excel(writer, sheet_name="Detail", index=False)
                    rekap.to_excel(writer, sheet_name="Rekap", index=False)
                st.download_button("📥 Download Laporan Excel", output.getvalue(), "laporan_live.xlsx")
        except Exception as e:
            st.error(f"Gagal connect ke Google Sheets: {e}")
