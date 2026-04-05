import { useCallback, useEffect, useRef, useState } from "react";
import type { AgentEvent, ChatMessage, ToolCall } from "./types";
import { useSocket } from "./hooks/useSocket";
import { MessageBubble } from "./components/MessageBubble";
import { ChatInput } from "./components/ChatInput";
import { ThinkingIndicator } from "./components/ThinkingIndicator";
import { cn } from "./utils/cn";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [busySince, setBusySince] = useState(0);
  const [model, setModel] = useState<string>("");
  const [tokenCount, setTokenCount] = useState(0);
  const [contextLength, setContextLength] = useState<number | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/info")
      .then((r) => r.json())
      .then((data) => {
        setModel(data.model);
        if (data.context_length) setContextLength(data.context_length);
      })
      .catch(() => setModel("unknown"));
  }, []);

  const onEvent = useCallback((event: AgentEvent) => {
    switch (event.type) {
      case "token":
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "assistant") {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + event.content },
            ];
          }
          return [...prev, { role: "assistant", content: event.content }];
        });
        break;

      case "tool_start":
        setMessages((prev) => [...prev, { role: "tool", calls: [] }]);
        break;

      case "tool_call":
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "tool") {
            const call: ToolCall = { name: event.name, args: event.args };
            return [
              ...prev.slice(0, -1),
              { ...last, calls: [...last.calls, call] },
            ];
          }
          return prev;
        });
        break;

      case "tool_result":
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === "tool" && last.calls.length > 0) {
            const calls = [...last.calls];
            calls[calls.length - 1] = {
              ...calls[calls.length - 1],
              result: event.result,
            };
            return [...prev.slice(0, -1), { ...last, calls }];
          }
          return prev;
        });
        break;

      case "error":
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: `Error: ${event.content}` },
        ]);
        setBusy(false);
        break;

      case "done":
        if (event.usage) {
          setTokenCount(event.usage.total_tokens);
        }
        setBusy(false);
        break;

      case "cleared":
        setMessages([{ role: "system", content: "Conversation cleared." }]);
        setTokenCount(0);
        setBusy(false);
        break;
    }
  }, []);

  const { sendMessage, connected, reconnect } = useSocket(onEvent);

  function handleSend(text: string) {
    if (text.toLowerCase() === "/clear") {
      sendMessage(text);
      return;
    }
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    sendMessage(text);
    setBusy(true);
    setBusySince(Date.now());
  }

  function handleCancel() {
    reconnect();
    setBusy(false);
  }

  useEffect(() => {
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === "Escape" && busy) handleCancel();
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [busy]);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  return (
    <div className="flex h-screen flex-col bg-gray-900 text-gray-200">
      <header
        className={cn(
          "flex justify-between px-5 py-3",
          "border-b border-gray-700 text-sm text-gray-500",
        )}
      >
        <span>Harness</span>
        <div className="flex items-center gap-3">
          <span className="flex items-center gap-1 text-gray-500">
            <svg
              viewBox="0 0 16 16"
              className="h-3.5 w-3.5"
              fill="none"
              stroke="currentColor"
              strokeWidth="1.5"
            >
              <ellipse cx="8" cy="11" rx="5" ry="2" />
              <ellipse cx="8" cy="8" rx="5" ry="2" />
              <ellipse cx="8" cy="5" rx="5" ry="2" />
              <line x1="3" y1="5" x2="3" y2="11" />
              <line x1="13" y1="5" x2="13" y2="11" />
            </svg>
            {(tokenCount / 1000).toFixed(1)}k
            {contextLength && ` / ${(contextLength / 1000).toFixed(1)}k`}
          </span>
          {model && <span className="text-gray-400">{model}</span>}
          <span
            className={cn(
              "inline-block h-2 w-2 rounded-full",
              connected ? "bg-green-500" : "bg-red-500",
            )}
            title={connected ? "Connected" : "Disconnected"}
          />
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-5">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        {busy && <ThinkingIndicator startTime={busySince} />}
        <div ref={bottomRef} />
      </div>

      <ChatInput
        onSend={handleSend}
        onCancel={handleCancel}
        busy={busy}
        disabled={!connected}
      />
    </div>
  );
}
