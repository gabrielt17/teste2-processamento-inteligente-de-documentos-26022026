# 🧾 Desafio Técnico — Extração e Geração de Fatura (Energia Solar)

## 📌 Contexto do Projeto

Este projeto consiste no desenvolvimento de uma ferramenta para processar **faturas de energia elétrica em formato de imagem**. O desafio abrange desde a extração de dados via OCR (Optical Character Recognition) até a aplicação de regras de negócio do setor elétrico para gerar um novo demonstrativo financeiro.

O objetivo principal é calcular a economia gerada pelo uso de créditos de energia solar e consolidar os valores para o consumidor final.

---

## 🚀 Objetivos

* **Extração de Dados:** Converter documentos não estruturados (imagens) em dados estruturados.
* **Processamento Financeiro:** Aplicar regras de compensação de créditos de energia.
* **Simulação Comparativa:** Demonstrar o cenário do cliente com e sem o uso de créditos de energia.
* **Interface de Saída:** Gerar um relatório claro e legível (via terminal ou arquivo).

---

## 🔎 Etapa 1 — Extração de Informações

Nesta fase, o sistema deve identificar e extrair os seguintes campos da fatura original:

### 📋 Dados Mapeados

| Campo | Descrição |
| --- | --- |
| **Cliente** | Nome completo do titular da conta. |
| **Instalação** | Número de identificação da unidade consumidora. |
| **Cronologia** | Datas de emissão, vencimento e mês de referência. |
| **Consumo Total (kWh)** | Volume total de energia consumida da rede. |
| **Energia Compensada (kWh)** | Créditos de energia elétrica compensados no mês. |
| **Valor Distribuidora (R$)** | Valor final cobrado pela concessionária local. |
| **Tarifa com Impostos** | Tarifa aplicada sobre a energia não compensada. |
| **Iluminação Pública** | Valor da taxa de iluminação (se aplicável). |

---

## 📐 Etapa 2 — Regras de Cálculo e Negócio

Para gerar a fatura consolidada, o sistema aplica as seguintes fórmulas matemáticas:

### 1. Valor devido à Usina

O cálculo do valor a pagar pelo crédito de energia compensada utiliza a tarifa com impostos aplicada pela distribuidora subtraída do desconto comercial acordado:

$$V_{usina} = E_{comp} \times T_{imp} \times (1 - D)$$

Onde:

* $V_{usina}$: Valor a pagar à usina solar.
* $E_{comp}$: Quantidade de energia compensada (kWh).
* $T_{imp}$: Tarifa com impostos.
* $D$: Percentual de desconto.

**Para a fatura a ser gerada considere um percentual de desconto de 10%.**

### 2. Identificação de Encargos

Caso os encargos extras não estejam explícitos, o sistema deve deduzir o valor residual:

$$Encargos = Valor_{APagarDistribuidora}  - Valor_{EnergiaNãoCompensada} - Taxa_{Iluminação}$$

---

## 📝 Exemplo de Saída Consolidada

O sistema deve gerar um log ou arquivo seguindo o padrão visual abaixo:

```text
============================================================
                FATURA CONSUMIDOR FINAL
============================================================
Cliente: João da Silva           Instalação: 12345678
Referência: JAN/2026             Vencimento: 20/01/2026
------------------------------------------------------------
TOTAL A PAGAR À DISTRIBUIDORA:               R$ 75,50
------------------------------------------------------------

VALOR A PAGAR À USINA
------------------------------------------------------------
Descrição               Qtd     Tarifa     Valor
Energia Compensada      450     0,819      R$ 368,55

FATURA SEM ENERGIA SOLAR
------------------------------------------------------------
Descrição               Qtd     Tarifa     Valor
Consumo Energia Total   500     0,91       R$ 455,00
Outros Encargos          -       -         R$ 15,00
Taxa Iluminação          -       -         R$ 15,00
------------------------------------------------------------
TOTAL SEM SOLAR                            R$ 485,00

FATURA COM ENERGIA SOLAR
------------------------------------------------------------
Descrição               Qtd     Tarifa     Valor
Energia Não Compensada  50      0,91       R$ 45,50
Energia Compensada      450     0,819      R$ 368,55
Outros Encargos          -       -         R$ 15,00
Taxa Iluminação          -       -         R$ 15,00
------------------------------------------------------------
TOTAL COM SOLAR                            R$ 444,05



RESUMO DE ECONOMIA
------------------------------------------------------------
TOTAL SEM SOLAR                            R$ 485,00
------------------------------------------------------------
TOTAL COM SOLAR                            R$ 444,05
------------------------------------------------------------
ECONOMIA CALCULADA                         R$ 40,95
------------------------------------------------------------


TOTAL A PAGAR (CONSOLIDADO):               R$ 368,55
============================================================

```

---

## 🛠️ Tecnologias Sugeridas

* **Linguagem:** Python 3.x
* **OCR:** Tesseract OCR ou Google Cloud Vision.
* **Estruturação:** JSON ou Dicionários Python.
* **Manipulação de Imagens:** OpenCV ou Pillow.

---

**Dica:** Certifique-se de que o OCR consiga ler corretamente os números decimais (vírgula vs ponto) para evitar erros nos cálculos financeiros!