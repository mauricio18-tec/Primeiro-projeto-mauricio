import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import json
from collections import defaultdict

# Configurações de cores e fontes
COR_FUNDO = "#1e1e1e"
COR_TEXTO = "#ffffff"
COR_BOTAO = "#4caf50"
COR_BOTAO_SECUNDARIO = "#2196f3"
COR_BOTAO_TERCIARIO = "#9c27b0"
COR_BOTAO_ERRO = "#f44336"
COR_ENTRADA = "#3d3d3d"
COR_DESTAQUE = "#ff9800"

FONTE_PRINCIPAL = ("Helvetica", 12, "bold")
FONTE_TITULO = ("Helvetica", 14, "bold")

# Dados de conversão de unidades (gramas para outras unidades)
CONVERSAO_UNIDADES = {
    'g': {
        'kg': lambda x: x / 1000,
        'mg': lambda x: x * 1000,
        'oz': lambda x: x * 0.035274,
        'lb': lambda x: x * 0.00220462
    },
    'ml': {
        'l': lambda x: x / 1000,
        'xícara': lambda x: x / 240,
        'colher de sopa': lambda x: x / 15,
        'colher de chá': lambda x: x / 5
    }
}

UNIDADES_PADRAO = ["g", "kg", "mg", "ml", "l", "xícara", 
                  "colher de sopa", "colher de chá", "unidades", 
                  "pitada", "a gosto", "oz", "lb"]

CATEGORIAS = ["Geral", "Sobremesas", "Massas", "Carnes", "Vegetariano", "Vegano", "Bebidas"]

class Ingrediente:
    def __init__(self, nome, quantidade, unidade):
        self.nome = nome.strip()
        self.quantidade = quantidade
        self.unidade = unidade.strip()

    def __str__(self):
        return f"{self.quantidade} {self.unidade} de {self.nome}"
    
    def to_dict(self):
        return {
            "nome": self.nome,
            "quantidade": self.quantidade,
            "unidade": self.unidade
        }

class Receita:
    def __init__(self, nome, ingredientes=None, rendimento=1, categoria="Geral", modo_preparo=""):
        self.nome = nome.strip()
        self.ingredientes = ingredientes if ingredientes else []
        self.rendimento = rendimento
        self.rendimento_original = rendimento
        self.categoria = categoria
        self.modo_preparo = modo_preparo

    def ajustar_porcoes(self, novo_rendimento):
        if self.rendimento <= 0 or novo_rendimento <= 0:
            raise ValueError("Rendimento deve ser positivo")
            
        fator = novo_rendimento / self.rendimento
        for ingrediente in self.ingredientes:
            if self._deve_arredondar_inteiro(ingrediente):
                ingrediente.quantidade = round(ingrediente.quantidade * fator)
            else:
                ingrediente.quantidade = round(ingrediente.quantidade * fator, 2)
        
        self.rendimento = novo_rendimento

    def _deve_arredondar_inteiro(self, ingrediente):
        unidades_inteiras = ["unidade", "un", "unidades", "ovo", "ovos"]
        return any(unidade in ingrediente.unidade.lower() for unidade in unidades_inteiras)

    def converter_ingrediente(self, index, nova_unidade):
        if index < 0 or index >= len(self.ingredientes):
            return False
            
        ingrediente = self.ingredientes[index]
        
        if ingrediente.unidade == nova_unidade:
            return False
            
        try:
            if ingrediente.unidade in CONVERSAO_UNIDADES and nova_unidade in CONVERSAO_UNIDADES[ingrediente.unidade]:
                conversao = CONVERSAO_UNIDADES[ingrediente.unidade][nova_unidade]
                ingrediente.quantidade = round(conversao(ingrediente.quantidade), 2)
                ingrediente.unidade = nova_unidade
                return True
        except:
            return False
            
        return False

    def exibir_receita(self):
        return "\n".join(str(ingrediente) for ingrediente in self.ingredientes)
    
    def to_dict(self):
        return {
            "nome": self.nome,
            "ingredientes": [ing.to_dict() for ing in self.ingredientes],
            "rendimento": self.rendimento,
            "categoria": self.categoria,
            "modo_preparo": self.modo_preparo
        }

    @classmethod
    def from_dict(cls, data):
        ingredientes = [
            Ingrediente(ing['nome'], ing['quantidade'], ing['unidade']) 
            for ing in data['ingredientes']
        ]
        rendimento = data.get('rendimento', 1)
        categoria = data.get('categoria', "Geral")
        modo_preparo = data.get('modo_preparo', "")
        return cls(data['nome'], ingredientes, rendimento, categoria, modo_preparo)

