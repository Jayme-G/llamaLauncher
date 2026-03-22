# ╭─────────────────────────────────────────────────────────────────────────╮
# │             🦙 llama Launcher - Versão para Linux e Windows             │
# ╰─────────────────────────────────────────────────────────────────────────╯

version = "1.40"
Author = "Copyright (C) 2026 Jayme Gonçalves"

import os
import sys
import subprocess
import threading
import platform
import webbrowser
import shlex
import shutil
import queue
import json
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter.messagebox import showinfo
from PIL import Image, ImageTk
from datetime import datetime

# ─── Classe Tooltip ──────────────────────────────────────────────
class CreateToolTip:
    tipwindow = None
    last_widget = None

    @classmethod
    def show_tip(cls, event=None):
        if cls.tipwindow or not hasattr(event, 'widget'):
            return

        widget = event.widget
        text = getattr(widget, 'tooltip_text', None)
        if not text:
            return

        x = widget.winfo_rootx() + 28
        y = widget.winfo_rooty() + 24

        cls.last_widget = widget
        tw = tk.Toplevel(widget)
        tw.wm_overrideredirect(True)
        # tw.wm_attributes("-topmost", True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=text, justify="left",
                         background="#ffffe0", relief="solid", borderwidth=1,
                         font=("Segoe UI", 10), padx=6, pady=4)
        label.pack()

        cls.tipwindow = tw

    @classmethod
    def hide_tip(cls, event=None):
        if cls.tipwindow:
            cls.tipwindow.destroy()
            cls.tipwindow = None
            cls.last_widget = None

    def __init__(self, widget, text):
        widget.tooltip_text = text
        widget.bind("<Enter>", self.__class__.show_tip)
        widget.bind("<Leave>", self.__class__.hide_tip)
        widget.bind("<ButtonPress>", self.__class__.hide_tip)

# ─── Diretório raiz (portátil) ──────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(SCRIPT_DIR)  # ← Crucial para Windows

models_dir = os.path.join(SCRIPT_DIR, "models")
bin_dir = os.path.join(SCRIPT_DIR, "bin")
os.makedirs(models_dir, exist_ok=True)
os.makedirs(bin_dir, exist_ok=True)

# ─── Configurações comuns ───────────────────────────────────────
CTX_SIZE = 4096
THREADS_FALLBACK = os.cpu_count() or 4
NGPU_LAYERS = "auto"

# ─── Funções de validação segura ────────────────────────────────
def safe_int(val, default=0):
    try:
        return int(val)
    except (ValueError, TypeError):
        return default

def safe_float(val, default=0.0):
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

# ─── Detecção automática de modelos ─────────────────────────────
gguf_files = [f for f in os.listdir(models_dir) if f.lower().endswith('.gguf')]

# Separa modelos principais (sem mmproj) e mmproj
main_models = [f for f in gguf_files if '-mmproj-' not in f.lower() and 'mmproj' not in f.lower()]
mmproj_map = {}

for main in main_models:
    base = os.path.splitext(main)[0]
    base_lower = base.lower()
    
    for f in gguf_files:
        f_lower = f.lower()
        if f_lower.startswith(base_lower + "-mmproj") and f_lower.endswith('.gguf'):
            mmproj_map[main] = f
            break

MODELS = {}
MMPROJ_FILES = {}

for i, file in enumerate(sorted(main_models), 1):
    name = os.path.splitext(file)[0]
    multi = file in mmproj_map
    MODELS[i] = {"name": name, "file": file, "multi": multi}
    if multi:
        MMPROJ_FILES[i] = mmproj_map[file]

# ─── CONFIGURAÇÕES SALVAS POR MODELO ────────────────────────────
DEFAULT_CONFIG = {
    "ctx_size": CTX_SIZE,
    "ngpu_layers": NGPU_LAYERS,
    "threads": "auto",
    "temp": 0.8,
    "top_p": 0.95,
    "top_k": 40,
    "min_p": 0.05,
    "typical_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 1.0,
    "repeat_penalty": 1.1,
    "mirostat": 0,
    "mirostat_tau": 5.0,
    "mirostat_eta": 0.1,
    "dynatemp_range": 0.0,
    "dynatemp_exp": 1.0,
    "xtc_probability": 0.0,
    "xtc_threshold": 0.1,
    "seed": -1,
    "rope_freq_scale": 1.0,
    "numa": "off",
    "reasoning_effort": "low",
    "use_mmproj": "1",
}

# ─── Labels e grupos ────────────────────────────────────────────
PARAM_LABELS = {
    "ctx_size": "Tamanho do Contexto (tokens)",
    "ngpu_layers": "Camadas na GPU",
    "threads": "Threads de CPU",
    "temp": "Temperatura",
    "top_p": "Top-p",
    "top_k": "Top-k",
    "min_p": "Min-p",
    "typical_p": "Typical-p",
    "frequency_penalty": "Penalidade de Frequência",
    "presence_penalty": "Penalidade de Presença",
    "repeat_penalty": "Penalidade de Repetição",
    "mirostat": "Mirostat",
    "mirostat_tau": "Mirostat Tau",
    "mirostat_eta": "Mirostat Eta",
    "dynatemp_range": "Faixa Dynamic Temp",
    "dynatemp_exp": "Expoente Dynamic Temp",
    "xtc_probability": "Probabilidade XTC",
    "xtc_threshold": "Limiar XTC",
    "seed": "Seed",
    "rope_freq_scale": "Escala RoPE",
    "numa": "Suporte NUMA",
    "reasoning_effort": "Raciocínio (quando aplicável)",
    "use_mmproj": "Multimodal (mmproj)",
}

GROUPS = {
    "Geral": ["ctx_size", "ngpu_layers", "threads", "numa", "rope_freq_scale", "reasoning_effort", "use_mmproj"],
    "Amostragem": ["temp", "top_p", "top_k", "min_p", "typical_p", "seed"],
    "Penalidades": ["repeat_penalty", "presence_penalty", "frequency_penalty"],
    "Mirostat": ["mirostat", "mirostat_tau", "mirostat_eta"],
    "Temp. Dinâmica": ["dynatemp_range", "dynatemp_exp"],
    "XTC": ["xtc_probability", "xtc_threshold"],
}

