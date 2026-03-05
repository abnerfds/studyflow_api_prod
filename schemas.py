# BaseModel é a classe principal do Pydantic. Tudo que herda dela ganha superpoderes de validação.
# EmailStr é um tipo específico que usa Regex internamente para garantir que é um e-mail válido.
from pydantic import BaseModel, EmailStr, ConfigDict

# --- SCHEMAS DE ENTRADA (Request) ---
# Equivalente ao FormRequest do Laravel. Define o que a API ACEITA receber no POST/PUT.
class CandidateCreate(BaseModel):
    name: str
    email: EmailStr # Se o cliente mandar "abner@com", o Pydantic recusa (Erro 422 Unprocessable Entity) sozinho.
    
    # A sintaxe 'str | None = None' significa: 
    # "Isso pode ser uma String OU Nulo. O valor padrão, caso o cliente não envie, é Nulo".
    exam_focus: str | None = None 

# --- SCHEMAS DE SAÍDA (Response / Resource) ---
# Equivalente aos API Resources do Laravel. Define o que a API DEVOLVE para o cliente,
# garantindo que não vamos vazar dados sensíveis (como senhas ou tokens) que estão no banco.
class CandidateResponse(BaseModel):
    id: int
    name: str
    email: str
    exam_focus: str | None

    # NOVO PADRÃO: Substitui a antiga 'class Config'
    model_config = ConfigDict(from_attributes=True)