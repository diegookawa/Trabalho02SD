# saved as greeting-client.py
import Pyro5.api
import threading

@Pyro5.api.expose
@Pyro5.api.callback
class cliente_callback(object):

    def __init__(self, nome) -> None:
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

    def cadastrarCompromisso(self):
        compromisso = {}
        convidadosCompromisso = None
        nomeCompromisso = input("Informe o nome do compromisso: ")
        dataCompromisso = input("Informe a data do compromisso: ")
        horarioCompromisso = input("Informe o horario do compromisso: ")

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
            option = int(input("Informe uma opcao:\n1 - Cadastrar compromisso\n2 - Cancelar compromisso\n3 - Consultar compromisso\n4 - Atualizar\n5 - Sair\n"))

            if option == 1:
                compromisso, convidadosCompromisso = callback.cadastrarCompromisso()
                servidor.cadastrarCompromisso(callback.nome, compromisso, convidadosCompromisso)

            elif option == 2:
                nomeCompromisso = input("Informe o nome do compromisso a ser cancelado: ")
                servidor.cancelarCompromisso(nomeCompromisso)

if __name__ == "__main__":
    main()