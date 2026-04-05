import { useCallback, useEffect, useRef, useState } from "react";
import type { AgentEvent, ChatMessage, ToolCall } from "./types";
import { useSocket } from "./hooks/useSocket";
import { MessageBubble } from "./components/MessageBubble";
import { ChatInput } from "./components/ChatInput";
import { cn } from "./utils/cn";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [busy, setBusy] = useState(false);
  const [model, setModel] = useState<string>("");
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetch("/api/info")
      .then((r) => r.json())
      .then((data) => setModel(data.model))
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
        setBusy(false);
        break;

      case "cleared":
        setMessages([]);
        setBusy(false);
        break;
    }
  }, []);

  const { sendMessage, connected } = useSocket(onEvent);

  function handleSend(text: string) {
    if (text.toLowerCase() === "/clear") {
      sendMessage(text);
      return;
    }
    setMessages((prev) => [...prev, { role: "user", content: text }]);
    sendMessage(text);
    setBusy(true);
  }

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

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
          {model && <span className="text-gray-400">{model}</span>}
          <span className={connected ? "text-green-500" : "text-red-500"}>
            {connected ? "Connected" : "Disconnected"}
          </span>
        </div>
      </header>

      <div className="flex flex-1 flex-col gap-4 overflow-y-auto p-5">
        {messages.map((msg, i) => (
          <MessageBubble key={i} message={msg} />
        ))}
        <div ref={bottomRef} />
      </div>

      <ChatInput onSend={handleSend} disabled={busy || !connected} />
    </div>
  );
}
