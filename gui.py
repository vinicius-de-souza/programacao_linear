import tkinter as tk
from tkinter import filedialog, scrolledtext
import implementacao_modelagem  # Assumindo que ambos os arquivos estão no mesmo diretório
import threading

class FreightOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Frete")
        
        # Definir tamanho inicial da janela
        self.root.geometry('610x450')
        
        # Centralizar a janela
        self.center_window()

        # Frame para o Status
        status_frame = tk.Frame(root, padx=10, pady=5)
        status_frame.pack(anchor="w")

        # Label do Status
        status_label = tk.Label(status_frame, text="Status:", anchor="w")
        status_label.pack(side=tk.LEFT)

        # Área de Texto do Status (somente leitura)
        self.status_text = tk.Text(status_frame, width=20, height=1, state=tk.DISABLED, bg="white", relief=tk.SUNKEN, bd=1)
        self.status_text.pack(side=tk.LEFT, padx=5)

        # Frame para a área de texto com margem
        text_frame = tk.Frame(root, padx=10, pady=5)
        text_frame.pack(pady=5)

        # Saída do Console
        self.console = scrolledtext.ScrolledText(text_frame, width=80, height=20)
        self.console.pack(padx=1, pady=1)

        # Frame dos Botões
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        # Botões
        self.attach_button = tk.Button(button_frame, text="Anexar Arquivos", command=self.attach_files, width=15, height=2)
        self.attach_button.pack(side=tk.LEFT, padx=5)

        self.solve_button = tk.Button(button_frame, text="Resolver", command=self.solve_problem, state=tk.DISABLED, width=15, height=2)
        self.solve_button.pack(side=tk.LEFT, padx=5)

        self.clear_button = tk.Button(button_frame, text="Limpar", command=self.clear_results, width=15, height=2)
        self.clear_button.pack(side=tk.LEFT, padx=5)

        # Armazenar caminhos dos arquivos
        self.file_paths = {}

        # Definir status inicial
        self.update_status("Pronto", "black")

    def center_window(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    def attach_files(self):
        file_types = [("Arquivos CSV", "*.csv")]
        files = filedialog.askopenfilenames(title="Selecione Arquivos CSV", filetypes=file_types)
        
        for file in files:
            if "Mapa030723" in file:
                self.file_paths['pedidos'] = file
            elif "valores_internos" in file:
                self.file_paths['valores_internos'] = file
            elif "valores_terceirizada" in file:
                self.file_paths['valores_terceirizada'] = file
            elif "base_de_caminhoes" in file:
                self.file_paths['caminhoes'] = file

        self.console.insert(tk.END, "Arquivos anexados\n\n")
        if len(self.file_paths) == 4:
            self.solve_button.config(state=tk.NORMAL)
        else:
            self.console.insert(tk.END, "Por favor, anexe todos os arquivos necessários.\n\n")

    def solve_problem(self):
        self.console.insert(tk.END, "Executando solver...\n\n")
        self.console.yview(tk.END)
        
        # Desabilitar botões enquanto resolve
        self.solve_button.config(state=tk.DISABLED)
        self.attach_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

        # Atualizar status para "Carregando..."
        self.update_status("Carregando...", "black")

        def run_solver():
            try:
                result = implementacao_modelagem.run_solver(
                    self.file_paths['pedidos'],
                    self.file_paths['valores_internos'],
                    self.file_paths['valores_terceirizada'],
                    self.file_paths['caminhoes']
                )
                self.console.insert(tk.END, f"{result}\n\n")
                self.update_status("Sucesso", "green", border_color="green")
            except Exception as e:
                self.console.insert(tk.END, f"Erro: {str(e)}\n\n")
                self.update_status("Erro", "red")
            finally:
                # Reabilitar botões
                self.attach_button.config(state=tk.NORMAL)
                self.clear_button.config(state=tk.NORMAL)
                if len(self.file_paths) == 4:
                    self.solve_button.config(state=tk.NORMAL)

            self.console.yview(tk.END)

        # Executar o solver em uma thread separada para manter a GUI responsiva
        threading.Thread(target=run_solver).start()

    def clear_results(self):
        self.console.delete(1.0, tk.END)
        self.file_paths.clear()
        self.solve_button.config(state=tk.DISABLED)
        self.update_status("Pronto", "black")

    def update_status(self, message, color, border_color=None):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, message)
        self.status_text.config(state=tk.DISABLED, fg=color)
        if border_color:
            self.status_text.config(highlightbackground=border_color, highlightcolor=border_color, highlightthickness=1)
        else:
            self.status_text.config(highlightthickness=0)

if __name__ == "__main__":
    root = tk.Tk()
    app = FreightOptimizerGUI(root)
    root.mainloop()