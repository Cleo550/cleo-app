import streamlit as st
import streamlit.components.v1 as components

def mostrar_calculadora():
    # Ocultar barra negra de Streamlit Cloud ("Gestionar la aplicación")
    st.markdown("""
    <style>
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="manage-app-button"] { display: none !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu { visibility: hidden !important; }
    footer { visibility: hidden !important; }
    </style>
    """, unsafe_allow_html=True)

    # Calculadora como componente HTML independiente (el JS funciona aquí)
    components.html("""
    <style>
      body { margin: 0; padding: 0; background: transparent; }

      #calc-btn {
        position: fixed;
        bottom: 24px;
        right: 18px;
        z-index: 99999;
        width: 52px;
        height: 52px;
        border-radius: 50%;
        background: #2ABFBF;
        color: white;
        font-size: 22px;
        border: none;
        cursor: pointer;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        transition: background 0.2s;
      }
      #calc-btn:hover { background: #22a8a8; }

      #calc-panel {
        position: fixed;
        bottom: 86px;
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
      }
      #calc-panel.open { display: flex; }

      #calc-expr {
        text-align: right;
        font-size: 11px;
        color: #aaa;
        min-height: 16px;
        padding: 0 4px;
        font-family: monospace;
      }
      #calc-display {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: right;
        font-size: 24px;
        font-weight: bold;
        color: #333;
        min-height: 48px;
        word-break: break-all;
        border: none;
        width: 100%;
        box-sizing: border-box;
        font-family: monospace;
      }
      .calc-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
      }
      .calc-grid button {
        border: none;
        border-radius: 10px;
        padding: 13px 0;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: filter 0.12s;
        font-family: sans-serif;
      }
      .calc-grid button:hover  { filter: brightness(0.91); }
      .calc-grid button:active { filter: brightness(0.80); }
      .btn-num  { background: #f0f0f0; color: #333; }
      .btn-op   { background: #ffe5f2; color: #e0558a; }
      .btn-eq   { background: #2ABFBF; color: white; }
      .btn-clr  { background: #ffe5f2; color: #e0558a; }
      .btn-del  { background: #f0f0f0; color: #666; }
      .btn-zero { grid-column: span 2; }
    </style>

    <button id="calc-btn" onclick="toggleCalc()">🧮</button>

    <div id="calc-panel">
      <div id="calc-expr"></div>
      <input id="calc-display" readonly value="0"/>
      <div class="calc-grid">
        <button class="btn-clr"           onclick="calcAC()">AC</button>
        <button class="btn-del"           onclick="calcDel()">⌫</button>
        <button class="btn-op"            onclick="calcOp('%')">%</button>
        <button class="btn-op"            onclick="calcOp('/')">÷</button>

        <button class="btn-num"           onclick="calcNum('7')">7</button>
        <button class="btn-num"           onclick="calcNum('8')">8</button>
        <button class="btn-num"           onclick="calcNum('9')">9</button>
        <button class="btn-op"            onclick="calcOp('*')">×</button>

        <button class="btn-num"           onclick="calcNum('4')">4</button>
        <button class="btn-num"           onclick="calcNum('5')">5</button>
        <button class="btn-num"           onclick="calcNum('6')">6</button>
        <button class="btn-op"            onclick="calcOp('-')">−</button>

        <button class="btn-num"           onclick="calcNum('1')">1</button>
        <button class="btn-num"           onclick="calcNum('2')">2</button>
        <button class="btn-num"           onclick="calcNum('3')">3</button>
        <button class="btn-op"            onclick="calcOp('+')">+</button>

        <button class="btn-num btn-zero"  onclick="calcNum('0')">0</button>
        <button class="btn-num"           onclick="calcDot()">.</button>
        <button class="btn-eq"            onclick="calcEq()">=</button>
      </div>
    </div>

    <script>
      var expr = "", result = "0", justEq = false;

      function toggleCalc() {
        document.getElementById("calc-panel").classList.toggle("open");
      }
      function upd() {
        document.getElementById("calc-display").value = result;
        document.getElementById("calc-expr").textContent = expr;
      }
      function calcNum(n) {
        if (justEq) { expr = ""; result = "0"; justEq = false; }
        result = (result === "0" && n !== ".") ? n : result + n;
        upd();
      }
      function calcDot() {
        if (justEq) { expr = ""; result = "0"; justEq = false; }
        if (result.indexOf(".") === -1) result += ".";
        upd();
      }
      function calcOp(op) {
        justEq = false;
        expr += result + " " + op + " ";
        result = "0";
        upd();
      }
      function calcEq() {
        try {
          var full = expr + result;
          var res = Function('"use strict";return(' + full + ')')();
          expr = full + " =";
          result = parseFloat(res.toFixed(10)).toString();
          justEq = true;
        } catch(e) { result = "Error"; expr = ""; }
        upd();
      }
      function calcAC() { expr = ""; result = "0"; justEq = false; upd(); }
      function calcDel() {
        result = result.length > 1 ? result.slice(0,-1) : "0";
        upd();
      }
    </script>
    """, height=0, scrolling=False)
