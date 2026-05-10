import streamlit as st
import requests
import streamlit.components.v1 as components
import json

st.set_page_config(
    page_title="Calza-Player",
    layout="centered",  # melhor para mobile
    initial_sidebar_state="collapsed"
)

# Esconde elementos do Streamlit desnecessários no mobile
st.markdown('''<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
.block-container {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100% !important;
}
</style>''', unsafe_allow_html=True)
st.title("🎵Calza-Player - chupa spotify 😁")

API_KEY = st.secrets["GOOGLE_API_KEY"]
FOLDER_ID = "1Xsvld85uv2nvUjg2xzfoeX17xIPGVTZu"

@st.cache_data(ttl=3600)
def fetch_playlist(folder_id, api_key):
    try:
        all_files = []
        page_token = None
        while True:
            url = "https://www.googleapis.com/drive/v3/files"
            params = {
                "q": f"'{folder_id}' in parents and trashed=false and (mimeType='audio/mpeg' or mimeType='audio/wav' or mimeType='audio/ogg')",
                "fields": "nextPageToken, files(id, name)",
                "key": api_key,
                "pageSize": 100,
                "orderBy": "name"
            }
            if page_token:
                params["pageToken"] = page_token
            response = requests.get(url, params=params)
            data = response.json()
            if "error" in data:
                st.error(f"Erro da API: {data['error']['message']}")
                return []
            all_files.extend(data.get("files", []))
            page_token = data.get("nextPageToken")
            if not page_token:
                break
        return all_files
    except Exception as e:
        st.exception(e)
        return []

playlist = fetch_playlist(FOLDER_ID, API_KEY)

if not playlist:
    st.error("⚠️ Não encontrei músicas.")
else:
    tracks = [{"id": f["id"], "name": f["name"]} for f in playlist]
    tracks_json = json.dumps(tracks)

    components.html(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <!-- Zoom com dois dedos liberado, escala inicial 1:1 no celular -->
        <meta name="viewport" content="width=device-width, initial-scale=1.0, minimum-scale=0.5, maximum-scale=4.0, user-scalable=yes">
    </head>
    <body>
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}

        html, body {{
            background: #1f1f35;
            color: #00ff99;
            font-family: 'Courier New', monospace;
            height: 100%;
            /* Permite pinch-zoom na página toda */
            touch-action: pan-x pan-y pinch-zoom;
        }}

        #player {{
            background: linear-gradient(180deg, #3c3c5c, #1f1f35);
            border: 3px solid #888;
            border-radius: 10px;
            padding: 16px;
            width: 100%;
            height: 100vh;
            display: flex;
            flex-direction: column;
            box-shadow: 0px 0px 20px #000;
        }}

        #titulo {{
            font-size: 20px;
            font-weight: bold;
            color: #00ff99;
            text-align: center;
            margin-bottom: 10px;
            flex-shrink: 0;
        }}

        #track-name {{
            font-size: 13px;
            color: #ccc;
            text-align: center;
            margin-bottom: 8px;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            flex-shrink: 0;
        }}

        #player-iframe {{
            flex-shrink: 0;
        }}
        #player-iframe iframe {{
            width: 100%;
            height: 80px;
            border: none;
            display: block;
            border-radius: 6px;
        }}

        #controls {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 8px;
            margin-top: 10px;
            flex-shrink: 0;
        }}

        .btn {{
            background: #2a2a4a;
            color: #00ff99;
            border: 1px solid #555;
            border-radius: 8px;
            padding: 10px 16px;
            cursor: pointer;
            font-size: 20px;
            /* Toque mais responsivo no mobile */
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            transition: background 0.15s;
            user-select: none;
        }}
        .btn:active {{ background: #555; }}
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
            flex-shrink: 0;
        }}

        #autoplay-tip {{
            font-size: 10px;
            color: #555;
            text-align: center;
            margin-top: 5px;
            flex-shrink: 0;
        }}

        #playlist {{
            background: black;
            color: #00ff99;
            padding: 8px;
            margin-top: 12px;
            flex-grow: 1;
            overflow-y: auto;
            border: 1px solid #444;
            border-radius: 6px;
            /* Scroll suave no iOS */
            -webkit-overflow-scrolling: touch;
        }}

        .track-item {{
            padding: 9px 6px;
            cursor: pointer;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
            border-radius: 4px;
            font-size: 13px;
            /* Toque preciso no mobile */
            touch-action: manipulation;
            -webkit-tap-highlight-color: transparent;
            user-select: none;
        }}
        .track-item:active {{ background: #333; }}
        .track-item.active {{
            color: white;
            background: #222;
        }}
    </style>

    <div id="player">
        <div id="titulo">🎵 WINAMP ONLINE</div>
        <div id="track-name">Selecione uma música...</div>
        <div id="player-iframe"></div>

        <div id="controls">
            <button class="btn" onclick="prevTrack()">⏮</button>
            <button class="btn" onclick="loadTrack(current)">🔄</button>
            <button class="btn" onclick="nextTrack()">⏭</button>
            <button class="btn" id="btn-shuffle" onclick="toggleShuffle()">🔀</button>
            <button class="btn" id="btn-repeat" onclick="toggleRepeat()">🔁</button>
        </div>

        <div id="status-bar">
            <span>🔀 <span id="val-shuffle">OFF</span></span>
            <span>🔁 <span id="val-repeat">OFF</span></span>
            <span id="track-count"></span>
        </div>

        <div id="autoplay-tip">▶️ Após selecionar, clique em play no player acima</div>

        <div id="playlist"></div>
    </div>

    <script>
        const tracks = {tracks_json};
        let current = 0;
        let shuffle = false;
        let repeat = false;
        let history = [];

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
                    style="border:none; border-radius:6px;">
                </iframe>`;
            renderPlaylist();
        }}

        function nextTrack() {{
            history.push(current);
            if (repeat) {{
                loadTrack(current);
            }} else if (shuffle) {{
                let next;
                do {{ next = Math.floor(Math.random() * tracks.length); }}
                while (next === current && tracks.length > 1);
                loadTrack(next);
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
            document.getElementById('btn-shuffle').classList.toggle('active-btn', shuffle);
            const val = document.getElementById('val-shuffle');
            val.innerText = shuffle ? 'ON' : 'OFF';
            val.style.color = shuffle ? '#00ff99' : '#888';
        }}

        function toggleRepeat() {{
            repeat = !repeat;
            document.getElementById('btn-repeat').classList.toggle('active-btn', repeat);
            const val = document.getElementById('val-repeat');
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

        loadTrack(0);
    </script>
    </body>
    </html>
    """, height=800)
