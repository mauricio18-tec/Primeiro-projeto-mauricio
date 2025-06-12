import tkinter as tk
from tkinter import messagebox, font, filedialog, simpledialog
import json

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

UNIDADES_PADRAO = ["g", "kg", "ml", "l", "xícara", "colher de sopa", 
                  "colher de chá", "unidades", "pitada", "a gosto"]

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
    def __init__(self, nome, ingredientes=None, rendimento=1):
        self.nome = nome.strip()
        self.ingredientes = ingredientes if ingredientes else []
        self.rendimento = rendimento  # Número de porções que a receita rende
        self.rendimento_original = rendimento  # Mantém o rendimento original

    def ajustar_porcoes(self, novo_rendimento):
        """Ajusta as quantidades para um novo rendimento"""
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
        """Determina se o ingrediente deve ser arredondado para número inteiro"""
        unidades_inteiras = ["unidade", "un", "unidades", "ovo", "ovos"]
        return any(unidade in ingrediente.unidade.lower() for unidade in unidades_inteiras)

    def exibir_receita(self):
        return "\n".join(str(ingrediente) for ingrediente in self.ingredientes)
    
    def to_dict(self):
        return {
            "nome": self.nome,
            "ingredientes": [ing.to_dict() for ing in self.ingredientes],
            "rendimento": self.rendimento
        }

    @classmethod
    def from_dict(cls, data):
        ingredientes = [
            Ingrediente(ing['nome'], ing['quantidade'], ing['unidade']) 
            for ing in data['ingredientes']
        ]
        rendimento = data.get('rendimento', 1)
        return cls(data['nome'], ingredientes, rendimento)

