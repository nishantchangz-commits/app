"""
Streamlit version of the Golden Nested Rectangle Click Effect.

Streamlit itself has no native way to capture live mouse clicks and
animate at 60fps, so this app embeds a small self-contained HTML5
<canvas> + JavaScript component (via st.components.v1.html) that
reproduces the exact same effect as the Pygame version:

    - Click anywhere on the canvas
    - A purple flash marks the click point
    - A shiny golden nested-rectangle structure grows outward and fades

Run with:
    streamlit run streamlit_app.py
"""

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Golden Nested Rectangle Click Effect", layout="wide")

st.title("✨ Golden Nested Rectangle Click Effect")
st.markdown(
    "Click anywhere inside the box below. Each click triggers a quick "
    "**purple flash** at the click point, followed by a **shiny golden "
    "nested-rectangle** structure that blooms outward and fades away."
)

# ---------------------------------------------------------------------------
# Sidebar controls — let the user tweak the effect without touching code
# ---------------------------------------------------------------------------
st.sidebar.header("Effect settings")
num_rects = st.sidebar.slider("Nested rectangles per click", 2, 12, 6)
max_size = st.sidebar.slider("Max structure size (px)", 40, 300, 140)
life_ms = st.sidebar.slider("Effect lifetime (ms)", 300, 3000, 1100, step=100)
bg_color = st.sidebar.color_picker("Background color", "#0c0c12")
purple_color = st.sidebar.color_picker("Click flash (purple)", "#9b30d2")
canvas_height = st.sidebar.slider("Canvas height (px)", 400, 900, 620, step=20)

gold_shades = ["#B8860B", "#DAA520", "#FFC125", "#FFD700", "#FFEFAA"]

html_code = f"""
<div style="width:100%;">
  <canvas id="goldCanvas" style="width:100%; height:{canvas_height}px;
      display:block; border-radius:10px; cursor:none;
      background:{bg_color};"></canvas>
</div>
<script>
(function() {{
  const canvas = document.getElementById('goldCanvas');
  const ctx = canvas.getContext('2d');

  // Config injected from Streamlit controls
  const NUM_RECTS   = {num_rects};
  const MAX_SIZE     = {max_size};
  const LIFE_MS      = {life_ms};
  const FLASH_MS      = Math.min(240, LIFE_MS * 0.2);
  const GROW_MS       = Math.min(500, LIFE_MS * 0.4);
  const GOLD_SHADES  = {gold_shades};
  const PURPLE        = "{purple_color}";

  function resize() {{
    const rect = canvas.getBoundingClientRect();
    canvas.width = rect.width;
    canvas.height = rect.height;
  }}
  window.addEventListener('resize', resize);
  resize();

  let effects = [];
  let mouseX = -100, mouseY = -100;

  canvas.addEventListener('mousemove', (e) => {{
    const rect = canvas.getBoundingClientRect();
    mouseX = e.clientX - rect.left;
    mouseY = e.clientY - rect.top;
  }});

  canvas.addEventListener('mousedown', (e) => {{
    const rect = canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    effects.push({{ x: x, y: y, start: performance.now() }});
  }});

  function hexToRgb(hex) {{
    const h = hex.replace('#', '');
    const bigint = parseInt(h, 16);
    return [(bigint >> 16) & 255, (bigint >> 8) & 255, bigint & 255];
  }}

  function easeOutCubic(t) {{
    return 1 - Math.pow(1 - t, 3);
  }}

  function drawCursor() {{
    ctx.save();
    ctx.strokeStyle = 'rgba(255,215,0,0.85)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(mouseX, mouseY, 9, 0, Math.PI * 2);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,239,170,1)';
    ctx.beginPath();
    ctx.arc(mouseX, mouseY, 2, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }}

  function drawEffect(effect, now) {{
    const age = now - effect.start;
    if (age > LIFE_MS) return false;

    const {{x, y}} = effect;

    // 1) Purple click flash
    if (age <= FLASH_MS) {{
      const t = age / FLASH_MS;
      const radius = 8 + t * 46;
      const alpha = 1 - t;
      const [r, g, b] = hexToRgb(PURPLE);

      ctx.save();
      ctx.globalAlpha = alpha;
      ctx.fillStyle = `rgb(${{r}},${{g}},${{b}})`;
      ctx.beginPath();
      ctx.arc(x, y, Math.max(2, radius / 3), 0, Math.PI * 2);
      ctx.fill();

      ctx.lineWidth = 3;
      ctx.strokeStyle = `rgb(${{Math.min(255,r+30)}},${{Math.min(255,g+35)}},${{Math.min(255,b+25)}})`;
      ctx.beginPath();
      ctx.arc(x, y, radius, 0, Math.PI * 2);
      ctx.stroke();
      ctx.restore();
    }}

    // 2) Golden nested rectangles growing outward
    const growT = Math.min(1, age / GROW_MS);
    const eased = easeOutCubic(growT);

    let overallAlpha = 1;
    if (age > GROW_MS) {{
      const fadeT = (age - GROW_MS) / (LIFE_MS - GROW_MS);
      overallAlpha = Math.max(0, 1 - fadeT);
    }}
    if (overallAlpha <= 0) return true;

    const size = MAX_SIZE * 2 * eased;
    if (size < 6) return true;

    for (let i = 0; i < NUM_RECTS; i++) {{
      const frac = (i + 1) / NUM_RECTS;
      const half = (size / 2) * frac;
      if (half < 2) continue;

      const color = GOLD_SHADES[i % GOLD_SHADES.length];
      const [r, g, b] = hexToRgb(color);

      ctx.save();
      ctx.globalAlpha = overallAlpha;
      ctx.strokeStyle = `rgb(${{r}},${{g}},${{b}})`;
      ctx.lineWidth = 3;
      ctx.strokeRect(x - half, y - half, half * 2, half * 2);

      // animated diagonal shine sweep
      const shinePhase = ((age * 0.35) + i * 40) % 360;
      const shineAlpha = Math.max(0, Math.pow(Math.sin(shinePhase * Math.PI / 180), 2)) * 0.6;
      ctx.globalAlpha = Math.min(overallAlpha, shineAlpha);
      ctx.strokeStyle = 'rgb(255,255,240)';
      ctx.lineWidth = 2;
      ctx.beginPath();
      ctx.moveTo(x - half, y - half);
      ctx.lineTo(x + half, y + half);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x + half, y - half);
      ctx.lineTo(x - half, y + half);
      ctx.stroke();
      ctx.restore();
    }}

    return true;
  }}

  function frame(now) {{
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    effects = effects.filter((eff) => drawEffect(eff, now));
    drawCursor();

    requestAnimationFrame(frame);
  }}
  requestAnimationFrame(frame);
}})();
</script>
"""

components.html(html_code, height=canvas_height + 20, scrolling=False)

st.caption(
    "Tip: use the sidebar to change the number of nested rectangles, "
    "their max size, the colors, and how long each burst lasts."
)
