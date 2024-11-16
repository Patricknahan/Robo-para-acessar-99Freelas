import tkinter as tk
from tkinter import scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import threading
import pywhatkit as kit  # Biblioteca para enviar mensagens no WhatsApp

# Configuração do Selenium
driver = webdriver.Chrome()

# URL de pesquisa no 99Freelas
url = "https://www.99freelas.com.br/projects?q="

# Número de destino para envio via WhatsApp (formato internacional)
numero_destino = "+5531997213062"


class FreelasBotApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bot 99Freelas")
        self.root.geometry("600x400")

        # Palavra-chave
        tk.Label(root, text="Palavra-chave:").pack(pady=5)
        self.keyword_entry = tk.Entry(root, width=50)
        self.keyword_entry.pack(pady=5)

        # Botão Iniciar
        self.start_button = tk.Button(root, text="Iniciar Busca", command=self.start_search)
        self.start_button.pack(pady=5)

        # Botão Parar
        self.stop_button = tk.Button(root, text="Parar Busca", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        # Caixa de texto para exibir links
        self.result_box = scrolledtext.ScrolledText(root, width=70, height=15)
        self.result_box.pack(pady=5)

        # Status
        self.status_label = tk.Label(root, text="Status: Pronto", fg="green")
        self.status_label.pack(pady=5)

        # Controle de execução
        self.running = False

    def update_status(self, message, color):
        """Atualiza a mensagem de status."""
        self.status_label.config(text=f"Status: {message}", fg=color)

    def start_search(self):
        """Inicia a busca em loop."""
        self.running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        keyword = self.keyword_entry.get().strip()
        if not keyword:
            self.update_status("Por favor, insira uma palavra-chave!", "red")
            return
        self.update_status("Buscando...", "blue")
        threading.Thread(target=self.search_loop, args=(keyword,), daemon=True).start()

    def stop_search(self):
        """Para a busca."""
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.update_status("Busca interrompida.", "red")

    def search_loop(self, keyword):
        """Executa a busca a cada 5 minutos."""
        while self.running:
            self.search_projects(keyword)
            for i in range(300):  # 5 minutos
                if not self.running:
                    break
                time.sleep(1)

    def search_projects(self, keyword):
        """Realiza a busca e coleta os links dos projetos."""
        try:
            driver.get(url)
            time.sleep(2)
            search_box = driver.find_element(By.ID, "palavras-chave")
            search_box.send_keys(keyword)
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)

            # Coletar links
            h1_elements = driver.find_elements(By.CSS_SELECTOR, "h1.title a")
            projeto_links = [", https://www.99freelas.com.br" + link.get_attribute("href") for link in h1_elements]

            if projeto_links:
                links_text = "".join(projeto_links)
                self.result_box.insert(tk.END, f"Links encontrados:\n{links_text}\n\n")
                self.result_box.see(tk.END)

                # Enviando os links via WhatsApp
                kit.sendwhatmsg_instantly(numero_destino, links_text)
                self.update_status("Mensagem enviada pelo WhatsApp!", "green")
            else:
                self.result_box.insert(tk.END, "Nenhum projeto encontrado.\n")
                self.result_box.see(tk.END)
                self.update_status("Nenhum projeto encontrado.", "orange")
        except Exception as e:
            self.update_status(f"Erro: {e}", "red")


# Interface gráfica
root = tk.Tk()
app = FreelasBotApp(root)
root.mainloop()
