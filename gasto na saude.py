import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats

# 1. IPCA and Data
ipca_factors = {
    2014: 1.6684, 2015: 1.5076, 2016: 1.4184, 2017: 1.3777,
    2018: 1.3279, 2019: 1.2731, 2020: 1.2180, 2021: 1.1067,
    2022: 1.0462, 2023: 1.0000
}

df_rec = pd.read_excel('dados_consolidados_trabalho.xlsx')
df_rec['Valor'] = df_rec['Valor'].astype(str).str.replace(',', '.').astype(float)
df_rec['Fator_Correcao'] = df_rec['Ano'].map(ipca_factors)
df_rec['Valor_Real'] = df_rec['Valor'] * df_rec['Fator_Correcao']

def get_despesa_total(df_city):
    res = []
    for ano in range(2014, 2023): # Only up to 2022 because we only have mortality data to 2022
        d = df_city[df_city['Ano'] == ano]
        desp_mask = d['Coluna'].str.contains('Empenhadas', case=False, na=False)
        desp_val = d[desp_mask]['Valor_Real'].max()
        if pd.isna(desp_val): desp_val = 0
        res.append({'Ano': ano, 'Despesa Total Real': desp_val})
    return pd.DataFrame(res)

desp_g = get_despesa_total(df_rec[df_rec['Cod.IBGE'] == 2606002])
desp_g['Cod.IBGE'] = 2606002
desp_s = get_despesa_total(df_rec[df_rec['Cod.IBGE'] == 1600600])
desp_s['Cod.IBGE'] = 1600600

# 2. Mortality Data from User Images
data_mortality = {
    'Ano': [2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022],
    'Mortalidade_Garanhuns': [12.71, 13.66, 14.69, 13.79, 13.83, 16.75, 13.22, 12.18, 11.65],
    'Mortalidade_Santana': [13.46, 14.56, 15.98, 17.82, 12.72, 17.94, 17.54, 15.91, 17.59]
}
df_mort = pd.DataFrame(data_mortality)

# Merge Garanhuns
df_g = pd.merge(desp_g, df_mort[['Ano', 'Mortalidade_Garanhuns']], on='Ano')
df_g.rename(columns={'Mortalidade_Garanhuns': 'Mortalidade'}, inplace=True)
df_g = df_g[df_g['Despesa Total Real'] > 0] # Filter out zeros if any

# Merge Santana
df_s = pd.merge(desp_s, df_mort[['Ano', 'Mortalidade_Santana']], on='Ano')
df_s.rename(columns={'Mortalidade_Santana': 'Mortalidade'}, inplace=True)
df_s = df_s[df_s['Despesa Total Real'] > 0] # Filter out zeros

# 3. Stats & Plotting
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

if not df_g.empty:
    slope_g, intercept_g, r_value_g, p_value_g, std_err_g = stats.linregress(df_g['Despesa Total Real'], df_g['Mortalidade'])
    axes[0].scatter(df_g['Despesa Total Real'] / 1e6, df_g['Mortalidade'], color='blue', s=80, alpha=0.7)
    axes[0].plot(df_g['Despesa Total Real'] / 1e6, intercept_g + slope_g * df_g['Despesa Total Real'], color='red', linestyle='--')
    axes[0].set_title(f'Garanhuns/PE - Efeito do Gasto na Saúde\nCorrelação (r): {r_value_g:.4f} | R²: {r_value_g**2:.4f}')
    axes[0].set_xlabel('Despesa Total Empenhada (Milhões R$ - Real)')
    axes[0].set_ylabel('Taxa de Mortalidade Infantil (por mil)')
    axes[0].grid(True, alpha=0.5)

if not df_s.empty and len(df_s) > 1:
    slope_s, intercept_s, r_value_s, p_value_s, std_err_s = stats.linregress(df_s['Despesa Total Real'], df_s['Mortalidade'])
    axes[1].scatter(df_s['Despesa Total Real'] / 1e6, df_s['Mortalidade'], color='green', s=80, alpha=0.7)
    axes[1].plot(df_s['Despesa Total Real'] / 1e6, intercept_s + slope_s * df_s['Despesa Total Real'], color='red', linestyle='--')
    axes[1].set_title(f'Santana/AP - Efeito do Gasto na Saúde\nCorrelação (r): {r_value_s:.4f} | R²: {r_value_s**2:.4f}')
    axes[1].set_xlabel('Despesa Total Empenhada (Milhões R$ - Real)')
    axes[1].set_ylabel('Taxa de Mortalidade Infantil (por mil)')
    axes[1].grid(True, alpha=0.5)
else:
    axes[1].text(0.5, 0.5, 'Dados de Despesa Insuficientes\n(Falha no FINBRA/Siconfi)', ha='center', va='center', fontsize=14)
    axes[1].set_title('Santana/AP - Efeito do Gasto na Saúde')

plt.tight_layout()
plt.show()

print("Garanhuns corr:", r_value_g if not df_g.empty else "N/A")