from datetime import datetime
import matplotlib.pyplot as plt
import pickle
import cv2

class Funcionário:
    def __init__(self, id: int, nome: str, telefone: int, função: str, salário: float) -> None:
        # Define as informações internas do objeto
        self.info = {
            "Id": id,
            "Nome": nome,
            "Telefone": telefone,
            "Função": função,
            "Salário": salário
        }
    
class Cliente:
    def __init__(self, id:int, nome: str, telefone: int, endereço: str, carrinho: str, carrinho_pago: str) -> None:
        # Define as informações internas do objeto
        self.info = {
            "Id": id,
            "Nome": nome,
            "Telefone": telefone,
            "Endereço": endereço,
            "Carrinho": carrinho,
            "Carrinho_Pago": carrinho_pago
        }

class Encomenda:
    def __init__(self, id: int, carrinho: str, cliente: str, data_de_entrega: str) -> None:
        # Define as informações internas do objeto
        self.info = {
            "Id": id,
            "Cliente": cliente,
            "Carrinho": carrinho,
            "Data": data_de_entrega
        }

class Conta:
    def __init__(self, id: int, cliente: str, descrição: str, preço: float, pago: str) -> None:
        # Define as informações internas do objeto
        self.info = {
            "Id": id,
            "Cliente": cliente,
            "Descrição": descrição,
            "Preço": preço,
            "Pago": pago
        }

class Caixa:
    def __init__(self, id: int, valor_não_pago: float, valor_pago: float, lucro: float) -> None:
        # Define as informações internas do objeto
        self.info = {
            "Id": id,
            "Valor_não_Pago": valor_não_pago,
            "Valor_Pago": valor_pago,
            "Lucro": lucro
        }

class Produto:
    def __init__(self, id: int, nome: str, preço: float, características: str, foto: str) -> None:
        # Define as informações internas do objeto
        self.info = {
            "Id": id,
            "Nome": nome,
            "Característica": características,
            "Preço": preço,
            "Foto": foto
        }

    def plotFoto(self, dc):
        # Conecta com o banco de dados
        conexão, cursor = dc.connect("db")

        # Busca a imagem no banco de dados
        array_imagem = pickle.loads(list(
            cursor.execute(f"SELECT Foto FROM Produtos WHERE Id = {self.info['Id']}")
            )[0][0])
        
        # Converte o esquema de cor para HSV
        array_imagem = cv2.cvtColor(array_imagem, cv2.COLOR_BGR2HSV)
        
        # Define a dimensão do x e y do kernal
        bloco = 25

        # Busca do dia de hoje para aplicar o filtro correto
        dia_semana = datetime.now().strftime("%A")

        # Define o tamanho das figuras que seram plotadas
        plt.figure(figsize=(11, 6))

        # 1 - Caso seja Domingo, Terça, Quinta ou Sábado, aplica na imagem o filtro de Média
        # 2 - Caso seja outro dia, aplica na imagem o filtro de Mediana
        if dia_semana.lower() in ["sunday", "tuesday", "thursday", "saturday"]:
            # Opção 1
            nova_imagem = cv2.blur(array_imagem, (bloco, bloco))
            plt.subplot(121), plt.imshow(cv2.cvtColor(array_imagem, cv2.COLOR_HSV2BGR)), plt.title('Original')
            plt.xticks([]), plt.yticks([])
            plt.subplot(122), plt.imshow(cv2.cvtColor(nova_imagem, cv2.COLOR_HSV2BGR)), plt.title('Filtro de Média')
        else:
            # Opção 2
            imagem2 = cv2.cvtColor(array_imagem, cv2.COLOR_HSV2BGR)
            nova_imagem = cv2.medianBlur(imagem2, bloco)
            plt.subplot(121), plt.imshow(imagem2), plt.title('Original')
            plt.xticks([]), plt.yticks([])
            plt.subplot(122), plt.imshow(nova_imagem), plt.title('Filtro de Mediana')

        # Plota o filtro selecionado
        plt.xticks([]), plt.yticks([])
        plt.show()

        # Fecha o banco de dados
        dc.close(conexão)
