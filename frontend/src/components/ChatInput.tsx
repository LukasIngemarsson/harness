import { useState } from "react";
import { cn } from "../utils/cn";

type Props = {
  onSend: (text: string) => void;
  disabled: boolean;
};

export function ChatInput({ onSend, disabled }: Props) {
  const [input, setInput] = useState("");

  function handleSend() {
    const text = input.trim();
    if (!text) return;
    onSend(text);
    setInput("");
  }

  return (
    <div
      className={cn(
        "mx-auto flex w-full max-w-3xl gap-3",
        "border-t border-gray-700 p-4",
      )}
    >
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && handleSend()}
        disabled={disabled}
        placeholder="Type a message..."
        autoComplete="off"
        className={cn(
          "flex-1 rounded-md px-4 py-2.5",
          "border border-gray-600 bg-gray-800",
          "text-sm text-gray-200 outline-none",
          "focus:border-blue-400 disabled:opacity-50",
        )}
      />
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
    </div>
  );
}
