import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 1. IPCA
ipca_factors = {
    2014: 1.6684, 2015: 1.5076, 2016: 1.4184, 2017: 1.3777,
    2018: 1.3279, 2019: 1.2731, 2020: 1.2180, 2021: 1.1067,
    2022: 1.0462, 2023: 1.0000
}

# 2. Receitas
df_rec = pd.read_excel('dados_consolidados_trabalho.xlsx')
df_rec['Valor'] = df_rec['Valor'].astype(str).str.replace(',', '.').astype(float)
df_rec['Fator_Correcao'] = df_rec['Ano'].map(ipca_factors)
df_rec['Valor_Real'] = df_rec['Valor'] * df_rec['Fator_Correcao']

def get_receitas(df_city):
    res = []
    for ano in range(2014, 2024):
        d = df_city[df_city['Ano'] == ano]
        rec_mask = d['Conta'].str.contains('Total Receita|RECEITAS \(EXCETO INTRA', case=False, na=False) & d['Coluna'].str.contains('Realizadas', case=False, na=False)
        rec_val = d[rec_mask]['Valor_Real'].sum()
        if rec_val == 0: 
            rec_mask2 = d['Conta'].str.contains('Receitas Correntes|Receitas de Capital', case=False, na=False) & d['Coluna'].str.contains('Realizadas', case=False, na=False)
            rec_val = d[rec_mask2]['Valor_Real'].sum()
        res.append({'Ano': ano, 'Receita Total': rec_val})
    return pd.DataFrame(res)

rec_g = get_receitas(df_rec[df_rec['Cod.IBGE'] == 2606002])
rec_g['Cod.IBGE'] = 2606002
rec_s = get_receitas(df_rec[df_rec['Cod.IBGE'] == 1600600])
rec_s['Cod.IBGE'] = 1600600
df_receitas = pd.concat([rec_g, rec_s])

# 3. PIB
df_pib_raw = pd.read_excel('tabela5938.xlsx', header=None)
years = df_pib_raw.iloc[3, 3:14].values.astype(int)
pib_s = df_pib_raw.iloc[4, 3:14].values.astype(float) * 1000
pib_g = df_pib_raw.iloc[5, 3:14].values.astype(float) * 1000

df_pib = pd.DataFrame({
    'Ano': list(years) * 2,
    'Cod.IBGE': [1600600]*len(years) + [2606002]*len(years),
    'PIB_Nominal': list(pib_s) + list(pib_g)
})
df_pib = df_pib[df_pib['Ano'].between(2014, 2023)].copy()
df_pib['Fator_Correcao'] = df_pib['Ano'].map(ipca_factors)
df_pib['PIB_Real'] = df_pib['PIB_Nominal'] * df_pib['Fator_Correcao']

# 4. Merge
df_reg = pd.merge(df_pib, df_receitas, on=['Ano', 'Cod.IBGE'])
df_reg = df_reg[df_reg['Receita Total'] > 0]

# 5. Regression & Plotting
df_g = df_reg[df_reg['Cod.IBGE'] == 2606002]
slope_g, intercept_g, r_value_g, p_value_g, std_err_g = stats.linregress(df_g['PIB_Real'], df_g['Receita Total'])

df_s = df_reg[df_reg['Cod.IBGE'] == 1600600]
slope_s, intercept_s, r_value_s, p_value_s, std_err_s = stats.linregress(df_s['PIB_Real'], df_s['Receita Total'])

fig, axes = plt.subplots(1, 2, figsize=(16, 6))

axes[0].scatter(df_g['PIB_Real'] / 1e9, df_g['Receita Total'] / 1e6, color='blue', s=80, alpha=0.7)
axes[0].plot(df_g['PIB_Real'] / 1e9, (intercept_g + slope_g * df_g['PIB_Real']) / 1e6, color='red', linestyle='--')
axes[0].set_title(f'Garanhuns/PE - Dispersão: Receita vs PIB (Real)\n$\\beta_1 = {slope_g:.4f} \\quad R^2 = {r_value_g**2:.4f}$')
axes[0].set_xlabel('PIB (Bilhões R$)')
axes[0].set_ylabel('Receita Total (Milhões R$)')
axes[0].grid(True, alpha=0.5)

axes[1].scatter(df_s['PIB_Real'] / 1e9, df_s['Receita Total'] / 1e6, color='green', s=80, alpha=0.7)
axes[1].plot(df_s['PIB_Real'] / 1e9, (intercept_s + slope_s * df_s['PIB_Real']) / 1e6, color='red', linestyle='--')
axes[1].set_title(f'Santana/AP - Dispersão: Receita vs PIB (Real)\n$\\beta_1 = {slope_s:.4f} \\quad R^2 = {r_value_s**2:.4f}$')
axes[1].set_xlabel('PIB (Bilhões R$)')
axes[1].set_ylabel('Receita Total (Milhões R$)')
axes[1].grid(True, alpha=0.5)

plt.tight_layout()
plt.show()