# Modelo de Previsão e Demanda

Este projeto utiliza o Streamlit para criar uma interface interativa. Siga as instruções abaixo para configurar e rodar o projeto em sua máquina.

## 📋 Pré-requisitos

Certifique-se de ter o seguinte instalado em sua máquina:

- Python 3.8 ou superior
- Git

## 🚀 Como Rodar a Aplicação

1. **Clone o repositório**  
   Abra o terminal e execute o comando abaixo para clonar este repositório:
   ```bash
   git clone git clone git@bitbucket.org:cog-ai/pro-ondemand.git
Navegue para o diretório do projeto

cd nome-do-repositorio
Crie um ambiente virtual (opcional, mas recomendado)

python -m venv venv
Ative o ambiente virtual:

Windows:

.\venv\Scripts\activate
Linux/Mac:
bash
Copiar código
source venv/bin/activate
Instale as dependências
Execute o comando abaixo para instalar os pacotes necessários:


pip install -r requirements.txt
Inicie a aplicação
Execute o seguinte comando para rodar a aplicação Streamlit:


streamlit run main.py
Acesse a aplicação
Após executar o comando acima, o Streamlit exibirá um link (http://localhost:8501) no terminal. Clique no link ou copie e cole no navegador para acessar a aplicação.

🛠️ Configuração Adicional
Se sua aplicação precisar de arquivos de entrada (como CSV, Excel, etc.), certifique-se de adicioná-los ao diretório apropriado antes de iniciar.

📂 Estrutura do Projeto
feature/pro-previsao-streamlit/
├── main.py               # Arquivo principal da aplicação Streamlit
├── demanda.py            # Funções auxiliares de demanda
├── requirements.txt      # Dependências do projeto
├── README.md             # Este arquivo
├── assets/               # (Opcional) Diretório para arquivos estáticos (imagens, etc.)
└── data/                 # Diretório para arquivos de entrada/saída
