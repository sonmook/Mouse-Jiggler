import customtkinter as ctk
import pyautogui
import threading
import sys  
import os 

def resource_path(relative_path):
    """
    Hack essencial para o PyInstaller:
    Quando compilamos o script para .exe, ele descompacta os arquivos (como o nosso mouse.ico)
    em uma pasta temporária (_MEIPASS). Essa função garante que o ícone seja encontrado
    tanto rodando direto no VSCode quanto pelo executável final.
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Desabilitamos o "FailSafe" do PyAutoGUI.
# Por padrão, se o usuário jogar o mouse para os cantos da tela, o PyAutoGUI aborta o script
# por segurança. Como é uma ferramenta desenhada para rodar em background, isso causaria crashes acidentais.
pyautogui.FAILSAFE = False

# Identidade visual do app: Foco em um design "Dark Mode" limpo, lembrando dashboards modernos.
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class MouseJigglerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- Configurações da Janela ---
        self.title("Auto Mouse TI")
        self.geometry("350x420")
        self.resizable(False, False) # Tamanho fixo para manter o layout do "card" alinhado
        self.iconbitmap(resource_path("mouse.ico"))

        # --- Estado da Aplicação ---
        # Aqui controlamos se o Jiggler está ativo, o tempo total definido pelo usuário
        # e o tempo que falta para o próximo movimento.
        self.rodando = False
        self.intervalo_total = 10 
        self.tempo_restante = self.intervalo_total

        self._construir_interface()

    def _construir_interface(self):
        """
        Separação de responsabilidades: toda a construção visual da tela fica aqui
        para não poluir o __init__. O design usa um frame central como um "cartão".
        """
        self.frame_bg = ctk.CTkFrame(self, corner_radius=15)
        self.frame_bg.pack(pady=20, padx=20, fill="both", expand=True)

        self.label_titulo = ctk.CTkLabel(self.frame_bg, text="ANTI-AFK SYSTEM", font=("Segoe UI", 22, "bold"))
        self.label_titulo.pack(pady=(15, 5))

        self.label_status = ctk.CTkLabel(self.frame_bg, text="Status: PAUSADO", text_color="#ff3b30", font=("Segoe UI", 14, "bold"))
        self.label_status.pack(pady=5)

        # --- Área do Cronômetro ---
        self.frame_timer = ctk.CTkFrame(self.frame_bg, fg_color="transparent")
        self.frame_timer.pack(pady=10)

        self.label_tempo = ctk.CTkLabel(self.frame_timer, text="00:10", font=("Segoe UI", 48, "bold"), text_color="#1f6aa5")
        self.label_tempo.pack()

        # A barra de progresso dá um feedback visual rápido de quanto tempo falta
        self.progress_bar = ctk.CTkProgressBar(self.frame_bg, width=220, height=12)
        self.progress_bar.pack(pady=(0, 15))
        self.progress_bar.set(1.0) 

        # --- Controles do Usuário ---
        self.label_slider = ctk.CTkLabel(self.frame_bg, text=f"Intervalo de Ação: {self.intervalo_total}s", font=("Segoe UI", 12))
        self.label_slider.pack(pady=(5, 0))
        
        self.slider = ctk.CTkSlider(self.frame_bg, from_=5, to=60, number_of_steps=55, command=self.atualizar_slider)
        self.slider.set(self.intervalo_total)
        self.slider.pack(pady=(0, 15))

        self.btn_toggle = ctk.CTkButton(self.frame_bg, text="▶ INICIAR", font=("Segoe UI", 15, "bold"), 
                                        fg_color="#28a745", hover_color="#218838", height=40,
                                        command=self.toggle_jiggler)
        self.btn_toggle.pack(pady=(5, 20))

    def atualizar_slider(self, valor):
        """Sincroniza a label de texto com o valor atual do slider em tempo real."""
        self.intervalo_total = int(valor)
        self.label_slider.configure(text=f"Intervalo de Ação: {self.intervalo_total}s")
        
        # Se o usuário mexer no tempo com o app pausado, já atualizamos o cronômetro visualmente
        if not self.rodando:
            self.tempo_restante = self.intervalo_total
            self.atualizar_visual_tempo()

    def toggle_jiggler(self):
        """
        Alterna entre iniciar e pausar o sistema.
        Gerencia a troca de cores, textos dos botões e trava o slider para evitar bugs de usabilidade.
        """
        if not self.rodando:
            # Ligando a automação
            self.rodando = True
            self.slider.configure(state="disabled") # Bloqueia alterações de tempo enquanto roda
            self.label_status.configure(text="Status: ATIVO", text_color="#28a745")
            self.btn_toggle.configure(text="⏸ PAUSAR", fg_color="#ff3b30", hover_color="#c82333")
            
            self.tempo_restante = self.intervalo_total
            self.atualizar_visual_tempo()
            self.iniciar_contagem()
        else:
            # Pausando a automação
            self.rodando = False
            self.slider.configure(state="normal") # Libera o slider novamente
            self.label_status.configure(text="Status: PAUSADO", text_color="#ff3b30")
            self.btn_toggle.configure(text="▶ INICIAR", fg_color="#28a745", hover_color="#218838")
            self.atualizar_visual_tempo()

    def iniciar_contagem(self):
        """
        O 'coração' da aplicação. Usamos o método .after() nativo do CustomTkinter
        em vez de time.sleep() para evitar que a interface gráfica (MainLoop) trave.
        """
        if not self.rodando:
            return # Interrompe a recursão se o usuário clicou em pausar

        if self.tempo_restante > 0:
            self.tempo_restante -= 1
            self.atualizar_visual_tempo()
            self.after(1000, self.iniciar_contagem) # Agenda a próxima contagem em 1 segundo
        else:
            # Feedback visual rápido de que o comando foi enviado
            self.label_tempo.configure(text="AÇÃO!", text_color="#e6aa68")
            self.progress_bar.set(1.0)
            
            # CRÍTICO: Rodar a automação em uma Thread separada!
            # Se o PyAutoGUI rodar na thread principal, ele vai 'engasgar' o relógio visual do app.
            threading.Thread(target=self.mover_mouse, daemon=True).start()
            
            # Reinicia o ciclo
            self.tempo_restante = self.intervalo_total
            
            # Aguarda 1.5s antes de retomar para dar tempo do usuário ler o "AÇÃO!" na tela
            self.after(1500, self.iniciar_contagem)

    def atualizar_visual_tempo(self):
        """Matemática simples para converter segundos em formato MM:SS e recalcular a barra de progresso."""
        minutos, segundos = divmod(self.tempo_restante, 60)
        self.label_tempo.configure(text=f"{minutos:02d}:{segundos:02d}", text_color="#1f6aa5")
        
        if self.intervalo_total > 0:
            progresso = self.tempo_restante / self.intervalo_total
            self.progress_bar.set(progresso)

    def mover_mouse(self):
        """
        A ação anti-AFK em si. 
        Mover 10 pixels e voltar é sutil e não atrapalha muito se o usuário estiver com a mão no mouse,
        mas é o suficiente para enganar o SO / Teams / Discord.
        Apertar 'a' garante que apps que ignoram apenas o mouse também registrem atividade.
        """
        pyautogui.moveRel(10, 0, duration=0.2)
        pyautogui.moveRel(-10, 0, duration=0.2)
        pyautogui.press('a')
        
        # --- Dica para forks/contribuidores focados em games ---
        # Se a ideia for criar um anti-AFK para jogos, movimentos muito sutis podem não bastar.
        # Segurar a tecla por uma fração de segundo (como o bloco comentado abaixo) costuma ser mais eficaz:
        #
        # pyautogui.keyDown('a')
        # pyautogui.sleep(0.2)
        # pyautogui.keyUp('a')
        # pyautogui.keyDown('d')
        # pyautogui.sleep(0.2)
        # pyautogui.keyUp('d')

if __name__ == "__main__":
    app = MouseJigglerApp()
    app.mainloop()
