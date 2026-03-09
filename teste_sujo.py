from fastapi import FastAPI

app = FastAPI()


def soma_numeros(a: int, b: int) -> int:
    resultado = a + b
    return resultado
