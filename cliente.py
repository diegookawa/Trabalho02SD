# saved as greeting-client.py
import Pyro5.api
import threading
import time

@Pyro5.api.expose
@Pyro5.api.callback
class cliente_callback(object):

    def __init__(self, nome):
        self.nome = nome
        self.public_key = ""
        self.referenciaCliente = ""

    def notificacao(self, msg):
        print("callback recebido do servidor!")

    def receberMensagemCompromisso(self, msg):
        option = int(input(msg))
        
        return option

    def loopThread(daemon):
        #thread para ficar escutando chamadas de método do servidor
        daemon.requestLoop()

    def getNome(self):
        return self.nome

    def setPublic_key(self, public_key):
        cliente_callback.public_key = public_key

    def imprimirCompromissos(self, compromissos):
        for compromisso in compromissos:
            print(f"Nome: {compromisso['nome']}, Data: {compromisso['data']}, Horário: {compromisso['horario']}", end=" ")
            if(compromisso['horarioAlerta'] is not None):
                print(f"Horário de Alerta: {compromisso['horarioAlerta']}")

        input("Digite ENTER para voltar...")

    def cadastrarCompromisso(self):
        compromisso = {}
        convidadosCompromisso = None
        nomeCompromisso = input("Informe o nome do compromisso: ")
        dataCompromisso = input("Informe a data do compromisso(dd/mm/aaaa): ")
        horarioCompromisso = input("Informe o horario do compromisso: ")
        compromisso["horarioAlerta"] = None

        optionConvidados = int(input("Deseja adicionar convidados?\n1 - Sim\n2 - Não\n"))
        if optionConvidados != 2:
            convidadosCompromisso = input("Informe o nome dos convidados separados por ,: ")

        optionAlerta = int(input("Deseja receber o alerta?\n1 - Sim\n2 - Não\n"))
        if optionAlerta != 2:
            horarioAlerta = input("Informe o horário do alerta: ")
            compromisso["horarioAlerta"] = horarioAlerta

        compromisso["nome"] = nomeCompromisso
        compromisso["data"] = dataCompromisso
        compromisso["horario"] = horarioCompromisso
        
        return compromisso, convidadosCompromisso

def main():
    with Pyro5.api.Daemon() as daemon:

        nome = input("Informe seu nome: ").strip()
        callback = cliente_callback(nome)
        callback.referenciaCliente = daemon.register(callback)

        #Inicializa a thread para receber notificações do servidor
        thread = threading.Thread(target=cliente_callback.loopThread, args=(daemon,))
        thread.daemon = True
        thread.start()

        ns = Pyro5.api.locate_ns()  
        uri = ns.lookup("Agenda")
        servidor = Pyro5.api.Proxy(uri)

        #Invoca método no servidor, passando a referência
        servidor.cadastro(callback.referenciaCliente, callback.nome)
    
        option = -1
        while option != 5:
            try:
                option = int(input("Informe uma opcao:\n1 - Cadastrar compromisso\n2 - Cancelar compromisso\n3 - Consultar compromisso\n4 - Atualizar\n5 - Sair\n"))

                if option == 1:
                    compromisso, convidadosCompromisso = callback.cadastrarCompromisso()
                    servidor.cadastrarCompromisso(callback.nome, compromisso, convidadosCompromisso)
                    time.sleep(0.3)

                elif option == 2:
                    nomeCompromisso = input("Informe o nome do compromisso a ser cancelado: ")
                    servidor.cancelarCompromisso(nomeCompromisso)
                    time.sleep(0.3)

                elif option == 3:
                    dataCompromisso = input("Informe a data do compromisso a ser consultado (dd/mm/aaaa): ")
                    servidor.consultarCompromisso(dataCompromisso, callback.referenciaCliente)
                    time.sleep(0.3)
                    
                elif option == 4:
                    time.sleep(0.3)

            except:
                pass

if __name__ == "__main__":
    main()