# ─── Valores mais usados ─────────────────────────────────────────
COMMON_VALUES = {
    "ctx_size": ["0", "2048", "4096", "8192", "16384", "32768", "65536", "131072", "262144"],
    "ngpu_layers": ["auto", "0", "10", "20", "30", "40", "50", "99", "999"],
    "threads": ["auto", "2", "4", "6", "8", "12", "16", "24", "32", "64", "128"],
    "temp": ["0.0", "0.5", "0.6", "0.7", "0.8", "0.9", "1.0", "1.2"],
    "top_p": ["0.0", "0.7", "0.8", "0.9", "0.95", "0.98", "1.0"],
    "top_k": ["0", "10", "20", "30", "40", "50", "100"],
    "min_p": ["0.0", "0.01", "0.05", "0.1", "0.2"],
    "typical_p": ["0.9", "0.95", "1.0"],
    "frequency_penalty": ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8"],
    "presence_penalty": ["0.0", "0.1", "0.2", "0.3", "0.4", "0.5", "0.6", "0.7", "0.8", "1.0", "1.5"],
    "repeat_penalty": ["1.0", "1.02", "1.03", "1.04", "1.05", "1.08", "1.1", "1.15", "1.18", "1.2", "1.25"],
    "mirostat": ["0", "1", "2"],
    "mirostat_tau": ["1.0", "3.0", "5.0", "8.0", "10.0"],
    "mirostat_eta": ["0.05", "0.1", "0.2", "0.3"],
    "dynatemp_range": ["0.0", "0.1", "0.3", "0.5", "1.0"],
    "dynatemp_exp": ["0.5", "1.0", "1.5", "2.0"],
    "xtc_probability": ["0.0", "0.1", "0.2", "0.3", "0.5", "0.8"],
    "xtc_threshold": ["0.05", "0.1", "0.2", "0.3"],
    "seed": ["-1", "42", "123", "1234", "9999"],
    "rope_freq_scale": ["0.5", "0.75", "1.0", "1.25", "2.0"],
    "numa": ["off", "distribute", "isolate"],
    "reasoning_effort": ["off", "low", "medium", "high"],
}

COMMON_IPS = ["127.0.0.1", "0.0.0.0"]
COMMON_PORTS = ["8080", "9000", "8082", "8081", "8000", "5000", "3000"]

# ─── Textos explicativos ────────────────────────────────────────
EXPLANATIONS = {
    "ctx_size": "Tamanho do contexto (tokens que o modelo lembra). Use 4096-8192 para uso geral, 32768+ em modelos long-context. Maior = mais VRAM/RAM. 0 = valor padrão do modelo.",
    "ngpu_layers": "Camadas offload para GPU. O 'auto' é o mais usado. 999 = todas as camadas (máximo de velocidade). Reduza se der erro de VRAM.",
    "threads": "Threads da CPU. O 'auto' usa todos os núcleos detectados. O '4' (4 núcleos) é padrão para diversas configurações. Reduza se o PC esquentar ou travar.",
    "temp": "Temperatura: controla criatividade. 0.0 = respostas idênticas toda vez. 0.7-0.9 = ótimo para chat. >1.0 = muito criativo/aleatório.",
    "top_p": "Probabilidade cumulativa. 0.9-0.95 é o mais usado. 1.0 = desliga (menos comum).",
    "top_k": "Mantém só os K tokens mais prováveis. 40 é o padrão. 0 = desliga completamente.",
    "min_p": "Filtra tokens muito improváveis. 0.05 é o valor mais recomendado.",
    "typical_p": "Typical sampling: prefere tokens 'típicos' do modelo. 0.9-1.0 dá texto mais natural e coerente.",
    "frequency_penalty": "Penaliza palavras que já apareceram muito. 0.0-0.2 é o mais usado para evitar repetição sem perder qualidade.",
    "presence_penalty": "Penaliza qualquer repetição (mais forte que frequency). 0.5-1.0 comum em chat/roleplay.",
    "repeat_penalty": "Penalidade geral de repetição. 1.05-1.15 é a faixa preferiada para chat.",
    "mirostat": "Controle avançado de qualidade/perplexidade. 0 = desligado (padrão), 2 = Mirostat 2.0 (quase sempre o mais recomendado).",
    "mirostat_tau": "Alvo de perplexidade/entropy. 5.0 é o valor padrão e mais usado.",
    "mirostat_eta": "Taxa de aprendizado do Mirostat. 0.1 é o padrão.",
    "dynatemp_range": "Faixa da temperatura dinâmica (aumenta criatividade quando o texto fica muito previsível). 0.0 = desligado. 0.3–0.5 é faixa comum.",
    "dynatemp_exp": "Expoente da dinâmica. 1.0 = padrão. <1.0 deixa a variação mais suave.",
    "xtc_probability": "XTC (Exclude Top Choices): aumenta criatividade e quebra clichês/repetições. 0.0 = desligado. 0.1–0.3 é uma faixa bastante utilizada.",
    "xtc_threshold": "Limiar do XTC (define quais tokens 'óbvios' são excluídos). 0.1 é o valor mais recomendado.",
    "seed": "Semente aleatória. -1 = diferente toda vez. Número fixo = respostas 100% reprodutíveis.",
    "rope_freq_scale": "Fator de escala RoPE para estender contexto. 1.0 = sem extensão (padrão). 0.4–0.75 comum com YaRN em contextos muito longos.",
    "numa": "Otimização para PCs/servidores com múltiplos CPUs. Fica em 'off' para 99% dos usuários. Use 'distribute' em servidores.",
    "reasoning_effort": "Nível de raciocínio ('off'/'low'/'medium'/'high'). O 'off' desliga completamente o <think>.",
    "use_mmproj": "Ativa, quando aplicável, suporte a imagem, áudio e vídeo, através de um arquivo mmproj. Desmarque para usar exclusivamente o chat do modelo (economiza VRAM e acelera bastante)."
}

# ─── Funções de config por modelo ───────────────────────────────
def get_config_path(model_file):
    base_name = os.path.splitext(model_file)[0]
    return os.path.join(SCRIPT_DIR, "models", base_name + ".txt")

def load_model_config(model_file):
    config = {k: str(v) for k, v in DEFAULT_CONFIG.items()}
    config_path = get_config_path(model_file)
    if os.path.isfile(config_path):
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = [x.strip() for x in line.split("=", 1)]
                        if key in config:
                            config[key] = value
        except Exception as e:
            pass
    return config, config_path

