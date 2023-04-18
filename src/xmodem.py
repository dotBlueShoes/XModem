import logging
from enum import Enum

import serial as ser
import cyclic_redundancy_check as crc

# Packets definitions.
SOH = b'\x01'
EOT = b'\x04'
ACK = b'\x06'
NAK = b'\x15'
CAN = b'\x18'
SUB = b'\x1A'
CRC = b'\x43'

class CheckSumEnum(Enum):
    algebraic = NAK
    crc = CRC

# Set up serial port parameters.
def initialize_serial(port: str, baudrate: int = 9600, timeout=3):
    serial_port = ser.Serial()
    serial_port.baudrate = baudrate
    serial_port.port = port
    serial_port.timeout = timeout
    serial_port.parity = ser.PARITY_NONE
    serial_port.stopbits = ser.STOPBITS_ONE
    serial_port.bytesize = ser.EIGHTBITS
    return serial_port


# Creates and sends packets created from data on serial_port.
def send(serial_port: ser.Serial, data: bytes):
    logging.info(f"Data length: {len(data)}")
    check_sum_type = wait_for_start_sending_and_get_check_sum_type(serial_port)
    logging.info(f"Starting transmission with {check_sum_type}")
    packets = prepare_packets(data, check_sum_type)

    packet_number = 0
    while packet_number < len(packets):
        serial_port.write(packets[packet_number])

        # When receiver sends NAK send packet another time.
        response = serial_port.read(1)
        if response == ACK:
            logging.info(f"{packet_number + 1} received ACK")
            packet_number += 1
        elif response == NAK:
            logging.error(f"{packet_number + 1} received NAK")
            continue
        else:
            logging.error(response)
            raise ReceiverSendUnexpectedResponseException

    response = None
    while response != ACK:
        logging.info("writing EOT")
        serial_port.write(EOT)
        response = serial_port.read()

# Check check-sum type on serial port.
def wait_for_start_sending_and_get_check_sum_type(serial_port: ser.Serial) -> CheckSumEnum:
    for i in range(6):
        # read header
        message = serial_port.read(1)
        if message == NAK:
            return CheckSumEnum.algebraic
        elif message == CRC:
            return CheckSumEnum.crc

    raise ReceiverDoesNotStartTransferException


# Splits a packet into blocks, creates headers, makes datablock 128-bytes long,
#  calculates check sum and puts everything together.
def prepare_packets(data: bytes, check_sum_type: CheckSumEnum) -> [bytes]:
    # Split data into 128 bytes long blocks.
    blocks = [data[i:i + 128] for i in range(0, len(data), 128)]

    packets = []
    for packet_number in range(len(blocks)):
        packet = bytearray()
        packet += create_header(packet_number)

        # Fill last packet with ^z to make it 128 byte length.
        if len(blocks[packet_number]) < 128:
            blocks[packet_number] = fill_block_with_sub(blocks[packet_number])

        # Append data block.
        packet += bytearray(blocks[packet_number])

        # Calculate check-sum and append it to packet.
        calculated_check_sum = calculate_check_sum(blocks[packet_number], check_sum_type)
        packet += bytearray(calculated_check_sum)

        # Append packet to packet list.
        packets.append(bytes(packet))

    return packets

# Creates header with info about check-sum type and the number of packet.
def create_header(packet_number: int) -> bytearray:
    # Append checkSumType.
    header = bytearray(SOH)

    # Packet number starts at 1 when it's lower than 255.
    packet_number += 1

    # Append packet number and it's compliment.
    header.append(packet_number % 255)
    header.append(255 - (packet_number % 255))

    return header

# Makes block from message exactly 128 bytes long.
def fill_block_with_sub(block: bytes):
    block = bytearray(block)
    for i in range(128 - len(block)):
        block += bytearray(SUB)
    return bytes(block)

