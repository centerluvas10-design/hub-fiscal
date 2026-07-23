import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import sys
import webbrowser
from pathlib import Path

# Obtém o diretório onde o hub está a correr
BASE_DIR = Path(__file__).resolve().parent

class HubFiscalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Plataforma de Automação Fiscal")
        self.root.geometry("850x600")
        self.root.configure(bg="#f4f6f9")
        
        # Estilos do Painel
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure("TFrame", background="#f4f6f9")
        self.style.configure("Title.TLabel", font=("Segoe UI", 20, "bold"), background="#f4f6f9", foreground="#2c3e50")
        self.style.configure("Subtitle.TLabel", font=("Segoe UI", 10), background="#f4f6f9", foreground="#7f8c8d")
        
        self._build_ui()

    def _build_ui(self):
        # Cabeçalho / Header
        header_frame = ttk.Frame(self.root)
        header_frame.pack(fill="x", pady=(30, 20), padx=40)
        
        ttk.Label(header_frame, text="🏛️ Hub de Automação Fiscal", style="Title.TLabel").pack(anchor="w")
        ttk.Label(header_frame, text="Selecione a ferramenta que deseja iniciar do seu ecossistema.", style="Subtitle.TLabel").pack(anchor="w", pady=(5,0))

        # Contentor para os cartões (Grid de Botões)
        grid_frame = ttk.Frame(self.root)
        grid_frame.pack(fill="both", expand=True, padx=40)

        # Definição e mapeamento das ferramentas do ecossistema
        ferramentas = [
            {
                "nome": "Processador NFC-e / NF-e (Planilhas)",
                "desc": "Interface Web para extrair chaves e valores de planilhas.",
                "tipo": "web",
                "arquivo": "nfce_nfe_processor_v8.html",
                "icone": "🌐"
            },
            {
                "nome": "Organizador de DANFEs",
                "desc": "Organiza PDFs e XMLs em pastas por CNPJ e Mês/Ano.",
                "tipo": "python",
                "arquivo": "organizar_danfes.py",
                "icone": "📁"
            },
            {
                "nome": "Conversor XML NFS-e para PDF",
                "desc": "Gera PDFs no layout da Prefeitura a partir de XMLs ABRASF.",
                "tipo": "python",
                "arquivo": "nfse_xml_to_pdf.py",
                "icone": "📄"
            },
            {
                "nome": "Processador NF-e por CFOP",
                "desc": "Lê PDFs de notas e separa em pastas baseadas em regras de CFOP/NCM.",
                "tipo": "python",
                "arquivo": "processador_nfe por cfop.py",
                "icone": "🗂️"
            },
            {
                "nome": "Atualizador de Faturamento",
                "desc": "Lê PDF de falecidos e atualiza valores na planilha do Excel.",
                "tipo": "python",
                "arquivo": "atualizar_faturamento.py",
                "icone": "📊"
            },
            {
                "nome": "Robô FSist (Download XML)",
                "desc": "Automação com Chrome para baixar XMLs em lote via FSist.",
                "tipo": "python",
                "arquivo": "robo_fsist_v2.py",
                "icone": "🤖"
            },
            {
                "nome": "Disparador Fiscal (Cobrança E-mail)",
                "desc": "Dispara e-mails solicitando protocolo de faturamento às filiais.",
                "tipo": "python",
                "arquivo": "disparador_fiscal_dezenas.py",
                "icone": "✉️"
            }
        ]

        # Geração dinâmica do grid de ferramentas (2 colunas)
        row, col = 0, 0
        for item in ferramentas:
            self._criar_cartao(grid_frame, item, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

        # Rodapé / Footer
        footer = ttk.Frame(self.root)
        footer.pack(side="bottom", fill="x", pady=10)
        ttk.Label(footer, text="Ambiente Integrado - Grupo Anjo da Guarda", font=("Segoe UI", 8), background="#f4f6f9", foreground="#bdc3c7").pack()

    def _criar_cartao(self, parent, item, row, col):
        # Frame do cartão interativo
        card = tk.Frame(parent, bg="white", highlightbackground="#e0e6ed", highlightthickness=1, padx=15, pady=15, cursor="hand2")
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        
        # Faz as colunas expandirem de forma proporcional
        parent.columnconfigure(col, weight=1)
        
        # Ícone e Título da ferramenta
        top_frame = tk.Frame(card, bg="white")
        top_frame.pack(fill="x")
        tk.Label(top_frame, text=item["icone"], font=("Segoe UI", 18), bg="white").pack(side="left", padx=(0, 10))
        tk.Label(top_frame, text=item["nome"], font=("Segoe UI", 11, "bold"), fg="#2c3e50", bg="white").pack(side="left")
        
        # Descrição do que a ferramenta faz
        tk.Label(card, text=item["desc"], font=("Segoe UI", 9), fg="#7f8c8d", bg="white", wraplength=300, justify="left").pack(fill="x", pady=(10, 0), anchor="w")

        # Efeitos visuais de Hover e Clique
        def on_enter(e):
            card.config(highlightbackground="#3498db")
        def on_leave(e):
            card.config(highlightbackground="#e0e6ed")
        def on_click(e):
            self._executar_ferramenta(item)

        # Associa os eventos a todos os elementos dentro do cartão
        for widget in [card] + card.winfo_children() + top_frame.winfo_children():
            widget.bind("<Enter>", on_enter)
            widget.bind("<Leave>", on_leave)
            widget.bind("<Button-1>", on_click)

    def _executar_ferramenta(self, item):
        caminho_base = BASE_DIR / item["arquivo"]
        
        try:
            # Caso seja ferramenta Web (HTML)
            if item["tipo"] == "web":
                if not caminho_base.exists():
                    messagebox.showerror("Erro", f"Ficheiro não encontrado:\n{caminho_base}")
                    return
                webbrowser.open(caminho_base.as_uri())
            
            # Caso seja um script Python
            elif item["tipo"] == "python":
                # Verifica se há uma versão compilada (.exe) na mesma pasta
                caminho_exe = caminho_base.with_suffix('.exe')
                comando = []
                
                if caminho_exe.exists():
                    comando = [str(caminho_exe)] 
                elif caminho_base.exists():
                    # Se o hub estiver congelado (.exe), usamos o interpretador 'python' do sistema
                    python_cmd = "python" if getattr(sys, 'frozen', False) else sys.executable
                    comando = [python_cmd, caminho_base.name] 
                else:
                    messagebox.showerror("Erro", f"Ficheiro não encontrado.\nEsperava encontrar:\n- {caminho_exe.name}\n- {caminho_base.name}")
                    return

                # Inicializa o processo abrindo um terminal de forma segura nas diferentes plataformas
                if sys.platform == "win32":
                    flags = getattr(subprocess, 'CREATE_NEW_CONSOLE', 0x00000010)
                    subprocess.Popen(comando, cwd=BASE_DIR, creationflags=flags)
                elif sys.platform == "darwin":  # macOS
                    if caminho_exe.exists():
                        subprocess.Popen(["open", "-a", "Terminal", str(caminho_exe)], cwd=BASE_DIR)
                    else:
                        py_cmd = "python3" if getattr(sys, 'frozen', False) else sys.executable
                        os.system(f"osascript -e 'tell application \"Terminal\" to do script \"{py_cmd} \\\"{caminho_base}\\\"\"'")
                else:  # Linux
                    subprocess.Popen(comando, cwd=BASE_DIR)
                    
                messagebox.showinfo("A Iniciar", f"A ferramenta '{item['nome']}' foi iniciada com sucesso.")
                
        except Exception as e:
            messagebox.showerror("Erro ao Executar", f"Ocorreu um erro ao tentar abrir a ferramenta:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HubFiscalApp(root)
    root.mainloop()