def save_model_config(config_path, config, model_name):
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(f"# Configuração salva para {model_name}\n")
            f.write(f"# Última alteração: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
            for k, v in config.items():
                f.write(f"{k}={v}\n")
        return True
    except Exception as e:
        pass
        return False

# ─── Aplicação GUI ──────────────────────────────────────────────
class llamaLauncher(tk.Tk):
    def __init__(self):
        super().__init__()
        icon_path = os.path.join(SCRIPT_DIR, "llama_icon.png")
        try:
            icon = tk.PhotoImage(file=icon_path)
            self.iconphoto(True, icon)
        except Exception as e:
            pass

        self.geometry("1280x720")
        self.resizable(True, True)
        self.configure(bg="#ffffff")
        
        self.model_var = tk.StringVar()
        self.mode_var = tk.StringVar(value="server")
        self.config_vars = {}
        self.mirostat_tau_widget = None
        self.mirostat_eta_widget = None
        self.xtc_threshold_widget = None
        self.dynatemp_exp_widget = None
        self.current_model = None
        self.config_path = None
        self.process = None
        self.output_queue = queue.Queue()
        self.server_host = tk.StringVar(value="127.0.0.1")
        self.server_port = tk.StringVar(value="8080")
        self.server_api_key = tk.StringVar(value="")
        self.mmproj_check = None
        self.mmproj_var = None
        self.title(f"llama Launcher - Versão {version} para Linux e Windows")

        # Estilo
        style = ttk.Style(self)
        style.theme_use("clam")
        
        # Customização global para radiobuttons
        style.configure("TRadiobutton", background="#ffffff")
        style.map("TRadiobutton",
            background=[("active", "#ffffff"), ("pressed", "#e6e6e6"), ("!disabled", "#ffffff")],
            foreground=[("disabled", "#a0a0a0")],
        )

        # Customização para checkbox (Multimodal mmproj)
        style.configure("TCheckbutton", background="#ffffff")
        style.map("TCheckbutton",
            background=[("active", "#ffffff"), 
                        ("!disabled", "#ffffff"),
                        ("selected", "#ffffff"),
                        ("!selected", "#ffffff")],
        )

        BG_MAIN = "#ffffff"
        BG_CARD = "#ffffff"
        ACCENT  = "#1e40af"
        TEXT_DARK = "#212529"

        style.configure("TFrame", background=BG_MAIN)
        style.configure("TLabelframe", background=BG_CARD, borderwidth=1, relief="solid", bordercolor="#d1d5db")
        style.configure("TLabelframe.Label", background=BG_CARD, font=("Segoe UI Emoji", 12, "bold"))
        style.configure("TLabel", background=BG_CARD, foreground=TEXT_DARK, font=("Segoe UI Emoji", 12))
        style.configure("TButton", font=("Segoe UI Emoji", 12, "bold"))
        style.configure("TCombobox", font=("Segoe UI Emoji", 12))
        style.configure("TEntry", font=("Segoe UI Emoji", 12))

        self.setup_ui()
        self.load_models()
        self.print_license_header()
        self.after(180, self.set_initial_sash)

    def log(self, message, level="INFO"):
        """Log centralizado → tudo vai para a Saída do Processo"""
        icons = {
            "INFO":    "ℹ️ ",
            "WARN":    "⚠️ ",
            "ERROR":   "❌ ",
            "SUCCESS": "✅ "
        }
        prefix = icons.get(level.upper(), "→ ")
        timestamp = datetime.now().strftime("%H:%M:%S")
        full_msg = f"[{timestamp}] {prefix}{message}\n"
        
        self.output_text.insert("end", full_msg)
        self.output_text.see("end")
        self.output_text.update_idletasks()

    def update_button_states(self):
        mode = self.mode_var.get()
        if mode == "cli":
            self.launch_btn.config(state="normal", text="🚀")
            self.stop_btn.config(state="disabled")
            self.input_entry.pack_forget()
        else:
            has_process = bool(self.process and self.process.poll() is None)
            self.launch_btn.config(state="disabled" if has_process else "normal")
            self.stop_btn.config(state="normal" if has_process else "disabled")
            if has_process:
                self.input_entry.pack(fill="x", pady=5)
            else:
                self.input_entry.pack_forget()
    
    def update_multi_status(self):
        """Atualiza o texto e cor do status + mostra/esconde a checkbox"""
        if not self.current_model:
            return

        if not self.current_model.get("multi"):
            self.multi_status.config(text="📄 Só Chat", foreground="#006400")
            if self.mmproj_check:
                self.mmproj_check.grid_remove()
            return

        # === Modelo Multimodal ===
        if self.mmproj_check:
            self.mmproj_check.grid()

        use = self.config_vars["use_mmproj"].get() in ("1", "true", "yes", "on")
        if use:
            self.multi_status.config(text="✅ + Multi", foreground="#006400")
        else:
            self.multi_status.config(text="📄 Só Chat", foreground="#d35400")

    def update_mirostat_fields(self, *args):
        miro_val = self.config_vars["mirostat"].get()
        state = "disabled" if miro_val == "0" else "readonly"
        
        if self.mirostat_tau_widget:
            self.mirostat_tau_widget.config(state=state)
        if self.mirostat_eta_widget:
            self.mirostat_eta_widget.config(state=state)

    def update_xtc_fields(self, *args):
        try:
            prob = float(self.config_vars["xtc_probability"].get() or 0)
        except:
            prob = 0.0
        state = "disabled" if prob <= 0 else "readonly"
        
        if self.xtc_threshold_widget:
            self.xtc_threshold_widget.config(state=state)

    def update_dynatemp_fields(self, *args):
        try:
            rng = float(self.config_vars["dynatemp_range"].get() or 0)
        except:
            rng = 0.0
        state = "disabled" if rng <= 0 else "readonly"
        
        if self.dynatemp_exp_widget:
            self.dynatemp_exp_widget.config(state=state)

    def setup_ui(self):
        # Toolbar
        toolbar = ttk.Frame(self, padding=(10, 6), relief="raised")
        toolbar.pack(side="top", fill="x")

        self.model_list = ttk.Combobox(toolbar, textvariable=self.model_var, state="readonly",
                                       width=36, font=("Segoe UI Emoji", 10))
        self.model_list.pack(side="left", padx=(0, 12))
        self.model_list.bind("<<ComboboxSelected>>", self.on_model_select)

        self.multi_status = ttk.Label(toolbar, text="", font=("Segoe UI Emoji", 10), foreground="#006400")
        self.multi_status.pack(side="left", padx=8)

        ttk.Radiobutton(toolbar, text="SERVER", variable=self.mode_var, value="server").pack(side="left", padx=10)
        ttk.Radiobutton(toolbar, text="CLI", variable=self.mode_var, value="cli").pack(side="left", padx=10)

        btn_padx = 2
        for btn_text, cmd, tooltip in [
            ("💾", self.save_config, "Salvar configurações deste modelo"),
            ("🔄", self.reset_config, "Restaurar valores padrão"),
            ("📁", self.open_models_folder, "Abrir pasta models"),
            ("🌐", self.open_browser, "Abrir navegador"),
            ("🔧", self.open_settings, "Configurações do Servidor (IP + Porta)"),
            ("🧹", self.clear_output, "Limpar saída"),
            ("⛔", self.stop_process, "Parar processo"),
            ("🚀", self.launch, "Iniciar modelo")
        ]:
            b = ttk.Button(toolbar, text=btn_text, width=3, command=cmd)
            b.pack(side="right", padx=btn_padx)
            CreateToolTip(b, tooltip)
            if btn_text == "🚀":
                self.launch_btn = b
            elif btn_text == "⛔":
                self.stop_btn = b

        # Paned_Window
        self.main_paned = ttk.PanedWindow(self, orient=tk.VERTICAL)
        self.main_paned.pack(fill="both", expand=True, padx=4, pady=4)

        config_pane = ttk.Frame(self.main_paned)
        output_pane = ttk.Frame(self.main_paned)

        self.main_paned.add(config_pane, weight=73)
        self.main_paned.add(output_pane, weight=27)

        # === ÁREA DE CONFIGURAÇÕES COM SCROLL (HORIZONTAL + VERTICAL) ===
        config_pane.grid_rowconfigure(0, weight=1)
        config_pane.grid_columnconfigure(0, weight=1)

        # Canvas + Scrollbars
        self.config_canvas = tk.Canvas(config_pane, bg="#ffffff", highlightthickness=0)
        self.config_vbar = ttk.Scrollbar(config_pane, orient="vertical", 
                                         command=self.config_canvas.yview)
        self.config_hbar = ttk.Scrollbar(config_pane, orient="horizontal", 
                                         command=self.config_canvas.xview)

        self.config_canvas.configure(
            yscrollcommand=self.config_vbar.set,
            xscrollcommand=self.config_hbar.set
        )

        # Frame interno (onde ficam todos os grupos)
        self.config_inner = ttk.Frame(self.config_canvas, padding=6)
        self.config_inner.columnconfigure(0, weight=1)
        self.config_inner.columnconfigure(1, weight=1)

        # Coloca o frame dentro do canvas
        self.config_inner_id = self.config_canvas.create_window(
            (0, 0), window=self.config_inner, anchor="nw"
        )

        # Layout do canvas + barras
        self.config_canvas.grid(row=0, column=0, sticky="nsew")
        self.config_vbar.grid(row=0, column=1, sticky="ns")
        self.config_hbar.grid(row=1, column=0, sticky="ew")

        # Bindings para atualizar a rolagem
        self.config_inner.bind("<Configure>", self._on_inner_configure)
        self.config_canvas.bind("<Configure>", self._on_canvas_configure)

        # Grupos - Configurações de espaçamento
        padding_frame = (8, 6)
        self._create_group(self.config_inner, "Geral",          GROUPS["Geral"],          0, 0, padding_frame)
        self._create_group(self.config_inner, "Mirostat",       GROUPS["Mirostat"],       1, 0, padding_frame)
        self._create_group(self.config_inner, "Temp. Dinâmica", GROUPS["Temp. Dinâmica"], 2, 0, padding_frame)

        self._create_group(self.config_inner, "Amostragem",     GROUPS["Amostragem"],     0, 1, padding_frame)
        self._create_group(self.config_inner, "Penalidades",    GROUPS["Penalidades"],    1, 1, padding_frame)
        self._create_group(self.config_inner, "XTC",            GROUPS["XTC"],            2, 1, padding_frame)

        # Área de saída
        output_outer = ttk.Frame(output_pane, padding=8, relief="sunken")
        output_outer.pack(fill="both", expand=True)

        ttk.Label(output_outer, text="📟 Saída do Processo:", 
                  font=("Segoe UI Emoji", 11, "bold")).pack(anchor="w", pady=(0, 5))

        output_frame = ttk.Frame(output_outer)
        output_frame.pack(fill="both", expand=True)

        self.output_text = tk.Text(output_frame, wrap="word", height=8,
                                   bg="#1e1e1e", fg="#d4d4d4", font=("Consolas", 10),
                                   relief="flat", bd=1)
        scroll = ttk.Scrollbar(output_frame, orient="vertical", command=self.output_text.yview)
        self.output_text.configure(yscrollcommand=scroll.set)
        self.output_text.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.input_entry = ttk.Entry(output_outer, font=("Segoe UI Emoji", 11))
        self.input_entry.bind("<Return>", self.send_input)
        self.input_entry.pack(fill="x", pady=5)
        self.input_entry.pack_forget()

    def _on_inner_configure(self, event):
        """Atualiza a região rolável sempre que o conteúdo muda de tamanho"""
        self.config_canvas.configure(scrollregion=self.config_canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        """Faz o frame interno se expandir quando a janela fica MAIOR
           e permite barra horizontal quando a janela fica MENOR"""
        self.config_canvas.itemconfigure(self.config_inner_id, width=event.width)

    def open_models_folder(self):
        try:
            if platform.system() == "Windows":
                os.startfile(models_dir)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", models_dir])
            else:
                subprocess.Popen(["xdg-open", models_dir])
        except Exception as e:
            self.log(f"Não foi possível abrir a pasta: {e}", level="ERROR")

    def _create_group(self, parent, title, keys, row, col, frame_padding):
        lf = ttk.LabelFrame(parent, text=title, padding=frame_padding)
        lf.grid(row=row, column=col, sticky="nsew", padx=3, pady=3)
        self._create_param_widgets(lf, keys)
        lf.columnconfigure(1, weight=1)

    def _create_param_widgets(self, parent_frame, param_keys):
        row = 0
        for key in param_keys:
            if key not in PARAM_LABELS: continue

            lbl = ttk.Label(parent_frame, text=PARAM_LABELS[key] + ":", anchor="w")
            lbl.grid(row=row, column=0, sticky="w", padx=(4, 6), pady=(1, 1))

            var = tk.StringVar(value=str(DEFAULT_CONFIG.get(key, "")))
            self.config_vars[key] = var

            widget = ttk.Combobox(parent_frame, textvariable=var,
                                  values=COMMON_VALUES.get(key, []), width=25)

            if key in ["ctx_size", "ngpu_layers", "threads", "temp", "top_p", "top_k", "min_p", "typical_p", "frequency_penalty", "presence_penalty", "repeat_penalty", "mirostat", "mirostat_tau", "mirostat_eta", "dynatemp_range", "dynatemp_exp", "xtc_probability", "xtc_threshold", "seed", "rope_freq_scale", "numa", "reasoning_effort"]:
                widget["state"] = "readonly"
            
            if key == "use_mmproj":
                var = tk.StringVar(value="1")
                self.config_vars[key] = var
                self.mmproj_var = var
                
                self.mmproj_check = ttk.Checkbutton(
                    parent_frame,
                    text=PARAM_LABELS[key],
                    variable=var,
                    onvalue="1",
                    offvalue="0"
                )
                self.mmproj_check.grid(row=row, column=1, columnspan=2, sticky="w", padx=4, pady=6)
                CreateToolTip(self.mmproj_check, EXPLANATIONS[key])
                
                # Atualiza o status visual EM TEMPO REAL quando marcar/desmarcar
                var.trace_add("write", lambda *args: self.update_multi_status())
                
                row += 1
                continue

            widget.grid(row=row, column=1, sticky="ew", padx=(2, 4), pady=(1, 1))

            if key == "mirostat_tau":
                self.mirostat_tau_widget = widget
            elif key == "mirostat_eta":
                self.mirostat_eta_widget = widget
            elif key == "mirostat":
                var.trace_add("write", self.update_mirostat_fields)
            elif key == "xtc_threshold":
                self.xtc_threshold_widget = widget
            elif key == "xtc_probability":
                var.trace_add("write", self.update_xtc_fields)
            elif key == "dynatemp_exp":
                self.dynatemp_exp_widget = widget
            elif key == "dynatemp_range":
                var.trace_add("write", self.update_dynatemp_fields)

            if key in EXPLANATIONS:
                CreateToolTip(lbl, EXPLANATIONS[key])
                CreateToolTip(widget, EXPLANATIONS[key])

            row += 1

    def get_internal_name(self, display):
        return display.replace("👀 ", "").strip()

    def load_models(self):
        display_values = []
        for i in sorted(MODELS.keys()):
            m = MODELS[i]
            prefix = "👀 " if m["multi"] else ""
            display_values.append(prefix + m["name"])

        self.model_list["values"] = display_values

        # Carrega config geral
        self.load_general_config()

        if not self.model_var.get() and display_values:
            self.model_var.set(display_values[0])
            self.on_model_select(None)
    
    def load_selected_model(self):
        """Carrega configurações do modelo selecionado SEM salvar nada"""
        display = self.model_var.get()
        internal_name = self.get_internal_name(display)

        for i, m in MODELS.items():
            if m["name"] == internal_name:
                self.current_model = MODELS[i].copy()
                self.current_model["choice"] = i
                break

        if self.current_model:
            model_file = self.current_model["file"]
            config, self.config_path = load_model_config(model_file)

            for key, val in config.items():
                if key in self.config_vars:
                    self.config_vars[key].set(val)

            if self.current_model.get("multi"):
                use = config.get("use_mmproj", "1") in ("1", "true", "yes", "on")
                status = "✅ + Multi (mmproj)" if use else "📄 Multimodal desativado"
                self.multi_status.config(text=status, foreground="#006400" if use else "#666666")
            else:
                self.multi_status.config(text="📄 Só Chat")

            self.update_multi_status()
            self.update_button_states()
            self.update_mirostat_fields()
            self.update_xtc_fields()
            self.update_dynatemp_fields()

        return internal_name if self.current_model else None

    def on_model_select(self, event=None):
        internal_name = self.load_selected_model()
        if internal_name:
            self.save_general_config(last_model=internal_name)

        for i, m in MODELS.items():
            if m["name"] == internal_name:
                self.current_model = MODELS[i].copy()
                self.current_model["choice"] = i
                break

        if self.current_model:
            model_file = self.current_model["file"]
            config, self.config_path = load_model_config(model_file)

            for key, val in config.items():
                if key in self.config_vars:
                    self.config_vars[key].set(val)

            if self.current_model.get("multi"):
                use = config.get("use_mmproj", "1") in ("1", "true", "yes", "on")
                status = "✅ + Multi (mmproj)" if use else "📄 Multi desativado"
                self.multi_status.config(text=status, foreground="#006400" if use else "#666666")
            else:
                self.multi_status.config(text="📄 Só Chat")
            
            self.update_multi_status()
            self.save_general_config(last_model=internal_name)
            self.update_button_states()
            self.update_mirostat_fields()
            self.update_xtc_fields()
            self.update_dynatemp_fields()

    def save_config(self):
        if not self.current_model:
            self.log("Selecione um modelo primeiro!", level="ERROR")
            return

        config = {k: v.get().strip() for k, v in self.config_vars.items()}

        if config["mirostat"] not in ("0", "1", "2"):
            self.log("Mirostat deve ser 0, 1 ou 2.", level="ERROR")
            return

        if save_model_config(self.config_path, config, self.current_model["name"]):
            self.log("Configurações salvas para este modelo!", level="SUCCESS")
        else:
            self.log("Falha ao salvar arquivo.", level="ERROR")
        
        self.update_multi_status()

    def reset_config(self):
        for key, var in self.config_vars.items():
            var.set(str(DEFAULT_CONFIG[key]))
        self.log("Todas as configurações voltaram para o padrão.", level="SUCCESS")

        self.update_multi_status()
        self.update_mirostat_fields()
        self.update_xtc_fields()
        self.update_dynatemp_fields()

    def launch(self):
        if self.process and self.process.poll() is None:
            self.log("Já existe um processo rodando!", level="ERROR")
            return
        if not self.current_model:
            self.log("Selecione um modelo!", level="ERROR")
            return

        mode = self.mode_var.get()
        is_windows = platform.system() == "Windows"

        # Nome do binário (suporte .exe)
        binary_name = "llama-cli" if mode == "cli" else "llama-server"
        if is_windows:
            binary_name += ".exe"

        binary_path = os.path.join(bin_dir, binary_name)
        model_path = os.path.join(models_dir, self.current_model["file"])

        if not os.path.isfile(binary_path):
            self.log(f"Binário não encontrado:\n{binary_path}\n\nColoque llama-cli{' .exe' if is_windows else ''} na pasta bin", level="ERROR")
            return
        if not os.path.isfile(model_path):
            self.log(f"Modelo não encontrado:\n{model_path}", level="ERROR")
            return

        config = {k: v.get().strip() for k, v in self.config_vars.items()}

        COMMON_PARAMS = [
            "-m", model_path,
            "--prio", "2",
            "--jinja",
            "--reasoning-format", "auto",
            "--flash-attn", "auto",
        ]
        
        # ─── Controle de Raciocínio ─────────────────────────────────────
        reasoning_effort = config.get("reasoning_effort", "low").strip().lower()

        if reasoning_effort == "off":
            COMMON_PARAMS.extend(["--reasoning-budget", "0"])
            COMMON_PARAMS.extend(["--reasoning", "off"])
            chat_kwargs = {}   # enable_thinking agora é feito pelo --reasoning
            self.output_text.insert("end", "🧠 Raciocínio desativado (--reasoning off + budget 0)\n")
        else:
            COMMON_PARAMS.extend(["--reasoning-budget", "-1"])
            COMMON_PARAMS.extend(["--reasoning", "on"])        # ← novo flag
            chat_kwargs = {"reasoning_effort": reasoning_effort}  # só o esforço continua no kwargs
            self.output_text.insert("end", f"🧠 Raciocínio ativado (nível: {reasoning_effort.upper()} + --reasoning on)\n")

        # Mantém --chat-template-kwargs apenas se ainda houver algo (ex: effort)
        if chat_kwargs:
            kwargs_json = json.dumps(chat_kwargs, ensure_ascii=False)
            COMMON_PARAMS.extend(["--chat-template-kwargs", kwargs_json])
            self.output_text.insert("end", f"   └─ --chat-template-kwargs {kwargs_json}\n")
        else:
            self.output_text.insert("end", "   └─ (enable_thinking removido → agora usa --reasoning)\n")

        for key, value in config.items():
            if key == "ctx_size":
                COMMON_PARAMS.extend(["-c", value])
            elif key == "ngpu_layers":
                COMMON_PARAMS.extend(["-ngl", value])
            elif key == "threads":
                if value.lower() == "auto":
                    actual = os.cpu_count() or THREADS_FALLBACK
                    COMMON_PARAMS.extend(["-t", str(actual)])
                    self.output_text.insert("end", f"→ Threads: auto ({actual} núcleos detectados)\n")
                else:
                    COMMON_PARAMS.extend(["-t", value])
            elif key == "temp": COMMON_PARAMS.extend(["--temp", value])
            elif key == "top_p": COMMON_PARAMS.extend(["--top-p", value])
            elif key == "top_k": COMMON_PARAMS.extend(["--top-k", value])
            elif key == "min_p": COMMON_PARAMS.extend(["--min-p", value])
            elif key == "typical_p": COMMON_PARAMS.extend(["--typical-p", value])
            elif key == "frequency_penalty": COMMON_PARAMS.extend(["--frequency-penalty", value])
            elif key == "presence_penalty": COMMON_PARAMS.extend(["--presence-penalty", value])
            elif key == "repeat_penalty": COMMON_PARAMS.extend(["--repeat-penalty", value])
            elif key == "mirostat" and int(value) > 0:
                COMMON_PARAMS.extend(["--mirostat", value])
            elif key == "mirostat_tau" and int(config.get("mirostat", 0)) > 0:
                COMMON_PARAMS.extend(["--mirostat-tau", value])
            elif key == "mirostat_eta" and int(config.get("mirostat", 0)) > 0:
                COMMON_PARAMS.extend(["--mirostat-eta", value])
            elif key == "dynatemp_range" and float(value) > 0:
                COMMON_PARAMS.extend(["--dynatemp-range", value])
            elif key == "dynatemp_exp" and float(config.get("dynatemp_range", 0)) > 0:
                COMMON_PARAMS.extend(["--dynatemp-exp", value])
            elif key == "xtc_probability" and float(value) > 0:
                COMMON_PARAMS.extend(["--xtc-probability", value])
            elif key == "xtc_threshold" and float(config.get("xtc_probability", 0)) > 0:
                COMMON_PARAMS.extend(["--xtc-threshold", value])
            elif key == "seed":
                COMMON_PARAMS.extend(["--seed", value])
            elif key == "rope_freq_scale" and float(value) != 1.0:
                COMMON_PARAMS.extend(["--rope-scale", value])
            elif key == "numa" and value != "off":
                COMMON_PARAMS.extend(["--numa", value])

        # ─── Multimodal ───────────────────────────────────────────
        use_mmproj = config.get("use_mmproj", "1") in ("1", "true", "yes", "on")

        if (self.current_model.get("multi") and 
            self.current_model["choice"] in MMPROJ_FILES and 
            use_mmproj):
            
            mmproj_file = MMPROJ_FILES[self.current_model["choice"]]
            mmproj_path = os.path.join(SCRIPT_DIR, "models", mmproj_file)
            if os.path.isfile(mmproj_path):
                COMMON_PARAMS.extend(["--mmproj", mmproj_path, "--no-mmproj-offload"])
                self.output_text.insert("end", "👀 Multimodal ativado\n")
            else:
                self.output_text.insert("end", "⚠️ mmproj não encontrado!\n")
        elif self.current_model.get("multi"):
            self.output_text.insert("end", "📄 Modo texto puro (mmproj desativado)\n")

        # ─── MODO CLI ─────────────────────────────────────────────
        if mode == "cli":
            cmd_list = [binary_path] + COMMON_PARAMS + ["--system-prompt", "Você é um assistente útil e amigável que responde apenas em texto plano com emotes. NÃO use notação Markdown, LaTeX ou Mermaid. Responda sempre usando apenas texto plano com emotes pelo terminal."]

            self.output_text.insert("end", "💬 Abrindo terminal separado...\n")
            self.output_text.see("end")

            try:
                if is_windows:
                    # ✅ Versão estável - abre console nativo do Windows
                    creationflags = subprocess.CREATE_NEW_CONSOLE
                    subprocess.Popen(
                        cmd_list,
                        cwd=SCRIPT_DIR,
                        creationflags=creationflags
                    )
                elif platform.system() == "Darwin":
                    shell_cmd = shlex.join(cmd_list)
                    subprocess.Popen(["osascript", "-e", f'tell application "Terminal" to do script "{shell_cmd}"'], cwd=SCRIPT_DIR)
                else:
                    terminals = [["gnome-terminal", "--"], ["xfce4-terminal", "--command"], ["konsole", "-e"], ["xterm", "-e"]]
                    launched = False
                    for term, *args in terminals:
                        if shutil.which(term):
                            subprocess.Popen([term] + args + cmd_list, cwd=SCRIPT_DIR)
                            launched = True
                            break
                    if not launched:
                        subprocess.Popen(cmd_list, cwd=SCRIPT_DIR)

                self.log("Janela do terminal aberta! Use ela para conversar.", level="INFO")
            except Exception as e:
                self.log(f"Falha ao abrir terminal: {e}", level="ERROR")
            return

        # ─── Modo Server (com encoding UTF-8) ─────────────────────
        else:
            # Usa o IP/porta configurado na janela 🔧
            host = self.server_host.get().strip() or "127.0.0.1"
            port = self.server_port.get().strip() or "8080"

            specific_params = ["--host", host, "--port", port]

            api_key = self.server_api_key.get().strip()
            if api_key and host != "127.0.0.1":
                specific_params.extend(["--api-key", api_key])
                self.output_text.insert("end", f"🔐 Proteção ativada com API Key\n")
                self.output_text.insert("end", "✅ Interface web no navegador também protegida!\n")
            elif api_key:
                self.output_text.insert("end", "🔑 API Key ignorada (apenas em IP de rede)\n")

            full_params = COMMON_PARAMS + specific_params

            self.output_text.insert("end", f"🌐 Iniciando servidor em http://{host}:{port}\n")
            self.output_text.insert("end", f"🔧 Comando: {binary_path} {' '.join(full_params)}\n\n")
            self.output_text.see("end")

            try:
                startupinfo = None
                creationflags = 0
                if is_windows:
                    startupinfo = subprocess.STARTUPINFO()
                    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                    creationflags = subprocess.CREATE_NO_WINDOW

                self.process = subprocess.Popen(
                    [binary_path] + full_params,
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',      # ← essencial para português
                    errors='replace',
                    bufsize=1,
                    cwd=SCRIPT_DIR,
                    startupinfo=startupinfo,
                    creationflags=creationflags
                )
                threading.Thread(target=self.read_output, daemon=True).start()
                self.check_output_queue()
                self.update_button_states()

            except Exception as e:
                self.log(f"Erro ao iniciar servidor: {e}", level="ERROR")
                self.update_button_states()
    
# ─── Saída Otimizada ──────────────────────────────────────────
    def read_output(self):
        try:
            for line in iter(self.process.stdout.readline, ''):
                self.output_queue.put(line)
        except:
            pass
        self.output_queue.put(None)
        self.process = None

    def check_output_queue(self):
        try:
            while True:
                line = self.output_queue.get_nowait()
                if line is None:
                    self.output_text.insert("end", "\n🏁 Processo finalizado.\n")
                    self.launch_btn.config(state="normal")
                    self.stop_btn.config(state="disabled")
                    self.process = None
                    self.update_button_states()                    
                    return
                self.output_text.insert("end", line)
                self.output_text.see("end")
        except queue.Empty:
            pass
        if self.process:
            self.after(10, self.check_output_queue)

    def send_input(self, event):
        if self.process and self.process.stdin:
            try:
                msg = self.input_entry.get().strip() + "\n"
                self.process.stdin.write(msg)
                self.process.stdin.flush()
                self.output_text.insert("end", f"> {msg}")
                self.output_text.see("end")
            except:
                pass
            self.input_entry.delete(0, "end")

    def stop_process(self):
        if self.mode_var.get() == "cli":
            showinfo("Aviso", "No modo CLI o processo é controlado pela janela do terminal.\nFeche a janela do terminal para encerrar.")
            return

        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass
            self.process = None
            self.output_text.insert("end", "\n⛔ Servidor interrompido.\n")
            self.output_text.see("end")

        self.launch_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        self.input_entry.pack_forget()

    def clear_output(self):
        self.output_text.delete("1.0", tk.END)
    
    def print_license_header(self):
        """Exibe o cabeçalho + licenças completas na saída assim que o app inicia
           (fica visível no binário PyInstaller mesmo sem arquivos externos)"""
        header = f"""╭─────────────────────────────────────────────────────────────────────────╮
│          🦙 llama Launcher - Versão {version} para Linux e Windows           │
╰─────────────────────────────────────────────────────────────────────────╯

1. Sobre o llamaLauncher (Frontend)

O 🦙 llama Launcher é uma aplicação ultra leve e multiplataforma (testado em Windows e Linux), feito 100% em Python para executar modelos de linguagem (GGUF) com o poderoso llama.cpp. Oferece GUI simplificada com configuração e salvamento de parâmetros, suporte multimodal (mmproj) e aceleração por GPU (se disponível) com foco em privacidade - tudo rodando 100% local no seu computador.

2. Aviso Legal / Disclaimer

O llamaLauncher é um lançador de código aberto que facilita a execução de binários do llama.cpp (projeto MIT do repositório https://github.com/ggml-org/llama.cpp) e de modelos GGUF compatíveis.
O autor não é responsável, de forma alguma, pelo uso que os usuários venham a fazer da ferramenta ou dos modelos carregados por ela.
Em particular, o autor não endossa nem se responsabiliza por:
- Conteúdo gerado pelos modelos (incluindo, mas não limitado a: desinformação, discurso de ódio, conteúdo ilegal, difamação, violação de direitos autorais);
- Uso dos modelos em desacordo com as licenças respectivas; e
- Qualquer dano direto ou indireto causado pelo uso ou pelos outputs gerados.
O software é fornecido "como está", sem garantias de qualquer espécie (expressas ou implícitas), incluindo, mas não se limitando a, garantias de adequação a um propósito específico, não violação de direitos ou funcionamento ininterrupto.
O uso desta ferramenta é de exclusiva responsabilidade do usuário final, que deve respeitar todas as leis aplicáveis, as licenças dos modelos e as políticas de uso aceitável dos provedores originais.

3. Licença do llamaLauncher (Frontend)

MIT License

{Author}

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Veja em: https://opensource.org/licenses/MIT

4. Bibliotecas utilizadas (último acesso aos links das fontes a seguir ocorreu em 08/03/2026)

- os          - módulo da biblioteca padrão do Python que oferece uma interface portátil para funcionalidades dependentes do sistema operacional (manipulação de arquivos/diretórios, variáveis de ambiente, processos etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/os.html e https://docs.python.org/3/license.html.
- sys         - módulo da biblioteca padrão do Python que fornece acesso a parâmetros e funções específicas do interpretador e do sistema (como argumentos de linha de comando, versão do Python, caminhos de busca etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/sys.html e https://docs.python.org/3/license.html.
- subprocess  - módulo que permite gerenciar subprocessos, conectar-se aos seus pipes de entrada/saída/erro e obter seus códigos de retorno. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/subprocess.html e https://docs.python.org/3/license.html.
- threading   - módulo da biblioteca padrão do Python que fornece suporte a programação concorrente baseada em threads. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/threading.html e https://docs.python.org/3/license.html.
- platform    - módulo da biblioteca padrão do Python que fornece informações sobre a plataforma subjacente (sistema operacional, arquitetura, etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/platform.html e https://docs.python.org/3/license.html.
- webbrowser  - módulo da biblioteca padrão do Python que permite abrir URLs em navegadores web de forma portátil. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/webbrowser.html e https://docs.python.org/3/license.html.
- shlex       - módulo da biblioteca padrão do Python para analisar sintaxe estilo shell (dividir comandos em argumentos). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/shlex.html e https://docs.python.org/3/license.html.
- shutil      - módulo da biblioteca padrão do Python que oferece operações de alto nível em arquivos e coleções de arquivos (cópia, movimentação, remoção, arquivamento etc.). Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/shutil.html e https://docs.python.org/3/license.html.
- queue       - módulo da biblioteca padrão do Python que implementa filas thread-safe (FIFO, LIFO, PriorityQueue etc.), muito usado em programação concorrente. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/queue.html e https://docs.python.org/3/license.html.
- json        - módulo da biblioteca padrão do Python para codificação e decodificação de JSON. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/json.html e https://docs.python.org/3/license.html.
- tkinter     - biblioteca de interface gráfica do usuário (GUI) Python de código aberto, incluída na biblioteca padrão. Ela está licenciada sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/tkinter.html e https://docs.python.org/3/license.html.
- PIL         - Pillow (fork amigável do Python Imaging Library - PIL) - biblioteca para processamento e manipulação de imagens. Licenciada sob a HPND (Historical Permission Notice and Disclaimer), equivalente à antiga licença do PIL (MIT-like). Veja em: https://pillow.readthedocs.io/en/stable/ e https://github.com/python-pillow/Pillow/blob/main/LICENSE
- datetime    - módulo da biblioteca padrão do Python para manipulação de datas e horas. Ele está licenciado sob a Python Software Foundation License. Veja em: https://docs.python.org/3/library/datetime.html e https://docs.python.org/3/license.html.

5. Backend license

llama.cpp - Engine de inferência de Large Language Models (LLM) em C/C++ de alto desempenho, com suporte a vários backends (CPU, GPU via CUDA/Metal/Vulkan/etc.) e formato GGUF. É a base principal deste launcher para execução local de modelos de linguagem. Licenciado sob a MIT License. Veja em: https://github.com/ggml-org/llama.cpp e https://github.com/ggml-org/llama.cpp/blob/master/LICENSE

6. Empacotador

pyinstaller - ferramenta que permite empacotar uma aplicação python e todas as suas dependências em um único pacote. Ele está licenciado sob uma licença dual, usando tanto a licença GPL 2.0, com uma exceção que permite usá-lo para construir produtos comerciais e a licença Apache, versão 2.0. Veja em: <https://pyinstaller.org/en/stable/license.html>.
"""
        # Insere no topo da saída (como texto inicial)
        self.output_text.insert("1.0", header + "\n" + "═" * 70 + "\n\n")
        self.output_text.tag_add("license", "1.0", "end")
        self.output_text.tag_config("license", foreground="#888888", font=("Consolas", 9))
        self.output_text.see("1.0")

    def open_browser(self):
        # Sempre lê do config.txt na hora do clique (mais seguro)
        config = self.load_general_config()
        
        host = config.get("server_host", "127.0.0.1").strip()
        port = config.get("server_port", "8080").strip()
        
        # Validação mínima
        if not port.isdigit() or not (1 <= int(port) <= 65535):
            port = "8080"
        
        url = f"http://{host}:{port}"
        
        try:
            api_key = self.server_api_key.get().strip()
            webbrowser.open(url)
            self.output_text.insert("end", f"🌐 Abrindo navegador...\n")
            self.output_text.see("end")
        except Exception as e:
            self.log(f"Não foi possível abrir o navegador: {e}", level="ERROR")

    def save_sash_position(self):
        """Salva a posição do divisor no config.txt"""
        try:
            pos = self.main_paned.sashpos(0)
            self.save_general_config(sash_position=pos)
        except:
            pass

    def load_sash_position(self):
        """Carrega a posição salva do config.txt"""
        config = self.load_general_config()
        try:
            return int(config.get("sash_position", "").strip())
        except:
            return None

    def load_general_config(self):
        """Carrega o config.txt inteiro como dict"""
        config = {}
        path = os.path.join(SCRIPT_DIR, "config.txt")
        if os.path.isfile(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = [x.strip() for x in line.split("=", 1)]
                            config[key] = value
            except:
                pass
        
        # Carrega configurações do servidor
        self.server_host.set(config.get("server_host", "127.0.0.1"))
        self.server_port.set(config.get("server_port", "8080"))
        self.server_api_key.set(config.get("server_api_key", ""))

        # Aplica o last_model se existir
        last_model = config.get("last_model")
        if last_model:
            for disp in self.model_list["values"]:
                if self.get_internal_name(disp) == last_model:
                    self.model_var.set(disp)
                    self.load_selected_model()
                    break

        return config

    def save_general_config(self, **kwargs):
        """Salva itens no config.txt e mantém as variáveis Tkinter sincronizadas"""
        config = self.load_general_config()  # carrega atual (inclui last_model, sash etc.)
        config.update(kwargs)                # aplica as novas alterações

        path = os.path.join(SCRIPT_DIR, "config.txt")
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"# Configurações gerais - {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                for k, v in config.items():
                    f.write(f"{k}={v}\n")
            
            if "server_host" in kwargs:
                self.server_host.set(kwargs["server_host"])
            if "server_port" in kwargs:
                self.server_port.set(kwargs["server_port"])
            if "server_api_key" in kwargs:
                self.server_api_key.set(kwargs["server_api_key"])

            return True
        except Exception as e:
            self.log(f"Falha ao salvar config.txt: {e}", level="ERROR")
            return False

        # ─── Janela de Configuração do Servidor ─────────────────────────────
    def open_settings(self):
        win = tk.Toplevel(self)
        win.title("🔧 Configurações do Servidor")
        win.geometry("450x450")
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        f = ttk.Frame(win, padding=20)
        f.pack(fill="both", expand=True)

        ttk.Label(f, text="IP / Host do servidor:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Combobox(f, textvariable=self.server_host, values=COMMON_IPS, state="readonly", font=("Consolas", 11), width=35).pack(fill="x", pady=(4, 15))

        ttk.Label(f, text="Porta:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Combobox(f, textvariable=self.server_port, values=COMMON_PORTS, state="readonly", font=("Consolas", 11), width=12).pack(anchor="w", pady=(4, 15))

        ttk.Label(f, text="API Key / Senha de acesso (proteção):", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        ttk.Entry(f, textvariable=self.server_api_key, font=("Consolas", 11), width=35, show="*").pack(fill="x", pady=(4, 15))

        ttk.Label(f, text="Sem senha -> Deixe em branco = sem proteção.\nCom senha -> APIs e WebUI no navegador protegidos!", 
                  foreground="#d35400", font=("Segoe UI", 9)).pack(anchor="w", pady=(5, 0))

        ttk.Label(f, text="IP -> 127.0.0.1 = só este PC.\nIP ->     0.0.0.0 = acessível na rede local.",
                  foreground="#555", font=("Segoe UI", 9)).pack(anchor="w", pady=(10, 0))

        # Botões
        btnf = ttk.Frame(f)
        btnf.pack(pady=30, fill="x")

        # Botão Padrão
        ttk.Button(btnf, text="⟲ Padrão", 
                command=self.reset_to_default_settings,
                width=12,
                style="Accent.TButton" if "Accent.TButton" in ttk.Style().theme_use() else "").pack(side="left", padx=1)

        # Espaçador para empurrar os outros botões para a direita
        ttk.Frame(btnf).pack(side="left", fill="x", expand=True)

        # Botão Salvar
        ttk.Button(btnf, text="💾 Salvar", 
                command=lambda: self.save_server_settings(win),
                width=12).pack(side="left", padx=1)

        # Botão Cancelar
        ttk.Button(btnf, text="Cancelar", 
                command=win.destroy,
                width=12).pack(side="right", padx=1)

        # Centraliza a janela
        win.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() - win.winfo_width()) // 2
        y = self.winfo_y() + (self.winfo_height() - win.winfo_height()) // 2
        win.geometry(f"+{x}+{y}")

    def reset_to_default_settings(self):
        """Restaura as configurações para os valores padrão"""
        self.server_host.set("127.0.0.1")
        self.server_port.set("8080")
        self.log("Valores restaurados para o padrão (127.0.0.1:8080)", level="INFO")
        self.server_api_key.set("")

    def save_server_settings(self, window):
        """Valida e salva IP/Porta na janela de configurações"""
        host = self.server_host.get().strip()
        port = self.server_port.get().strip()   # ← agora definimos aqui (sem validação)
        key = self.server_api_key.get().strip()
        
        if host != "127.0.0.1" and not key:
            if not messagebox.askyesno("⚠️ Segurança", "IP de rede sem API Key!\nO servidor ficará aberto para qualquer um.\nContinuar mesmo assim?"):
                return

        # Salva (agora as variáveis ficam sincronizadas)
        if self.save_general_config(server_host=host, server_port=port, server_api_key=key):
            self.log(f"Configurações do servidor atualizadas!\n\nhttp://{host}:{port}", level="SUCCESS")
            window.destroy()
        else:
            self.log("Falha ao salvar o arquivo config.txt", level="ERROR")

    def set_initial_sash(self):
        """Define posição inicial (salva ou padrão)"""
        # Espera a janela estar totalmente desenhada
        total_height = self.winfo_height()
        if total_height < 500:
            self.after(50, self.set_initial_sash)
            return

        saved = self.load_sash_position()
        if saved and 250 < saved < total_height - 180:
            self.main_paned.sashpos(0, saved)
        else:
            # 73% para configurações (ótimo equilíbrio)
            default_pos = int(total_height * 0.73)
            self.main_paned.sashpos(0, default_pos)

    def on_closing(self):
        self.save_sash_position()        
        if self.process:
            self.stop_process()
        self.destroy()

if __name__ == "__main__":
    app = llamaLauncher()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
