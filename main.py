from conexao_database import DataControl
from tabulate import *
import pandas as pd

def inputMenu(msg: str, r: range, msg_erro: str) -> str:
    escolha = input("\n" + msg)
    poss = [str(i) for i in r]

    while escolha not in poss:
        print(msg_erro)
        escolha = input(msg)
    
    return int(escolha)


if __name__ == "__main__":

    db = DataControl("data.db", "data.xlsx")
    escolha = -1

    while escolha != 0:
        print("\n===================================================\n")
        print("\nBEM VINDO À NOSSA LOJA!")
        print("O que você deseja? ")
        print("\n1 - Ver os produtos em estoque")
        print("2 - Fazer uma encomenda")
        print("3 - Mostrar estatísticas")
        print("0 - Sair")

        escolha = inputMenu("ESCOLHA UMA OPÇÃO: ", range(4), "OPÇÃO INVÁLIDA!")

        print("\n===================================================\n")
            
        df = pd.DataFrame({
            "ID": [produto.info["Id"] for produto in db.itens["Produtos"]], 
            "NOME": [produto.info["Nome"] for produto in db.itens["Produtos"]],
            "PREÇO": ["R$" + str(produto.info["Preço"]) for produto in db.itens["Produtos"]]
            })
            
        if escolha == 1:           
            print(tabulate(df, headers = "keys", showindex = False))

            escolha_id = input("\nDigite o ID do produto que desejas ter mais detalhes. Caso desejas sair desse menu, digite '-1' (ou um ID inválido/inexistente): ")

            if escolha_id in [str(id) for id in df["ID"]]:
                escolha_id = int(escolha_id)
                print(f"\nNOME: {db.itens['Produtos'][escolha_id].info['Nome']}")
                print(f"PREÇO: {db.itens['Produtos'][escolha_id].info['Preço']}")
                print(f"CARACTERÍSTICAS: {db.itens['Produtos'][escolha_id].info['Característica']}")
                db.itens['Produtos'][escolha_id].plotFoto(db)
            else:
                print("\n===== RETORNANDO AO MENU =====\n")
            

        elif escolha == 2:
            cliente = None

            while cliente is None:
                nome = input("Digite o nome do cliente: ")

                if db.verificar_cliente(nome):
                    cliente = db.buscar_cliente(nome)

                else:
                    print("\nCLIENTE NÃO CADASTRADO! INFORME AS DEMAIS INFORMAÇÕES:")
                    telefone = input("Digite o telefone: ")
                    endereço = input("Digite o endereço: ")

                    db.add_cliente(nome, telefone, endereço)
                    cliente = db.itens["Clientes"][-1]

            print()
            print(tabulate(df, headers = "keys", showindex = False))

            ids = {}
            for key in [str(id) for id in df["ID"]]:
                ids[key] = 0

            escolha_id = input("\nDigite o ID do produto que desejas encomendar. Caso desejas sair desse menu, digite '-1' (ou um ID inválido/inexistente): ")
            while escolha_id in [str(id) for id in df["ID"]]:
                ids[escolha_id] += 1
                escolha_id = input("\nDigite o ID do próximo produto que desejas encomendar. Caso desejas finalizar a encomenda, digite '-1' (ou um ID inválido/inexistente): ")
            
            if not all([True if item == 0 else False for item in list(ids.values())]):
                data = input("\nQuando será a data de entrega? ")
                db.add_encomenda(cliente, ids, data)
                
                print("\n===== ENCOMENDA REALIZADA! =====\n")
            else:
                print("\n===== RETORNANDO AO MENU =====\n")
            
        
        if escolha == 3:
            database, cursor = db.connect("db")
            
            print("\n===== ENCOMENDAS DO DIA 08/06/2021 =====\n")

            busca_encomendas = list(cursor.execute("SELECT Carrinho, Cliente, Data FROM Encomendas WHERE Data = '08/06/2021'"))
            clientes_das_encomendas = []
            for encomenda in busca_encomendas:
                clientes_das_encomendas += [db.buscar_cliente(encomenda[1])]
            
            encomendas_dia8 = list(zip(busca_encomendas, clientes_das_encomendas))
            for encomenda, cliente in encomendas_dia8:
                print(f"\nCliente: {cliente.info['Nome']}")
                print(f"Telefone: {cliente.info['Telefone']}")
                print(f"Endereço: {cliente.info['Endereço']}")
                print(f"Carrinho: {encomenda[0]}")
                
            
            print("\n===== ENCOMENDAS FEITAS POR ANA =====\n")

            busca_encomendas = list(cursor.execute("SELECT Carrinho, Cliente, Data FROM Encomendas WHERE Cliente = 'Ana'"))
            ana = db.buscar_cliente("Ana")           
            print(f"\nNome: {ana.info['Nome']}")
            print(f"Telefone: {ana.info['Telefone']}")
            print(f"Endereço: {ana.info['Endereço']}")

            for encomenda in busca_encomendas:
                print(f"\nData da Encomenda: {encomenda[2]}")
                print(f"Carrinho da Encomenda: {encomenda[0]}")
            
            print("\n===== QUANTIDADE DE X - TUDOS VENDIDOS =====\n")
            
            busca_encomendas = list(cursor.execute("SELECT Carrinho FROM Encomendas"))
            contador_xtudo = 0

            for encomenda in busca_encomendas:
                temp = [item.strip() for item in encomenda[0].split(";")]
                contador_xtudo += temp.count("X – Tudo")
            
            print(f"\nFORAM VENDIDOS {contador_xtudo} X-TUDOS DESDE QUE A LOJA FOI ABERTA!!!\n")

            print("\n============================================\n")
        
        db.save()

            
            

            




                
                

            
            
