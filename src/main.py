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
    text = "Nulla mollis aliquet risus eget tincidunt. " \
        "Nam bibendum congue lectus vel ultrices. Phasellus " \
        "sodales leo placerat, aliquam libero vitae, bibendum " \
        " erat. Donec elementum laoreet iaculis. Quisque " \
        "condimentum ante sit amet viverra ultrices. Nunc " \
        "egestas ante eget ex faucibus scelerisque. Duis pulvinar " \
        "eu purus vitae accumsan. Aenean eget luctus ex, volutpat " \
        "bibendum elit. Vivamus cursus, augue mattis cursus vehicula, " \
        "nunc augue fermentum ligula, id consectetur ex nulla ac magna."
        
#endregion [ Other ]

if __name__ == "__main__":
    main()
