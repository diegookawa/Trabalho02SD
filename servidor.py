# saved as greeting-server.py
import Pyro5.api
from Crypto.PublicKey import RSA

@Pyro5.api.expose
class Servidor(object):

    clientes = {}
    compromissos = []

    @Pyro5.server.oneway
    def cadastro(self, referenciaCliente, nome):
        cliente = Pyro5.api.Proxy(referenciaCliente)
        key = RSA.generate(2048)
        public_key = key.publickey().exportKey("PEM")
        private_key = key.exportKey("PEM")
        Servidor.clientes[nome] = (referenciaCliente, private_key)

        cliente.setPublic_key(public_key)

    @Pyro5.server.oneway
    def cadastrarCompromisso(self, nome, compromisso, convidadosCompromisso):
        Servidor.compromissos.append((nome, compromisso))

        if(convidadosCompromisso is not None):
            convidados = convidadosCompromisso.split(",")
            nomeCompromisso = compromisso["nome"]

            for convidado in convidados:
                if(Servidor.clientes.get(convidado) is not None):
                    callbackConvidado = Pyro5.api.Proxy(Servidor.clientes[convidado][0])
                    option = callbackConvidado.receberMensagemCompromisso(f"Deseja participar do compromisso: {nomeCompromisso}?\n1 - Sim\n2 - Não\n")
                    
                    if option == 1:
                        Servidor.compromissos.append((callbackConvidado.getNome(), compromisso))

def main():
    daemon = Pyro5.server.Daemon()         # make a Pyro daemon
    ns = Pyro5.api.locate_ns()             # find the name server
    uri = daemon.register(Servidor)        # register the greeting maker as a Pyro object
    ns.register("Agenda", uri)             # register the object with a name in the name server

    print("Ready.")
    daemon.requestLoop()                   # start the event loop of the server to wait for calls

if __name__ == "__main__":
    main()