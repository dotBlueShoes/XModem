def message_from_file(path):
    with open(path, "rb") as message_file:
        result = message_file.read()
    return result

def message_to_file(message: bytes, path):
    with open(path, "wb+") as message_file:
        message_file.write(message)