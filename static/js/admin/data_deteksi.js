function showModal(fotoPath, gradcamPath, namaFile, namaUser, jenisKerusakan, tanggal) {
  document.getElementById('modalFotoImg').src = fotoPath || '';
  document.getElementById('modalNamaFile').textContent = namaFile || '-';
  document.getElementById('modalNamaUser').textContent = namaUser || '-';
  document.getElementById('modalJenis').textContent = jenisKerusakan || '-';
  document.getElementById('modalTanggal').textContent = tanggal || '-';
  document.getElementById('modalDownloadBtn').href = fotoPath || '#';

  // Grad-CAM
  if (gradcamPath) {
    document.getElementById('modalGradcamImg').src = gradcamPath;
    document.getElementById('modalDownloadGradcam').href = gradcamPath;
    document.getElementById('gradcamWrap').style.display = 'block';
  } else {
    document.getElementById('gradcamWrap').style.display = 'none';
  }

  document.getElementById('modalOverlay').style.display = 'flex';
}
function hideModal() {
  document.getElementById('modalOverlay').style.display = 'none';
}