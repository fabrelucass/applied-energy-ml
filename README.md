# Applied Energy ML & Hydrogen Analytics 🌍⚡

Este repositório reúne projetos práticos de Data Science aplicados à **Transição Energética**, com foco em previsão de carga, produção de Hidrogênio Verde (H2V) e armazenamento de energia.

## 📖 Sobre o Projeto

**Por que escolhi a Transição Energética para aplicar Data Science?**

Sempre acreditei que dados devem gerar impacto real. Nos últimos meses, mergulhei fundo em datasets do setor elétrico para entender na prática como algoritmos podem ajudar a integrar renováveis e hidrogênio verde.

Construí este repositório onde explorei:
✅ **Previsão de carga horária** com Python (Pandas/Scikit-Learn).
✅ **Simulação de produção de Hidrogênio** em horários off-peak.
✅ **Análise de eficiência de Baterias e Supercapacitores**.

Mais do que métricas de acurácia, o objetivo é entender a complexidade e a beleza do grid elétrico.

---

## 📂 Estrutura do Repositório

O repositório está organizado em módulos temáticos:

### 1. Previsão de Carga e Potencial H2 (PJM Interconnection)
📍 **Diretório:** `energy_hourly_consuption_dataset/`

Este é o projeto principal, utilizando dados da rede PJM (EUA).
- **Forecasting:** Modelos de Gradient Boosting para previsão de carga horária (1h à frente).
- **Análise H2V:** Estimativa de produção de hidrogênio utilizando energia "off-peak" (horários de menor demanda), calculando o potencial de produção (kg) e redução de emissões.
- **Destaques:** Comparação entre modelo de ML e Baseline (Persistência), demonstrando a capacidade do modelo de antecipar picos de demanda.

### 2. MVP Hidrogênio (MVP H2)
📍 **Diretório:** `mvp_h2/`

Um Minimum Viable Product focado especificamente na análise exploratória e limpeza de dados para projetos de hidrogênio.
- Scripts de ETL e EDA dedicados.

### 3. Armazenamento Híbrido (HESS)
📍 **Diretório:** `hybrid_energy_storage_dataset/`

Análise de sistemas de armazenamento híbrido (Baterias + Supercapacitores).
- **Foco:** Eficiência, degradação e otimização do uso combinado de tecnologias de armazenamento.

### 4. Perfis de Carga Industrial
📍 **Diretório:** `Load profile data of 50 industrial plants/`

Estudo de perfis de consumo de 50 plantas industriais para entender padrões de demanda em grandes consumidores.

---

## 🚀 Resultados em Destaque

### Forecasting: ML vs Persistência
O modelo desenvolvido supera o baseline de persistência (que assume $t+1 = t$), eliminando o atraso (lag) na previsão e capturando corretamente o *timing* das rampas de subida e descida da carga.

### Hidrogênio Verde
Simulação de operação de eletrolisadores apenas em janelas de baixa carga (off-peak), maximizando o uso de energia excedente e minimizando custos operacionais.

---

## 🛠️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Análise e Manipulação:** Pandas, NumPy
- **Machine Learning:** Scikit-Learn (Gradient Boosting, Linear Regression), XGBoost
- **Visualização:** Matplotlib, Seaborn
- **Ferramentas:** Git, Jupyter Notebooks

---

## ⚙️ Como Executar

1. **Clone o repositório:**
   ```bash
   git clone https://github.com/fabrelucass/applied-energy-ml.git
   cd applied-energy-ml
   ```

2. **Instale as dependências:**
   Navegue até o diretório do projeto desejado (ex: `energy_hourly_consuption_dataset`) e instale os requisitos:
   ```bash
   pip install -r energy_hourly_consuption_dataset/requirements.txt
   ```

3. **Explore os Notebooks e Relatórios:**
   - Os relatórios detalhados estão nas pastas `docs/` e `reports/` de cada módulo.
   - Scripts de execução principal geralmente estão na pasta `src/` ou na raiz do módulo (ex: `mvp_energy.py`).

---

## 📬 Contato

**Lucas Fabre Alves**
[LinkedIn](https://www.linkedin.com/in/lucas-fabre-alves/) | [GitHub](https://github.com/fabrelucass)

---
*Este projeto é parte de um portfólio pessoal focado em Data Science para o setor de energia.*
