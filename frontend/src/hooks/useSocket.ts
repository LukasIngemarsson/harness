import { useEffect, useRef, useCallback, useState } from "react";
import type { AgentEvent } from "../types";

export function useSocket(onEvent: (event: AgentEvent) => void) {
  const wsRef = useRef<WebSocket | null>(null);
  const connectRef = useRef<() => void>(() => {});
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    function connect() {
      const protocol = location.protocol === "https:" ? "wss:" : "ws:";
      const ws = new WebSocket(`${protocol}//${location.host}/ws`);
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => {
        setConnected(false);
        setTimeout(connect, 1000);
      };
      ws.onmessage = (e) => {
        const event: AgentEvent = JSON.parse(e.data);
        onEvent(event);
      };
    }

    connectRef.current = connect;
    connect();
    return () => wsRef.current?.close();
  }, [onEvent]);

  const sendMessage = useCallback((text: string) => {
    wsRef.current?.send(JSON.stringify({ message: text }));
  }, []);

  const sendConfirm = useCallback((approved: boolean) => {
    wsRef.current?.send(JSON.stringify({ approved }));
  }, []);

  const reconnect = useCallback(() => {
    wsRef.current?.close();
  }, []);

  return { sendMessage, sendConfirm, connected, reconnect };
}
