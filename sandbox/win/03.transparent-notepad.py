# win32_transparent.py - Buat window transparan!

import win32gui
import win32con
import time

def cari_notepad():
    """Cari window Notepad"""
    notepad = win32gui.FindWindow(None, "Untitled - Notepad")
    
    if notepad == 0:
        notepad = win32gui.FindWindow(None, "🎉 HELLO WIN32! 🎉")
    
    if notepad == 0:
        print("❌ Buka Notepad dulu!")
        print("💡 Buka Notepad, lalu jalankan program ini")
        return None
        
    print("✅ Notepad ditemukan!")
    return notepad

def buat_transparan(window_id):
    """Buat window jadi transparan"""
    print("✨ Membuat Notepad transparan...")
    
    # Langkah 1: Set window jadi "layered window"
    # (syarat wajib untuk transparansi)
    print("  🔧 Step 1: Setting layered window...")
    
    # PERBAIKAN: Dapatkan style saat ini, lalu tambahkan layered
    current_style = win32gui.GetWindowLong(window_id, win32con.GWL_EXSTYLE)
    new_style = current_style | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(window_id, win32con.GWL_EXSTYLE, new_style)
    
    # Langkah 2: Set tingkat transparansi
    print("  🔧 Step 2: Setting transparansi...")
    
    # Angka transparansi:
    # 255 = tidak transparan (normal)
    # 128 = setengah transparan  
    # 0   = tidak terlihat sama sekali
    
    transparency = 128  # 50% transparan
    
    win32gui.SetLayeredWindowAttributes(
        window_id,              # Window yang mau dibuat transparan
        0,                      # Warna (tidak dipakai untuk alpha)
        transparency,           # Tingkat transparansi (0-255)
        win32con.LWA_ALPHA     # Mode alpha (semi transparan)
    )
    
    print(f"✅ Notepad sekarang {transparency}/255 transparan!")

def demo_transparansi(window_id):
    """Demo berbagai tingkat transparansi"""
    print("🎬 Demo berbagai tingkat transparansi...")
    
    # PERBAIKAN: Setup layered window dulu sebelum demo
    print("  🔧 Setup layered window untuk demo...")
    current_style = win32gui.GetWindowLong(window_id, win32con.GWL_EXSTYLE)
    new_style = current_style | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(window_id, win32con.GWL_EXSTYLE, new_style)
    
    # Berbagai tingkat transparansi
    levels = [
        (255, "Normal (tidak transparan)"),
        (200, "Sedikit transparan"),
        (150, "Transparan sedang"),
        (100, "Sangat transparan"),
        (50,  "Hampir tidak terlihat"),
        (255, "Kembali normal")
    ]
    
    for level, desc in levels:
        print(f"  👀 {desc} (level: {level})")
        
        # Set transparansi
        win32gui.SetLayeredWindowAttributes(
            window_id, 0, level, win32con.LWA_ALPHA
        )
        
        # Tunggu biar keliatan perubahannya
        time.sleep(2)
    
    print("✅ Demo transparansi selesai!")

def buat_always_on_top(window_id):
    """Buat window selalu di atas"""
    print("⬆️ Membuat Notepad selalu di atas...")
    
    win32gui.SetWindowPos(
        window_id,                  # Window yang mau diatur
        win32con.HWND_TOPMOST,     # Set sebagai "always on top"
        0, 0, 0, 0,                # Posisi dan ukuran (diabaikan)
        win32con.SWP_NOMOVE | win32con.SWP_NOSIZE  # Jangan ubah posisi/ukuran
    )
    
    print("✅ Notepad sekarang selalu di atas!")

# Main program  
if __name__ == "__main__":
    print("✨ Program Transparansi Simple!")
    print("=" * 35)
    
    # Cari Notepad
    notepad = cari_notepad()
    
    if notepad:
        print("\n📋 Instruksi:")
        print("1. Pastikan ada window lain di belakang Notepad")
        print("2. Perhatikan perubahan transparansi Notepad")
        
        input("\nTekan Enter untuk mulai...")
        
        # Demo 1: Always on top
        buat_always_on_top(notepad)
        
        print("\n⏳ Mulai demo transparansi dalam 2 detik...")
        time.sleep(2)
        
        # Demo 2: Transparansi
        demo_transparansi(notepad)
        
        print("\n🎉 Demo selesai!")
        print("💡 Sekarang Anda sudah tahu cara buat window transparan!")
    
    print("\n🏁 Program selesai")