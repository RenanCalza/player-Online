import streamlit as st
import requests
import streamlit.components.v1 as components
import json

st.set_page_config(
    page_title="Calza-Player",
    layout="centered",
    initial_sidebar_state="collapsed"
)

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
                "fields": "nextPageToken, files(id, name, videoMediaMetadata)",
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
    tracks = [
        {
            "id": f["id"],
            "name": f["name"],
            "duration": int(f.get("videoMediaMetadata", {}).get("durationMillis", 240000)) // 1000
        }
        for f in playlist
    ]

    tracks_json = json.dumps(tracks)

    components.html(f"""
<!DOCTYPE html>
<html>
<head>
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

  /* Audio player nativo estilizado */
  #audio-player {{
    width: 100%;
    height: 36px;
    border-radius: 6px;
    outline: none;
    flex-shrink: 0;
    accent-color: #00ff99;
    filter: invert(1) hue-rotate(90deg) brightness(0.85);
  }}

  #progress-bar-container {{
    width: 100%;
    height: 4px;
    background: #333;
    border-radius: 2px;
    margin-top: 8px;
    flex-shrink: 0;
    overflow: hidden;
  }}
  #progress-bar {{
    height: 4px;
    background: #00ff99;
    width: 0%;
    border-radius: 2px;
    transition: width 0.5s linear;
  }}
  #timer-label {{
    font-size: 10px;
    color: #555;
    text-align: right;
    margin-top: 3px;
    flex-shrink: 0;
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
  #loading-msg {{
    font-size: 11px;
    color: #555;
    text-align: center;
    margin-top: 4px;
    flex-shrink: 0;
    min-height: 16px;
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
  <div id="track-name">Carregando...</div>

  <!-- Player HTML5 nativo — sem iframe do Google Drive -->
  <audio id="audio-player" controls preload="none"></audio>

  <div id="progress-bar-container">
    <div id="progress-bar"></div>
  </div>
  <div id="timer-label">--:-- / --:--</div>
  <div id="loading-msg"></div>

  <div id="controls">
    <button class="btn" onclick="prevTrack()">⏮</button>
    <button class="btn" id="btn-playpause" onclick="togglePlayPause()">▶️</button>
    <button class="btn" onclick="nextTrack()">⏭</button>
    <button class="btn" id="btn-shuffle" onclick="toggleShuffle()">🔀</button>
    <button class="btn" id="btn-repeat" onclick="toggleRepeat()">🔁</button>
  </div>

  <div id="status-bar">
    <span>🔀 <span id="val-shuffle">OFF</span></span>
    <span>🔁 <span id="val-repeat">OFF</span></span>
    <span id="track-count"></span>
  </div>

  <div id="playlist"></div>
</div>

<script>
  const tracks = {tracks_json};
  const audio = document.getElementById('audio-player');

  let current = 0;
  let shuffle = false;
  let repeat = false;
  let history = [];

  document.getElementById('track-count').innerText = `🎵 ${{tracks.length}} músicas`;

  function cleanName(name) {{
    return name.replace(/\.(mp3|wav|ogg)$/i, '');
  }}

  function formatTime(seconds) {{
    if (isNaN(seconds) || seconds < 0) return '--:--';
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = Math.floor(seconds % 60).toString().padStart(2, '0');
    return `${{m}}:${{s}}`;
  }}

  function setLoadingMsg(msg) {{
    document.getElementById('loading-msg').innerText = msg;
  }}

  function loadTrack(index, autoplay = true) {{
    current = index;
    const track = tracks[index];

    document.getElementById('track-name').innerText = '▶️ ' + cleanName(track.name);
    document.getElementById('progress-bar').style.width = '0%';
    document.getElementById('timer-label').innerText = '--:-- / --:--';
    document.getElementById('btn-playpause').innerText = '⏸️';
    setLoadingMsg('⏳ Carregando...');

    // URL de download direto — bypassa o player nativo do Google Drive
    const directUrl = `https://drive.google.com/uc?export=download&id=${{track.id}}`;
    audio.src = directUrl;
    audio.load();

    if (autoplay) {{
      audio.play().catch(err => {{
        setLoadingMsg('⚠️ Clique ▶️ para tocar');
        document.getElementById('btn-playpause').innerText = '▶️';
        console.warn('Autoplay bloqueado:', err);
      }});
    }}

    renderPlaylist();
  }}

  // Atualiza barra de progresso e timer em tempo real
  audio.addEventListener('timeupdate', () => {{
    const duration = audio.duration || 0;
    const current_time = audio.currentTime || 0;
    const pct = duration > 0 ? (current_time / duration) * 100 : 0;
    document.getElementById('progress-bar').style.width = pct + '%';
    document.getElementById('timer-label').innerText =
      `${{formatTime(current_time)}} / ${{formatTime(duration)}}`;
  }});

  audio.addEventListener('playing', () => {{
    setLoadingMsg('');
    document.getElementById('btn-playpause').innerText = '⏸️';
  }});

  audio.addEventListener('pause', () => {{
    document.getElementById('btn-playpause').innerText = '▶️';
  }});

  audio.addEventListener('waiting', () => {{
    setLoadingMsg('⏳ Buffering...');
  }});

  audio.addEventListener('canplay', () => {{
    setLoadingMsg('');
  }});

  audio.addEventListener('error', (e) => {{
    setLoadingMsg('❌ Erro ao carregar. Arquivo grande? Tente novamente.');
    console.error('Audio error:', e);
  }});

  // Avança automaticamente ao terminar a faixa
  audio.addEventListener('ended', () => {{
    nextTrack();
  }});

  function togglePlayPause() {{
    if (audio.paused) {{
      audio.play();
    }} else {{
      audio.pause();
    }}
  }}

  function nextTrack() {{
    history.push(current);
    if (repeat) {{
      audio.currentTime = 0;
      audio.play();
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
    // Se passou mais de 3 segundos, reinicia a faixa atual
    if (audio.currentTime > 3) {{
      audio.currentTime = 0;
      return;
    }}
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
    audio.loop = repeat;
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
      div.innerText = (i === current ? '▶️ ' : '   ') + num + '. ' + cleanName(t.name);
      div.onclick = () => {{ history.push(current); loadTrack(i); }};
      container.appendChild(div);
    }});
    const active = container.querySelector('.active');
    if (active) active.scrollIntoView({{ block: 'nearest' }});
  }}

  // Inicia na primeira faixa (sem autoplay forçado — respeita política do browser)
  loadTrack(0, false);
  renderPlaylist();
</script>
</body>
</html>
""", height=800)