class ReceitaApp:
    def __init__(self, root):
        self.root = root
        self._configurar_janela()
        self._criar_widgets()
        self.receita = Receita("Nova Receita")
        self._configurar_redimensionamento()
        self.carregar_categorias()

    def carregar_categorias(self):
        try:
            with open('categorias.json', 'r', encoding='utf-8') as f:
                self.categorias = json.load(f)
        except:
            self.categorias = CATEGORIAS
            self.salvar_categorias()

    def salvar_categorias(self):
        with open('categorias.json', 'w', encoding='utf-8') as f:
            json.dump(self.categorias, f, ensure_ascii=False, indent=2)

    # ... (mantenha os métodos existentes de _configurar_janela, _configurar_redimensionamento) ...

    def _criar_widgets(self):
        self._criar_painel_insercao()
        self._criar_painel_numerico()
        self._criar_controle_rendimento()
        self._criar_botoes_gerenciamento()
        self._criar_painel_categoria()
        self._criar_painel_modo_preparo()
        
    def _criar_painel_categoria(self):
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=4, column=0, columnspan=4, padx=10, pady=5, sticky="ew")

        tk.Label(frame, text="Categoria:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=0, sticky="w")

        self.categoria_var = tk.StringVar(value="Geral")
        self.combo_categoria = ttk.Combobox(frame, textvariable=self.categoria_var, 
                                          values=self.categorias, font=FONTE_PRINCIPAL)
        self.combo_categoria.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        tk.Button(frame, text="+", font=FONTE_PRINCIPAL, width=3,
                bg=COR_BOTAO_TERCIARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.adicionar_categoria).grid(row=0, column=2, padx=5, pady=5)

    def _criar_painel_modo_preparo(self):
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")

        tk.Label(frame, text="Modo de Preparo:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=0, sticky="w")

        self.modo_preparo_text = tk.Text(frame, font=FONTE_PRINCIPAL, width=50, height=8,
                                       bg=COR_ENTRADA, fg=COR_TEXTO, insertbackground="white")
        self.modo_preparo_text.grid(row=1, column=0, columnspan=3, padx=5, pady=5, sticky="ew")

        scroll = tk.Scrollbar(frame, command=self.modo_preparo_text.yview)
        scroll.grid(row=1, column=3, sticky="ns")
        self.modo_preparo_text.config(yscrollcommand=scroll.set)

        tk.Button(frame, text="Salvar Modo de Preparo", font=FONTE_PRINCIPAL,
                bg=COR_BOTAO_SECUNDARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.salvar_modo_preparo).grid(row=2, column=0, columnspan=4, pady=5, sticky="ew")

    def adicionar_categoria(self):
        nova_categoria = simpledialog.askstring("Nova Categoria", "Digite o nome da nova categoria:")
        if nova_categoria and nova_categoria.strip() and nova_categoria.strip() not in self.categorias:
            self.categorias.append(nova_categoria.strip())
            self.combo_categoria['values'] = self.categorias
            self.categoria_var.set(nova_categoria.strip())
            self.salvar_categorias()

    def salvar_modo_preparo(self):
        self.receita.modo_preparo = self.modo_preparo_text.get("1.0", tk.END).strip()
        messagebox.showinfo("Sucesso", "Modo de preparo salvo com sucesso!")

    def carregar_modo_preparo(self):
        self.modo_preparo_text.delete("1.0", tk.END)
        self.modo_preparo_text.insert("1.0", self.receita.modo_preparo)

    def converter_unidade(self):
        selecionado = self.lista_ingredientes.curselection()
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um ingrediente para converter.")
            return
            
        index = selecionado[0]
        ingrediente = self.receita.ingredientes[index]
        
        unidades_disponiveis = []
        if ingrediente.unidade in CONVERSAO_UNIDADES:
            unidades_disponiveis = list(CONVERSAO_UNIDADES[ingrediente.unidade].keys())
        
        if not unidades_disponiveis:
            messagebox.showinfo("Informação", f"Não há conversões disponíveis para {ingrediente.unidade}")
            return
            
        nova_unidade = simpledialog.askstring(
            "Converter Unidade", 
            f"Converter {ingrediente.unidade} para:",
            initialvalue=unidades_disponiveis[0]
        )
        
        if nova_unidade and nova_unidade in unidades_disponiveis:
            if self.receita.converter_ingrediente(index, nova_unidade):
                self.lista_ingredientes.delete(index)
                self.lista_ingredientes.insert(index, str(self.receita.ingredientes[index]))
                self.atualizar_receita()
                messagebox.showinfo("Sucesso", "Unidade convertida com sucesso!")
            else:
                messagebox.showerror("Erro", "Falha na conversão")

    # ... (atualize os métodos existentes para incluir categoria e modo de preparo) ...

    def salvar_receita(self):
        nome = self.nova_receita_nome.get().strip()
        
        if not nome:
            messagebox.showerror("Erro", "O nome da receita é obrigatório.")
            return
            
        if not self.receita.ingredientes:
            messagebox.showerror("Erro", "Adicione pelo menos um ingrediente.")
            return
            
        try:
            rendimento = float(self.rendimento_atual.get())
            if rendimento <= 0:
                raise ValueError("Rendimento deve ser positivo")
        except ValueError:
            messagebox.showerror("Erro", "Rendimento deve ser um número positivo válido.")
            return
            
        self.receita.nome = nome
        self.receita.rendimento = rendimento
        self.receita.rendimento_original = rendimento
        self.receita.categoria = self.categoria_var.get()
        self.receita.modo_preparo = self.modo_preparo_text.get("1.0", tk.END).strip()
        
        messagebox.showinfo("Sucesso", "Receita salva com sucesso!")
        self.atualizar_receita()

    def carregar_receita_arquivo(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
            title="Selecione uma Receita"
        )
        
        if arquivo:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                self.receita = Receita.from_dict(dados)
                self.nova_receita_nome.set(self.receita.nome)
                self.rendimento_atual.set(str(self.receita.rendimento))
                self.novo_rendimento.set(str(self.receita.rendimento))
                self.categoria_var.set(self.receita.categoria)
                
                self.lista_ingredientes.delete(0, tk.END)
                for ingrediente in self.receita.ingredientes:
                    self.lista_ingredientes.insert(tk.END, str(ingrediente))
                
                self.carregar_modo_preparo()
                self.atualizar_receita()
                messagebox.showinfo("Sucesso", "Receita carregada com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar receita: {str(e)}")

    def atualizar_receita(self):
        texto = f"Receita: {self.receita.nome}\n"
        texto += f"Categoria: {self.receita.categoria}\n"
        texto += f"Rendimento: {self.receita.rendimento} porção(ões)\n\n"
        texto += "Ingredientes:\n"
        texto += self.receita.exibir_receita()
        self.label_receita.config(text=texto)

    # ... (adicione este novo botão no método _criar_botoes_gerenciamento) ...

    def _criar_botoes_gerenciamento(self):
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        botoes = [
            ("Salvar em Arquivo", COR_BOTAO_SECUNDARIO, self.salvar_receita_arquivo),
            ("Carregar de Arquivo", COR_BOTAO_SECUNDARIO, self.carregar_receita_arquivo),
            ("Editar Nome", COR_BOTAO_TERCIARIO, self.editar_nome_receita),
            ("Editar Ingrediente", COR_BOTAO_TERCIARIO, self.editar_ingrediente),
            ("Excluir Ingrediente", COR_BOTAO_ERRO, self.excluir_ingrediente),
            ("Converter Unidade", COR_DESTAQUE, self.converter_unidade),
            ("Nova Receita", COR_DESTAQUE, self.nova_receita)
        ]

        for i, (texto, cor, comando) in enumerate(botoes):
            tk.Button(frame, text=texto, font=FONTE_PRINCIPAL, width=18,
                    bg=cor, fg=COR_TEXTO, bd=2, relief="raised",
                    command=comando).grid(row=i//3, column=i%3, padx=2, pady=2, sticky="ew")

def main():
    root = tk.Tk()
    app = ReceitaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()