from bot_engine import AnomalyHunterBot

if __name__ == "__main__":
    # Inisialisasi bot
    bot = AnomalyHunterBot()
    
    try:
        # Jalankan satu iterasi (bisa dimasukkan dalam loop untuk operasi kontinu)
        bot.run_single_iteration()
        
        print("\n" + "="*50)
        print("ANOMALY HUNTER PRO - INISIALISASI SUKSES")
        print("="*50)
        print("✓ Multi-source data redundancy diimplementasikan")
        print("✓ Database SQLite diinisialisasi")
        print("✓ Error handling dan logging dikonfigurasi")
        print("✓ Siap untuk implementasi anomaly detection")
        print("="*50)
        
    except Exception as e:
        print(f"Error selama inisialisasi: {e}")
        print("Silakan cek API keys dan koneksi internet Anda")
