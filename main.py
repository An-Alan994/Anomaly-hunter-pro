import time
from bot_engine import AnomalyHunterBot

def main():
    # Inisialisasi bot
    bot = AnomalyHunterBot()
    
    print("=" * 60)
    print("ANOMALY HUNTER PRO - LONG ONLY THE ANOMALY STRATEGY")
    print("=" * 60)
    print("Strategi: Mencari coin hijau di lautan merah")
    print("Provider: CoinGecko, KuCoin, CryptoPanic")
    print("Fiturs: Redundancy Check, Risk Management, Anomaly Detection")
    print("=" * 60)
    
    try:
        # Jalankan bot dalam loop
        iteration_count = 0
        while True:
            iteration_count += 1
            print(f"\n🔄 Iteration #{iteration_count}")
            print("-" * 40)
            
            bot.run_single_iteration()
            
            # Tunggu 5 menit sebelum iterasi berikutnya
            print("⏳ Waiting 5 minutes for next iteration...")
            time.sleep(300)
            
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("=" * 60)
        print("ANOMALY HUNTER PRO - SHUTDOWN COMPLETE")
        print("=" * 60)

if __name__ == "__main__":
    main()
