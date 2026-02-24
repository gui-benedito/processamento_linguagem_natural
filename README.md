# Assistente de Monitoramento Climático (Local LLM)

Um script Python interativo que utiliza um modelo de linguagem leve e *open-source* (`Qwen2.5-0.5B-Instruct`) para interpretar perguntas em linguagem natural sobre o clima e responder com base em uma base de dados local (`monitoramento_clima.csv`).

O processamento do modelo é feito de forma **100% local**, sem necessidade de internet (após o primeiro download), chaves de API ou autenticação.

---

## Funcionalidades

- **Interpretação de Datas Flexível**: Você pode perguntar sobre o clima usando datas numéricas (`20/01/2024`) ou por extenso (`vinte de janeiro de 2024`, `oito de janeiro`).
- **Filtro Inteligente**: O assistente responde **apenas** sobre a informação que você solicitou (se você pedir só umidade, ele não vai listar temperatura para não poluir a resposta).
- **Consultas em CSV Genéricos**: Toda a busca real de dados acontece cruzando a data com a base estática do Pandas, garantindo 0 alucinação em valores numéricos.
- **Respostas Humanas**: Em vez de cuspir os dados brutos de forma técnica na tela, o assistente gera uma frase única, como um meteorologista experiente.

---

## Como Instalar e Rodar

### 1. Requisitos
Você precisa ter o **Python 3.8+** instalado em sua máquina.

### 2. Configurar o Ambiente

Recomendamos criar um ambiente virtual (venv) na pasta do projeto para não sujar o Python do seu sistema:

#### No Windows:
```bash
python -m venv venv
.\venv\Scripts\activate
```

#### No Linux/Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instalar Dependências

Com o ambiente ativado, instale os pacotes principais, como o `transformers` e `torch`:

```bash
pip install -r requirements.txt
```

---

## Como Utilizar

Basta executar o script com o comando:

```bash
python consulta_clima.py
```

Na **primeira execução**, o script baixará os pesos do modelo ~Qwen2.5-0.5B~ para cache localmente na sua máquina (`~1GB`). Nas próximas execuções, o carregamento será instantâneo.

Ao abrir, ele mostrará uma interface de Chat e você pode testar com frases variadas:
- `"Qual foi a umidade em dez de janeiro de 2024?"`
- `"Temperatura em vinte e oito de janeiro de 2024"`
- `"Como estava o clima no dia 15/01/2024?"`

Digite **`sair`** a qualquer momento no input para encerrar a conversa.

---

## Base de Dados
O script lê a fonte de verdade do arquivo `monitoramento_clima.csv` presente na mesma pasta.
Garanta que ele obedece a estrutura:
```csv
Data,Temperatura,Umidade
2024-01-01,25.4,65
```
