import streamlit as st

def mostrar_calculadora():
    st.markdown("""
    <style>
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
        display: flex;
        align-items: center;
        justify-content: center;
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
        box-shadow: 0 8px 32px rgba(0,0,0,0.18);
        padding: 14px;
        display: none;
        flex-direction: column;
        gap: 8px;
    }
    #calc-panel.open { display: flex; }

    #calc-display {
        background: #f5f5f5;
        border-radius: 10px;
        padding: 10px 14px;
        text-align: right;
        font-size: 22px;
        font-weight: bold;
        color: #333;
        min-height: 48px;
        word-break: break-all;
        border: none;
        width: 100%;
        box-sizing: border-box;
    }
    #calc-expr {
        text-align: right;
        font-size: 11px;
        color: #aaa;
        min-height: 16px;
        padding: 0 4px;
    }

    .calc-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 6px;
    }
    .calc-grid button {
        border: none;
        border-radius: 10px;
        padding: 12px 0;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition: filter 0.15s;
    }
    .calc-grid button:hover { filter: brightness(0.92); }
    .calc-grid button:active { filter: brightness(0.82); }

    .btn-num  { background: #f0f0f0; color: #333; }
    .btn-op   { background: #ffe5f2; color: #FF69B4; }
    .btn-eq   { background: #2ABFBF; color: white; }
    .btn-clr  { background: #ffe5f2; color: #FF69B4; }
    .btn-del  { background: #f0f0f0; color: #666; }
    .btn-zero { grid-column: span 2; }
    </style>

    <button id="calc-btn" onclick="toggleCalc()">🧮</button>

    <div id="calc-panel">
        <div id="calc-expr"></div>
        <input id="calc-display" readonly value="0"/>
        <div class="calc-grid">
            <button class="btn-clr" onclick="calcAC()">AC</button>
            <button class="btn-del" onclick="calcDel()">⌫</button>
            <button class="btn-op"  onclick="calcOp('%')">%</button>
            <button class="btn-op"  onclick="calcOp('/')">÷</button>

            <button class="btn-num" onclick="calcNum('7')">7</button>
            <button class="btn-num" onclick="calcNum('8')">8</button>
            <button class="btn-num" onclick="calcNum('9')">9</button>
            <button class="btn-op"  onclick="calcOp('*')">×</button>

            <button class="btn-num" onclick="calcNum('4')">4</button>
            <button class="btn-num" onclick="calcNum('5')">5</button>
            <button class="btn-num" onclick="calcNum('6')">6</button>
            <button class="btn-op"  onclick="calcOp('-')">−</button>

            <button class="btn-num" onclick="calcNum('1')">1</button>
            <button class="btn-num" onclick="calcNum('2')">2</button>
            <button class="btn-num" onclick="calcNum('3')">3</button>
            <button class="btn-op"  onclick="calcOp('+')">+</button>

            <button class="btn-num btn-zero" onclick="calcNum('0')">0</button>
            <button class="btn-num" onclick="calcDot()">.</button>
            <button class="btn-eq"  onclick="calcEq()">=</button>
        </div>
    </div>

    <script>
    var calcExpr = "";
    var calcResult = "0";
    var calcJustEq = false;

    function toggleCalc() {
        var p = document.getElementById("calc-panel");
        p.classList.toggle("open");
    }

    function updateDisplay() {
        document.getElementById("calc-display").value = calcResult;
        document.getElementById("calc-expr").textContent = calcExpr;
    }

    function calcNum(n) {
        if (calcJustEq) { calcExpr = ""; calcResult = "0"; calcJustEq = false; }
        if (calcResult === "0" && n !== ".") calcResult = n;
        else calcResult += n;
        updateDisplay();
    }

    function calcDot() {
        if (calcJustEq) { calcExpr = ""; calcResult = "0"; calcJustEq = false; }
        if (calcResult.indexOf(".") === -1) calcResult += ".";
        updateDisplay();
    }

    function calcOp(op) {
        calcJustEq = false;
        calcExpr += calcResult + " " + op + " ";
        calcResult = "0";
        updateDisplay();
    }

    function calcEq() {
        try {
            var expr = calcExpr + calcResult;
            var res = Function('"use strict"; return (' + expr + ')')();
            calcExpr = expr + " =";
            calcResult = parseFloat(res.toFixed(10)).toString();
            calcJustEq = true;
        } catch(e) {
            calcResult = "Error";
            calcExpr = "";
        }
        updateDisplay();
    }

    function calcAC() {
        calcExpr = ""; calcResult = "0"; calcJustEq = false;
        updateDisplay();
    }

    function calcDel() {
        if (calcResult.length > 1) calcResult = calcResult.slice(0,-1);
        else calcResult = "0";
        updateDisplay();
    }
    </script>
    """, unsafe_allow_html=True)
