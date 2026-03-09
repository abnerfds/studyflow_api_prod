# Importamos as ferramentas do Pydantic criadas especificamente para ler arquivos .env.
# No PHP raiz, você usaria $_ENV ou getenv(). No Laravel, usaria a facade env().
# No Python moderno, nós tipamos as variáveis de ambiente para o código quebrar
# imediatamente se estiver faltando alguma credencial no servidor (cultura DevOps/Fail-fast).
from pydantic_settings import BaseSettings, SettingsConfigDict


# Criamos uma classe que herda de BaseSettings.
# Ela vai procurar variáveis de ambiente que tenham exatamente os mesmos nomes dos atributos abaixo.
class Settings(BaseSettings):
    # Tipamos como string. Se o DATABASE_URL não existir no .env, o Pydantic impede a API de ligar.
    database_url: str

    # Instrução interna do Pydantic para dizer a ele: "Leia as variáveis do arquivo chamado .env"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


# Instanciamos a classe em um objeto chamado 'settings'.
# Agora, em qualquer lugar do projeto, basta importar este objeto. É um padrão Singleton prático.
settings = Settings()
