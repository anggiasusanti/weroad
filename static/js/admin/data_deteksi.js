// data_deteksi.js
function showModal(fotoPath, namaFile, namaUser, jenisKerusakan, tanggal) {
  document.getElementById('modalFotoImg').src = fotoPath || '';
  document.getElementById('modalNamaFile').textContent = namaFile || '-';
  document.getElementById('modalNamaUser').textContent = namaUser || '-';
  document.getElementById('modalJenis').textContent = jenisKerusakan || '-';
  document.getElementById('modalTanggal').textContent = tanggal || '-';
  document.getElementById('modalDownloadBtn').href = fotoPath || '#';
  document.getElementById('modalOverlay').style.display = 'flex';
}
function hideModal() {
  document.getElementById('modalOverlay').style.display = 'none';
}
