let recognition;
let finalText = "";
let isRecording = false;
let timerInterval;
let secondsElapsed = 0;
let meetingStartTime;
let summaryData = null;
let bulletsData = [];

function showScreen(id) {
    document
        .querySelectorAll(".screen")
        .forEach((s) => s.classList.remove("active"));
    document.getElementById(id).classList.add("active");
}

function formatTime(s) {
    const m = Math.floor(s / 60)
        .toString()
        .padStart(2, "0");
    const sec = (s % 60).toString().padStart(2, "0");
    return `${m}:${sec}`;
}

function startTimer() {
    secondsElapsed = 0;
    timerInterval = setInterval(() => {
        secondsElapsed++;
        document.getElementById("timerDisplay").textContent =
            formatTime(secondsElapsed);
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

function startRecording() {
    finalText = "";
    summaryData = null;
    bulletsData = [];

    recognition = new (
        window.SpeechRecognition || window.webkitSpeechRecognition
    )();
    recognition.continuous = true;
    recognition.interimResults = true;

    isRecording = true;
    meetingStartTime = new Date();

    recognition.onresult = (event) => {
        let interim = "";
        for (let i = event.resultIndex; i < event.results.length; i++) {
            const t = event.results[i][0].transcript;
            if (event.results[i].isFinal) finalText += t + " ";
            else interim += t;
        }
        const liveEl = document.getElementById("liveText");
        liveEl.classList.remove("placeholder");
        liveEl.textContent = finalText + interim;
    };

    recognition.onend = () => {
        if (isRecording) recognition.start();
    };
    recognition.start();

    showScreen("recordingScreen");
    document.getElementById("endBtn").style.display = "block";
    startTimer();
}

function undoLast() {
    const words = finalText.trim().split(" ");
    words.pop();
    finalText = words.join(" ") + (words.length ? " " : "");
    const liveEl = document.getElementById("liveText");
    liveEl.textContent = finalText;
}

function stopRecording() {
    endMeeting();
}

async function endMeeting() {
    isRecording = false;
    if (recognition) recognition.stop();
    stopTimer();

    const now = new Date();
    const dateStr = now.toLocaleDateString("en-US", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
    });
    const timeStr = now.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
    });
    document.getElementById("notesMeta").textContent =
        `${dateStr} · ${timeStr}`;
    document.getElementById("notesDuration").textContent =
        `Duration: ${formatTime(secondsElapsed)}`;
    document.getElementById("notesTranscript").textContent = finalText || "—";

    document.getElementById("notesSummary").textContent = "Generating summary…";
    document.getElementById("notesBullets").innerHTML =
        "<li>Extracting key points…</li>";
    document.getElementById("endBtn").style.display = "none";
    showScreen("notesScreen");

    try {
        const res = await fetch("http://127.0.0.1:8000/process-text", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: finalText }),
        });
        const data = await res.json();
        summaryData = data.summary;
        bulletsData = data.bullets;

        document.getElementById("notesSummary").textContent = data.summary;
        document.getElementById("notesBullets").innerHTML = data.bullets
            .map((b) => `<li>${b}</li>`)
            .join("");

        document.getElementById("liveSummary").classList.remove("placeholder");
        document.getElementById("liveSummary").textContent = data.summary;
        const bulletsEl = document.getElementById("liveBullets");
        bulletsEl.classList.remove("placeholder");
        bulletsEl.innerHTML = `<ul class="bullet-list">${data.bullets.map((b) => `<li>${b}</li>`).join("")}</ul>`;
    } catch (e) {
        document.getElementById("notesSummary").textContent =
            "Could not connect to backend. Check that your server is running on port 8000.";
        document.getElementById("notesBullets").innerHTML = "";
    }
}

function copyNotes() {
    const text = [
        "MEETING NOTES",
        document.getElementById("notesMeta").textContent,
        "",
        "SUMMARY",
        document.getElementById("notesSummary").textContent,
        "",
        "KEY POINTS",
        ...Array.from(document.querySelectorAll("#notesBullets li")).map(
            (li) => "• " + li.textContent,
        ),
        "",
        "FULL TRANSCRIPT",
        document.getElementById("notesTranscript").textContent,
    ].join("\n");
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.querySelector(".btn-copy");
        btn.textContent = "✓ Copied!";
        setTimeout(() => {
            btn.innerHTML = `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg> Copy`;
        }, 2000);
    });
}

async function downloadPDF() {
    try {
        const res = await fetch("http://127.0.0.1:8000/generate-pdf", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                summary: summaryData,
                bullets: bulletsData,
            }),
        });

        if (!res.ok) {
            alert("Failed to generate PDF");
            return;
        }

        const blob = await res.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "notes.pdf";
        document.body.appendChild(a);
        a.click();
        a.remove();
    } catch (err) {
        console.error(err);
        alert("Backend not reachable");
    }
}
function newMeeting() {
    finalText = "";
    summaryData = null;
    bulletsData = [];
    document.getElementById("liveText").innerHTML =
        '<div class="placeholder">Listening…</div>';
    document.getElementById("liveSummary").className = "panel-body placeholder";
    document.getElementById("liveSummary").textContent =
        "Summary will appear after recording ends";
    document.getElementById("liveBullets").className = "panel-body placeholder";
    document.getElementById("liveBullets").textContent =
        "Key points will be extracted from your meeting";
    document.getElementById("timerDisplay").textContent = "00:00";
    showScreen("idleScreen");
}
window.downloadPDF = downloadPDF;

document.addEventListener("DOMContentLoaded", () => {
    document.getElementById("endBtn").addEventListener("click", endMeeting);
    document
        .getElementById("startBtn")
        .addEventListener("click", startRecording);
    document.getElementById("stopBtn").addEventListener("click", stopRecording);
    document.querySelector(".btn-undo").addEventListener("click", undoLast);
    document.querySelector(".btn-copy").addEventListener("click", copyNotes);
    document
        .querySelector(".btn-download")
        .addEventListener("click", downloadPDF);
    document.querySelector(".btn-new").addEventListener("click", newMeeting);
});