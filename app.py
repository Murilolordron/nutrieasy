import streamlit as st
from fpdf import FPDF

# Configuração da página do Streamlit
st.set_page_config(page_title="NutriApp Pro", page_icon="🥑", layout="centered")

st.title("🥑 NutriApp: Macros, Porções & Substitutos")
st.write("Calcule suas metas, fragmente suas refeições e encontre substitutos equivalentes.")

# --- ENTRADA DE DADOS DO USUÁRIO ---
st.header("1. Informações Pessoais")
col1, col2 = st.columns(2)

with col1:
    genero = st.radio("Gênero Biológico:", ["Masculino", "Feminino"])
    idade = st.number_input("Idade (anos):", min_value=1, max_value=110, value=25)
    peso = st.number_input("Peso Atual (kg):", min_value=30.0, max_value=250.0, value=70.0, step=0.1)

with col2:
    altura = st.number_input("Altura (cm):", min_value=100, max_value=250, value=170)
    
    atividade_fatores = {
        "Sedentário (pouco ou nenhum exercício)": 1.2,
        "Leve (exercício leve 1-3 dias/semana)": 1.375,
        "Moderado (exercício moderado 3-5 dias/semana)": 1.55,
        "Intenso (exercício pesado 6-7 dias/semana)": 1.725
    }
    atividade = st.selectbox("Nível de Atividade Física:", list(atividade_fatores.keys()))
    fator_atividade = atividade_fatores[atividade]

    objetivo = st.selectbox("Qual é o seu objetivo principal?", ["Emagrecimento", "Manutenção de Peso", "Ganho de Massa (Hipertrofia)"])

# --- ESTRUTURA DA DIETA ---
st.header("2. Estrutura da Dieta")
num_refeicoes = st.slider("Em quantas refeições deseja fragmentar o seu dia?", min_value=3, max_value=6, value=4)

# --- CÁLCULOS METABÓLICOS ---
if genero == "Masculino":
    tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
else:
    tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161

get = tmb * fator_atividade

if objetivo == "Emagrecimento":
    calorias_alvo = get - 500
    pct_p, pct_c, pct_g = 0.30, 0.40, 0.30
elif objetivo == "Ganho de Massa (Hipertrofia)":
    calorias_alvo = get + 400
    pct_p, pct_c, pct_g = 0.25, 0.55, 0.20
else:
    calorias_alvo = get
    pct_p, pct_c, pct_g = 0.25, 0.45, 0.30

# Totais Diários
g_proteina_total = (calorias_alvo * pct_p) / 4
g_carbo_total = (calorias_alvo * pct_c) / 4
g_gordura_total = (calorias_alvo * pct_g) / 9

# Divisão Proporcional por Refeição
calorias_por_refeicao = calorias_alvo / num_refeicoes
g_proteina_por_ref = g_proteina_total / num_refeicoes
g_carbo_por_ref = g_carbo_total / num_refeicoes
g_gordura_por_ref = g_gordura_total / num_refeicoes

# --- EXIBIÇÃO DE RESULTADOS NA TELA ---
st.header("3. Seu Diagnóstico Energético")
res1, res2, res3 = st.columns(3)
res1.metric("Metabolismo Basal", f"{int(tmb)} kcal")
res2.metric("Gasto Diário Total", f"{int(get)} kcal")
res3.metric("Meta Calórica Diária", f"{int(calorias_alvo)} kcal")

st.subheader(f"Metas por Refeição (Fragmentado em {num_refeicoes}x)")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🔥 Calorias / Ref", f"{int(calorias_por_refeicao)} kcal")
m2.metric("🍗 Proteínas / Ref", f"{int(g_proteina_por_ref)}g")
m3.metric("🍞 Carboidratos / Ref", f"{int(g_carbo_por_ref)}g")
m4.metric("🥑 Gorduras / Ref", f"{int(g_gordura_por_ref)}g")

# --- BANCO DE DADOS DE ALIMENTOS E SUBSTITUTOS (ARROZ BRANCO COMO PRINCIPAL) ---
alimentos_base = {
    "Proteínas": {
        "Frango grelhado": ["100g de Patinho moído", "120g de Tilápia/Pescada", "4 Ovos inteiros", "30g de Whey Protein"],
        "Ovos mexidos": ["70g de Frango desfiado", "80g de Queijo Minas Frescal", "70g de Atum em lata"]
    },
    "Carboidratos": {
        "Arroz branco": ["100g de Arroz integral", "100g de Batata-doce cozida", "100g de Mandioca cozida", "90g de Macarrão cozido", "35g de Aveia em flocos", "200g de Melão (Opção Fruta)", "160g de Maçã (Opção Fruta)", "200g de Morango (Opção Fruta)"],
        "Pão integral": ["30g de Tapioca", "20g de Aveia em flocos", "1 Banana Prata pequena (Opção Fruta)", "150g de Mamão Formosa (Opção Fruta)"]
    },
    "Gorduras": {
        "Azeite de oliva": ["15g de Pasta de amendoim", "15g de Castanhas de Caju", "50g de Abacate"]
    }
}

