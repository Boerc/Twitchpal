import { useEffect, useMemo, useRef, useState } from "react";
import io from "socket.io-client";
import { BACKEND_URL, apiLogin, apiGetState, apiToggle } from "../lib/api";

export default function Home() {
  const [token, setToken] = useState<string>("");
  const [username, setUsername] = useState("admin");
  const [password, setPassword] = useState("admin123");
  const [state, setState] = useState<any>({});
  const [image, setImage] = useState<string>("");
  const [commentary, setCommentary] = useState<string>("");

  // WebSocket: use native, since backend serves plain ws
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    if (!token) return;
    const wsUrl = BACKEND_URL.replace(/^http/, "ws") + "/ws";
    const ws = new WebSocket(wsUrl);
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.type === "frame") {
          setImage(msg.image);
          if (msg.commentary) setCommentary(msg.commentary);
        }
      } catch {}
    };
    wsRef.current = ws;
    return () => ws.close();
  }, [token]);

  async function doLogin() {
    const res = await apiLogin(username, password);
    setToken(res.access_token);
    const s = await apiGetState(res.access_token);
    setState(s);
  }

  async function toggle(payload: any) {
    if (!token) return;
    const s = await apiToggle(token, payload);
    setState(s);
  }

  return (
    <div style={{ padding: 24, fontFamily: "Inter, system-ui, sans-serif" }}>
      <h2>Stream Companion</h2>

      {!token ? (
        <div style={{ display: "grid", gap: 8, maxWidth: 320 }}>
          <input placeholder="username" value={username} onChange={e => setUsername(e.target.value)} />
          <input placeholder="password" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          <button onClick={doLogin}>Login</button>
        </div>
      ) : (
        <>
          <div style={{ display: "flex", gap: 24 }}>
            <div style={{ minWidth: 400 }}>
              <h3>Controls</h3>
              <label>
                <input type="checkbox" checked={!!state.screen_reading_enabled} onChange={e => toggle({ screen_reading_enabled: e.target.checked })} />
                Screen Reading
              </label>
              <br />
              <label>
                <input type="checkbox" checked={!!state.chat_moderation_enabled} onChange={e => toggle({ chat_moderation_enabled: e.target.checked })} />
                Chat Moderation
              </label>
              <br />
              <label>
                <input type="checkbox" checked={!!state.tts_enabled} onChange={e => toggle({ tts_enabled: e.target.checked })} />
                TTS
              </label>
              <br />
              <label>
                <input type="checkbox" checked={!!state.stt_enabled} onChange={e => toggle({ stt_enabled: e.target.checked })} />
                STT
              </label>
              <br />
              <label>
                Personality
                <select value={state.selected_personality || "Analytical Expert"} onChange={e => toggle({ selected_personality: e.target.value })}>
                  {[
                    "Sarcastic Coach",
                    "Encouraging Mentor",
                    "Analytical Expert",
                    "Chill Commentator",
                    "Hype Caster",
                  ].map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </label>
            </div>

            <div>
              <h3>Live Preview</h3>
              {image ? (
                <img src={image} alt="screen" style={{ maxWidth: 800, border: "1px solid #ccc" }} />
              ) : (
                <div style={{ width: 800, height: 450, border: "1px dashed #aaa", display: "grid", placeItems: "center" }}>No frames yet</div>
              )}
              <div style={{ marginTop: 12, padding: 12, background: "#111", color: "#0f0", borderRadius: 8 }}>
                <strong>Commentary:</strong> {commentary || "(waiting...)"}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
