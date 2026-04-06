export enum EventType {
  Token = "token",
  ToolStart = "tool_start",
  ToolCall = "tool_call",
  ToolResult = "tool_result",
  ToolEnd = "tool_end",
  Error = "error",
  Done = "done",
  Cleared = "cleared",
  TaskUpdate = "task_update",
}

export enum MessageRole {
  User = "user",
  Assistant = "assistant",
  System = "system",
  Tool = "tool",
}

type TokenEvent = { type: EventType.Token; content: string };
type ToolStartEvent = { type: EventType.ToolStart };
type ToolCallEvent = {
  type: EventType.ToolCall;
  name: string;
  args: Record<string, unknown>;
};
type ToolResultEvent = { type: EventType.ToolResult; result: string };
type ToolEndEvent = { type: EventType.ToolEnd };
type ErrorEvent = { type: EventType.Error; content: string };
type Usage = {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
};
type DoneEvent = { type: EventType.Done; usage: Usage | null };
type ClearedEvent = { type: EventType.Cleared };
type TaskUpdateEvent = { type: EventType.TaskUpdate; tasks: Task[] };

export type AgentEvent =
  | TokenEvent
  | ToolStartEvent
  | ToolCallEvent
  | ToolResultEvent
  | ToolEndEvent
  | ErrorEvent
  | DoneEvent
  | ClearedEvent
  | TaskUpdateEvent;

export type ChatMessage =
  | { role: MessageRole.User; content: string }
  | { role: MessageRole.Assistant; content: string; toolCalls?: ToolCall[] }
  | { role: MessageRole.Tool; calls: ToolCall[] }
  | { role: MessageRole.System; content: string };

export type Task = {
  id: string;
  goal: string;
  status: string;
  steps: TaskStep[];
};

export type TaskStep = {
  description: string;
  status: string;
};

export type ToolCall = {
  name: string;
  args: Record<string, unknown>;
  result?: string;
};
