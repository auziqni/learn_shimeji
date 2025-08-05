# win32_move.py - Gerakkan window!

import win32gui
import time

def cari_notepad():
    """Cari window Notepad"""
    notepad = win32gui.FindWindow(None, "Untitled - Notepad")
    
    if notepad == 0:
        notepad = win32gui.FindWindow(None, "🎉 HELLO WIN32! 🎉")  # Coba nama lain juga
    
    if notepad == 0:
        print("❌ Buka Notepad dulu!")
        return None
        
    print("✅ Notepad ditemukan!")
    return notepad

def gerakkan_window(window_id):
    """Gerakkan window ke posisi berbeda"""
    print("🎬 Menggerakkan Notepad...")
    
    # Posisi-posisi yang akan dikunjungi
    posisi = [
        (100, 100),   # Kiri atas
        (400, 100),   # Kanan atas  
        (400, 300),   # Kanan bawah
        (100, 300),   # Kiri bawah
        (250, 200)    # Tengah
    ]
    
    for i, (x, y) in enumerate(posisi):
        print(f"  📍 Pindah ke posisi {i+1}: ({x}, {y})")
        
        # Pindahkan window ke posisi (x, y) dengan ukuran 300x200
        win32gui.SetWindowPos(
            window_id,  # Window yang mau dipindah
            0,          # Tidak perlu always on top
            x, y,       # Posisi baru
            300, 200,   # Ukuran window
            0           # Flag default
        )
        
        # Tunggu sebentar biar keliatan
        time.sleep(1)
    
    print("✅ Selesai menggerakkan window!")

def ubah_ukuran_window(window_id):
    """Ubah ukuran window jadi besar-kecil"""
    print("📏 Mengubah ukuran Notepad...")
    
    # Ukuran yang berbeda-beda
    ukuran = [
        (200, 150),   # Kecil
        (400, 300),   # Sedang
        (600, 450),   # Besar
        (300, 200)    # Normal
    ]
    
    for i, (width, height) in enumerate(ukuran):
        print(f"  📐 Ukuran {i+1}: {width} x {height}")
        
        # Ubah ukuran (posisi tetap di 250, 200)
        win32gui.SetWindowPos(
            window_id,
            0,
            250, 200,        # Posisi tetap
            width, height,   # Ukuran baru
            0
        )
        
        time.sleep(1)
    
    print("✅ Selesai mengubah ukuran!")

# Main program
if __name__ == "__main__":
    print("🎮 Program Gerakkan Window!")
    print("=" * 30)
    
    # Cari Notepad
    notepad = cari_notepad()
    
    if notepad:
        print("\n🚀 Demo dimulai dalam 2 detik...")
        time.sleep(2)
        
        # Demo 1: Gerakkan window
        gerakkan_window(notepad)
        
        print("\n⏳ Demo 2 dimulai dalam 2 detik...")
        time.sleep(2)
        
        # Demo 2: Ubah ukuran
        ubah_ukuran_window(notepad)
        
        print("\n🎉 Demo selesai!")
    
    print("\n🏁 Program selesai")