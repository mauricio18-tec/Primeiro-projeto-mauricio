import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
import time
import webbrowser
from datetime import datetime
from fpdf import FPDF
import os
from collections import defaultdict

# Configurações globais
CONFIG = {
    'cores': {
        'fundo': "#1e1e1e",
        'texto': "#ffffff",
        'botao': "#4caf50",
        'botao_sec': "#2196f3",
        'botao_ter': "#9c27b0",
        'erro': "#f44336",
        'destaque': "#ff9800",
        'entrada': "#3d3d3d",
        'favorito': "#ffeb3b"
    },
    'fontes': {
        'principal': ("Helvetica", 12, "bold"),
        'titulo': ("Helvetica", 14, "bold")
    },
    'unidades': ["g", "kg", "mg", "ml", "l", "xícara", "colher de sopa", 
                "colher de chá", "unidades", "pitada", "a gosto", "oz", "lb"],
    'categorias': ["Geral", "Sobremesas", "Massas", "Carnes", "Vegetariano", "Vegano", "Bebidas"],
    'dados_nutricionais': {
        "Farinha": {"calorias": 364, "carboidratos": 76, "proteinas": 10, "gorduras": 1},
        "Açúcar": {"calorias": 387, "carboidratos": 100, "proteinas": 0, "gorduras": 0},
        # Adicione mais ingredientes aqui
    }
}

# Classe para gerenciar temporizador
class TimerManager:
    def __init__(self, root):
        self.root = root
        self.timers = []
        self.next_id = 1
        
    def add_timer(self, minutes, descricao):
        timer_id = self.next_id
        self.next_id += 1
        end_time = time.time() + minutes * 60
        self.timers.append({
            'id': timer_id,
            'end_time': end_time,
            'descricao': descricao,
            'running': True
        })
        self.update_timers()
        return timer_id
        
    def update_timers(self):
        now = time.time()
        for timer in self.timers[:]:
            if timer['running'] and now >= timer['end_time']:
                messagebox.showinfo("Timer Concluído", f"Timer #{timer['id']}: {timer['descricao']}")
                timer['running'] = False
                
        self.timers = [t for t in self.timers if t['running']]
        if self.timers:
            self.root.after(1000, self.update_timers)

# Classe para gerar PDF
class PDFGenerator(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'Livro de Receitas', 0, 1, 'C')
        
    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(4)
        
    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 8, body)
        self.ln()

