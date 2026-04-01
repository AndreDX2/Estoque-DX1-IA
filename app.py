import streamlit as st
import pandas as pd

st.set_page_config(page_title="Logística Inteligente", layout="wide")

st.title("📦 Gestor de Estoque 2.0")

# Upload do Arquivo na barra lateral
uploaded_file = st.sidebar.file_uploader("Suba sua base Excel", type=["xlsx"])
qtd_minima = st.sidebar.number_input("Definir Estoque Mínimo para Ressuprimento", min_value=1, value=5)

if 'erros' not in st.session_state:
    st.session_state.erros = []

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    
    # Criamos as 4 abas de trabalho
    tab1, tab2, tab3, tab4 = st.tabs(["🔄 Consolidação", "🚀 Ressuprimento", "🚨 Alerta Pulmão", "📝 Correções"])

    with tab1:
        st.subheader("Tarefas de Consolidação (Limpeza de Picking)")
        picking = df[df['tipo_posicao'].str.upper() == 'PICKING'].copy()
        duplicados = picking[picking.duplicated(subset=['id'], keep=False)]
        
        if not duplicados.empty:
            duplicados = duplicados.sort_values(by=['id', 'posicao'], ascending=[True, False])
            for item_id in duplicados['id'].unique():
                itens = duplicados[duplicados['id'] == item_id]
                destino = itens.iloc[0]
                origens = itens.iloc[1:]
                for _, orig in origens.iterrows():
                    with st.expander(f"Mover {orig['descricao']} (ID: {item_id})"):
                        st.write(f"**DE:** {orig['posicao']} | **PARA:** {destino['posicao']} | **Qtd:** {orig['quantidade']}")
                        if st.button("✅ Concluído", key=f"c_{orig['posicao']}_{item_id}"):
                            st.success("Feito!")
        else:
            st.info("Nenhum item duplicado no picking.")

    with tab2:
        st.subheader("Sugestões de Ressuprimento")
        st.write(f"Itens no Picking com quantidade menor ou igual a **{qtd_minima}**:")
        
        # Filtra quem está baixo no picking
        baixo_estoque = df[(df['tipo_posicao'].str.upper() == 'PICKING') & (df['quantidade'] <= qtd_minima)]
        
        if not baixo_estoque.empty:
            for _, item in baixo_estoque.iterrows():
                # Busca se esse item existe no pulmão (Reserva) para poder puxar
                estoque_reserva = df[(df['id'] == item['id']) & (df['tipo_posicao'].str.upper() == 'RESERVA')]
                
                with st.expander(f"Repor: {item['descricao']} (Atual: {item['quantidade']})"):
                    st.write(f"**Posição de Venda:** {item['posicao']}")
                    if not estoque_reserva.empty:
                        st.write("**Onde buscar (Reserva):**")
                        st.dataframe(estoque_reserva[['posicao', 'quantidade']])
                    else:
                        st.error("⚠️ Atenção: Não há estoque desse item na Reserva!")
        else:
            st.success("Estoque de picking abastecido!")

    with tab3:
        st.subheader("Itens 'Presos' no Pulmão")
        ids_no_picking = df[df['tipo_posicao'].str.upper() == 'PICKING']['id'].unique()
        pulmao_sem_picking = df[(df['tipo_posicao'].str.upper() == 'RESERVA') & (~df['id'].isin(ids_no_picking))]
        st.dataframe(pulmao_sem_picking[['id', 'descricao', 'posicao', 'quantidade']])

    with tab4:
        st.subheader("Lista de Auditoria")
        if st.session_state.erros:
            st.table(pd.DataFrame(st.session_state.erros))
            if st.button("Limpar"): st.session_state.erros = []
        else:
            st.info("Sem erros registrados.")
else:
    st.info("Por favor, suba o arquivo Excel para começar.")