# Calculates check-sum according to check_sum_type.
def calculate_check_sum(data_block: bytes, check_sum_type: CheckSumEnum):
    if check_sum_type == CheckSumEnum.algebraic:
        return crc.algebraic_check_sum(data_block)
    else:
        return crc.crc_check_sum(data_block)


# Receives packet on serial_port with given check_sum_type.
def receive(serial_port: ser.Serial, check_sum_type: CheckSumEnum) -> bytes:
    result = bytearray()
    # Wait for sender response.
    for i in range(20):
        serial_port.write(check_sum_type.value)
        packet_number = 1
        while True:
            try:
                data_block = read_and_check_packet(serial_port, packet_number, check_sum_type)
                result += bytearray(data_block)
                logging.info("Received block:")
                logging.info(data_block)
                logging.info(f"{packet_number} Sending ACK")
                serial_port.write(ACK)
                packet_number += 1
            except NAKException:
                serial_port.read(serial_port.in_waiting)
                logging.info(f"{packet_number} Sending NAK")
                serial_port.write(NAK)
            except EOTHeaderException:
                serial_port.write(ACK)
                result = remove_ctrl_z(result)
                logging.info(f"Data length: {len(result)}")
                return bytes(result)
            except SenderDoesNotAcceptTransferException:
                break

    raise SenderDoesNotAcceptTransferException


# Reads packet from serial port & does checksum.
def read_and_check_packet(serial_port: ser.Serial, packet_number: int, check_sum_type: CheckSumEnum) -> bytes:
    header = check_header(serial_port, packet_number)
    # Calculate check sum and extract data data_block.
    data_block = serial_port.read(128)
    message_sum = read_check_sum(serial_port, check_sum_type)
    calculated_sum = calculate_check_sum(data_block, check_sum_type)

    # Check is transmitted checksum is the same as calculated.
    if message_sum != calculated_sum:
        logging.error(f"sums aren't the same. Calculated: {calculated_sum}, received: {message_sum}")
        raise WrongCheckSumException

    return data_block


# Checks whether header flag, message number and 
#  message number completion integer is correct
def check_header(serial_port: ser.Serial, packet_number) -> bytearray:
    # Check if header is all good.
    header = serial_port.read(1)

    if len(header) == 0:
        logging.warning("Sender does not accept")
        raise SenderDoesNotAcceptTransferException
    elif header == EOT:
        raise EOTHeaderException
    elif header != SOH:
        logging.error("Wrong header")
        raise WrongHeaderException

    message_number = serial_port.read(1)
    message_number_integer = int.from_bytes(message_number, "big")

    if packet_number % 255 != message_number_integer:
        logging.error("Wrong packet number")
        raise WrongPacketNumberException

    message_number_completion = serial_port.read(1)
    message_number_completion_integer = int.from_bytes(message_number_completion, "big")

    if 255 - (packet_number % 255) != message_number_completion_integer:
        logging.error("Wrong packet number completion")
        raise WrongPacketNumberException

    return bytearray(header) + bytearray(message_number) + bytearray(message_number_completion)

# Reads check sum according to check_sum_type.
def read_check_sum(serial_port: ser.Serial, check_sum_type: CheckSumEnum):
    if check_sum_type == CheckSumEnum.algebraic:
        return serial_port.read(1)
    else:
        return serial_port.read(2)

# Removes char created by clicking CTRL+Z [input].
def remove_ctrl_z(data: bytearray):
    print(data[-1])
    while data[-1] == 0x1A:
        data.pop()

    return data

#region [ Exceptions ]

class ReceiverDoesNotStartTransferException(Exception):
    pass

class SenderDoesNotAcceptTransferException(Exception):
    pass

class NAKException(Exception):
    pass

class WrongPacketNumberException(NAKException):
    pass

class WrongCheckSumException(NAKException):
    pass

class WrongHeaderException(NAKException):
    pass

class EOTHeaderException(Exception):
    pass

class ReceiverSendUnexpectedResponseException(Exception):
    pass

#endregion [ Exceptions ]