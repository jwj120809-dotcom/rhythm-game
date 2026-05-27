import streamlit as str
import streamlit.components.v1 as components

# 페이지 설정
str.set_page_config(page_title="Streamlit QWER Rhythm Game", layout="centered")

str.title("🎵 QWER 리듬 게임")
str.subheader("스트림릿에서 즐기는 실시간 리듬 게임")

# 게임 설명
str.markdown("""
* **조작 방법**: `Q`, `W`, `E`, `R` 키를 타이밍에 맞춰 누르세요!
* 노트가 하단의 **판정선(붉은색 선)**에 닿았을 때 정확히 누르면 득점합니다.
* 아래 게임 화면을 **한 번 클릭**하여 포커스를 준 후 플레이해주세요.
""")

# JavaScript + HTML5 Canvas 기반의 게임 코드
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
            font-family: 'Arial', sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            margin: 0;
            overflow: hidden;
        }
        canvas {
            border: 4px solid #00D2FF;
            background-color: #111;
            box-shadow: 0px 0px 20px rgba(0,0,0,0.5);
        }
        #scoreBoard {
            font-size: 24px;
            margin-bottom: 10px;
            font-weight: bold;
        }
        #comboBoard {
            font-size: 20px;
            color: #FFD700;
            margin-bottom: 5px;
            height: 24px;
        }
    </style>
</head>
<body>

<div id="scoreBoard">SCORE: <span id="score">0</span></div>
<div id="comboBoard"><span id="combo"></span></div>
<canvas id="gameCanvas" width="400" height="500"></canvas>

<script>
const canvas = document.getElementById("gameCanvas");
const ctx = canvas.getContext("2d");

// QWER 게임 설정 변경
const lanes = ['Q', 'W', 'E', 'R'];
const laneX = { 'Q': 50, 'W': 150, 'E': 250, 'R': 350 };
const laneWidth = 100;
const judgmentLineY = 430; // 판정선 위치
const noteSpeed = 5;       // 노트 하강 속도
const tolerance = 30;      // 판정 범위 (픽셀)

let score = 0;
let combo = 0;
let notes = [];
let keyStates = { 'Q': false, 'W': false, 'E': false, 'R': false };
let judgmentTexts = []; // 판정 텍스트 이펙트 저장

// 노트 생성 타이머 (주기적으로 노트 생성)
setInterval(() => {
    const randomLane = lanes[Math.floor(Math.random() * lanes.length)];
    notes.push({
        lane: randomLane,
        y: 0,
        color: getRandomColor(randomLane)
    });
}, 600);

// 레인별 노트 색상 지정
function getRandomColor(lane) {
    if (lane === 'Q') return '#FF5733'; // 주황
    if (lane === 'W') return '#33FF57'; // 연두
    if (lane === 'E') return '#3357FF'; // 파랑
    if (lane === 'R') return '#F3FF33'; // 노랑
}

// 키보드 입력 이벤트
window.addEventListener('keydown', (e) => {
    let key = e.key.toUpperCase();
    if (lanes.includes(key) && !keyStates[key]) {
        keyStates[key] = true;
        checkJudgment(key);
    }
});

window.addEventListener('keyup', (e) => {
    let key = e.key.toUpperCase();
    if (lanes.includes(key)) {
        keyStates[key] = false;
    }
});

// 판정 체크
function checkJudgment(key) {
    let hit = false;
    for (let i = 0; i < notes.length; i++) {
        let note = notes[i];
        if (note.lane === key) {
            let distance = Math.abs(note.y - judgmentLineY);
            if (distance <= tolerance) {
                // Perfect 판정
                score += 100;
                combo += 1;
                addJudgmentEffect(key, "PERFECT", "#00FFCC");
                notes.splice(i, 1);
                hit = true;
                break;
            } else if (distance <= tolerance * 2) {
                // Good 판정
                score += 50;
                combo += 1;
                addJudgmentEffect(key, "GOOD", "#FFCC00");
                notes.splice(i, 1);
                hit = true;
                break;
            }
        }
    }
    
    document.getElementById("score").innerText = score;
    document.getElementById("combo").innerText = combo > 0 ? combo + " COMBO" : "";
}

function addJudgmentEffect(key, text, color) {
    judgmentTexts.push({
        x: laneX[key],
        y: judgmentLineY - 50,
        text: text,
        color: color,
        alpha: 1.0
    });
}

// 게임 메인 루프
function update() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // 1. 레인 가이드라인 그리기
    lanes.forEach(lane => {
        ctx.strokeStyle = "#333";
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(laneX[lane] - laneWidth/2, 0);
        ctx.lineTo(laneX[lane] - laneWidth/2, canvas.height);
        ctx.stroke();
        
        // 키 누름 효과
        if (keyStates[lane]) {
            ctx.fillStyle = "rgba(255, 255, 255, 0.15)";
            ctx.fillRect(laneX[lane] - laneWidth/2, 0, laneWidth, canvas.height);
        }
        
        // 레인 이름 표시 (Q, W, E, R)
        ctx.fillStyle = "#A0A0A0";
        ctx.font = "bold 22px Arial";
        ctx.fillText(lane, laneX[lane] - 10, canvas.height - 20);
    });

    // 2. 판정선 그리기
    ctx.strokeStyle = "#FF3333";
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(0, judgmentLineY);
    ctx.lineTo(canvas.width, judgmentLineY);
    ctx.stroke();

    // 3. 노트 업데이트 및 그리기
    for (let i = notes.length - 1; i >= 0; i--) {
        let note = notes[i];
        note.y += noteSpeed;

        // 노트 렌더링
        ctx.fillStyle = note.color;
        ctx.fillRect(laneX[note.lane] - 42, note.y - 10, 84, 20);

        // 놓쳤을 때 (Miss 처리)
        if (note.y > canvas.height) {
            notes.splice(i, 1);
            combo = 0; 
            document.getElementById("combo").innerText = "";
            addJudgmentEffect(note.lane, "MISS", "#FF3333");
        }
    }

    // 4. 판정 텍스트 이펙트 렌더링
    for (let i = judgmentTexts.length - 1; i >= 0; i--) {
        let jt = judgmentTexts[i];
        ctx.fillStyle = jt.color;
        ctx.globalAlpha = jt.alpha;
        ctx.font = "bold 20px Arial";
        ctx.fillText(jt.text, jt.x - 35, jt.y);
        
        jt.y -= 1.2; 
        jt.alpha -= 0.04; 
        
        if (jt.alpha <= 0) {
            judgmentTexts.splice(i, 1);
        }
    }
    ctx.globalAlpha = 1.0; 

    requestAnimationFrame(update);
}

// 게임 시작
update();
</script>
</body>
</html>
"""

# 스트림릿 컴포넌트로 HTML 삽입
components.html(game_html, height=600)
