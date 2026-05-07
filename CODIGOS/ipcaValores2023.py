import pandas as pd
import matplotlib.pyplot as plt

# Fatores IPCA para valores de 2023
ipca_factors = {
    2014: 1.6684, 2015: 1.5076, 2016: 1.4184, 2017: 1.3777,
    2018: 1.3279, 2019: 1.2731, 2020: 1.2180, 2021: 1.1067,
    2022: 1.0462, 2023: 1.0000
}

# Lê e trata os dados
df = pd.read_excel('dados_consolidados_trabalho.xlsx')
df['Valor'] = df['Valor'].astype(str).str.replace(',', '.').astype(float)
df['Fator_Correcao'] = df['Ano'].map(ipca_factors)
df['Valor_Real'] = df['Valor'] * df['Fator_Correcao']

# Função de extração
def get_fiscal_data(df_city):
    res = []
    for ano in range(2014, 2024):
        d = df_city[df_city['Ano'] == ano]
        
        # Receita Total
        rec_mask = d['Conta'].str.contains('Total Receita|RECEITAS \(EXCETO INTRA', case=False, na=False) & d['Coluna'].str.contains('Realizadas', case=False, na=False)
        rec_val = d[rec_mask]['Valor_Real'].sum()
        if rec_val == 0: 
            rec_mask2 = d['Conta'].str.contains('Receitas Correntes|Receitas de Capital', case=False, na=False) & d['Coluna'].str.contains('Realizadas', case=False, na=False)
            rec_val = d[rec_mask2]['Valor_Real'].sum()

        # Receita Tributária
        trib_mask = d['Conta'].str.contains('Receita Tributária|Impostos, Taxas', case=False, na=False) & d['Coluna'].str.contains('Realizadas', case=False, na=False)
        trib_val = d[trib_mask]['Valor_Real'].max()
        if pd.isna(trib_val): trib_val = 0

        # Despesa Total
        desp_mask = d['Coluna'].str.contains('Empenhadas', case=False, na=False)
        desp_val = d[desp_mask]['Valor_Real'].max()
        if pd.isna(desp_val): desp_val = 0
        
        res.append({'Ano': ano, 'Receita Total': rec_val, 'Receita Tributária': trib_val, 'Despesa Total': desp_val})
    return pd.DataFrame(res)

# Processa cidades
res_g = get_fiscal_data(df[df['Cod.IBGE'] == 2606002])
res_s = get_fiscal_data(df[df['Cod.IBGE'] == 1600600])

res_g['Outras Receitas'] = res_g['Receita Total'] - res_g['Receita Tributária']
res_s['Outras Receitas'] = res_s['Receita Total'] - res_s['Receita Tributária']

# ---- GRÁFICO 1: QUESTÃO 3 (Composição da Receita) ----
fig1, axes1 = plt.subplots(1, 2, figsize=(16, 6))

axes1[0].stackplot(res_g['Ano'], res_g['Receita Tributária'] / 1e6, res_g['Outras Receitas'] / 1e6, labels=['Receita Tributária', 'Outras Receitas (Transferências, etc.)'], alpha=0.8, colors=['#1f77b4', '#ff7f0e'])
axes1[0].set_title('Garanhuns/PE - Composição da Receita (Real)')
axes1[0].legend(loc='upper left')
axes1[0].set_ylabel('R$ Milhões')
axes1[0].grid(axis='y', alpha=0.3)

axes1[1].stackplot(res_s['Ano'], res_s['Receita Tributária'] / 1e6, res_s['Outras Receitas'] / 1e6, labels=['Receita Tributária', 'Outras Receitas (Transferências, etc.)'], alpha=0.8, colors=['#1f77b4', '#ff7f0e'])
axes1[1].set_title('Santana/AP - Composição da Receita (Real)')
axes1[1].legend(loc='upper left')
axes1[1].set_ylabel('R$ Milhões')
axes1[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.show()

# ---- GRÁFICO 2: QUESTÃO 4 (Evolução Conjunta) ----
fig2, axes2 = plt.subplots(1, 2, figsize=(16, 6))

axes2[0].plot(res_g['Ano'], res_g['Receita Total'] / 1e6, marker='o', label='Receita Total', color='blue', linewidth=2)
axes2[0].plot(res_g['Ano'], res_g['Despesa Total'] / 1e6, marker='x', label='Despesa Total', color='red', linewidth=2, linestyle='--')
axes2[0].set_title('Garanhuns/PE - Evolução Fiscal Real (2014-2023)\nValores Base 2023')
axes2[0].set_xlabel('Ano')
axes2[0].set_ylabel('R$ Milhões')
axes2[0].grid(True)
axes2[0].legend()

axes2[1].plot(res_s['Ano'], res_s['Receita Total'] / 1e6, marker='o', label='Receita Total', color='blue', linewidth=2)
axes2[1].plot(res_s['Ano'], res_s['Despesa Total'] / 1e6, marker='x', label='Despesa Total', color='red', linewidth=2, linestyle='--')
axes2[1].set_title('Santana/AP - Evolução Fiscal Real (2014-2023)\nValores Base 2023')
axes2[1].set_xlabel('Ano')
axes2[1].set_ylabel('R$ Milhões')
axes2[1].grid(True)
axes2[1].legend()

plt.tight_layout()
plt.show()