class ReceitaApp:
    def __init__(self, root):
        self.root = root
        self._configurar_janela()
        self._criar_widgets()
        self.receita = Receita("Nova Receita")
        self._configurar_redimensionamento()

    def _configurar_janela(self):
        self.root.title("Calculadora de Receitas com Rendimento")
        self.root.geometry("650x900")
        self.root.configure(bg=COR_FUNDO)
        self.root.minsize(600, 850)

    def _configurar_redimensionamento(self):
        for i in range(4):
            self.root.grid_columnconfigure(i, weight=1)
        for i in range(7):
            self.root.grid_rowconfigure(i, weight=1)

    def _criar_widgets(self):
        self._criar_painel_insercao()
        self._criar_painel_numerico()
        self._criar_controle_rendimento()
        self._criar_botoes_gerenciamento()
        
    def _criar_painel_insercao(self):
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.nova_receita_nome = tk.StringVar()
        self.novo_ingrediente_nome = tk.StringVar()
        self.novo_ingrediente_quantidade = tk.StringVar()
        self.novo_ingrediente_unidade = tk.StringVar(value=UNIDADES_PADRAO[0])

        tk.Label(frame, text="Nome da Receita:", font=FONTE_TITULO, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=0, sticky="w")
        
        tk.Entry(frame, textvariable=self.nova_receita_nome, font=FONTE_PRINCIPAL, 
                width=30, bg=COR_ENTRADA, fg=COR_TEXTO, 
                insertbackground="white").grid(row=0, column=1, columnspan=3, padx=5, pady=5)

        tk.Label(frame, text="Ingrediente:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=1, column=0, sticky="w")
        
        tk.Entry(frame, textvariable=self.novo_ingrediente_nome, font=FONTE_PRINCIPAL, 
                width=15, bg=COR_ENTRADA, fg=COR_TEXTO, 
                insertbackground="white").grid(row=1, column=1, padx=5, pady=5)

        tk.Label(frame, text="Quantidade:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=1, column=2, sticky="w")
        
        tk.Entry(frame, textvariable=self.novo_ingrediente_quantidade, font=FONTE_PRINCIPAL, 
                width=10, bg=COR_ENTRADA, fg=COR_TEXTO, 
                insertbackground="white").grid(row=1, column=3, padx=5, pady=5)

        tk.Label(frame, text="Unidade:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=2, column=0, sticky="w")
        
        self.combo_unidade = tk.OptionMenu(frame, self.novo_ingrediente_unidade, *UNIDADES_PADRAO)
        self.combo_unidade.config(font=FONTE_PRINCIPAL, bg=COR_ENTRADA, fg=COR_TEXTO, 
                                highlightthickness=0)
        self.combo_unidade.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(frame, text="Adicionar Ingrediente", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.adicionar_ingrediente).grid(row=2, column=2, columnspan=2, 
                                                        padx=5, pady=5, sticky="ew")

        self.lista_ingredientes = tk.Listbox(frame, font=FONTE_PRINCIPAL, 
                                           width=40, height=5, bg=COR_ENTRADA, 
                                           fg=COR_TEXTO, selectbackground=COR_BOTAO)
        self.lista_ingredientes.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="ew")

        tk.Button(frame, text="Salvar Receita", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_SECUNDARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.salvar_receita).grid(row=4, column=0, columnspan=4, 
                                               padx=5, pady=5, sticky="ew")

    def _criar_painel_numerico(self):
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=1, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.fator = tk.StringVar(value="1.0")
        tk.Entry(frame, textvariable=self.fator, font=FONTE_PRINCIPAL, 
                justify="right", bd=5, relief="flat", bg=COR_ENTRADA, 
                fg=COR_TEXTO, insertbackground="white").grid(row=0, column=0, 
                                                           columnspan=4, 
                                                           padx=10, pady=10, 
                                                           sticky="ew")

        botoes_numericos = [
            ('7', 1, 0), ('8', 1, 1), ('9', 1, 2),
            ('4', 2, 0), ('5', 2, 1), ('6', 2, 2),
            ('1', 3, 0), ('2', 3, 1), ('3', 3, 2),
            ('0', 4, 0), ('.', 4, 1), ('C', 4, 2)
        ]

        for (texto, linha, coluna) in botoes_numericos:
            tk.Button(frame, text=texto, font=FONTE_PRINCIPAL, 
                     bg=COR_ENTRADA, fg=COR_TEXTO, bd=2, relief="raised",
                     command=lambda t=texto: self._inserir_numero(t)).grid(
                         row=linha, column=coluna, padx=5, pady=5, sticky="nsew")

        tk.Button(frame, text="Multiplicar", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.multiplicar).grid(row=1, column=3, 
                                             padx=5, pady=5, sticky="nsew")
        
        tk.Button(frame, text="Dividir", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_ERRO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.dividir).grid(row=2, column=3, 
                                         padx=5, pady=5, sticky="nsew")

        self.label_receita = tk.Label(frame, text="", font=FONTE_PRINCIPAL, 
                                    bg=COR_FUNDO, fg=COR_TEXTO, justify="left")
        self.label_receita.grid(row=5, column=0, columnspan=4, 
                              padx=10, pady=10, sticky="w")

    def _criar_controle_rendimento(self):
        """Cria os controles para gerenciar o rendimento da receita"""
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        tk.Label(frame, text="Rendimento Atual:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=0, sticky="w")
        
        self.rendimento_atual = tk.StringVar(value="1")
        tk.Entry(frame, textvariable=self.rendimento_atual, font=FONTE_PRINCIPAL, 
                width=5, bg=COR_ENTRADA, fg=COR_TEXTO, 
                insertbackground="white", state='readonly').grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame, text="Novo Rendimento:", font=FONTE_PRINCIPAL, 
                bg=COR_FUNDO, fg=COR_TEXTO).grid(row=0, column=2, sticky="e")
        
        self.novo_rendimento = tk.StringVar(value="1")
        tk.Entry(frame, textvariable=self.novo_rendimento, font=FONTE_PRINCIPAL, 
                width=5, bg=COR_ENTRADA, fg=COR_TEXTO, 
                insertbackground="white").grid(row=0, column=3, padx=5, pady=5)

        tk.Button(frame, text="Ajustar", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_TERCIARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.ajustar_rendimento).grid(row=0, column=4, padx=5, pady=5, sticky="ew")

    def _criar_botoes_gerenciamento(self):
        frame = tk.Frame(self.root, bg=COR_FUNDO, bd=2, relief="groove")
        frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        tk.Button(frame, text="Salvar em Arquivo", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_SECUNDARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.salvar_receita_arquivo).grid(row=0, column=0, 
                                                        padx=5, pady=5, sticky="ew")
        
        tk.Button(frame, text="Carregar de Arquivo", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_SECUNDARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.carregar_receita_arquivo).grid(row=0, column=1, 
                                                          padx=5, pady=5, sticky="ew")
        
        tk.Button(frame, text="Editar Nome", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_TERCIARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.editar_nome_receita).grid(row=0, column=2, 
                                                     padx=5, pady=5, sticky="ew")

        tk.Button(frame, text="Editar Ingrediente", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_TERCIARIO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.editar_ingrediente).grid(row=1, column=0, 
                                                    padx=5, pady=5, sticky="ew")
        
        tk.Button(frame, text="Excluir Ingrediente", font=FONTE_PRINCIPAL, 
                bg=COR_BOTAO_ERRO, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.excluir_ingrediente).grid(row=1, column=1, 
                                                     padx=5, pady=5, sticky="ew")
        
        tk.Button(frame, text="Nova Receita", font=FONTE_PRINCIPAL, 
                bg=COR_DESTAQUE, fg=COR_TEXTO, bd=2, relief="raised",
                command=self.nova_receita).grid(row=1, column=2, 
                                              padx=5, pady=5, sticky="ew")

    def _inserir_numero(self, valor):
        if valor == 'C':
            self.fator.set("")
        else:
            current = self.fator.get()
            if current == "0" and valor != ".":
                self.fator.set(valor)
            else:
                self.fator.set(current + valor)

    def adicionar_ingrediente(self):
        nome = self.novo_ingrediente_nome.get().strip()
        quantidade_str = self.novo_ingrediente_quantidade.get().strip()
        unidade = self.novo_ingrediente_unidade.get().strip()

        if not nome:
            messagebox.showerror("Erro", "O nome do ingrediente é obrigatório.")
            return

        try:
            quantidade = float(quantidade_str)
            if quantidade <= 0:
                raise ValueError("Quantidade deve ser positiva")
        except ValueError:
            messagebox.showerror("Erro", "Quantidade deve ser um número positivo válido.")
            return

        if not unidade:
            messagebox.showerror("Erro", "Selecione uma unidade de medida.")
            return

        ingrediente = Ingrediente(nome, quantidade, unidade)
        self.receita.ingredientes.append(ingrediente)
        self.lista_ingredientes.insert(tk.END, str(ingrediente))
        
        self.novo_ingrediente_nome.set("")
        self.novo_ingrediente_quantidade.set("")
        self.atualizar_receita()

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
        messagebox.showinfo("Sucesso", "Receita salva com sucesso!")
        self.atualizar_receita()

    def salvar_receita_arquivo(self):
        if not self.receita.ingredientes:
            messagebox.showerror("Erro", "Nenhuma receita para salvar.")
            return
            
        arquivo = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
            title="Salvar Receita Como"
        )
        
        if arquivo:
            try:
                with open(arquivo, 'w', encoding='utf-8') as f:
                    json.dump(self.receita.to_dict(), f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Sucesso", "Receita salva em arquivo com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao salvar receita: {str(e)}")

    def carregar_receita_arquivo(self):
        arquivo = filedialog.askopenfilename(
            filetypes=[("Arquivos JSON", "*.json"), ("Todos os arquivos", "*.*")],
            title="Selecione uma Receita"
        )
        
        if arquivo:
            try:
                with open(arquivo, 'r', encoding='utf-8') as f:
                    dados = json.load(f)
                
                ingredientes = [
                    Ingrediente(ing['nome'], ing['quantidade'], ing['unidade']) 
                    for ing in dados['ingredientes']
                ]
                rendimento = dados.get('rendimento', 1)
                
                self.receita = Receita(dados['nome'], ingredientes, rendimento)
                self.nova_receita_nome.set(self.receita.nome)
                self.rendimento_atual.set(str(self.receita.rendimento))
                self.novo_rendimento.set(str(self.receita.rendimento))
                
                self.lista_ingredientes.delete(0, tk.END)
                for ingrediente in self.receita.ingredientes:
                    self.lista_ingredientes.insert(tk.END, str(ingrediente))
                
                self.atualizar_receita()
                messagebox.showinfo("Sucesso", "Receita carregada com sucesso!")
                
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao carregar receita: {str(e)}")

    def ajustar_rendimento(self):
        try:
            novo_rend = float(self.novo_rendimento.get())
            if novo_rend <= 0:
                raise ValueError("Rendimento deve ser positivo")
                
            self.receita.ajustar_porcoes(novo_rend)
            self.rendimento_atual.set(str(novo_rend))
            
            # Atualiza a lista de ingredientes
            self.lista_ingredientes.delete(0, tk.END)
            for ingrediente in self.receita.ingredientes:
                self.lista_ingredientes.insert(tk.END, str(ingrediente))
                
            self.atualizar_receita()
            messagebox.showinfo("Sucesso", f"Receita ajustada para {novo_rend} porções!")
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")

    def editar_nome_receita(self):
        novo_nome = simpledialog.askstring(
            "Editar Nome", 
            "Digite o novo nome da receita:",
            initialvalue=self.receita.nome
        )
        
        if novo_nome and novo_nome.strip():
            self.receita.nome = novo_nome.strip()
            self.nova_receita_nome.set(novo_nome.strip())
            self.atualizar_receita()

    def editar_ingrediente(self):
        selecionado = self.lista_ingredientes.curselection()
        
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um ingrediente para editar.")
            return
            
        index = selecionado[0]
        ingrediente = self.receita.ingredientes[index]
        
        novo_nome = simpledialog.askstring(
            "Editar Ingrediente", 
            "Novo nome:", 
            initialvalue=ingrediente.nome
        )
        
        nova_quantidade = simpledialog.askstring(
            "Editar Ingrediente", 
            "Nova quantidade:", 
            initialvalue=str(ingrediente.quantidade)
        )
        
        nova_unidade = simpledialog.askstring(
            "Editar Ingrediente", 
            "Nova unidade:", 
            initialvalue=ingrediente.unidade
        )
        
        if novo_nome and nova_quantidade and nova_unidade:
            try:
                quantidade = float(nova_quantidade)
                if quantidade <= 0:
                    raise ValueError("Quantidade deve ser positiva")
                    
                ingrediente.nome = novo_nome.strip()
                ingrediente.quantidade = quantidade
                ingrediente.unidade = nova_unidade.strip()
                
                self.lista_ingredientes.delete(index)
                self.lista_ingredientes.insert(index, str(ingrediente))
                self.atualizar_receita()
                
            except ValueError:
                messagebox.showerror("Erro", "Quantidade deve ser um número positivo válido.")

    def excluir_ingrediente(self):
        selecionado = self.lista_ingredientes.curselection()
        
        if not selecionado:
            messagebox.showerror("Erro", "Selecione um ingrediente para excluir.")
            return
            
        index = selecionado[0]
        self.receita.ingredientes.pop(index)
        self.lista_ingredientes.delete(index)
        self.atualizar_receita()

    def nova_receita(self):
        if self.receita.ingredientes:
            if not messagebox.askyesno("Confirmar", "Deseja descartar a receita atual?"):
                return
                
        self.receita = Receita("Nova Receita")
        self.nova_receita_nome.set("Nova Receita")
        self.rendimento_atual.set("1")
        self.novo_rendimento.set("1")
        self.lista_ingredientes.delete(0, tk.END)
        self.atualizar_receita()

    def multiplicar(self):
        try:
            fator = float(self.fator.get())
            if fator <= 0:
                raise ValueError("Fator deve ser positivo")
                
            for ingrediente in self.receita.ingredientes:
                if self.receita._deve_arredondar_inteiro(ingrediente):
                    ingrediente.quantidade = round(ingrediente.quantidade * fator)
                else:
                    ingrediente.quantidade = round(ingrediente.quantidade * fator, 2)
            
            # Atualiza a lista de ingredientes
            self.lista_ingredientes.delete(0, tk.END)
            for ingrediente in self.receita.ingredientes:
                self.lista_ingredientes.insert(tk.END, str(ingrediente))
            
            self.atualizar_receita()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")

    def dividir(self):
        try:
            fator = float(self.fator.get())
            if fator <= 0:
                raise ValueError("Fator deve ser positivo")
                
            for ingrediente in self.receita.ingredientes:
                if self.receita._deve_arredondar_inteiro(ingrediente):
                    ingrediente.quantidade = round(ingrediente.quantidade / fator)
                else:
                    ingrediente.quantidade = round(ingrediente.quantidade / fator, 2)
            
            # Atualiza a lista de ingredientes
            self.lista_ingredientes.delete(0, tk.END)
            for ingrediente in self.receita.ingredientes:
                self.lista_ingredientes.insert(tk.END, str(ingrediente))
            
            self.atualizar_receita()
            
        except ValueError as e:
            messagebox.showerror("Erro", f"Valor inválido: {str(e)}")

    def atualizar_receita(self):
        texto = f"Receita: {self.receita.nome}\n"
        texto += f"Rendimento: {self.receita.rendimento} porção(ões)\n\n"
        texto += "Ingredientes:\n"
        texto += self.receita.exibir_receita()
        self.label_receita.config(text=texto)

def main():
    root = tk.Tk()
    app = ReceitaApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()