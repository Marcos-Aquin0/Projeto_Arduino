#define NUM_LINHAS 6
int pinosLeitura[NUM_LINHAS] = {A0, A1, A2, A3, A4, A5};
float limiteFalha = 0.2;  // Tensão abaixo deste valor indica falha
unsigned long tempoFalha[NUM_LINHAS] = {0};

int PinHigh = 9;  // Pino do LED

void setup() {
    Serial.begin(9600);
    pinMode(PinHigh, OUTPUT);

    Serial.println("LABEL,Date,Time,Timer,Pino A0,Pino A1,Pino A2,Pino A3,Pino A4,Pino A5");  // Define os rótulos das colunas
}

void loop() {
    digitalWrite(PinHigh, HIGH);  // permite tensão de 5V no pino 9

    // Lê as tensões dos pinos analógicos
    float tensoes[NUM_LINHAS];
    for (int i = 0; i < NUM_LINHAS; i++) {
        tensoes[i] = analogRead(pinosLeitura[i]) * (5.0 / 1023.0);  // Converte o valor analógico para tensão
        if (tensoes[i] < limiteFalha) {
            tempoFalha[i] = millis();  // Registra o tempo da falha
            Serial.print("Falha detectada no pino A");
            Serial.print(i);
            Serial.print(" em ");
            Serial.print(tempoFalha[i] / 1000.0);
            Serial.println(" segundos.");
        }
        // Verifica se todos os pinos estão em falha
        bool todasLinhasComFalha = true;
        for (int i = 0; i < NUM_LINHAS; i++) {
            if (tensoes[i] >= limiteFalha) {
                todasLinhasComFalha = false;
                break;
            }
        }
        // Para o programa apenas se todas as linhas falharem
        if (todasLinhasComFalha) {
            Serial.println("Falha detectada em todos os pinos. Parando o sistema.");
            digitalWrite(PinHigh, LOW);  // Desliga o pino 9
            while (1);  // Para o programa apenas quando todas as linhas falharem
        }
    }

    // Envia os dados para o Excel
    Serial.print("DATA,");
    for (int i = 0; i < NUM_LINHAS; i++) {
        Serial.print(tensoes[i]);
        if (i < NUM_LINHAS - 1) Serial.print(",");  // Adiciona vírgula entre os valores
    }
    Serial.println();  // Finaliza a linha de dados

    delay(500);  // Aguarda 500 ms antes da próxima leitura
}