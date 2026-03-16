import streamlit as st
import pandas as pd
from datetime import datetime
import gspread

# ==========================================
# 1. CONEXÃO COM O GOOGLE SHEETS (VIA NUVEM)
# ==========================================
st.set_page_config(page_title="O Meu Segundo Cérebro", layout="wide", page_icon="🧠")

try:
    # O código agora puxa a chave no formato blindado do Streamlit (TOML)!
    credenciais_dict = dict(st.secrets["google_credentials"])
    gc = gspread.service_account_from_dict(credenciais_dict)
    
    # Abre a planilha pelo nome exato e seleciona a primeira aba
    planilha = gc.open("Base_Segundo_Cerebro").sheet1
except Exception as e:
    st.error(f"⚠️ Erro de Conexão com a Nuvem: {e}")
    st.info("Verifique se o texto no 'Secrets' do Streamlit Cloud está no formato [google_credentials] e se guardou as alterações.")
    st.stop()

# ==========================================
# 2. INTERFACE
# ==========================================
st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <h1>🧠 O Meu Segundo Cérebro</h1>
        <p>Base de conhecimento conectada em tempo real ao Google Sheets.</p>
    </div>
    """, unsafe_allow_html=True)
st.divider()

aba_novo, aba_biblioteca = st.tabs(["💡 Registar Novo Conhecimento", "📚 Explorar a Biblioteca"])

# --- ABA 1: REGISTAR IDEIA ---
with aba_novo:
    st.subheader("O que você aprendeu hoje?")
    
    with st.form(key="form_ideia", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo_registo = st.selectbox("O que está a registar?", ["Livro", "Artigo", "Insight Solto", "Documentário"])
            titulo = st.text_input("Título do Livro ou Tema Central*")
            autor = st.text_input("Autor ou Fonte")
            
        with col2:
            categoria = st.selectbox("Categoria Principal", [
                "Direito", "Teologia e Filosofia", "Logística e Operações", 
                "Desenvolvimento Pessoal", "Física e Saúde", "Outros"
            ])
            tags = st.text_input("Palavras-chave (separadas por vírgula)")
            
        insight = st.text_area("O Insight (A grande lição aprendida)*", height=150)
        
        btn_salvar = st.form_submit_button("💾 Enviar para a Nuvem", type="primary", use_container_width=True)
        
        if btn_salvar:
            if titulo.strip() == "" or insight.strip() == "":
                st.error("Preencha o Título e o Insight principal!")
            else:
                # Prepara a linha exatamente na mesma ordem das colunas do Sheets
                nova_linha = [
                    datetime.now().strftime("%d/%m/%Y %H:%M"),
                    tipo_registo, titulo, autor, categoria, insight, tags
                ]
                # A magia acontece aqui: envia os dados diretos para a nuvem
                planilha.append_row(nova_linha)
                st.success(f"Excelente! '{titulo}' foi guardado em segurança no seu Google Drive.")

# --- ABA 2: EXPLORAR BIBLIOTECA ---
with aba_biblioteca:
    st.subheader("🔍 Pesquisar nos seus Registos")
    
    with st.spinner("A ler dados da nuvem..."):
        # Puxa tudo o que está no Google Sheets
        try:
            dados = planilha.get_all_records()
        except Exception as e:
            st.error(f"Erro ao ler a planilha: {e}")
            dados = []
    
    if dados:
        df_ideias = pd.DataFrame(dados)
        
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            filtro_cat = st.multiselect("Filtrar por Categoria", df_ideias['Categoria'].unique())
        with col_f2:
            busca_texto = st.text_input("Buscar palavra")
            
        df_mostrar = df_ideias.copy()
        if filtro_cat:
            df_mostrar = df_mostrar[df_mostrar['Categoria'].isin(filtro_cat)]
        if busca_texto:
            mask = df_mostrar['Titulo'].str.contains(busca_texto, case=False, na=False) | \
                   df_mostrar['Insight_Principal'].str.contains(busca_texto, case=False, na=False)
            df_mostrar = df_mostrar[mask]
            
        st.markdown(f"**A mostrar {len(df_mostrar)} registos:**")
        
        for index, row in df_mostrar.iterrows():
            with st.expander(f"📖 {row['Titulo']} ({row['Categoria']}) - {row['Data_Registo']}"):
                st.markdown(f"**Fonte:** {row['Autor_Fonte']} | **Tipo:** {row['Tipo']}")
                st.info(row['Insight_Principal'])
                st.caption(f"🏷️ Tags: {row['Tags']}")
    else:
        st.info("A sua planilha do Google ainda está vazia.")
