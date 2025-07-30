# project Shimeji

## Panduan

### First Setup

Panduan ini hanya dilakukan sekali saat pertama kali membuat project baru.

- **Creating env**

  ```bash
  # Windows
  python -m venv env

  # Linux/Mac
  python3 -m venv env
  ```

- **Install dep**

  Windows

  ```bash

  env\Scripts\activate
  pip install package_name_here
  ```

  Linux/Mac

  ```bash
  source env/Scripts/activate
  pip install package_name_here
  ```

- **Freeze**

  ```bash
  pip freeze > requirements.txt
  ```

- **Git init**

  ```bash
  git init
  ```

- **Creating git ignore**

  ```bash
  # Buat file .gitignore dan tambahkan:
  env/
  __pycache__/
  *.pyc
  *.pyo
  *.pyd
  .Python
  *.so
  .coverage
  .pytest_cache/
  ```

- **Remote**

  ```bash
  git remote add origin https://github.com/username/repository-name.git
  ```

- **Push**
  ```bash
  git add .
  git commit -m "Initial commit"
  git push -u origin main
  ```

### Clone

#### First Clone

Panduan ini hanya dilakukan sekali saat pertama kali clone repository.

- **Clone**

  ```bash
  git clone https://github.com/username/repository-name.git
  cd repository-name
  ```

- **Env**

  ```bash
  # Windows
  python -m venv env

  # Linux/Mac
  python3 -m venv env
  ```

- **Install requirement**

  ```bash
  # Windows
  env\Scripts\activate
  pip install -r requirements.txt

  # Linux/Mac
  source env/Scripts/activate
  pip install -r requirements.txt
  ```

#### Update

- **Pull normal**

  ```bash
  git pull origin main
  ```

- **Pull force** (⚠️ **WARNING**: Ini akan menghapus semua perubahan local yang belum di-commit)
  ```bash
  git fetch origin
  git reset --hard origin/main
  ```

### Penggunaan

Panduan untuk menjalankan project setelah repository sudah di-clone.

- **Activate env**

  ```bash
  # Windows
  env\Scripts\activate

  # Linux/Mac
  source env/Scripts/activate
  ```

- **Running main.py**
  ```bash
  python main.py
  ```
