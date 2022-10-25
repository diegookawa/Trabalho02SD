# saved as greeting-server.py
import Pyro5.api
import datetime
import threading
import time
from Crypto.PublicKey import RSA

@Pyro5.api.expose
class Servidor(object):
    key = RSA.generate(2048)
    clientes = {}
    compromissos = []
    public_key = key.publickey().exportKey("PEM")
    private_key = key.exportKey("PEM")

    @Pyro5.server.oneway
    def cadastro(self, referenciaCliente, nome):
        cliente = Pyro5.api.Proxy(referenciaCliente)
        Servidor.clientes[nome] = (referenciaCliente)
        cliente.setPublic_key(Servidor.public_key)

    @Pyro5.server.oneway
    def cadastrarCompromisso(self, nome, compromisso, convidadosCompromisso):
        Servidor.compromissos.append((nome, compromisso))

        if(convidadosCompromisso is not None):
            convidados = convidadosCompromisso.split(",")
            nomeCompromisso = compromisso["nome"]

            for convidado in convidados:
                if(Servidor.clientes.get(convidado) is not None):
                    callbackConvidado = Pyro5.api.Proxy(Servidor.clientes[convidado])            
                    option = callbackConvidado.receberMensagemCompromisso(f"Deseja participar do compromisso: {nomeCompromisso}?\n1 - Sim\n2 - Não\n")
                    
                    if option == 1:
                        Servidor.compromissos.append((callbackConvidado.getNome(), compromisso))

    @Pyro5.server.oneway
    def cancelarCompromisso(self, nome):
        for i, compromisso in enumerate(Servidor.compromissos):
            if nome == compromisso[1]["nome"]:
                Servidor.compromissos.pop(i)

    @Pyro5.server.oneway
    def consultarCompromisso(self, data, referenciaCliente):
        callbackCliente = Pyro5.api.Proxy(referenciaCliente)
        comp = []        

        for compromisso in Servidor.compromissos:
            if data == compromisso[1]["data"] and compromisso[0] == callbackCliente.getNome():
                if not self.isInList(comp, compromisso[1]["nome"]):
                    comp.append(compromisso[1])

        callbackCliente.imprimirCompromissos(comp)   
    
    def isInList(self, list, name):
        for element in list:
            if name == element['nome']:
                return True
        return False

def verificarAlertas():
    while True:
        try:
            for compromisso in Servidor.compromissos:
                if compromisso[1]["data"] == str(datetime.date.today()):
                    t = time.localtime()
                    horarioAtual = time.strftime("%H:%M", t)
                    if compromisso[1]["horarioAlerta"] == str(horarioAtual) and compromisso[1]["alertado"] == False:
                        nomeCompromisso = compromisso[1]["nome"]
                        callbackCliente = Pyro5.api.Proxy(Servidor.clientes[compromisso[0]])
                        callbackCliente.notificacao(f"ALERTA DE COMPROMISSO: {nomeCompromisso}")
                        compromisso[1]["alertado"] = True
        except:
            pass

        time.sleep(0.3)

def main():
    daemon = Pyro5.server.Daemon()         # make a Pyro daemon
    ns = Pyro5.api.locate_ns()             # find the name server
    uri = daemon.register(Servidor)        # register the greeting maker as a Pyro object
    ns.register("Agenda", uri)             # register the object with a name in the name server

    print("Ready.")  
    thread = threading.Thread(target=verificarAlertas)
    thread.start()              
    daemon.requestLoop()   
    
if __name__ == "__main__":
    main()