import { useState, useRef, useEffect } from "react";
import { Command } from "../types";
import { cn } from "../utils/cn";

type CommandEntry = {
  name: Command;
  description: string;
};

const COMMANDS: CommandEntry[] = [
  { name: Command.Clear, description: "Clear conversation history" },
  {
    name: Command.Mode,
    description: "Switch agent profile",
  },
];

type Props = {
  onSend: (text: string) => void;
  onCancel: () => void;
  busy: boolean;
  disabled: boolean;
};

export function ChatInput({ onSend, onCancel, busy, disabled }: Props) {
  const [input, setInput] = useState("");
  const [selectedIndex, setSelectedIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  const isCommandMode = input.startsWith("/");
  const filteredCommands = isCommandMode
    ? COMMANDS.filter((cmd) =>
        cmd.name.toLowerCase().startsWith(input.toLowerCase()),
      )
    : [];
  const showMenu = isCommandMode && filteredCommands.length > 0 && !busy;

  useEffect(() => {
    setSelectedIndex(0);
  }, [input]);

  function handleSend() {
    const text = input.trim();
    if (!text) return;
    onSend(text);
    setInput("");
  }

  function selectCommand(cmd: CommandEntry) {
    if (cmd.name === Command.Mode) {
      setInput(`${Command.Mode} `);
      inputRef.current?.focus();
      return;
    }
    onSend(cmd.name);
    setInput("");
    inputRef.current?.focus();
  }

  function handleKeyDown(e: React.KeyboardEvent) {
    if (showMenu) {
      const isUp = e.key === "ArrowUp" || (e.key === "p" && e.ctrlKey);
      const isDown = e.key === "ArrowDown" || (e.key === "n" && e.ctrlKey);
      if (isUp) {
        e.preventDefault();
        setSelectedIndex((i) => (i > 0 ? i - 1 : filteredCommands.length - 1));
        return;
      }
      if (isDown) {
        e.preventDefault();
        setSelectedIndex((i) => (i < filteredCommands.length - 1 ? i + 1 : 0));
        return;
      }
      if (e.key === "Enter" || e.key === "Tab") {
        e.preventDefault();
        selectCommand(filteredCommands[selectedIndex]);
        return;
      }
    }

    if (e.key === "Enter" && !busy) {
      handleSend();
    }
  }

  return (
    <div className="relative mx-auto w-full max-w-3xl">
      {showMenu && (
        <div
          className={cn(
            "absolute bottom-full mb-1 w-full",
            "rounded-md border border-gray-700 bg-gray-800",
            "overflow-hidden shadow-lg",
          )}
        >
          {filteredCommands.map((cmd, i) => (
            <button
              key={cmd.name}
              onClick={() => selectCommand(cmd)}
              className={cn(
                "flex w-full items-center gap-3 px-4 py-2.5 text-left text-sm",
                i === selectedIndex
                  ? "bg-gray-700 text-gray-200"
                  : "text-gray-400 hover:bg-gray-700",
              )}
            >
              <span className="font-mono text-blue-400">{cmd.name}</span>
              <span className="text-gray-500">{cmd.description}</span>
            </button>
          ))}
        </div>
      )}

      <div className={cn("flex gap-3 border-t border-gray-700 p-4")}>
        <input
          ref={inputRef}
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled}
          placeholder="Type a message..."
          autoComplete="off"
          className={cn(
            "flex-1 rounded-md px-4 py-2.5",
            "border bg-gray-800 text-sm text-gray-200 outline-none",
            isCommandMode && !busy
              ? "border-blue-500"
              : "border-gray-600 focus:border-blue-400",
            "disabled:opacity-50",
          )}
        />
        {busy ? (
          <button
            onClick={onCancel}
            className={cn(
              "rounded-md px-5 py-2.5",
              "bg-gray-700 text-sm font-semibold text-gray-300",
              "hover:bg-red-600 hover:text-white",
            )}
          >
            Cancel
          </button>
        ) : (
          <button
            onClick={handleSend}
            disabled={disabled || !input.trim()}
            className={cn(
              "rounded-md px-5 py-2.5",
              "bg-blue-500 text-sm font-semibold text-white",
              "hover:bg-blue-600",
              "disabled:cursor-not-allowed disabled:opacity-50",
            )}
          >
            Send
          </button>
        )}
      </div>
    </div>
  );
}
