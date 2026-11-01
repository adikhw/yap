# yap (yet another project)

CLI kecil berbasis Python untuk memulai project baru dengan satu perintah. `yap python my_app` langsung membuat folder berisi `main.py`, `README.md`, `.gitignore`, `pyproject.toml`, repo git, dan `.venv`. `yap web my_web` membuat kerangka web statis yang siap dibuka lewat `python -m http.server`.

Tidak perlu lagi membuat folder dan file awal satu per satu setiap kali punya ide baru.

## Kebutuhan

- Python 3.10 atau lebih baru (`python3 --version`)
- `git` (opsional; kalau tidak ada, yap memberi peringatan dan tetap membuat project)
- Shell `zsh` (contoh di bawah), Linux atau macOS

yap hanya memakai library standar Python. Tidak ada dependensi yang perlu dipasang.

## Instalasi

1. Letakkan folder project ini di `~/yap` (atau di mana saja, sesuaikan path-nya).
2. Beri izin eksekusi pada `yap.py`:

   ```sh
   chmod +x ~/yap/yap.py
   ```

3. Pastikan `~/.local/bin` ada, lalu buat symlink bernama `yap`:

   ```sh
   mkdir -p ~/.local/bin
   ln -sfn ~/yap/yap.py ~/.local/bin/yap
   ```

4. Pastikan `~/.local/bin` ada di `PATH`. Kalau belum, tambahkan baris ini ke `~/.zshrc` (atau `~/.zshenv`):

   ```sh
   export PATH="$HOME/.local/bin:$PATH"
   ```

5. Buka terminal baru, lalu cek:

   ```sh
   which yap
   ```

   Hasilnya harus menunjuk ke `~/.local/bin/yap`. Karena berupa symlink, perubahan pada `yap.py` langsung terasa tanpa perlu install ulang.

## Cara pakai

```text
yap python <name> [--path <parent>] [--add <package> ...]
yap web <name> [--path <parent>]
```

- `<name>` hanya boleh berisi huruf, angka, `_`, dan `-`, serta diawali huruf atau angka.
- `--path <parent>` memilih folder induk tempat project dibuat. Path relatif dihitung dari home, path absolut (diawali `/` atau `~`) dipakai apa adanya. Folder induk dibuat kalau belum ada.
- `--add` hanya untuk `python`: memasang library ke `.venv` project tersebut, lalu menulis hasil `pip freeze` ke `requirements.txt`.

### Project Python

```sh
yap python my_app
```

Hasilnya:

```text
my_app/
├── main.py
├── README.md
├── .gitignore
├── pyproject.toml
├── requirements.txt     # hanya kalau memakai --add
└── .venv/
```

Contoh dengan library:

```sh
yap python my_app --add requests beautifulsoup4
```

Setelah selesai, jalankan project-nya:

```sh
cd ~/my_app
source .venv/bin/activate
python main.py
```

### Project web statis

```sh
yap web my_web
```

Hasilnya:

```text
my_web/
├── index.html
├── css/
│   └── style.css
├── js/
│   └── script.js
├── assets/
│   ├── favicon.svg
│   └── images/
│       └── .gitkeep
├── README.md
└── .gitignore
```

Project web tidak memakai venv, `pyproject.toml`, atau `--add`. Untuk melihat hasilnya:

```sh
cd ~/my_web
python -m http.server
```

Lalu buka <http://localhost:8000>.

### Memilih folder induk

```sh
yap python my_app --path projects/My_project
```

Perintah di atas membuat `~/projects/My_project/my_app`.

## Contoh tampilan

```text
$ yap python my_app
Creating python project 'my_app' in /home/user/my_app...

and yet another project... To continue type:
cd /home/user/my_app && source .venv/bin/activate
Happy Coding!
```

Pesan akhir sengaja berupa perintah yang bisa langsung di-copy-paste. yap tidak bisa memindahkan folder shell yang memanggilnya, jadi `cd` dan `source` tetap dilakukan oleh kamu.

## Exit code

| Kode | Arti |
|---|---|
| `0` | Berhasil |
| `1` | Gagal (folder sudah ada, perintah luar gagal, dibatalkan) |
| `2` | Cara pakai salah (argumen kurang, nama tidak valid, `web --add`) |

## Catatan

- yap tidak pernah menimpa atau menghapus folder yang sudah ada. Kalau gagal di tengah jalan, folder yang setengah jadi dibiarkan dan pesan errornya ditampilkan.
- Venv dibuat dari interpreter yang sedang menjalankan yap, dan pip dipanggil langsung lewat `.venv/bin/python`. Tidak perlu `activate` untuk memasang library.
- Isi `requirements.txt` berasal dari `pip freeze`, jadi dependency turunan ikut tercatat.
- Kalau `git` tidak ditemukan di `PATH`, yap memberi peringatan dan melanjutkan tanpa `git init`.
