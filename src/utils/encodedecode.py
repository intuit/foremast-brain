from base64 import b64decode, b64encode

def encoded(str):
   return b64encode(str.encode())

def decoded(data):
    return b64decode(data).decode()
