import { useState } from "react";
import type { ToolCall } from "../types";
import { cn } from "../utils/cn";

type Props = {
  call: ToolCall;
};

const PREVIEW_LINES = 3;

export function ToolBlock({ call }: Props) {
  const [expanded, setExpanded] = useState(false);

  const result = call.result ?? "";
  const lines = result.split("\n");
  const isLong = lines.length > PREVIEW_LINES;
  const preview = lines.slice(0, PREVIEW_LINES).join("\n");

  return (
    <div
      className={cn(
        "my-2 rounded p-3",
        "border-l-3 border-gray-600 bg-gray-800",
        "font-mono text-sm break-all",
      )}
    >
      <div className="mb-1 text-xs text-gray-500 uppercase">Tool Call</div>
      <div>
        {call.name}({JSON.stringify(call.args)})
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
              {expanded
                ? "Show less"
                : `... ${lines.length - PREVIEW_LINES} more lines`}
            </button>
          )}
        </>
      )}
    </div>
  );
}
