# bibliotecas
import serial 
import time
import datetime
import pandas as pd
import threading

def collect_arduino_data(port='COM5', baud_rate=9600, limite_falha=0.2):
    """
    Coletar dados e salvar em uma planilha excel
    
    Parâmetros:
    - port: porta serial do arduíno (varia de acordo com o sistema)
    - baud_rate: Serial.begin() value do arduíno
    - limite_falha: valor abaixo do qual considera-se uma falha (deve ser igual ao definido no Arduino)
    """
    try:
        print(f"Tentando conectar ao Arduino na porta {port}...")
        ser = serial.Serial(port, baud_rate, timeout=1)
        print("Conexão estabelecida! Aguardando inicialização do Arduino...")
        
        # espera a inicialização do arduino
        time.sleep(2)
        
        # dict para armazenar os dados em df
        data = {
            'Timestamp': [],
            'A0': [], 'A1': [], 'A2': [], 
            'A3': [], 'A4': [], 'A5': [],
            'Falhas': []  # Nova coluna para registrar falhas
        }
        
        start_time = datetime.datetime.now()
        print("Começando a coletar dados...")
        
        # Flag para parar a coleta de dados
        stop_collection = False
        
        # Thread para esperar o input enquanto apresenta os dados paralelamente
        def check_input():
            nonlocal stop_collection
            input("Pressione Enter para parar a coleta de dados...\n")
            stop_collection = True
        
        input_thread = threading.Thread(target=check_input)
        input_thread.daemon = True
        input_thread.start()
        
        # Conta quantos dados foram coletados
        count = 0
        
        while not stop_collection:
            # lê e decodifica os dados
            if ser.in_waiting:
                try:
                    line_bytes = ser.readline()
                    try:
                        line = line_bytes.decode('utf-8', errors='replace').strip()
                    except UnicodeDecodeError:
                        line = line_bytes.decode('latin-1').strip()
                    
                    print(f"Dados recebidos: {line}")  # Debug print
                    
                    if line.startswith('DATA'):
                        parts = line.split(',')
                        print(f"Partes divididas: {parts}")  # Debug print
                        
                        if len(parts) >= 7:  # 6 valores de tensão + 1 timestamp
                            current_time = datetime.datetime.now()
                            data['Timestamp'].append(current_time)
                            
                            # Verificar falhas
                            tem_falha = 0  # 0 = sem falha, 1 = com falha
                            
                            for i, value in enumerate(parts[1:7]):
                                try:
                                    float_value = float(value)
                                    data[f'A{i}'].append(float_value)
                                    
                                    # Verifica se este pino está em falha
                                    if float_value < limite_falha:
                                        tem_falha = 1
                                        print(f"⚠️ Falha detectada no pino A{i}: {float_value}V < {limite_falha}V")
                                    
                                    print(f"A{i}: {float_value}")  # Debug print
                                except ValueError:
                                    print(f"Erro na conversão: A{i} = {value}")
                                    data[f'A{i}'].append(None)
                            
                            # Registra se houve falha nesta leitura
                            data['Falhas'].append(tem_falha)
                            if tem_falha == 1:
                                print("⚠️ ALERTA: Falha detectada nesta leitura!")
                            
                            count += 1
                            if count % 10 == 0:  # conferindo a cada 10 linhas
                                print(f"Coletados {count} pontos de dados até agora")
                except Exception as e:
                    print(f"Erro ao processar linha: {e}")
                    continue
            
            # delay para prevenir o overload da CPU
            time.sleep(0.01)
        
        # encerra a conexão serial
        ser.close()
        
        # converte para df
        df = pd.DataFrame(data)
        
        if len(df) == 0:
            print("Nenhum dado foi coletado. Verifique a comunicação com o Arduino.")
            return None
            
        
        # Excel
        filename = f'arduino_data_{start_time.strftime("%Y%m%d_%H%M%S")}.xlsx'
        df.to_excel(filename, index=False)
        print(f"Dados salvos em {filename}")
        
        # Resumo de falhas
        total_falhas = df['Falhas'].sum()
        print(f"\nResumo das falhas:")
        print(f"- Total de leituras: {len(df)}")
        print(f"- Leituras com falha: {total_falhas} ({total_falhas/len(df)*100:.1f}%)")
        
        return df
    
    except serial.SerialException as e:
        print(f"Erro na conexão com Arduino: {e}")
        print("Verifique se:")
        print(" - O Arduino está conectado ao computador")
        print(f" - A porta COM está correta (atualmente usando {port})")
        print(" - Nenhum outro programa está usando a porta serial")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    finally:
        # garantir que a conexão serial seja finalizada
        try:
            ser.close()
        except:
            pass

if __name__ == "__main__":
    try:
        port = input("Digite a porta COM do Arduino (padrão: COM5): ") or "COM5"    
        dataframe = collect_arduino_data(port=port)
        if dataframe is not None and not dataframe.empty:
            print(f"Dados coletados: {len(dataframe)} pontos")
            print("\nPrimeiras 5 linhas:")
            print(dataframe.head())
    except KeyboardInterrupt:
        print("\nColeta de dados interrompida pelo usuário.")