import streamlit as st
import streamlit.components.v1 as components

def mostrar_calculadora():
    # Ocultar barra "Gestionar la aplicación" con CSS puro (esto sí funciona en st.markdown)
    st.markdown("""
    <style>
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    </style>
    """, unsafe_allow_html=True)

    # Calculadora en iframe independiente — el JS funciona aquí siempre
    components.html("""
    <!DOCTYPE html>
    <html>
    <head>
    <style>
      * { margin:0; padding:0; box-sizing:border-box; }
      body { background: transparent; font-family: sans-serif; }

      #fab {
        position: fixed;
        top: 10px;
        right: 10px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #2ABFBF;
        color: white;
        font-size: 20px;
        border: none;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,0,0,0.25);
        z-index: 9999;
      }
      #fab:hover { background: #22a8a8; }

      #panel {
        position: fixed;
        top: 62px;
        right: 10px;
        width: 232px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 28px rgba(0,0,0,0.2);
        padding: 12px;
        display: none;
        flex-direction: column;
        gap: 7px;
        z-index: 9998;
      }
      #panel.open { display: flex; }

      #expr {
        text-align: right;
        font-size: 11px;
        color: #bbb;
        min-height: 15px;
        font-family: monospace;
      }
      #screen {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 9px 12px;
        text-align: right;
        font-size: 26px;
        font-weight: bold;
        color: #222;
        font-family: monospace;
        word-break: break-all;
        min-height: 50px;
      }
      .grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 5px;
      }
      .grid button {
        border: none;
        border-radius: 9px;
        padding: 12px 0;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
      }
      .grid button:active { opacity: 0.7; }
      .n { background: #f0f0f0; color: #333; }
      .o { background: #ffe5f2; color: #d0457a; }
      .e { background: #2ABFBF; color: white; }
      .z { grid-column: span 2; }
    </style>
    </head>
    <body>

    <button id="fab" onclick="document.getElementById('panel').classList.toggle('open')">🧮</button>

    <div id="panel">
      <div id="expr"></div>
      <div id="screen">0</div>
      <div class="grid">
        <button class="o" onclick="ac()">AC</button>
        <button class="n" onclick="del_()">⌫</button>
        <button class="o" onclick="op('%')">%</button>
        <button class="o" onclick="op('/')">÷</button>
        <button class="n" onclick="num('7')">7</button>
        <button class="n" onclick="num('8')">8</button>
        <button class="n" onclick="num('9')">9</button>
        <button class="o" onclick="op('*')">×</button>
        <button class="n" onclick="num('4')">4</button>
        <button class="n" onclick="num('5')">5</button>
        <button class="n" onclick="num('6')">6</button>
        <button class="o" onclick="op('-')">−</button>
        <button class="n" onclick="num('1')">1</button>
        <button class="n" onclick="num('2')">2</button>
        <button class="n" onclick="num('3')">3</button>
        <button class="o" onclick="op('+')">+</button>
        <button class="n z" onclick="num('0')">0</button>
        <button class="n" onclick="dot()">.</button>
        <button class="e" onclick="eq()">=</button>
      </div>
    </div>

    <script>
      var ex="", res="0", jeq=false;
      function upd(){
        document.getElementById("screen").textContent = res;
        document.getElementById("expr").textContent = ex;
      }
      function num(n){
        if(jeq){ex="";res="0";jeq=false;}
        res = (res==="0" && n!==".") ? n : res+n;
        upd();
      }
      function dot(){
        if(jeq){ex="";res="0";jeq=false;}
        if(res.indexOf(".")===-1) res+=".";
        upd();
      }
      function op(o){
        jeq=false;
        ex += res+" "+o+" ";
        res="0";
        upd();
      }
      function eq(){
        try{
          var f = ex+res;
          var r = Function('"use strict";return('+f+')')();
          ex = f+" =";
          res = parseFloat(r.toFixed(10)).toString();
          jeq=true;
        }catch(e){ res="Error"; ex=""; }
        upd();
      }
      function ac(){ ex=""; res="0"; jeq=false; upd(); }
      function del_(){ res = res.length>1 ? res.slice(0,-1) : "0"; upd(); }
    </script>
    </body>
    </html>
    """, height=60, scrolling=False)