nomes_refeicoes = {
    3: ["Café da Manhã", "Almoço", "Jantar"],
    4: ["Café da Manhã", "Almoço", "Lanche da Tarde", "Jantar"],
    5: ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar"],
    6: ["Café da Manhã", "Lanche da Manhã", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
}

st.header("4. Cardápio Sugerido & Substituições")

multiplicador = 1.4 if objetivo == "Ganho de Massa (Hipertrofia)" else (0.9 if objetivo == "Emagrecimento" else 1.1)
fator_ajuste_refeicoes = 4 / num_refeicoes 
fator_final = multiplicador * fator_ajuste_refeicoes

cardapio_gerado = []

for i, nome_ref in enumerate(nomes_refeicoes[num_refeicoes]):
    st.subheader(f"🔹 Refeição {i+1}: {nome_ref}")
    
    # Define alimentos com base no tipo de refeição
    if "Almoço" in nome_ref or "Jantar" in nome_ref:
        p_nome, p_qtd, p_tipo = "Frango grelhado", f"{int(100 * fator_final)}g", "Proteínas"
        c_nome, c_qtd, c_tipo = "Arroz branco", f"{int(120 * fator_final)}g", "Carboidratos"
        g_nome, g_qtd, g_tipo = "Azeite de oliva", "1 colher de chá", "Gorduras"
        
        texto_principal = f"• {p_qtd} de {p_nome}\n• {c_qtd} de {c_nome}\n• {g_qtd} de {g_nome}\n• Salada verde à vontade"
    else:
        p_nome, p_qtd, p_tipo = "Ovos mexidos", f"{max(2, int(2 * fator_final))} un", "Proteínas"
        c_nome, c_qtd, c_tipo = "Pão integral", f"{max(1, int(1.5 * fator_final))} fatia(s)", "Carboidratos"
        g_nome, g_qtd, g_tipo = "Azeite de oliva", "Usar apenas um fio para grelhar", "Gorduras"
        
        texto_principal = f"• {p_qtd} de {p_nome}\n• {c_qtd} de {c_nome}\n• {g_qtd}"

    # Exibição do Cardápio Principal
    st.markdown("**Opção Principal Sugerida:**")
    st.info(texto_principal)

    # Busca os substitutos
    sub_p = "\n• ".join(alimentos_base[p_tipo][p_nome])
    sub_c = "\n• ".join(alimentos_base[c_tipo][c_nome])
    
    texto_substitutos = f"**Substitutos para a Proteína (Escolha 1):**\n• {sub_p}\n\n**Substitutos para o Carboidrato (Escolha 1):**\n• {sub_c}"
    
    # Exibição das Substituições Separadas
    with st.expander("🔄 Ver Opções de Substitutos Equivalentes para esta refeição"):
        st.success(texto_substitutos)
    
    # Salva os dados estruturados para a geração do PDF
    cardapio_gerado.append({
        "refeicao": nome_ref,
        "principal": texto_principal,
        "substitutos": texto_substitutos
    })
    st.markdown("---")

# --- FUNÇÃO PARA GERAR O PDF ---
def gerar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    
    # Título do Relatório
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(200, 10, txt="Plano Alimentar Inteligente Pro", ln=True, align="C")
    pdf.ln(5)
    
    # Metas Nutricionais
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(200, 10, txt="1. Metas Nutricionais Diarias", ln=True)
    pdf.set_font("Helvetica", size=11)
    pdf.cell(200, 8, txt=f"Objetivo: {objetivo} | Divisao: {num_refeicoes} refeicoes", ln=True)
    pdf.cell(200, 8, txt=f"Meta Calorica: {int(calorias_alvo)} kcal/dia ({int(calorias_por_refeicao)} kcal por refeicao)", ln=True)
    pdf.cell(200, 8, txt=f"Macros por Refeicao: P: {int(g_proteina_por_ref)}g | C: {int(g_carbo_por_ref)}g | G: {int(g_gordura_por_ref)}g", ln=True)
    pdf.ln(5)
    
    # Detalhamento do Cardápio
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(200, 10, txt="2. Cardapio Detalhado", ln=True)
    pdf.ln(2)
    
    for item in cardapio_gerado:
        # Nome da Refeição
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(200, 8, txt=f"=== {item['refeicao'].upper()} ===", ln=True)
        
        # Bloco Principal
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(200, 6, txt="[OPCAO PRINCIPAL]", ln=True)
        pdf.set_font("Helvetica", size=10)
        for linha in item['principal'].split('\n'):
            txt_formatado = linha.replace('• ', '- ').encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(200, 5, txt=txt_formatado, ln=True)
        
        pdf.ln(2)
        
        # Bloco Substitutos
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(200, 6, txt="[SUGESTOES DE SUBSTITUICAO]", ln=True)
        pdf.set_font("Helvetica", size=9) 
        for linha in item['substitutos'].split('\n'):
            txt_formatado = linha.replace('• ', '- ').replace('**', '').encode('latin-1', 'ignore').decode('latin-1')
            pdf.cell(200, 5, txt=txt_formatado, ln=True)
            
        pdf.ln(4)
        
    return bytes(pdf.output())

# --- BOTÃO DE DOWNLOAD ---
st.subheader("💾 Salvar Resultados")
pdf_bytes = gerar_pdf()

st.download_button(
    label="📥 Baixar Plano Alimentar  (PDF)",
    data=pdf_bytes,
    file_name="plano_alimentar_avancado.pdf",
    mime="application/pdf"
)


