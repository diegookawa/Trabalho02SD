# saved as greeting-client.py
import Pyro5.api
import threading

@Pyro5.api.expose
@Pyro5.api.callback

class cliente_callback(object):
    def notificacao(self, msg):
        print("callback recebido do servidor!")

    def loopThread(daemon):
        #thread para ficar escutando chamadas de método do servidor
        daemon.requestLoop()

def main():
    name = input("What is your name? ").strip()
    ns = Pyro5.api.locate_ns()  
    daemon = Pyro5.server.Daemon() 
    servidor = Pyro5.api.Proxy("PYRONAME:Agenda")
    referenciaCliente = daemon.register(cliente_callback)

    #Invoca método no servidor, passando a referência
    public_key = servidor.cadastro(referenciaCliente, name)
    print(public_key)

    #Inicializa a thread para receber notificações do servidor
    thread = threading.Thread(target=cliente_callback.loopThread, args=(daemon,))
    thread.daemon = True
    thread.start()

if __name__ == "__main__":
    main()