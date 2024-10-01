import tkinter as tk
from tkinter import filedialog, scrolledtext
from tkinter import ttk  # Import ttk for styling
from ttkthemes import ThemedTk  # Import ThemedTk for additional themes
import implementacao_modelagem  # Assuming both files are in the same directory
import threading

class FreightOptimizerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Otimização de Frete")
        
        # Set initial window size
        self.root.geometry('610x500')
        
        # Center the window
        self.center_window()

        # Create a style object
        self.style = ttk.Style()
        self.style.theme_use('yaru')  # You can choose 'clam', 'alt', 'default', or 'classic'

        # Define styles
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Custom.TEntry', relief="flat", padding=5, background="white", bordercolor="#d3d3d3", borderwidth=1)

        # Frame for Status
        status_frame = ttk.Frame(root, padding=(15, 15, 10, 0))
        status_frame.pack(anchor="w")

        # Label for Status
        status_label = ttk.Label(status_frame, text="Status:", anchor="w")
        status_label.pack(side=tk.LEFT)

        # Entry field for Status
        self.status_text = ttk.Entry(status_frame, width=20, style="Custom.TEntry", state="readonly", font=('Arial', 10))
        self.status_text.pack(side=tk.LEFT, padx=5)

        # Frame for text area with border and padding
        text_frame = ttk.Frame(root, padding=(5, 5), style="Custom.TFrame")
        text_frame.pack(pady=5, expand=True, fill="both")

        # ScrolledText with a border around it
        self.console_frame = ttk.Frame(text_frame, padding=1, style="Custom.TFrame")
        self.console_frame.pack(expand=True, fill="both")
        
        # Text area
        self.console = scrolledtext.ScrolledText(self.console_frame, wrap=tk.WORD, borderwidth=1, relief=tk.FLAT, width=80, height=20, highlightbackground="#c6cace", highlightcolor="#c6cace", highlightthickness=1)
        self.console.pack(padx=5, pady=5, fill="both", expand=True)

        # Frame for Buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(fill=tk.X, pady=(0, 15))

        # Left-aligned button frame
        left_button_frame = ttk.Frame(button_frame)
        left_button_frame.pack(side=tk.LEFT)

        # Right-aligned button frame
        right_button_frame = ttk.Frame(button_frame)
        right_button_frame.pack(side=tk.RIGHT)

        # Buttons
        self.attach_button = ttk.Button(left_button_frame, text="Anexar Arquivos", command=self.attach_files, width=15)
        self.attach_button.pack(side=tk.LEFT, padx=15)

        self.solve_button = ttk.Button(left_button_frame, text="Resolver", command=self.solve_problem, state=tk.DISABLED, width=15)
        self.solve_button.pack(side=tk.LEFT, padx=15)

        self.clear_button = ttk.Button(right_button_frame, text="Limpar", command=self.clear_results, width=15)
        self.clear_button.pack(side=tk.RIGHT, padx=(0, 35))

        # Store file paths
        self.file_paths = {}

        # Set initial status
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
        
        # Disable buttons while solving
        self.solve_button.config(state=tk.DISABLED)
        self.attach_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)

        # Update status to "Loading..."
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
                # Re-enable buttons
                self.attach_button.config(state=tk.NORMAL)
                self.clear_button.config(state=tk.NORMAL)
                if len(self.file_paths) == 4:
                    self.solve_button.config(state=tk.NORMAL)

            self.console.yview(tk.END)

        # Run the solver in a separate thread to keep the GUI responsive
        threading.Thread(target=run_solver).start()

    def clear_results(self):
        self.console.delete(1.0, tk.END)
        self.file_paths.clear()
        self.solve_button.config(state=tk.DISABLED)
        self.update_status("Pronto", "black")

    def update_status(self, message, color, border_color=None):
        self.status_text.config(state="normal")
        self.status_text.delete(0, tk.END)
        self.status_text.insert(0, message)
        self.status_text.config(state="readonly")

if __name__ == "__main__":
    root = ThemedTk(theme="yaru")  # Use ThemedTk and set a theme
    app = FreightOptimizerGUI(root)
    root.mainloop()