# Classe principal da aplicação
class ReceitaApp:
    def __init__(self, root):
        self.root = root
        self.timer_manager = TimerManager(root)
        self.favoritos = self.carregar_favoritos()
        self.configurar_janela()
        self.criar_widgets()
        self.receita = Receita("Nova Receita")
        self.carregar_categorias()
        
    def configurar_janela(self):
        self.root.title("Super Calculadora de Receitas")
        self.root.geometry("850x950")
        self.root.configure(bg=CONFIG['cores']['fundo'])
        self.root.minsize(800, 900)
        
        for i in range(5):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(8):
            self.root.grid_rowconfigure(i, weight=1)
    
    def criar_widgets(self):
        # Painéis principais
        self.criar_painel_insercao()
        self.criar_painel_numerico()
        self.criar_controle_rendimento()
        self.criar_painel_categoria()
        self.criar_painel_modo_preparo()
        self.criar_painel_timer()
        self.criar_painel_nutricional()
        self.criar_botoes_gerenciamento()
        
    def criar_painel_timer(self):
        frame = tk.Frame(self.root, bg=CONFIG['cores']['fundo'], bd=2, relief="groove")
        frame.grid(row=6, column=0, columnspan=5, padx=10, pady=5, sticky="ew")
        
        tk.Label(frame, text="Timer de Preparo:", font=CONFIG['fontes']['titulo'], 
                bg=CONFIG['cores']['fundo'], fg=CONFIG['cores']['texto']).pack(pady=5)
                
        subframe = tk.Frame(frame, bg=CONFIG['cores']['fundo'])
        subframe.pack(pady=5)
        
        tk.Label(subframe, text="Minutos:", font=CONFIG['fontes']['principal'], 
                bg=CONFIG['cores']['fundo'], fg=CONFIG['cores']['texto']).grid(row=0, column=0)
        
        self.timer_minutos = tk.Entry(subframe, font=CONFIG['fontes']['principal'], 
                                     width=5, bg=CONFIG['cores']['entrada'], fg=CONFIG['cores']['texto'])
        self.timer_minutos.grid(row=0, column=1, padx=5)
        
        tk.Label(subframe, text="Descrição:", font=CONFIG['fontes']['principal'], 
                bg=CONFIG['cores']['fundo'], fg=CONFIG['cores']['texto']).grid(row=0, column=2)
        
        self.timer_desc = tk.Entry(subframe, font=CONFIG['fontes']['principal'], 
                                  width=20, bg=CONFIG['cores']['entrada'], fg=CONFIG['cores']['texto'])
        self.timer_desc.grid(row=0, column=3, padx=5)
        
        tk.Button(frame, text="Iniciar Timer", font=CONFIG['fontes']['principal'], 
                 bg=CONFIG['cores']['botao_ter'], fg=CONFIG['cores']['texto'],
                 command=self.iniciar_timer).pack(pady=5)
    
    def iniciar_timer(self):
        try:
            minutos = int(self.timer_minutos.get())
            descricao = self.timer_desc.get()
            if minutos <= 0:
                raise ValueError("Tempo deve ser positivo")
                
            timer_id = self.timer_manager.add_timer(minutos, descricao)
            messagebox.showinfo("Timer Iniciado", 
                              f"Timer #{timer_id} para '{descricao}' iniciado por {minutos} minutos")
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")
    
    def criar_painel_nutricional(self):
        frame = tk.Frame(self.root, bg=CONFIG['cores']['fundo'], bd=2, relief="groove")
        frame.grid(row=7, column=0, columnspan=5, padx=10, pady=5, sticky="ew")
        
        tk.Label(frame, text="Informação Nutricional:", font=CONFIG['fontes']['titulo'], 
                bg=CONFIG['cores']['fundo'], fg=CONFIG['cores']['texto']).pack(pady=5)
                
        self.nutricional_text = tk.Text(frame, font=CONFIG['fontes']['principal'], 
                                       width=80, height=6, bg=CONFIG['cores']['entrada'], 
                                       fg=CONFIG['cores']['texto'], state='disabled')
        self.nutricional_text.pack(padx=5, pady=5)
        
        tk.Button(frame, text="Calcular Valores Nutricionais", font=CONFIG['fontes']['principal'], 
                 bg=CONFIG['cores']['botao_sec'], fg=CONFIG['cores']['texto'],
                 command=self.calcular_nutricional).pack(pady=5)
    
    def calcular_nutricional(self):
        totais = {
            'calorias': 0,
            'carboidratos': 0,
            'proteinas': 0,
            'gorduras': 0
        }
        
        for ingrediente in self.receita.ingredientes:
            nome = ingrediente.nome.lower()
            for chave, dados in CONFIG['dados_nutricionais'].items():
                if chave.lower() in nome:
                    fator = ingrediente.quantidade / 100  # Valores nutricionais são por 100g
                    totais['calorias'] += dados['calorias'] * fator
                    totais['carboidratos'] += dados['carboidratos'] * fator
                    totais['proteinas'] += dados['proteinas'] * fator
                    totais['gorduras'] += dados['gorduras'] * fator
                    break
        
        texto = (f"Calorias: {totais['calorias']:.1f}kcal\n"
                 f"Carboidratos: {totais['carboidratos']:.1f}g\n"
                 f"Proteínas: {totais['proteinas']:.1f}g\n"
                 f"Gorduras: {totais['gorduras']:.1f}g\n\n"
                 f"Por {self.receita.rendimento} porção(ões)")
        
        self.nutricional_text.config(state='normal')
        self.nutricional_text.delete(1.0, tk.END)
        self.nutricional_text.insert(1.0, texto)
        self.nutricional_text.config(state='disabled')
    
    def gerar_pdf(self):
        if not self.receita.ingredientes:
            messagebox.showerror("Erro", "Nenhuma receita para exportar")
            return
            
        pdf = PDFGenerator()
        pdf.add_page()
        
        # Cabeçalho
        pdf.chapter_title(f"{self.receita.nome} ({self.receita.categoria})")
        
        # Ingredientes
        ingredientes = "\n".join(str(i) for i in self.receita.ingredientes)
        pdf.chapter_body(f"Ingredientes ({self.receita.rendimento} porções):\n{ingredientes}")
        
        # Modo de preparo
        if self.receita.modo_preparo:
            pdf.chapter_body(f"Modo de Preparo:\n{self.receita.modo_preparo}")
        
        # Informação nutricional (se disponível)
        if self.nutricional_text.get(1.0, tk.END).strip():
            pdf.chapter_body(f"Informação Nutricional por porção:\n{self.nutricional_text.get(1.0, tk.END)}")
        
        # Salvar arquivo
        nome_arquivo = f"Receita_{self.receita.nome.replace(' ', '_')}.pdf"
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=nome_arquivo,
            filetypes=[("PDF Files", "*.pdf")]
        )
        
        if arquivo:
            pdf.output(arquivo)
            messagebox.showinfo("Sucesso", f"Receita exportada para PDF!\n{arquivo}")
            if messagebox.askyesno("Abrir PDF", "Deseja abrir o PDF gerado?"):
                webbrowser.open(arquivo)
    
    def toggle_favorito(self):
        if not self.receita.nome or self.receita.nome == "Nova Receita":
            messagebox.showerror("Erro", "Salve a receita antes de favoritar")
            return
            
        if self.receita.nome in self.favoritos:
            self.favoritos.remove(self.receita.nome)
            messagebox.showinfo("Info", "Receita removida dos favoritos")
        else:
            self.favoritos.append(self.receita.nome)
            messagebox.showinfo("Info", "Receita adicionada aos favoritos")
            
        self.salvar_favoritos()
        self.atualizar_botao_favorito()
    
    def atualizar_botao_favorito(self):
        cor = CONFIG['cores']['favorito'] if self.receita.nome in self.favoritos else CONFIG['cores']['botao']
        texto = "★ Desfavoritar" if self.receita.nome in self.favoritos else "☆ Favoritar"
        self.botao_favorito.config(bg=cor, text=texto)
    
    def carregar_favoritos(self):
        try:
            with open('favoritos.json', 'r') as f:
                return json.load(f)
        except:
            return []
    
    def salvar_favoritos(self):
        with open('favoritos.json', 'w') as f:
            json.dump(self.favoritos, f)

# ... (mantenha as outras classes e funções como Ingrediente, Receita, etc.)

def main():
    root = tk.Tk()
    app = ReceitaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()