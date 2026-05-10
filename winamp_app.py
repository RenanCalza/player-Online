import streamlit as st
import requests

st.set_page_config(page_title="Calza-Player", layout="wide")

st.markdown('''<style>
.main { background-color: #111; color: white; }
.winamp {
    background: linear-gradient(180deg, #3c3c5c, #1f1f35);
    border: 3px solid #888;
    border-radius: 10px;
    padding: 20px;
    max-width: 500px;
    margin: auto;
    box-shadow: 0px 0px 20px #000;
}
.title {
    font-size: 24px; font-weight: bold;
    color: #00ff99; text-align: center; margin-bottom: 15px;
}
.playlist-container {
    background: black; color: #00ff99;
    padding: 10px; margin-top: 15px;
    height: 200px; overflow-y: auto;
    font-family: 'Courier New', Courier, monospace;
    border: 1px solid #444;
}
.active-track { color: white; background-color: #222; padding: 2px 5px; }
</style>''', unsafe_allow_html=True)

st.title("🎵 Calza-Player Online")
st.write("Conectado automaticamente à sua pasta do Drive!")

API_KEY = st.secrets["GOOGLE_API_KEY"]
FOLDER_ID = "1Xsvld85uv2nvUjg2xzfoeX17xIPGVTZu"

@st.cache_data(ttl=3600)
def fetch_playlist(folder_id, api_key):
    try:
        url = "https://www.googleapis.com/drive/v3/files"
        params = {
            "q": f"'{folder_id}' in parents and trashed=false and (mimeType='audio/mpeg' or mimeType='audio/wav' or mimeType='audio/ogg')",
            "fields": "files(id, name)",
            "key": api_key,
            "pageSize": 100
        }
        response = requests.get(url, params=params)
        data = response.json()

        if "error" in data:
            st.error(f"Erro da API: {data['error']['message']}")
            return []

        return data.get("files", [])
    except Exception as e:
        st.exception(e)
        return []

playlist = fetch_playlist(FOLDER_ID, API_KEY)

if not playlist:
    st.error("⚠️ Não encontrei músicas. Verifique se a pasta no Drive está como 'Qualquer pessoa com o link pode ler'.")
else:
    st.markdown('<div class="winamp">', unsafe_allow_html=True)
    st.markdown('<div class="title">🎵 WINAMP ONLINE</div>', unsafe_allow_html=True)

    nomes = [f['name'] for f in playlist]
    selecao = st.selectbox("Escolha a faixa:", nomes)

    arquivo = next(f for f in playlist if f['name'] == selecao)

    embed_url = f"https://drive.google.com/file/d/{arquivo['id']}/preview"
    st.markdown(f'''
        <iframe src="{embed_url}" 
            width="100%" height="80" 
            allow="autoplay"
            style="border:none; background:transparent;">
        </iframe>
    ''', unsafe_allow_html=True)

    st.markdown('<div class="playlist-container">', unsafe_allow_html=True)
    for i, track in enumerate(playlist):
        num = str(i+1).zfill(2)
        if track['name'] == selecao:
            st.markdown(f'<div class="active-track">▶️ {num}. {track["name"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div>&nbsp;&nbsp; {num}. {track["name"]}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

st.info("💡 Se a música demorar a carregar, é o Google Drive processando o link direto. Manda ver no play!")