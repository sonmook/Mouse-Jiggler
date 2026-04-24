import customtkinter as ctk
import pyautogui
import threading
import sys  # NOVO
import os   # NOVO

# Função para encontrar o caminho correto dos arquivos no PyInstaller
def resource_path(relative_path):
    """ Obtém o caminho absoluto para o arquivo, funcionando no VSCode e no .exe """
    try:
        # PyInstaller cria uma pasta temporária e guarda o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configurações do PyAutoGUI (Segurança)
pyautogui.FAILSAFE = False

# Configuração de Cores Premium
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MouseJigglerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Auto Mouse TI")
        self.geometry("350x420")
        self.resizable(False, False)
        self.iconbitmap(resource_path("mouse.ico"))

        # Variáveis de Controle
        self.rodando = False
        self.intervalo_total = 10 # Tempo padrão em segundos
        self.tempo_restante = self.intervalo_total

        # --- UI ELEMENTS ---
        # Frame Principal (dá um efeito de "cartão" no fundo)
        self.frame_bg = ctk.CTkFrame(self, corner_radius=15)
        self.frame_bg.pack(pady=20, padx=20, fill="both", expand=True)

        self.label_titulo = ctk.CTkLabel(self.frame_bg, text="ANTI-AFK SYSTEM", font=("Segoe UI", 22, "bold"))
        self.label_titulo.pack(pady=(15, 5))

        self.label_status = ctk.CTkLabel(self.frame_bg, text="Status: PAUSADO", text_color="#ff3b30", font=("Segoe UI", 14, "bold"))
        self.label_status.pack(pady=5)

        # --- TIMER AREA ---
        self.frame_timer = ctk.CTkFrame(self.frame_bg, fg_color="transparent")
        self.frame_timer.pack(pady=10)

        self.label_tempo = ctk.CTkLabel(self.frame_timer, text="00:10", font=("Segoe UI", 48, "bold"), text_color="#1f6aa5")
        self.label_tempo.pack()

        self.progress_bar = ctk.CTkProgressBar(self.frame_bg, width=220, height=12)
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(1.0) # Começa cheia

        # --- SLIDER DE TEMPO ---
        self.label_slider = ctk.CTkLabel(self.frame_bg, text=f"Intervalo de Ação: {self.intervalo_total}s", font=("Segoe UI", 12))
        self.label_slider.pack(pady=(5, 0))
        
        self.slider = ctk.CTkSlider(self.frame_bg, from_=5, to=60, number_of_steps=55, command=self.atualizar_slider)
        self.slider.set(self.intervalo_total)
        self.slider.pack(pady=(0, 15))

        # --- BOTÃO PRINCIPAL ---
        self.btn_toggle = ctk.CTkButton(self.frame_bg, text="▶ INICIAR", font=("Segoe UI", 15, "bold"), 
                                        fg_color="#28a745", hover_color="#218838", height=40,
                                        command=self.toggle_jiggler)
        self.btn_toggle.pack(pady=(5, 20))

    def atualizar_slider(self, valor):
        """Atualiza o texto e a variável de tempo quando o usuário mexe na barra"""
        self.intervalo_total = int(valor)
        self.label_slider.configure(text=f"Intervalo de Ação: {self.intervalo_total}s")
        if not self.rodando:
            self.tempo_restante = self.intervalo_total
            self.atualizar_visual_tempo()

    def toggle_jiggler(self):
        """Liga ou Desliga o sistema"""
        if not self.rodando:
            # LIGAR
            self.rodando = True
            self.slider.configure(state="disabled") # Trava o slider enquanto roda
            self.label_status.configure(text="Status: ATIVO", text_color="#28a745")
            self.btn_toggle.configure(text="⏸ PAUSAR", fg_color="#ff3b30", hover_color="#c82333")
            
            self.tempo_restante = self.intervalo_total
            self.atualizar_visual_tempo()
            self.iniciar_contagem()
        else:
            # DESLIGAR
            self.rodando = False
            self.slider.configure(state="normal") # Destrava o slider
            self.label_status.configure(text="Status: PAUSADO", text_color="#ff3b30")
            self.btn_toggle.configure(text="▶ INICIAR", fg_color="#28a745", hover_color="#218838")
            self.atualizar_visual_tempo()

    def iniciar_contagem(self):
        """Loop que roda a cada 1 segundo (1000 milissegundos)"""
        if not self.rodando:
            return # Se foi pausado, quebra o loop

        if self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.atualizar_visual_tempo()
            # Chama essa mesma função de novo após 1 segundo
            self.after(1000, self.iniciar_contagem)
        else:
            # Tempo zerou! Mostra um feedback visual e executa a ação
            self.label_tempo.configure(text="AÇÃO!", text_color="#e6aa68")
            self.progress_bar.set(1.0)
            
            # Roda o movimento numa Thread rápida para não congelar o relógio
            threading.Thread(target=self.mover_mouse, daemon=True).start()
            
            # Reinicia a contagem
            self.tempo_restante = self.intervalo_total
            # Espera 1.5s antes de retomar a contagem para dar tempo de ler "AÇÃO!"
            self.after(1500, self.iniciar_contagem)

    def atualizar_visual_tempo(self):
        """Atualiza os números grandes e a barra de progresso"""
        minutos, segundos = divmod(self.tempo_restante, 60)
        self.label_tempo.configure(text=f"{minutos:02d}:{segundos:02d}", text_color="#1f6aa5")
        
        # Calcula a porcentagem para a barra de progresso
        if self.intervalo_total > 0:
            progresso = self.tempo_restante / self.intervalo_total
            self.progress_bar.set(progresso)

    def mover_mouse(self):
        """Ação real que acontece quando o cronômetro zera"""
        # Move o mouse
        pyautogui.moveRel(10, 0, duration=0.2)
        pyautogui.moveRel(-10, 0, duration=0.2)
        
        # Pressiona tecla
        pyautogui.press('a')
        
        # Dica Pro para Jogos (Dança):
        # pyautogui.keyDown('a')
        # pyautogui.sleep(0.2)
        # pyautogui.keyUp('a')
        # pyautogui.keyDown('d')
        # pyautogui.sleep(0.2)
        # pyautogui.keyUp('d')

if __name__ == "__main__":
    app = MouseJigglerApp()
    app.mainloop()