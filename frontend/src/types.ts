type TokenEvent = { type: "token"; content: string };
type ToolStartEvent = { type: "tool_start" };
type ToolCallEvent = {
  type: "tool_call";
  name: string;
  args: Record<string, unknown>;
};
type ToolResultEvent = { type: "tool_result"; result: string };
type ToolEndEvent = { type: "tool_end" };
type ErrorEvent = { type: "error"; content: string };
type Usage = {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
};
type DoneEvent = { type: "done"; usage: Usage | null };
type ClearedEvent = { type: "cleared" };

export type AgentEvent =
  | TokenEvent
  | ToolStartEvent
  | ToolCallEvent
  | ToolResultEvent
  | ToolEndEvent
  | ErrorEvent
  | DoneEvent
  | ClearedEvent;

export type ChatMessage =
  | { role: "user"; content: string }
  | { role: "assistant"; content: string; toolCalls?: ToolCall[] }
  | { role: "tool"; calls: ToolCall[] }
  | { role: "system"; content: string };

export type ToolCall = {
  name: string;
  args: Record<string, unknown>;
  result?: string;
};
