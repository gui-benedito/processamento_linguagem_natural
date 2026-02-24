import pandas as pd
import torch
import re
import warnings
from transformers import pipeline
from transformers import logging as hf_logging

# silencia os warnings e logs internos do transformers na pipeline
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")
warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
hf_logging.set_verbosity_error()

# arquivo CSV
CSV_PATH = 'monitoramento_clima.csv'

def load_data(filepath):
    try:
        return pd.read_csv(filepath)
    except Exception as e:
        print(f"Erro ao ler o CSV: {e}")
        return None

def setup_llm():
    print("Iniciando o carregamento do modelo Qwen/Qwen2.5-0.5B-Instruct...")
    print("Por ser um modelo leve e livre, será executado localmente sem necessidade de autenticação.")
    try:
        # pipeline para geração de texto
        generator = pipeline(
            "text-generation",
            model="Qwen/Qwen2.5-0.5B-Instruct",
            device_map="auto",
            torch_dtype=torch.float16
        )
        print("Modelo carregado com sucesso!\n")
        return generator
    except Exception as e:
        print(f"Erro ao carregar o LLM: {e}")
        print("Certifique-se de ter os pacotes 'transformers', 'torch' e 'accelerate' instalados.")
        return None

def extract_date(generator, user_input):
    """
    Usa o LLM para converter qualquer formato de data falado pelo usuário para YYYY-MM-DD.
    """
    prompt = f"""<|im_start|>system
Você converte as datas do português para o formato YYYY-MM-DD.
Meses: janeiro=01, fevereiro=02, marco=03, abril=04, maio=05, junho=06, julho=07, agosto=08, setembro=09, outubro=10, novembro=11, dezembro=12.
Exemplos:
'21/04/2024' -> 2024-04-21
'doze de janeiro de 2024' -> 2024-01-12
'vinte e oito de janeiro de 2024' -> 2024-01-28
'trinta de janeiro de 2024' -> 2024-01-30
'vinte de janeiro de 2024' -> 2024-01-20
'vinte e quatro de janeiro de 2024' -> 2024-01-24
'oito de janeiro de 2024' -> 2024-01-08
Responda APENAS a data convertida (YYYY-MM-DD), nada mais.
<|im_end|>
<|im_start|>user
'{user_input}' -> <|im_end|>
<|im_start|>assistant
"""
    
    result = generator(prompt, max_new_tokens=15, return_full_text=False, temperature=0.01)
    text = result[0]['generated_text'].strip()
    return text

def generate_report(generator, date, temp=None, humidity=None, found=True):
    """
    Usa o LLM para responder de forma natural sobre a informação climática da data,
    ou avisar que não existe a informação caso a data não seja encontrada.
    """
    if found:
        if temp is not None and humidity is not None:
            sys_msg = "Você é um meteorologista amigável. Responda em uma única frase informando exatamente a temperatura e a umidade passadas pelo usuário. Use verbos no passado e inclua os valores exatos."
            user_msg = f"Data: {date}\nTemperatura: {temp}°C\nUmidade: {humidity}%"
        elif temp is not None:
            sys_msg = "Você é um meteorologista amigável. Responda em uma única frase informando exatamente a temperatura passada pelo usuário. Use verbos no passado e OBRIGATORIAMENTE inclua o valor numérico da temperatura na frase."
            user_msg = f"Data: {date}\nTemperatura exata: {temp}°C"
        elif humidity is not None:
            sys_msg = "Você é um meteorologista amigável. Responda em uma única frase informando exatamente a umidade passada pelo usuário. Use verbos no passado e OBRIGATORIAMENTE inclua o valor numérico da umidade na frase."
            user_msg = f"Data: {date}\nUmidade exata: {humidity}%"
    else:
        sys_msg = "Você é um assistente virtual. Informe que os dados para esta data não existem."
        user_msg = f"Data: {date}"
        
    prompt = f"""<|im_start|>system
{sys_msg}<|im_end|>
<|im_start|>user
{user_msg}\nResponda agora:<|im_end|>
<|im_start|>assistant
"""
    result = generator(prompt, max_new_tokens=60, return_full_text=False, temperature=0.1)
    return result[0]['generated_text'].strip()

def main():
    # carrega a base de dados
    df = load_data(CSV_PATH)
    if df is None:
        return
        
    # carrega o modelo
    generator = setup_llm()
    if generator is None:
        return
        
    print("="*60)
    print("Chat do Clima Iniciado!")
    print("Dados disponiveis entre 2024-01-01 e 2024-01-30")
    print("(Digite 'sair' a qualquer momento para encerrar)")
    print("="*60)
    
    while True:
        try:
            print("\n")
            user_input = input(">> Qual data você deseja consultar? (""sair"" para fechar): ").strip()
            
            if not user_input:
                continue
                
            if user_input.lower() in ['sair', 'exit', 'quit']:
                print("Encerrando o programa. Até logo!")
                break
                
            print("Processando a data com o LLM...")
            parsed_date_text = extract_date(generator, user_input)
            
            # limpeza caso o modelo retorne algo a mais:
            match = re.search(r'\d{4}-\d{2}-\d{2}', parsed_date_text)
            if not match:
                print(f"Não consegui entender a data a partir da sua entrada: '{user_input}'. O LLM interpretou como: {parsed_date_text}. Tente novamente usando outro formato, por exemplo: '12/01/2024'.")
                continue
                
            standard_date = match.group()
            print(f"Data interpretada como: {standard_date}")
            
            # buscar na base csv
            row = df[df['Data'] == standard_date]
            print("Gerando mensagem com o LLM...")
            
            if not row.empty:
                temp_db = row.iloc[0]['Temperatura']
                umid_db = row.iloc[0]['Umidade']
                
                # identifica o que o usuário quer saber
                input_lower = user_input.lower()
                quer_temp = 'temperatura' in input_lower
                quer_umid = 'umidade' in input_lower
                
                # se não perguntar nada específico, devolve os dois
                if not quer_temp and not quer_umid:
                    quer_temp = True
                    quer_umid = True
                    
                temp_info = temp_db if quer_temp else None
                umid_info = umid_db if quer_umid else None
                
                resposta = generate_report(generator, standard_date, temp=temp_info, humidity=umid_info, found=True)
                print(f"\n[RESPOSTA]:\n{resposta}")
            else:

                print(f"\n[RESPOSTA]:\nDesculpe, a data {standard_date} não foi encontrada em nossa base de clima. Tente novamente!")
                
        except KeyboardInterrupt:
            print("\nEncerrando o programa. Até logo!")
            break

if __name__ == "__main__":
    main()