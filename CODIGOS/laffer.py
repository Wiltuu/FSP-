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

# 2. Receitas (including Receita Tributária)
df_rec = pd.read_excel('dados_consolidados_trabalho.xlsx')
df_rec['Valor'] = df_rec['Valor'].astype(str).str.replace(',', '.').astype(float)
df_rec['Fator_Correcao'] = df_rec['Ano'].map(ipca_factors)
df_rec['Valor_Real'] = df_rec['Valor'] * df_rec['Fator_Correcao']

def get_receitas_com_tributaria(df_city):
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

        res.append({'Ano': ano, 'Receita Total': rec_val, 'Receita Tributária': trib_val})
    return pd.DataFrame(res)

rec_g = get_receitas_com_tributaria(df_rec[df_rec['Cod.IBGE'] == 2606002])
rec_g['Cod.IBGE'] = 2606002
rec_s = get_receitas_com_tributaria(df_rec[df_rec['Cod.IBGE'] == 1600600])
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
df_laffer = pd.merge(df_pib, df_receitas, on=['Ano', 'Cod.IBGE'])

# Calculate Proxy Carga Tributaria = (Receita Tributaria / PIB) * 100
df_laffer['Carga_Tributaria_Proxy'] = (df_laffer['Receita Tributária'] / df_laffer['PIB_Real']) * 100

# Drop 2014 for Santana if 0
df_laffer = df_laffer[df_laffer['Receita Tributária'] > 0]

df_g = df_laffer[df_laffer['Cod.IBGE'] == 2606002].copy()
df_s = df_laffer[df_laffer['Cod.IBGE'] == 1600600].copy()

# Fit Polynomials (Degree 2) for Laffer Curve
p_g = np.polyfit(df_g['Carga_Tributaria_Proxy'], df_g['Receita Tributária'], 2)
p_s = np.polyfit(df_s['Carga_Tributaria_Proxy'], df_s['Receita Tributária'], 2)

x_g = np.linspace(df_g['Carga_Tributaria_Proxy'].min()*0.8, df_g['Carga_Tributaria_Proxy'].max()*1.2, 100)
x_s = np.linspace(df_s['Carga_Tributaria_Proxy'].min()*0.8, df_s['Carga_Tributaria_Proxy'].max()*1.2, 100)

y_g = np.polyval(p_g, x_g)
y_s = np.polyval(p_s, x_s)

# Plotting
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

axes[0].scatter(df_g['Carga_Tributaria_Proxy'], df_g['Receita Tributária'] / 1e6, color='blue', s=80)
axes[0].plot(x_g, y_g / 1e6, color='red', linestyle='--')
axes[0].set_title('Garanhuns/PE - Curva de Laffer Empírica\n(Receita Trib. vs Carga Tributária Local)')
axes[0].set_xlabel('Proxy Carga Tributária (Rec. Tributária / PIB) %')
axes[0].set_ylabel('Receita Tributária Real (Milhões R$)')
axes[0].grid(True, alpha=0.5)

axes[1].scatter(df_s['Carga_Tributaria_Proxy'], df_s['Receita Tributária'] / 1e6, color='green', s=80)
axes[1].plot(x_s, y_s / 1e6, color='red', linestyle='--')
axes[1].set_title('Santana/AP - Curva de Laffer Empírica\n(Receita Trib. vs Carga Tributária Local)')
axes[1].set_xlabel('Proxy Carga Tributária (Rec. Tributária / PIB) %')
axes[1].set_ylabel('Receita Tributária Real (Milhões R$)')
axes[1].grid(True, alpha=0.5)

plt.tight_layout()
plt.show()

print("Polynomial Coefficients Garanhuns:", p_g)
print("Polynomial Coefficients Santana:", p_s)