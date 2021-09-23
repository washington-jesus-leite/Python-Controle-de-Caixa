from classes_entidades import *
from numpy import asarray
import sqlite3 as sql
import openpyxl as opx
import pickle
import string
import PIL

class DataControl:
    def __init__(self, local_db: str, local_excel: str):
        self.locais = {
            "db": local_db,
            "wb": local_excel
        }

        self.itens = {
            "Caixa": None,
            "Contas": [],
            "Produtos": [],
            "Encomendas": [],
            "Clientes": [],
            "Funcionários": []
        }

        self.load()
    
    def connect(self, local: str) -> tuple:
        # Começa uma conexão dependendo do parâmetro
        if local.lower() == "db":
            temp = sql.connect(self.locais["db"])
            return temp, temp.cursor()
        elif local.lower() == "wb":
            return opx.load_workbook(self.locais["wb"])
        return None
    
    def close(self, conexão) -> None:
        # Encerra uma conexão
        conexão.close()

    def verificar_existencia(self, tabela: str, coluna: str, parâmetro, is_string: bool) -> bool:
        # Começa uma conexão no banco de dados
        db, cursor = self.connect("db")

        # Monta o código SQL para ser executado
        string_code = f"SELECT * FROM {tabela} WHERE {coluna} = "
        string_code += "'" if is_string else ""
        string_code += f"{parâmetro}"
        string_code += "'" if is_string else ""

        # Resultado da pesquisa
        resultado = list(cursor.execute(string_code))

        # Fecha a conexão com o Banco de Dados
        self.close(db)

        # Caso tenha ao menos 1 elemento em resultados, retorna True
        return len(resultado) > 0 


    def load(self):
        def ler_caixa(workbook: opx.Workbook, nome_sheet: str, locais: list[str]) -> list:
            '''Sub-função dedicada a ler os dados do caixa do excel'''
            return [workbook[nome_sheet][locais[i]].value for i in range(3)] 

        def ler_sheet(workbook: opx.Workbook, nome_sheet: str, linha_inicial: int,  p_types: list) -> list[list]:
            '''Sub-Função dedicada a ler os dados de um sheet do Workbook'''
            
            colunas = list(string.ascii_uppercase)
            coluna_final = len(p_types)

            linha_atual = linha_inicial
            
            values = []
            while workbook[nome_sheet]["A" + str(linha_atual)].value is not None:
                value = [linha_atual - linha_inicial]
                
                for j in range(coluna_final):
                    value += [p_types[j](workbook[nome_sheet][colunas[j] + str(linha_atual)].value)]
                
                values += [value]
                linha_atual += 1

            print(f"{nome_sheet}: OK")

            return values

        def apagar_db(banco: sql.Connection, cursor: sql.Cursor) -> None:
            '''Sub-Função que apaga todos os dados no banco de dados'''
            for item in ["Clientes", "Contas", "Encomendas", "Funcionários", "Produtos"]:
                cursor.execute(f"DELETE FROM {item};")
                banco.commit()

        def selecionar_fotos(cursor: sql.Cursor, produtos: list[list]):
            for produto in produtos:
                busca = list(cursor.execute(f"SELECT Foto FROM Produtos WHERE Nome = '{produto[1]}'"))

                if produto[-1].strip() == "-" and len(busca):
                    produto[-1] = busca[0][-1]
                else:
                    try:
                        temp_foto = asarray(PIL.Image.open(r"Fotos/" + produto[-1]))
                    except:
                        temp_foto = asarray(PIL.Image.open(r"Fotos/image_not_found.png"))
                    produto[-1] = pickle.dumps(temp_foto, pickle.HIGHEST_PROTOCOL)            
                    
        def escrever_db(banco: sql.Connection, cursor: sql.Cursor, table: str, values: list, is_string: dict):
            '''Sub-Função dedicada a escrever os dados em uma tabela do banco de dados'''

            i = 0
            string_valores = ""
            for item in values:
                info = item.info.copy()
                string_valores += "\n("
                keys = list(info.keys())

                for j in range(len(keys)):
                    string_valores += f"'{info[keys[j]]}'" if is_string[keys[j]] else f"{info[keys[j]]}"
                    if j < len(info) - 1:
                        string_valores += ", "
                string_valores += ")"

                if i < len(values) - 1:
                    string_valores += ", "
                i += 1
            
            i = 0
            string_keys = "("
            for key in keys:
                string_keys += key

                if i < len(keys) - 1:
                    string_keys += ", "
                i += 1

            if string_keys[-1] == " " and string_keys[-2] == ",":
                string_keys = string_keys[:-2]
            string_keys += ")"

            cursor.execute(f"INSERT INTO {table}\n" + string_keys + "\nVALUES" + string_valores)
            banco.commit()


        # Abrindo as conexões com o Banco de dados e o Workbook do Excel.
        # Apaga, também, toda a informação antiga do Banco de Dados
        wb = self.connect("wb")
        db, cursor = self.connect("db")

        # Lendo as tabelas do excel e do Banco de Dados
        info_leitura = {
            "Contas": [str, str, float, str],
            "Produtos": [str, float, str, str],
            "Encomendas": [str, str, str],
            "Clientes": [str, int, str, str, str],
            "Funcionários": [str, int, str, float]
        }

        leitura_excel = {"Caixa": ler_caixa(wb, "Caixa", ["B2", "D2", "F2"])}
        for key in info_leitura:
            leitura_excel[key] = ler_sheet(wb, key, 3, info_leitura[key])
        
        selecionar_fotos(cursor, leitura_excel["Produtos"])
        apagar_db(db, cursor)


        # Armazena os dados dentro do objeto
        info_objetos = {
            "Contas": Conta,
            "Produtos": Produto,
            "Encomendas": Encomenda,
            "Clientes": Cliente,
            "Funcionários": Funcionário
        }

        self.itens["Caixa"] = Caixa(*[float(item) for item in leitura_excel["Caixa"]] + [0])
        for key in info_objetos:
            self.itens[key] = [info_objetos[key](*item) for item in leitura_excel[key]]



        # Armazenando os dados atualizados no banco de dados (com exceção dos produtos)
        info_escrever_db = {
            "Contas": {"Id": False, "Cliente": True, "Descrição": True, "Preço": False, "Pago": False},
            "Encomendas": {"Id": False, "Cliente": True, "Carrinho": True, "Data": True},
            "Clientes": {"Id": False, "Nome": True, "Telefone": False, "Endereço": True, "Carrinho": True, "Carrinho_Pago": True},
            "Funcionários": {"Id": False, "Nome": True, "Telefone": False, "Função": True, "Salário": False}
        }

        for key in info_escrever_db:
            escrever_db(db, cursor, key, self.itens[key], info_escrever_db[key])

        # Armazenando os produtos no banco de dados
        for produto in self.itens["Produtos"]:
            cursor.execute(f"INSERT INTO Produtos (Id, Nome, Característica, Preço, Foto) VALUES ({produto.info['Id']}, "
                            + f"'{produto.info['Nome']}', '{produto.info['Característica']}', {produto.info['Preço']}, ?);", 
                            [sql.Binary(produto.info["Foto"])])
            db.commit()

        # Fechando as conexões
        self.close(db)
        self.close(wb)

    def save(self):
        wb = self.connect("wb")
        db, cursor = self.connect("db")

        dados = {
            "Clientes": list(cursor.execute("SELECT Nome, Telefone, Endereço, Carrinho, Carrinho_Pago FROM Clientes;")),
            "Funcionários": list(cursor.execute("SELECT Nome, Telefone, Função, Salário FROM Funcionários;")),
            "Encomendas": list(cursor.execute("SELECT Carrinho, Cliente, Data FROM Encomendas;")),
            "Produtos": list(cursor.execute("SELECT Nome, Preço, Característica, Foto FROM Produtos;")),
            "Contas": list(cursor.execute("SELECT Cliente, Descrição, Preço, Pago FROM Contas;"))
        }

        colunas = list(string.ascii_uppercase)

        for key in dados:
            for i in range(len(dados[key])):
                for j in range(len(dados[key][i])):
                    if key == "Produtos" and j == 3:
                        wb[key][colunas[j] + str(i + 3)] = "-"
                    else:
                        wb[key][colunas[j] + str(i + 3)] = dados[key][i][j]
                    

        wb.save(self.locais["wb"])
        self.close(db)
        self.close(wb)


    def verificar_cliente(self, nome: str):
        db, cursor = self.connect("db")
        itens = list(cursor.execute(f"SELECT * FROM Clientes WHERE Nome = '{nome}'"))
        self.close(db)

        return len(itens) > 0

    def buscar_cliente(self, nome: str):
        for cliente in self.itens["Clientes"]:
            if cliente.info["Nome"] == nome:
                return cliente
        return None

    def add_cliente(self, nome: str, telefone: str, endereço: str) -> None:
        db, cursor = self.connect("db")

        self.itens["Clientes"] += [Cliente(len(self.itens["Clientes"]), nome, telefone, endereço, "", "")]

        cursor.execute("INSERT INTO Clientes (Id, Nome, Telefone, Endereço, Carrinho, Carrinho_Pago) "
                          + f"VALUES ({self.itens['Clientes'][-1].info['Id']}, '{self.itens['Clientes'][-1].info['Nome']}', {self.itens['Clientes'][-1].info['Telefone']}, "
                          + f"'{self.itens['Clientes'][-1].info['Endereço']}', '{self.itens['Clientes'][-1].info['Carrinho']}', '{self.itens['Clientes'][-1].info['Carrinho_Pago']}');")
        db.commit()
        db.close()

    def add_encomenda(self, cliente: Cliente, produtos_ids: dict, data: str):

        db, cursor = self.connect("db")

        carrinho_list = []
        for id in produtos_ids:
            carrinho_list += produtos_ids[id] * [self.itens["Produtos"][int(id)].info["Nome"]]

        string_carrinho = str(carrinho_list)[1:-1].replace(",", ";").replace("'", "").replace('"', "")
        self.itens["Encomendas"] += [Encomenda(len(self.itens["Encomendas"]), string_carrinho, cliente.info["Nome"], data)]

        cursor.execute("INSERT INTO Encomendas (Id, Carrinho, Cliente, Data) VALUES "
                        + f"({self.itens['Encomendas'][-1].info['Id']}, '{self.itens['Encomendas'][-1].info['Carrinho']}', "
                        + f"'{self.itens['Encomendas'][-1].info['Cliente']}', '{self.itens['Encomendas'][-1].info['Data']}');")
        
        db.commit()
        db.close()


