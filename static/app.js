const messages = document.getElementById("messages");
const input = document.getElementById("input");
const sendBtn = document.getElementById("send");

let ws = null;
let currentAssistant = null;
let toolContainer = null;

function connect() {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  ws = new WebSocket(`${protocol}//${location.host}/ws`);

  ws.onmessage = (e) => {
    const event = JSON.parse(e.data);
    handleEvent(event);
  };

  ws.onclose = () => {
    setTimeout(connect, 1000);
  };
}

function handleEvent(event) {
  if (event.type === "token" || event.type === "tool_start") {
    const el = document.getElementById("loading");
    if (el) el.remove();
  }
  switch (event.type) {
    case "token":
      if (!currentAssistant) {
        currentAssistant = addMessage("assistant", "");
      }
      currentAssistant.querySelector(".content").textContent += event.content;
      scrollToBottom();
      break;

    case "tool_start":
      toolContainer = document.createElement("div");
      toolContainer.className = "message assistant";
      toolContainer.innerHTML = `<div class="role">tools</div>`;
      if (currentAssistant) {
        messages.insertBefore(toolContainer, currentAssistant);
      } else {
        messages.appendChild(toolContainer);
      }
      scrollToBottom();
      break;

    case "tool_call":
      const callBlock = document.createElement("div");
      callBlock.className = "tool-block";
      callBlock.innerHTML =
        `<div class="label">Tool Call</div>${event.name}(${JSON.stringify(event.args)})`;
      toolContainer.appendChild(callBlock);
      scrollToBottom();
      break;

    case "tool_result":
      const resultBlock = document.createElement("div");
      resultBlock.className = "tool-block";
      resultBlock.innerHTML =
        `<div class="label">Result</div>${escapeHtml(event.result)}`;
      toolContainer.appendChild(resultBlock);
      scrollToBottom();
      break;

    case "tool_end":
      toolContainer = null;
      break;

    case "error":
      const errorBlock = document.createElement("div");
      errorBlock.className = "tool-block error";
      errorBlock.innerHTML =
        `<div class="label">Error</div>${escapeHtml(event.content)}`;
      (toolContainer || getTargetContainer()).appendChild(errorBlock);
      scrollToBottom();
      break;

    case "done":
      currentAssistant = null;
      setReady();
      break;

    case "cleared":
      messages.innerHTML = "";
      currentAssistant = null;
      setReady();
      break;
  }
}

function getTargetContainer() {
  if (!currentAssistant) {
    currentAssistant = addMessage("assistant", "");
  }
  return currentAssistant;
}

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = `message ${role}`;
  div.innerHTML =
    `<div class="role">${role}</div><div class="content">${escapeHtml(text)}</div>`;
  messages.appendChild(div);
  scrollToBottom();
  return div;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function setBusy() {
  sendBtn.disabled = true;
  input.disabled = true;
  const indicator = document.createElement("div");
  indicator.id = "loading";
  indicator.className = "message assistant";
  indicator.innerHTML = `<div class="role">assistant</div><div class="content loading-dots">Thinking</div>`;
  messages.appendChild(indicator);
  scrollToBottom();
}

function setReady() {
  sendBtn.disabled = false;
  input.disabled = false;
  const el = document.getElementById("loading");
  if (el) el.remove();
  input.focus();
}

function scrollToBottom() {
  messages.scrollTop = messages.scrollHeight;
}

function send() {
  const text = input.value.trim();
  if (!text || !ws || ws.readyState !== WebSocket.OPEN) return;

  if (text.toLowerCase() !== "/clear") {
    addMessage("user", text);
  }

  ws.send(JSON.stringify({ message: text }));
  input.value = "";
  setBusy();
}

input.addEventListener("keydown", (e) => {
  if (e.key === "Enter") send();
});

sendBtn.addEventListener("click", send);

connect();
