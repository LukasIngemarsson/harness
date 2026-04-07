import { useState } from "react";
import type { ToolCall } from "../types";
import { cn } from "../utils/cn";

type Props = {
  call: ToolCall;
  compact?: boolean;
};

const PREVIEW_LINES = 3;
const PREVIEW_CHARS = 300;
const ARGS_PREVIEW_CHARS = 80;

export function ToolBlock({ call, compact = false }: Props) {
  const [expanded, setExpanded] = useState(false);
  const [argsExpanded, setArgsExpanded] = useState(false);

  const result = call.result ?? "";
  const lines = result.split("\n");
  const tooManyLines = lines.length > PREVIEW_LINES;
  const tooManyChars = result.length > PREVIEW_CHARS;
  const isLong = tooManyLines || tooManyChars;
  const preview = tooManyLines
    ? lines.slice(0, PREVIEW_LINES).join("\n")
    : result.slice(0, PREVIEW_CHARS);

  const argsStr = JSON.stringify(call.args);
  const argsIsLong = argsStr.length > ARGS_PREVIEW_CHARS;

  return (
    <div
      className={cn(
        "my-2 rounded p-3",
        "border-l-3 border-gray-600 bg-gray-800",
        "font-mono break-all",
        compact ? "text-xs" : "text-sm",
      )}
    >
      <div className="mb-1 text-xs text-gray-500 uppercase">Tool Call</div>
      <div>
        {call.name}(
        {argsIsLong && !argsExpanded ? (
          <>
            {argsStr.slice(0, ARGS_PREVIEW_CHARS)}
            <button
              onClick={() => setArgsExpanded(true)}
              className="text-gray-500 hover:text-gray-300"
            >
              ...
            </button>
          </>
        ) : (
          argsStr
        )}
        )
        {argsIsLong && argsExpanded && (
          <button
            onClick={() => setArgsExpanded(false)}
            className="ml-2 text-xs text-gray-500 hover:text-gray-300"
          >
            Show less
          </button>
        )}
      </div>
      {call.result !== undefined && (
        <>
          <div className="mt-2 mb-1 text-xs text-gray-500 uppercase">
            Result
          </div>
          <div className="whitespace-pre-wrap">
            {expanded || !isLong ? result : preview}
          </div>
          {isLong && (
            <button
              onClick={() => setExpanded(!expanded)}
              className={cn(
                "mt-1 text-xs text-gray-500",
                "hover:text-gray-300",
              )}
            >
              {expanded ? "Show less" : "... Show more"}
            </button>
          )}
        </>
      )}
    </div>
  );
}
