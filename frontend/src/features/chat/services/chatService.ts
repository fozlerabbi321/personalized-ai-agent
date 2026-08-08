const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface StreamCallbacks {
  onToken: (token: string) => void;
  onWidget: (widgetJson: any) => void;
  onDone: (sessionId: string) => void;
  onError: (error: string) => void;
}

export const chatService = {
  async streamChat(
    message: string,
    sessionId: string,
    token: string,
    callbacks: StreamCallbacks
  ): Promise<void> {
    const res = await fetch(`${API_URL}/api/chat/stream`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({ message, session_id: sessionId }),
    });

    if (!res.ok) {
      const errText = await res.text().catch(() => "Stream request failed");
      callbacks.onError(errText);
      return;
    }

    if (!res.body) {
      callbacks.onError("No response body received from server");
      return;
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder("utf-8");
    let buffer = "";

    try {
      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process line-by-line SSE events
        const lines = buffer.split("\n\n");
        buffer = lines.pop() || ""; // Keep incomplete chunk in buffer

        for (const block of lines) {
          if (!block.trim()) continue;

          let eventName = "";
          let dataStr = "";

          for (const line of block.split("\n")) {
            if (line.startsWith("event: ")) {
              eventName = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              dataStr = line.slice(6).trim();
            }
          }

          if (dataStr) {
            try {
              const payload = JSON.parse(dataStr);
              const type = payload.type || eventName;

              if (type === "token" && payload.content) {
                callbacks.onToken(payload.content);
              } else if (type === "widget" && payload.widget_json) {
                callbacks.onWidget(payload.widget_json);
              } else if (type === "done") {
                callbacks.onDone(payload.session_id || sessionId);
              } else if (type === "error") {
                callbacks.onError(payload.message || "An error occurred");
              }
            } catch {
              // Fail-safe raw data fallback
              if (eventName === "token") {
                callbacks.onToken(dataStr);
              }
            }
          }
        }
      }
    } catch (err: any) {
      callbacks.onError(err.message || "Stream interrupted");
    } finally {
      reader.releaseLock();
    }
  },
};
