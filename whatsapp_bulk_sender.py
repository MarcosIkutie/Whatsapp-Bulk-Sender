import os
import sys
import subprocess
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


def get_chrome_version():
    """Obtém a versão principal do Chrome instalado (ex: '137' para 137.0.7151.123)"""
    try:
        # Windows
        if sys.platform == 'win32':
            path = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
            version = subprocess.check_output(
                f'wmic datafile where name="{path}" get Version /value',
                shell=True
            ).decode().strip().split('=')[1]
            return version.split('.')[0]  # Retorna a versão principal
        # MacOS
        elif sys.platform == 'darwin':
            version = subprocess.check_output(
                '/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version',
                shell=True
            ).decode().strip().split()[-2]
            return version.split('.')[0]
        # Linux
        else:
            version = subprocess.check_output(
                'google-chrome --version',
                shell=True
            ).decode().strip().split()[-1]
            return version.split('.')[0]
    except Exception:
        return None


def whatsapp_bulk_sender():
    """Função principal para envio de mensagens em massa"""
    try:
        # Configuração do driver com detecção de versão
        chrome_version = get_chrome_version()

        if chrome_version:
            service = Service(ChromeDriverManager(version=chrome_version).install())
        else:
            service = Service(ChromeDriverManager().install())

        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")

        driver = webdriver.Chrome(service=service, options=options)
        driver.get("https://web.whatsapp.com")
        input("Escaneie o QR Code e pressione Enter...")

        # Carregar números e mensagem da interface
        numbers = entry_numbers.get("1.0", "end-1c").splitlines()
        message = entry_message.get("1.0", "end-1c")

        if not numbers or not message:
            messagebox.showerror("Erro", "Preencha números e mensagem!")
            return

        for number in numbers:
            try:
                if not number.strip(): continue

                driver.get(f"https://web.whatsapp.com/send?phone={number}&text={message}")

                # Aguardar carregamento da caixa de mensagem
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
                )

                # Aguardar botão de enviar
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, '//span[@data-icon="send"]'))
                ).click()

                time.sleep(3)  # Evitar bloqueio
                log(f"Mensagem enviada para: {number}")

            except Exception as e:
                log(f"Falha no número {number}: {str(e)}")
                time.sleep(2)

        log("Processo completo!")
        messagebox.showinfo("Sucesso", "Mensagens enviadas com sucesso!")

    except Exception as e:
        log(f"ERRO CRÍTICO: {str(e)}")
        messagebox.showerror("Erro", f"Falha no sistema: {str(e)}")
    finally:
        try:
            driver.quit()
        except:
            pass


def browse_file():
    """Abre um arquivo TXT com números"""
    filepath = filedialog.askopenfilename(filetypes=[("Arquivos TXT", "*.txt")])
    if filepath:
        with open(filepath, 'r', encoding='utf-8') as f:
            entry_numbers.delete("1.0", tk.END)
            entry_numbers.insert(tk.END, f.read())


def log(message):
    """Adiciona mensagem ao log"""
    txt_log.config(state=tk.NORMAL)
    txt_log.insert(tk.END, message + "\n")
    txt_log.config(state=tk.DISABLED)
    txt_log.see(tk.END)


# Configuração da interface gráfica
root = tk.Tk()
root.title("WhatsApp Bulk Sender")
root.geometry("600x500")

# Frame principal
frame = tk.Frame(root, padx=10, pady=10)
frame.pack(fill=tk.BOTH, expand=True)

# Números
tk.Label(frame, text="Números (1 por linha):").grid(row=0, column=0, sticky="w")
entry_numbers = tk.Text(frame, height=8, width=50)
entry_numbers.grid(row=1, column=0, columnspan=2, pady=5)
btn_browse = tk.Button(frame, text="Abrir TXT", command=browse_file)
btn_browse.grid(row=1, column=2, padx=5)

# Mensagem
tk.Label(frame, text="Mensagem:").grid(row=2, column=0, sticky="w", pady=(10, 0))
entry_message = tk.Text(frame, height=5, width=50)
entry_message.grid(row=3, column=0, columnspan=3, pady=5)

# Botão de envio
btn_send = tk.Button(frame, text="Enviar Mensagens", command=whatsapp_bulk_sender, height=2, bg="#25D366", fg="white")
btn_send.grid(row=4, column=0, columnspan=3, pady=10)

# Log
tk.Label(frame, text="Log de Execução:").grid(row=5, column=0, sticky="w", pady=(10, 0))
txt_log = tk.Text(frame, height=8, width=70, state=tk.DISABLED)
txt_log.grid(row=6, column=0, columnspan=3)

# Rodapé
tk.Label(frame, text="⚠️ Não envie spam! Respeite os limites do WhatsApp", fg="red").grid(row=7, column=0, columnspan=3,
                                                                                          pady=(10, 0))

root.mainloop()