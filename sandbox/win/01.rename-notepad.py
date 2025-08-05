# win32_hello.py - PALING SIMPLE!

import win32gui

# 1. Cari window Notepad (buka Notepad dulu!)
def cari_notepad():
    print("🔍 Mencari window Notepad...")
    
    # Cari window dengan nama "Notepad"
    notepad_window = win32gui.FindWindow(None, "Untitled - Notepad")
    
    if notepad_window == 0:
        print("❌ Notepad tidak ditemukan!")
        print("💡 Buka Notepad dulu, lalu jalankan program ini lagi")
        return None
    
    print(f"✅ Notepad ditemukan! ID: {notepad_window}")
    return notepad_window

# 2. Ubah judul Notepad
def ubah_judul_notepad(window_id):
    print("📝 Mengubah judul Notepad...")
    
    # Ubah judul window
    win32gui.SetWindowText(window_id, "🎉 HELLO WIN32! 🎉")
    print("✅ Judul Notepad berubah!")

# Main program
if __name__ == "__main__":
    print("🚀 Program Win32 Paling Simple!")
    print("=" * 40)
    
    # Cari Notepad
    notepad = cari_notepad()
    
    if notepad:
        # Ubah judulnya
        ubah_judul_notepad(notepad)
        
        print("\n🎯 Berhasil!")
        print("👀 Lihat judul Notepad Anda!")
    
    print("\n🏁 Program selesai")