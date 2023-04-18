import logging
from enum import Enum

import cyclic_redundancy_check as cs
import file_io as fio
import serial as ser
import xmodem

# Apllication Entry.
def main():
    user_input = ""
    serial_port_name = "None"
    baudrate = "None"
    check = "Checksum"
    debugging = False # Dont used anymore.

    # Loop through console IO.
    while user_input != "q":
        print(f"Port: {serial_port_name}")
        print(f"Baudrate: {baudrate}")
        print(f"Typ sumy kontrolnej: {check}")
        print()

        user_input = input('''Podaj, czy chcesz:\n(1) Wysłać pakiet\n(2) Odebrać pakiet\n(3) Zmien ustawienia portu szeregowego\n(4) Zmien typ sumy kontrolnej\n(q) Wyjść\n> ''')
        match user_input:
            case '1':
                send_packet(serial_port_name, baudrate)
            case '2':
                receive_packet(serial_port_name, baudrate, check)
            case '3':
                serial_port_name, baudrate = get_port_io()
            case '4':
                if check == "CRC":
                    check = "Checksum"
                else:
                    check = "CRC"
            #case '5':
            #    debugging = not debugging
            #    if debugging:
            #        logging.basicConfig(level=logging.DEBUG)
            #    else:
            #        logging.basicConfig(level=logging.ERROR)
            case _:
                continue

def send_packet(port_name, baudrate):
    data = bytes()
    
    match input("\nWiadomość:\n(1) Predefiniowana\n(2) Wpisana ręcznie\n(3) Z pliku\n> "):
        case '1':
            data = bytes(get_example.text.value, 'utf-8')
        case '2':
            data = input("Podaj wiadomość: ")
            data = bytes(data, 'utf-8')
        case '3':
            data = fio.message_from_file(input("Podaj ścieżkę: "))

    try:
        serial_port = xmodem.initialize_serial(port_name, baudrate)
        serial_port.open()
        xmodem.send(serial_port, data)
        serial_port.close()
    except (serial.SerialException, ValueError):
        print("Ustawienia Portu są nie poprawne, spróbuj ponownie")
    except xmodem.ReceiverSendUnexpectedResponseException:
        print("Odbiorca nie rozpoczął transmisji, spróbuj ponownie")

def receive_packet(port_name, baudrate, check):
    serial_port = xmodem.initialize_serial(port_name, baudrate)

    try:
        serial_port.open()
        if check == "CRC":
            check = xmodem.CheckSumEnum.crc
        else:
            check = xmodem.CheckSumEnum.algebraic
        data = xmodem.receive(serial_port, check)
        serial_port.close()
    except (serial.SerialException, ValueError):
        print("Ustawienia Portu są nie poprawne, spróbuj ponownie")
    except xmodem.SenderDoesNotAcceptTransferException:
        print("Nadawca nie zaakceptował transmisji, spróbuj ponownie")

    print("Cała wiadomość: ")
    print(data.decode("utf-8"))

    path = input("Podaj gdzie zapisać: ")
    fio.message_to_file(data, path)

#region [ Other ]

def get_port_io():
    port_name = input("Podaj nazwę portu: ")
    baudrate = int(input("Podaj baudrate: "))
    return port_name, baudrate

class get_example(Enum):
    text = "Litwo! Ojczyzno moja! Ty jestes jak zdrowie," \
        "Ile cie trzeba cenic, ten tylko sie dowie," \
        "Kto cie stracil. Dzis pieknosc twa w calej ozdobie " \
        "Widze i opisuje, bo tesknie po tobie " \
        "Panno swieta, co Jasnej bronisz Czestochowy " \
        "I w Ostrej swiecisz Bramie! Ty, co grod zamkowy " \
        "Nowogrodzki ochraniasz z jego wiernym ludem! " \
        "Jak mnie dziecko do zdrowia powrocilas cudem, " \
        "(Gdy od placzacej matki pod Twoja opieke " \
        "Ofiarowany, martwa podnioslem powieke " \
        "I zaraz moglem pieszo do Twych swiatyn progu " \
        "Isc za wrocone zycie podziekowac Bogu), " \
        "Tak nas powrocisz cudem na Ojczyzny lono. " \
        "Tymczasem przenos moja dusze uteskniona " \
        "Do tych pagorkow lesnych, do tych lak zielonych, " \
        "Szeroko nad blekitnym Niemnem rozciagnionych; " \
        "Do tych pol malowanych zbozem rozmaitem, " \
        "Wyzlacanych pszenica, posrebrzanych zytem; " \
        "Gdzie bursztynowy swierzop, gryka jak snieg biala, " \
        "Gdzie panienskim rumiencem dziecielina pala, " \
        "A wszystko przepasane jakby wstega, miedza " \
        "Zielona, na niej z rzadka ciche grusze siedza."
        
#endregion [ Other ]

if __name__ == "__main__":
    main()
