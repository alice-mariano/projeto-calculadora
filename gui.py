import tkinter as tk
from tkinter import ttk, messagebox
import json
from modelos import Usuario, AlimentoPorGrama, AlimentoPorUnidade, Refeicao


NOME_ARQUIVO_ALIMENTOS = "alimentos.json"


def carregar_alimentos():
    try:
        with open(NOME_ARQUIVO_ALIMENTOS, "r") as f:
            dados = json.load(f)
        lista = []
        for item in dados:
            if item["tipo"] == "grama":
                obj = AlimentoPorGrama(item["nome"], item["calorias"])
            else:
                obj = AlimentoPorUnidade(item["nome"], item["calorias"])
            lista.append(obj)
        return lista
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def salvar_alimentos(lista):
    dados = [a.to_dict() for a in lista]
    with open(NOME_ARQUIVO_ALIMENTOS, "w") as f:
        json.dump(dados, f, indent=4)


class AppCalculadora(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Calculadora de Calorias - Nível IV")
        self.geometry("900x600")

        self.usuario = Usuario()
        self.banco_alimentos = carregar_alimentos()
        self.refeicoes_dia = []

        self.configurar_estilos()
        self.abas = ttk.Notebook(self)
        self.abas.pack(expand=True, fill="both", padx=10, pady=10)

        self.aba_resumo = ttk.Frame(self.abas)
        self.abas.add(self.aba_resumo, text="🏠 Início e Resumo")
        self.montar_aba_resumo()

        self.aba_alimentos = ttk.Frame(self.abas)
        self.abas.add(self.aba_alimentos, text="🍎 Gerenciar Alimentos")
        self.montar_aba_alimentos()

        self.aba_refeicao = ttk.Frame(self.abas)
        self.abas.add(self.aba_refeicao, text="🍽️ Nova Refeição")
        self.montar_aba_refeicao()

    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")

        cor_fundo = "#f0f0f0"
        cor_primaria = "#4a7a8c"
        cor_texto = "#333333"

        self.configure(bg=cor_fundo)
        style.configure("TFrame", background=cor_fundo)

        style.configure(
            "TButton",
            font=("Helvetica", 10, "bold"),
            background=cor_primaria,
            foreground="white",
        )
        style.map("TButton", background=[("active", "#365c69")])

        style.configure(
            "TLabel", font=("Helvetica", 11), background=cor_fundo, foreground=cor_texto
        )
        style.configure(
            "Titulo.TLabel", font=("Helvetica", 16, "bold"), foreground=cor_primaria
        )

        style.configure(
            "Treeview",
            font=("Helvetica", 12),
            rowheight=35,
            background="white",
            foreground=cor_texto,
        )
        style.configure(
            "Treeview.Heading",
            font=("Helvetica", 12, "bold"),
            background="#dddddd",
            foreground=cor_texto,
        )

    def montar_aba_resumo(self):
        frame_meta = ttk.LabelFrame(
            self.aba_resumo, text="Definir Meta Diária", padding=20
        )
        frame_meta.pack(fill="x", padx=20, pady=10)

        ttk.Label(frame_meta, text="Meta (kcal):").pack(side="left", padx=5)
        self.entry_meta = ttk.Entry(frame_meta, width=10)
        self.entry_meta.pack(side="left", padx=5)
        ttk.Button(frame_meta, text="Salvar Meta", command=self.salvar_meta).pack(
            side="left", padx=5
        )

        frame_dados = ttk.LabelFrame(self.aba_resumo, text="Resumo do Dia", padding=20)
        frame_dados.pack(fill="both", expand=True, padx=20, pady=10)

        self.lbl_resumo_texto = ttk.Label(
            frame_dados,
            text="Defina uma meta e adicione refeições para ver o resumo.",
            justify="left",
        )
        self.lbl_resumo_texto.pack(anchor="w")

        ttk.Button(
            frame_dados, text="Atualizar Resumo", command=self.atualizar_resumo
        ).pack(pady=10)

    def salvar_meta(self):
        try:
            valor = float(self.entry_meta.get())
            self.usuario.set_meta_calorica(valor)
            messagebox.showinfo("Sucesso", f"Meta definida: {valor} kcal")
            self.atualizar_resumo()
        except ValueError:
            messagebox.showerror("Erro", "Digite um número válido.")

    def atualizar_resumo(self):
        texto = f"META DIÁRIA: {self.usuario.get_meta_calorica()} kcal\n\n"
        total_dia = 0
        if not self.refeicoes_dia:
            texto += "Nenhuma refeição registrada hoje."
        else:
            for refeicao in self.refeicoes_dia:
                cal_ref = refeicao.calcular_total_calorias()
                total_dia += cal_ref
                texto += f"• {refeicao.get_nome()}: {cal_ref:.1f} kcal\n"

        saldo = self.usuario.get_meta_calorica() - total_dia
        texto += f"\nTOTAL CONSUMIDO: {total_dia:.1f} kcal"
        texto += f"\nSALDO RESTANTE: {saldo:.1f} kcal"
        self.lbl_resumo_texto.config(text=texto)

    def montar_aba_alimentos(self):
        colunas = ("nome", "tipo", "calorias")
        self.tree_alimentos = ttk.Treeview(
            self.aba_alimentos, columns=colunas, show="headings"
        )

        self.tree_alimentos.heading("nome", text="Nome")
        self.tree_alimentos.heading("tipo", text="Tipo")
        self.tree_alimentos.heading("calorias", text="Kcal")

        self.tree_alimentos.column("nome", anchor="center", width=200)
        self.tree_alimentos.column("tipo", anchor="center", width=150)
        self.tree_alimentos.column("calorias", anchor="center", width=100)

        self.tree_alimentos.pack(fill="both", expand=True, padx=20, pady=10)
        self.atualizar_lista_alimentos()

        frame_botoes = ttk.Frame(self.aba_alimentos)
        frame_botoes.pack(fill="x", padx=20, pady=10)

        ttk.Button(
            frame_botoes, text="Excluir Selecionado", command=self.excluir_alimento
        ).pack(side="right")
        ttk.Button(
            frame_botoes, text="Adicionar Novo", command=self.janela_novo_alimento
        ).pack(side="right", padx=10)

    def atualizar_lista_alimentos(self):
        for i in self.tree_alimentos.get_children():
            self.tree_alimentos.delete(i)
        for alimento in self.banco_alimentos:
            dic = alimento.to_dict()
            tipo_txt = "Por Grama (100g)" if dic["tipo"] == "grama" else "Por Unidade"
            self.tree_alimentos.insert(
                "", "end", values=(dic["nome"], tipo_txt, dic["calorias"])
            )

    def janela_novo_alimento(self):
        top = tk.Toplevel(self)
        top.title("Novo Alimento")
        top.geometry("300x250")

        ttk.Label(top, text="Nome:").pack(pady=5)
        entry_nome = ttk.Entry(top)
        entry_nome.pack()

        ttk.Label(top, text="Tipo:").pack(pady=5)
        combo_tipo = ttk.Combobox(top, values=["Por Grama", "Por Unidade"])
        combo_tipo.pack()

        ttk.Label(top, text="Calorias (kcal):").pack(pady=5)
        entry_cal = ttk.Entry(top)
        entry_cal.pack()

        def confirmar():
            nome = entry_nome.get()
            tipo = combo_tipo.get()
            try:
                cal = float(entry_cal.get())
                if tipo == "Por Grama":
                    novo = AlimentoPorGrama(nome, cal)
                else:
                    novo = AlimentoPorUnidade(nome, cal)
                self.banco_alimentos.append(novo)
                salvar_alimentos(self.banco_alimentos)
                self.atualizar_lista_alimentos()
                self.atualizar_combo_refeicao()
                top.destroy()
                messagebox.showinfo("Sucesso", "Alimento cadastrado!")
            except ValueError:
                messagebox.showerror("Erro", "Verifique os dados.")

        ttk.Button(top, text="Salvar", command=confirmar).pack(pady=10)

    def excluir_alimento(self):
        selecionado = self.tree_alimentos.selection()
        if not selecionado:
            return
        index = self.tree_alimentos.index(selecionado[0])
        del self.banco_alimentos[index]
        salvar_alimentos(self.banco_alimentos)
        self.atualizar_lista_alimentos()
        self.atualizar_combo_refeicao()

    def montar_aba_refeicao(self):
        ttk.Label(self.aba_refeicao, text="Nome da Refeição (ex: Almoço):").pack(pady=5)
        self.entry_nome_ref = ttk.Entry(self.aba_refeicao)
        self.entry_nome_ref.pack(pady=5)

        ttk.Label(self.aba_refeicao, text="Selecione o Alimento:").pack(pady=5)
        self.combo_alimentos = ttk.Combobox(self.aba_refeicao)
        self.combo_alimentos.pack(pady=5)
        self.atualizar_combo_refeicao()

        ttk.Label(self.aba_refeicao, text="Quantidade (g ou unid):").pack(pady=5)
        self.entry_qtd = ttk.Entry(self.aba_refeicao)
        self.entry_qtd.pack(pady=5)

        ttk.Button(
            self.aba_refeicao,
            text="Registrar Refeição",
            command=self.registrar_refeicao,
        ).pack(pady=20)

    def atualizar_combo_refeicao(self):
        nomes = [a.get_nome() for a in self.banco_alimentos]
        self.combo_alimentos["values"] = nomes

    def registrar_refeicao(self):
        nome_ref = self.entry_nome_ref.get().strip()
        nome_alim = self.combo_alimentos.get()
        qtd_str = self.entry_qtd.get()

        if not nome_ref or not nome_alim or not qtd_str:
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        alimento_obj = next(
            (a for a in self.banco_alimentos if a.get_nome() == nome_alim), None
        )

        if alimento_obj:
            try:
                qtd = float(qtd_str)
                refeicao_encontrada = next(
                    (
                        r
                        for r in self.refeicoes_dia
                        if r.get_nome().lower() == nome_ref.lower()
                    ),
                    None,
                )

                if refeicao_encontrada:
                    refeicao_encontrada.adicionar_item(alimento_obj, qtd)
                    msg = f"Item adicionado ao '{refeicao_encontrada.get_nome()}'!"
                else:
                    nova_ref = Refeicao(nome_ref)
                    nova_ref.adicionar_item(alimento_obj, qtd)
                    self.refeicoes_dia.append(nova_ref)
                    msg = f"Refeição '{nome_ref}' criada!"

                messagebox.showinfo("Sucesso", msg)
                self.entry_qtd.delete(0, "end")
                self.combo_alimentos.set("")
                self.atualizar_resumo()
            except ValueError:
                messagebox.showerror("Erro", "Quantidade inválida.")


if __name__ == "__main__":
    app = AppCalculadora()
    app.mainloop()
