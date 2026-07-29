-- skripsi.sql — Struktur Database roaddetection

CREATE DATABASE IF NOT EXISTS roadscan CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE roadscan;

-- Tabel users
CREATE TABLE IF NOT EXISTS users (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  nama_depan  VARCHAR(50) NOT NULL,
  nama_belakang VARCHAR(50) NOT NULL,
  email       VARCHAR(100) NOT NULL UNIQUE,
  password    VARCHAR(255) NOT NULL,
  role        ENUM('user', 'admin') DEFAULT 'user',
  aktif       TINYINT(1) DEFAULT 1,
  created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Tabel hasil_deteksi
CREATE TABLE IF NOT EXISTS hasil_deteksi (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  user_id          INT NOT NULL,
  foto_path        VARCHAR(255) NOT NULL,
  jenis_kerusakan  VARCHAR(50) NOT NULL,
  confidence       FLOAT NOT NULL,
  tanggal          DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Akun admin default (password: admin123)
INSERT INTO users (nama_depan, nama_belakang, email, password, role)
VALUES ('Admin', 'RoadScan', 'admin@roadscan.com',
'pbkdf2:sha256:260000$placeholder', 'admin')
ON DUPLICATE KEY UPDATE email = email;
