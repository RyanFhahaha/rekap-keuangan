from flask import Flask, render_template_string, request, redirect, url_for
import json, os
from datetime import datetime

app = Flask(__name__)
DATA_FILE = "data_keuangan.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"transaksi": []}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

HTML = """<!DOCTYPE html><html lang="id"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Rekap Keuangan</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Segoe UI',sans-serif;background:#f0f4f8;color:#333}
header{background:#2563eb;color:white;padding:20px 40px}
header h1{font-size:1.8rem}
header p{opacity:.85;font-size:.95rem}
.container{max-width:900px;margin:30px auto;padding:0 20px}
.summary{display:grid;grid-template-columns:repeat(3,1fr);gap:16px;margin-bottom:30px}
.card{background:white;border-radius:12px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.07)}
.card h3{font-size:.85rem;color:#888;margin-bottom:6px;text-transform:uppercase}
.card .amount{font-size:1.5rem;font-weight:700}
.pemasukan .amount{color:#16a34a}
.pengeluaran .amount{color:#dc2626}
.saldo .amount{color:#2563eb}
.section{background:white;border-radius:12px;padding:24px;box-shadow:0 2px 8px rgba(0,0,0,.07);margin-bottom:30px}
.section h2{margin-bottom:16px;font-size:1.1rem}
.form-row{display:grid;grid-template-columns:1fr 1fr 1fr 1fr auto;gap:12px;align-items:end}
label{display:block;font-size:.82rem;color:#666;margin-bottom:4px}
input,select{width:100%;padding:8px 12px;border:1px solid #ddd;border-radius:8px;font-size:.9rem}
button{padding:9px 20px;background:#2563eb;color:white;border:none;border-radius:8px;cursor:pointer;font-size:.9rem}
button:hover{background:#1d4ed8}
table{width:100%;border-collapse:collapse}
th{background:#f8fafc;padding:10px 14px;text-align:left;font-size:.82rem;color:#888;text-transform:uppercase;border-bottom:2px solid #e5e7eb}
td{padding:12px 14px;border-bottom:1px solid #f1f5f9;font-size:.9rem}
.badge{padding:3px 10px;border-radius:20px;font-size:.78rem;font-weight:600}
.badge-pemasukan{background:#dcfce7;color:#16a34a}
.badge-pengeluaran{background:#fee2e2;color:#dc2626}
.empty{text-align:center;color:#aaa;padding:40px}
.del{background:#fee2e2;color:#dc2626;padding:4px 10px;font-size:.78rem}
</style></head><body>
<header><h1>Rekap Keuangan</h1><p>Catat dan pantau pemasukan serta pengeluaran Anda</p></header>
<div class="container">
<div class="summary">
<div class="card pemasukan"><h3>Total Pemasukan</h3><div class="amount">Rp {{ "{:,.0f}".format(masuk) }}</div></div>
<div class="card pengeluaran"><h3>Total Pengeluaran</h3><div class="amount">Rp {{ "{:,.0f}".format(keluar) }}</div></div>
<div class="card saldo"><h3>Saldo</h3><div class="amount">Rp {{ "{:,.0f}".format(saldo) }}</div></div>
</div>
<div class="section"><h2>Tambah Transaksi</h2>
<form method="POST" action="/tambah"><div class="form-row">
<div><label>Tanggal</label><input type="date" name="tanggal" value="{{ today }}" required></div>
<div><label>Keterangan</label><input type="text" name="keterangan" placeholder="Misal: Gaji, Makan..." required></div>
<div><label>Jumlah (Rp)</label><input type="number" name="jumlah" placeholder="0" min="1" required></div>
<div><label>Jenis</label><select name="jenis"><option value="pemasukan">Pemasukan</option><option value="pengeluaran">Pengeluaran</option></select></div>
<div><label>&nbsp;</label><button type="submit">Simpan</button></div>
</div></form></div>
<div class="section"><h2>Riwayat Transaksi</h2>
{% if data %}
<table><thead><tr><th>Tanggal</th><th>Keterangan</th><th>Jenis</th><th>Jumlah</th><th></th></tr></thead>
<tbody>{% for t in data|reverse %}<tr>
<td>{{ t.tanggal }}</td><td>{{ t.keterangan }}</td>
<td><span class="badge badge-{{ t.jenis }}">{{ t.jenis.capitalize() }}</span></td>
<td>Rp {{ "{:,.0f}".format(t.jumlah) }}</td>
<td><form method="POST" action="/hapus/{{ loop.revindex0 }}" style="display:inline">
<button class="del" onclick="return confirm('Hapus?')">Hapus</button></form></td>
</tr>{% endfor %}</tbody></table>
{% else %}<div class="empty">Belum ada transaksi. Tambahkan transaksi pertama Anda!</div>{% endif %}
</div></div></body></html>"""

@app.route("/")
def index():
    data = load_data()
    t = data["transaksi"]
    masuk = sum(x["jumlah"] for x in t if x["jenis"] == "pemasukan")
    keluar = sum(x["jumlah"] for x in t if x["jenis"] == "pengeluaran")
    return render_template_string(HTML, data=t, masuk=masuk, keluar=keluar,
        saldo=masuk-keluar, today=datetime.now().strftime("%Y-%m-%d"))

@app.route("/tambah", methods=["POST"])
def tambah():
    data = load_data()
    data["transaksi"].append({
        "tanggal": request.form["tanggal"],
        "keterangan": request.form["keterangan"],
        "jumlah": float(request.form["jumlah"]),
        "jenis": request.form["jenis"]
    })
    save_data(data)
    return redirect(url_for("index"))

@app.route("/hapus/<int:idx>", methods=["POST"])
def hapus(idx):
    data = load_data()
    real = len(data["transaksi"]) - 1 - idx
    if 0 <= real < len(data["transaksi"]):
        data["transaksi"].pop(real)
        save_data(data)
    return redirect(url_for("index"))

if __name__ == "__main__":
    print("=" * 50)
    print("  Rekap Keuangan berjalan!")
    print("  Buka: http://localhost:5000")
    print("=" * 50)
    app.run(debug=False, port=5000)
