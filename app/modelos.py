from dataclasses import dataclass

@dataclass
class Bobina:

    numero: str
    produto: str
    gramatura: int
    formato: int
    diametro: int
    peso: int
    rua: int = 1
    fornecedor: str = ""
    descricao_original: str = ""
