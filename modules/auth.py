import streamlit as st

def login():
    # Senha definida aqui
    SENHA_CORRETA = "Proc@2025"
    
    st.title("🔒 Acesso Protegido")
    senha_input = st.text_input("Digite a senha para acessar:", type="password")
    
    if senha_input == SENHA_CORRETA:
        st.success("Acesso permitido!")
        return True
    elif senha_input:
        st.error("Senha incorreta!")
        return False
    else:
        return False