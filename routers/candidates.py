# APIRouter é a classe que permite criar rotas fora do main.py. 
# É o equivalente a criar um Controller no MVC tradicional ou usar o Route::group() no Laravel.
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# Importamos a injeção de dependência do banco, o Model do banco e os DTOs de validação.
from database import get_db
from models import Candidate
from schemas import CandidateCreate, CandidateResponse

# Instanciamos o router. 
# prefix="/candidates": Todas as rotas aqui dentro já começam com esse caminho.
# tags=["Candidates"]: Organiza visualmente o Swagger lá na documentação interativa.
router = APIRouter(prefix="/candidates", tags=["Candidates"])

# Definimos uma rota POST. 
# response_model=CandidateResponse: Força a saída a passar pelo DTO de saída que criamos.
# status_code=201: Respeita a semântica REST HTTP de que um recurso foi criado (Created).
@router.post("/", response_model=CandidateResponse, status_code=201)
async def create_candidate(
    # Injeção de Dependência 1: O FastAPI pega o JSON do body da requisição e valida usando o CandidateCreate.
    candidate: CandidateCreate, 
    
    # Injeção de Dependência 2: Depends(get_db) abre uma conexão com o Postgres EXCLUSIVA 
    # para esta requisição HTTP e garante que ela será fechada no final.
    db: AsyncSession = Depends(get_db) 
):
    # Instanciamos a classe do ORM com os dados limpos e validados pelo Pydantic (candidate.name, etc.)
    new_candidate = Candidate(
        name=candidate.name,
        email=candidate.email,
        exam_focus=candidate.exam_focus
    )
    
    # Prepara o objeto para ser inserido (equivalente ao persist() do Doctrine PHP)
    db.add(new_candidate)
    
    # FEATURE ASSÍNCRONA: O 'await' pausa esta função específica e libera o servidor (Uvicorn) 
    # para atender outros usuários enquanto o Postgres executa o comando de INSERT pesado.
    await db.commit()
    
    # FEATURE DO ORM: Atualiza a variável 'new_candidate' com os dados reais do banco
    # (por exemplo, busca o 'id' auto-incrementado que o Postgres acabou de gerar).
    await db.refresh(new_candidate)
    
    # Retorna o objeto do SQLAlchemy. O FastAPI, vendo o 'response_model' lá em cima, 
    # passa esse objeto pelo schema CandidateResponse, converte pra JSON e devolve pro cliente.
    return new_candidate

# --- NOVA ROTA GET (Listagem) ---
# O response_model aqui usa list[] porque vamos devolver um array de candidatos
@router.get("/", response_model=list[CandidateResponse])
async def list_candidates(db: AsyncSession = Depends(get_db)):
    # 1. Monta a query estruturada (equivalente a SELECT * FROM candidates)
    query = select(Candidate)
    
    # 2. Executa a query de forma ASSÍNCRONA no Postgres (o servidor não trava aqui)
    result = await db.execute(query)
    
    # 3. Extrai os objetos reais do banco de dentro do resultado bruto
    candidates = result.scalars().all()
    
    # O FastAPI converte a lista de objetos Python para um Array JSON automaticamente
    return candidates