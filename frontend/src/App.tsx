import { useCallback, useEffect, useRef, useState } from "react";
import type { AgentEvent, ChatMessage, Task, ToolCall } from "./types";
import { Command, EventType, MessageRole, TaskStatus } from "./types";
import { useSocket } from "./hooks/useSocket";
import { MessageBubble } from "./components/MessageBubble";
import { ChatInput } from "./components/ChatInput";
import { TaskProgress } from "./components/TaskProgress";
import { ThinkingIndicator } from "./components/ThinkingIndicator";
import { cn } from "./utils/cn";

export default function App() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [tasks, setTasks] = useState<Record<string, Task>>({});
  const [busy, setBusy] = useState(false);
  const [busySince, setBusySince] = useState(0);
  const [model, setModel] = useState<string>("");
  const [profile, setProfile] = useState<string>("default");
  const [tokenCount, setTokenCount] = useState<number | null>(null);
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

    fetch("/api/history")
      .then((r) => r.json())
      .then((data) => {
        if (data.messages?.length) setMessages(data.messages);
        if (data.tasks?.length) {
          const taskMap: Record<string, Task> = {};
          for (const t of data.tasks) {
            taskMap[t.id] = t;
          }
          setTasks(taskMap);
        }
      })
      .catch(() => {});
  }, []);

  const onEvent = useCallback((event: AgentEvent) => {
    switch (event.type) {
      case EventType.Token:
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === MessageRole.Assistant) {
            return [
              ...prev.slice(0, -1),
              { ...last, content: last.content + event.content },
            ];
          }
          return [
            ...prev,
            { role: MessageRole.Assistant, content: event.content },
          ];
        });
        break;

      case EventType.ToolStart:
        setMessages((prev) => [...prev, { role: MessageRole.Tool, calls: [] }]);
        break;

      case EventType.ToolCall:
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === MessageRole.Tool) {
            const call: ToolCall = { name: event.name, args: event.args };
            return [
              ...prev.slice(0, -1),
              { ...last, calls: [...last.calls, call] },
            ];
          }
          return prev;
        });
        break;

      case EventType.ToolResult:
        setMessages((prev) => {
          const last = prev[prev.length - 1];
          if (last?.role === MessageRole.Tool && last.calls.length > 0) {
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

      case EventType.TaskUpdate:
        setTasks((prev) => {
          const next = { ...prev };
          for (const t of event.tasks) {
            next[t.id] = t;
          }
          return next;
        });
        break;

      case EventType.Error:
        setMessages((prev) => [
          ...prev,
          {
            role: MessageRole.Assistant,
            content: `Error: ${event.content}`,
          },
        ]);
        setBusy(false);
        break;

      case EventType.Done:
        if (event.usage) {
          setTokenCount(event.usage.total_tokens);
        }
        setBusy(false);
        break;

      case EventType.Cleared:
        setMessages([
          { role: MessageRole.System, content: "Conversation cleared." },
        ]);
        setTasks({});
        setTokenCount(null);
        setBusy(false);
        break;

      case EventType.SystemMessage:
        setMessages((prev) => [
          ...prev,
          { role: MessageRole.System, content: event.content },
        ]);
        break;
    }
  }, []);

  const { sendMessage, connected, reconnect } = useSocket(onEvent);

  function handleSend(text: string) {
    if (text.toLowerCase() === Command.Clear) {
      sendMessage(text);
      setProfile("default");
      return;
    }
    if (text.toLowerCase().startsWith(Command.Mode)) {
      const parts = text.split(/\s+/, 2);
      if (parts.length > 1) setProfile(parts[1].toLowerCase());
      sendMessage(text);
      return;
    }
    setMessages((prev) => [...prev, { role: MessageRole.User, content: text }]);
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

  const activeTask =
    Object.values(tasks)
      .filter((t) => t.status !== TaskStatus.Completed)
      .at(-1) ?? null;

  return (
    <div className="flex h-screen flex-col bg-gray-900 text-gray-200">
      <header
        className={cn(
          "flex justify-between px-5 py-3",
          "border-b border-gray-700 text-sm text-gray-500",
        )}
      >
        <span>
          Harness
          <span className="ml-2 text-gray-600">/ {profile}</span>
        </span>
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
            {tokenCount !== null ? `${(tokenCount / 1000).toFixed(1)}k` : "–"}
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

      {activeTask && (
        <div className="border-b border-gray-700 px-5 py-3">
          <div className="mx-auto max-w-3xl">
            <TaskProgress goal={activeTask.goal} steps={activeTask.steps} />
          </div>
        </div>
      )}

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
