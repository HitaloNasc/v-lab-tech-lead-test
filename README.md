# Como rodar o projeto FastAPI

1. Ative o ambiente virtual:
   
   source .venv/bin/activate

2. Instale as dependências (se necessário):
   
   pip install -r requirements.txt

3. Execute o servidor:
   
   uvicorn src.main:app --reload

4. Acesse http://127.0.0.1:8000/ no navegador.

5. Para verificar o endpoint de saúde:
   
   http://127.0.0.1:8000/health

6. Para documentação automática:
   
   http://127.0.0.1:8000/docs
