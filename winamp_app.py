import streamlit as st
import requests
import streamlit.components.v1 as components
import json

#st.set_page_config(page_title="Calza-Player", layout="wide")

st.markdown('''<style>
.main { background-color: #111; color: white; }
</style>''', unsafe_allow_html=True)

st.title("🎵 Calza-Player Online")
st.write("Conectado automaticamente à sua pasta do Drive!")

API_KEY =st.secrets ["GOOGLE_API_KEY"]
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
    tracks = [{"id": f["id"], "name": f["name"]} for f in playlist]
    tracks_json = json.dumps(tracks)

    components.html(f"""
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: linear-gradient(180deg, #3c3c5c, #1f1f35);
            color: #00ff99;
            font-family: 'Courier New', monospace;
            padding: 15px;
        }}
        #player {{
            background: linear-gradient(180deg, #3c3c5c, #1f1f35);
            border: 3px solid #888;
            border-radius: 10px;
            padding: 20px;
            max-width: 500px;
            margin: auto;
            box-shadow: 0px 0px 20px #000;
        }}
        #titulo {{
            font-size: 22px;
            font-weight: bold;
            color: #00ff99;
            text-align: center;
            margin-bottom: 12px;
        }}
        #track-name {{
            font-size: 12px;
            color: #ccc;
            text-align: center;
            margin-bottom: 10px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        #player-iframe iframe {{
            width: 100%;
            height: 80px;
            border: none;
            display: block;
        }}
        #controls {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 12px;
        }}
        .btn {{
            background: #2a2a4a;
            color: #00ff99;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 6px 14px;
            cursor: pointer;
            font-family: 'Courier New', monospace;
            font-size: 16px;
            transition: background 0.2s;
        }}
        .btn:hover {{ background: #444; }}
        .btn.active-btn {{
            background: #00ff99;
            color: #111;
            border-color: #00ff99;
        }}
        #status-bar {{
            display: flex;
            justify-content: center;
            gap: 15px;
            margin-top: 8px;
            font-size: 11px;
            color: #888;
        }}
        .status-on {{ color: #00ff99; }}
        #playlist {{
            background: black;
            color: #00ff99;
            padding: 10px;
            margin-top: 15px;
            height: 350px;
            overflow-y: auto;
            border: 1px solid #444;
        }}
        .track-item {{
            padding: 3px 5px;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border-radius: 3px;
        }}
        .track-item:hover {{ background: #333; }}
        .track-item.active {{ color: white; background: #222; }}
    </style>

    <div id="player">
        <div id="titulo">🎵 Renan Calza - ONLINE</div>
        <div id="track-name">Selecione uma música...</div>
        <div id="player-iframe"></div>

        <div id="controls">
            <button class="btn" onclick="prevTrack()" title="Anterior">⏮</button>
            <button class="btn" onclick="loadTrack(current)" title="Reiniciar">🔄</button>
            <button class="btn" onclick="nextTrack()" title="Próxima">⏭</button>
            <button class="btn" id="btn-shuffle" onclick="toggleShuffle()" title="Aleatório">🔀</button>
            <button class="btn" id="btn-repeat" onclick="toggleRepeat()" title="Repetir">🔁</button>
        </div>

        <div id="status-bar">
            <span id="lbl-shuffle">🔀 Aleatório: <span id="val-shuffle">OFF</span></span>
            <span id="lbl-repeat">🔁 Repetir: <span id="val-repeat">OFF</span></span>
            <span id="track-count"></span>
        </div>

        <div id="playlist"></div>
    </div>

    <script>
        const tracks = {tracks_json};
        let current = 0;
        let shuffle = false;
        let repeat = false;
        let history = []; // histórico para o botão anterior no modo shuffle

        document.getElementById('track-count').innerText = `🎵 ${{tracks.length}} músicas`;

        function cleanName(name) {{
            return name.replace(/\.(mp3|wav|ogg)$/i, '');
        }}

        function loadTrack(index) {{
            current = index;
            const track = tracks[index];
            document.getElementById('track-name').innerText = '▶️ ' + cleanName(track.name);

            document.getElementById('player-iframe').innerHTML = `
                <iframe 
                    src="https://drive.google.com/file/d/${{track.id}}/preview"
                    width="100%" 
                    height="80"
                    allow="autoplay"
                    style="border:none;">
                </iframe>`;

            renderPlaylist();
        }}

        function nextTrack() {{
            history.push(current);
            if (shuffle) {{
                let next;
                do {{ next = Math.floor(Math.random() * tracks.length); }}
                while (next === current && tracks.length > 1);
                loadTrack(next);
            }} else if (repeat) {{
                loadTrack(current);
            }} else {{
                loadTrack((current + 1) % tracks.length);
            }}
        }}

        function prevTrack() {{
            if (history.length > 0) {{
                loadTrack(history.pop());
            }} else {{
                loadTrack((current - 1 + tracks.length) % tracks.length);
            }}
        }}

        function toggleShuffle() {{
            shuffle = !shuffle;
            const btn = document.getElementById('btn-shuffle');
            const val = document.getElementById('val-shuffle');
            btn.classList.toggle('active-btn', shuffle);
            val.innerText = shuffle ? 'ON' : 'OFF';
            val.style.color = shuffle ? '#00ff99' : '#888';
        }}

        function toggleRepeat() {{
            repeat = !repeat;
            const btn = document.getElementById('btn-repeat');
            const val = document.getElementById('val-repeat');
            btn.classList.toggle('active-btn', repeat);
            val.innerText = repeat ? 'ON' : 'OFF';
            val.style.color = repeat ? '#00ff99' : '#888';
        }}

        function renderPlaylist() {{
            const container = document.getElementById('playlist');
            container.innerHTML = '';
            tracks.forEach((t, i) => {{
                const div = document.createElement('div');
                div.className = 'track-item' + (i === current ? ' active' : '');
                const num = String(i + 1).padStart(2, '0');
                div.innerText = (i === current ? '▶️ ' : '    ') + num + '. ' + cleanName(t.name);
                div.onclick = () => {{ history.push(current); loadTrack(i); }};
                container.appendChild(div);
            }});
            const active = container.querySelector('.active');
            if (active) active.scrollIntoView({{ block: 'nearest' }});
        }}

        // Inicia na primeira faixa
        loadTrack(0);
    </script>
    """, height=700)

#st.info("💡 Se a música demorar a carregar, é o Google Drive processando o link direto. Manda ver no play!"
