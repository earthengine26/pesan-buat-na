from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# --- KONFIGURASI ---
ROUTER_IP = "http://192.168.0.1"
PASSWORD_ADMIN = "TULIS_PASSWORD_ADMIN_DISINI" # Ganti dengan password login router Anda
# Daftar MAC Address perangkat resmi (HP/Laptop Anda) agar tidak dikira pencuri
PERANGKAT_RESMI = ["AA:BB:CC:DD:EE:FF", "11:22:33:44:55:66"] 

def setup_driver():
    options = webdriver.ChromeOptions()
    # options.add_argument('--headless') # Hapus tanda pagar jika ingin berjalan tanpa muncul jendela browser
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

def login(driver):
    print("Mencoba login ke router...")
    driver.get(ROUTER_IP)
    try:
        # Menunggu kolom password muncul (ID 'pc-login-password' umum di TL-WR840N baru)
        pw_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pc-login-password"))
        )
        pw_field.send_keys(PASSWORD_ADMIN)
        driver.find_element(By.ID, "pc-login-btn").click()
        print("Login Berhasil!")
        time.sleep(2)
    except Exception as e:
        print(f"Gagal login: {e}")

def cek_pencuri(driver):
    print("\n--- Memeriksa Daftar Perangkat Terhubung ---")
    # Navigasi ke menu DHCP Client List
    driver.get(f"{ROUTER_IP}/userRpm/DhcpClientListRpm.htm")
    time.sleep(2)
    
    # Mengambil semua baris di tabel client
    rows = driver.find_elements(By.CLASS_NAME, "tp-table-row") # Sesuaikan class jika berbeda
    
    pencuri_ditemukan = False
    for row in rows:
        text = row.text
        if text:
            is_resmi = any(mac.lower() in text.lower() for mac in PERANGKAT_RESMI)
            if not is_resmi:
                print(f"[PERINGATAN] Perangkat Asing Terdeteksi: {text}")
                pencuri_ditemukan = True
            else:
                print(f"[AMAN] Perangkat Resmi: {text}")
    
    if not pencuri_ditemukan:
        print("Tidak ada perangkat asing.")

def reboot(driver):
    print("\nMelakukan Reboot...")
    driver.get(f"{ROUTER_IP}/userRpm/SysRebootRpm.htm")
    reboot_btn = driver.find_element(By.ID, "reboot")
    reboot_btn.click()
    driver.switch_to.alert.accept()
    print("Perintah Reboot terkirim. Koneksi akan terputus sementara.")

# --- EKSEKUSI UTAMA ---
if __name__ == "__main__":
    my_driver = setup_driver()
    try:
        login(my_driver)
        
        # Jalankan fungsi sesuai kebutuhan:
        cek_pencuri(my_driver)
        
        # Buka tanda pagar di bawah jika ingin langsung reboot
        # reboot(my_driver) 
        
    finally:
        time.sleep(5)
        my_driver.quit()