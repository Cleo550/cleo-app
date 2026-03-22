import streamlit as st

def mostrar_calculadora():
    # Ocultar barra "Gestionar la aplicación"
    st.markdown("""
    <style>
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }

    #calc-fab {
        position: fixed;
        top: 14px;
        right: 18px;
        z-index: 99999;
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: #2ABFBF;
        color: white;
        font-size: 20px;
        border: none;
        cursor: pointer;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        line-height: 42px;
        text-align: center;
    }
    #calc-fab:hover { background: #22a8a8; }

    #calc-panel {
        position: fixed;
        top: 64px;
        right: 18px;
        z-index: 99998;
        width: 240px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.22);
        padding: 14px;
        display: none;
        flex-direction: column;
        gap: 8px;
        font-family: sans-serif;
    }
    #calc-panel.open { display: flex; }

    #calc-expr {
        text-align: right;
        font-size: 11px;
        color: #aaa;
        min-height: 16px;
        font-family: monospace;
    }
    #calc-screen {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: right;
        font-size: 24px;
        font-weight: bold;
        color: #333;
        font-family: monospace;
        word-break: break-all;
    }
    .cgrid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
    }
    .cgrid button {
        border: none;
        border-radius: 10px;
        padding: 13px 0;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
    }
    .cgrid button:active { filter: brightness(0.80); }
    .bn { background: #f0f0f0; color: #333; }
    .bo { background: #ffe5f2; color: #e0558a; }
    .be { background: #2ABFBF; color: white; }
    .bz { grid-column: span 2; }
    </style>

    <button id="calc-fab" onclick="document.getElementById('calc-panel').classList.toggle('open')">🧮</button>

    <div id="calc-panel">
      <div id="calc-expr"></div>
      <div id="calc-screen">0</div>
      <div class="cgrid">
        <button class="bo" onclick="cAC()">AC</button>
        <button class="bn" onclick="cDel()">⌫</button>
        <button class="bo" onclick="cOp('%')">%</button>
        <button class="bo" onclick="cOp('/')">÷</button>
        <button class="bn" onclick="cNum('7')">7</button>
        <button class="bn" onclick="cNum('8')">8</button>
        <button class="bn" onclick="cNum('9')">9</button>
        <button class="bo" onclick="cOp('*')">×</button>
        <button class="bn" onclick="cNum('4')">4</button>
        <button class="bn" onclick="cNum('5')">5</button>
        <button class="bn" onclick="cNum('6')">6</button>
        <button class="bo" onclick="cOp('-')">−</button>
        <button class="bn" onclick="cNum('1')">1</button>
        <button class="bn" onclick="cNum('2')">2</button>
        <button class="bn" onclick="cNum('3')">3</button>
        <button class="bo" onclick="cOp('+')">+</button>
        <button class="bn bz" onclick="cNum('0')">0</button>
        <button class="bn" onclick="cDot()">.</button>
        <button class="be" onclick="cEq()">=</button>
      </div>
    </div>

    <script>
    (function(){
      var ex="", res="0", jeq=false;
      function upd(){
        document.getElementById("calc-screen").textContent=res;
        document.getElementById("calc-expr").textContent=ex;
      }
      window.cNum=function(n){
        if(jeq){ex="";res="0";jeq=false;}
        res=(res==="0"&&n!==".")?n:res+n; upd();
      };
      window.cDot=function(){
        if(jeq){ex="";res="0";jeq=false;}
        if(res.indexOf(".")===-1)res+="."; upd();
      };
      window.cOp=function(op){
        jeq=false; ex+=res+" "+op+" "; res="0"; upd();
      };
      window.cEq=function(){
        try{
          var f=ex+res;
          var r=Function('"use strict";return('+f+')')();
          ex=f+" ="; res=parseFloat(r.toFixed(10)).toString(); jeq=true;
        }catch(e){res="Error";ex="";}
        upd();
      };
      window.cAC=function(){ex="";res="0";jeq=false;upd();};
      window.cDel=function(){res=res.length>1?res.slice(0,-1):"0";upd();};
    })();
    </script>
    """, unsafe_allow_html=True)
