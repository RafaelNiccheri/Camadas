#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#esta é a camada superior, de aplicação do seu software de comunicação serial UART.
#para acompanhar a execução e identificar erros, construa prints ao longo do código!


from enlace import *
import time
import numpy as np
import sys

# voce deverá descomentar e configurar a porta com através da qual ira fazer comunicaçao
#   para saber a sua porta, execute no terminal :
#   python -m serial.tools.list_ports
# se estiver usando windows, o gerenciador de dispositivos informa a porta

#use uma das 3 opcoes para atribuir à variável a porta usada
#serialName = "/dev/ttyACM0"           # Ubuntu (variacao de)
#serialName = "/dev/tty.usbmodem1411" # Mac    (variacao de)
serialName = "COM3"                  # Windows(variacao de)

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)

        # Ativa comunicacao. Inicia os threads e a comunicação seiral 
        com1.enable()
        #Se chegamos até aqui, a comunicação foi aberta com sucesso. Faça um print para informar.
        print("Abriu a comunicação")

        # Esperando byte de sacrifício
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        print(rxBuffer[0])
        if rxBuffer[0] == 0:
            print("Recebido byte de sacrifício")
        com1.rx.clearBuffer() # Limpa o buffer de recebimento para receber os comandos
        time.sleep(0.1)

        eop = b'\x01\x02\x03'
        rxBuffer, nRx = com1.getData(12)
        if rxBuffer == b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t':
            rxHandshake = rxBuffer
            rxBuffer, nRx = com1.getData(3)
            if rxBuffer == eop:
                print("Handshake realizado com sucesso")
                com1.sendData(np.asarray(rxHandshake))
                comandos = []

                # rxBuffer, nRx = com1.getData(1) # Recebe o tamanho do primeiro comando

                #Loop para receber os comandos do client
                con = True
                pacote_atual = 0
                while con:

                    print('começando o loop')

                    if rxBuffer[0] == 17: #b'\x11' - byte de finalização
                        print('')
                        print("________________Finalizando comunicação________________")
                        print('')

                        txBuffer = len(comandos).to_bytes(1, byteorder='big')
                        print(txBuffer)
                        #print(f'O tamanho do array é {len(txBuffer)}')

                        txSize = com1.tx.getStatus()
                        com1.sendData(np.asarray(txBuffer))
                        print(f'Server enviou {txBuffer.to_bytes(1, byteorder="big")} comandos')
                        #print(f'Server enviou {txSize} bytes')

                        # Encerra comunicação
                        print("-------------------------")
                        print("Comunicação encerrada")
                        print("-------------------------")
                        com1.disable()
                        con = False

                    else:
                        rxBuffer, nRx = com1.getData(12) # Recebe o head
                        #print(int.from_bytes(rxBuffer[0], byteorder='big'))
                        print(rxBuffer)
                        print(rxBuffer[0], 'aaaaaa')
                        if rxBuffer[0] == pacote_atual+1:
                            pacote_atual = rxBuffer[0]
                            print(f'Server recebeu o comando {rxBuffer}')
                            rxBuffer, nRx = com1.getData(rxBuffer[2])
                            comandos.append(rxBuffer)
                            rxBuffer, nRx = com1.getData(3) # Atualiza o rxBuffer para receber o próximo comando ou finalizar a comunicação
                        else:
                            print('pocote pulado')
                            com1.disable()
                            break
            else:
                print("Handshake não realizado")
                com1.disable()
        else:
            print("Handshake não realizado")
            com1.disable()
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()


    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()