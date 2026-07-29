// deteksi.js
const uploadArea   = document.getElementById('uploadArea');
const previewArea  = document.getElementById('previewArea');
const btnAnalisis  = document.getElementById('btnAnalisis');
const inputFile    = document.getElementById('inputFile');     // input yang dikirim ke server
const inputKamera  = document.getElementById('inputKamera');    // input khusus kamera
const inputGaleri  = document.getElementById('inputGaleri');    // input khusus galeri
const previewImg   = document.getElementById('previewImg');
const namaFile     = document.getElementById('namaFile');

function showPreview(file) {
  const reader = new FileReader();
  reader.onload = function(e) {
    previewImg.src = e.target.result;
    namaFile.textContent = file.name;
    uploadArea.style.display = 'none';
    previewArea.style.display = 'block';
    btnAnalisis.disabled = false;
  };
  reader.readAsDataURL(file);
}

function hidePreview() {
  uploadArea.style.display = 'flex';
  previewArea.style.display = 'none';
  btnAnalisis.disabled = true;
  inputFile.value   = '';
  inputKamera.value = '';
  inputGaleri.value = '';
}

// Fungsi untuk "memindahkan" file dari input kamera/galeri ke inputFile (yang akan dikirim ke server)
function setFotoFromInput(sourceInput) {
  if (sourceInput.files && sourceInput.files[0]) {
    const file = sourceInput.files[0];
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    inputFile.files = dataTransfer.files;
    showPreview(file);
  }
}

// Saat user ambil foto dari kamera
inputKamera.addEventListener('change', function() {
  setFotoFromInput(inputKamera);
});

// Saat user pilih foto dari galeri
inputGaleri.addEventListener('change', function() {
  setFotoFromInput(inputGaleri);
});

// Drag & drop
uploadArea.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = '#F5C518';
  uploadArea.style.background = '#FFFDF0';
});
uploadArea.addEventListener('dragleave', () => {
  uploadArea.style.borderColor = '#D0D0CC';
  uploadArea.style.background = '#FAFAFA';
});
uploadArea.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadArea.style.borderColor = '#D0D0CC';
  uploadArea.style.background = '#FAFAFA';
  const file = e.dataTransfer.files[0];
  if (file && file.type.startsWith('image/')) {
    const dataTransfer = new DataTransfer();
    dataTransfer.items.add(file);
    inputFile.files = dataTransfer.files;
    showPreview(file);
  }
});