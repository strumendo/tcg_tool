"use client";

interface ChatMessageProps {
  role: "user" | "assistant";
  content: string;
  timestamp: string;
  isStreaming?: boolean;
}

export default function ChatMessage({
  role,
  content,
  timestamp,
  isStreaming,
}: ChatMessageProps) {
  const isUser = role === "user";

  // Simple markdown-like rendering: bold, code blocks, lists
  const formatContent = (text: string) => {
    // Split by code blocks first
    const parts = text.split(/(```[\s\S]*?```)/g);
    return parts.map((part, i) => {
      if (part.startsWith("```") && part.endsWith("```")) {
        const code = part.slice(3, -3).replace(/^\w+\n/, "");
        return (
          <pre
            key={i}
            className="bg-gray-800 text-gray-100 rounded-lg p-3 my-2 overflow-x-auto text-sm font-mono"
          >
            {code}
          </pre>
        );
      }

      // Process inline formatting
      const lines = part.split("\n");
      return lines.map((line, j) => {
        // Headers
        if (line.startsWith("### ")) {
          return (
            <p key={`${i}-${j}`} className="font-bold text-base mt-3 mb-1">
              {line.slice(4)}
            </p>
          );
        }
        if (line.startsWith("## ")) {
          return (
            <p key={`${i}-${j}`} className="font-bold text-lg mt-3 mb-1">
              {line.slice(3)}
            </p>
          );
        }

        // List items
        if (line.match(/^[-*] /)) {
          return (
            <p key={`${i}-${j}`} className="ml-4 before:content-['•'] before:mr-2">
              {formatInline(line.slice(2))}
            </p>
          );
        }

        // Numbered list
        if (line.match(/^\d+\. /)) {
          return (
            <p key={`${i}-${j}`} className="ml-4">
              {formatInline(line)}
            </p>
          );
        }

        // Empty line
        if (line.trim() === "") {
          return <br key={`${i}-${j}`} />;
        }

        return (
          <p key={`${i}-${j}`}>{formatInline(line)}</p>
        );
      });
    });
  };

  const formatInline = (text: string) => {
    // Bold **text**
    const parts = text.split(/(\*\*[^*]+\*\*)/g);
    return parts.map((part, i) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return (
          <strong key={i} className="font-semibold">
            {part.slice(2, -2)}
          </strong>
        );
      }
      // Inline code `text`
      const codeParts = part.split(/(`[^`]+`)/g);
      return codeParts.map((cp, j) => {
        if (cp.startsWith("`") && cp.endsWith("`")) {
          return (
            <code
              key={`${i}-${j}`}
              className="bg-gray-200 text-gray-800 px-1.5 py-0.5 rounded text-sm font-mono"
            >
              {cp.slice(1, -1)}
            </code>
          );
        }
        return cp;
      });
    });
  };

  const time = new Date(timestamp).toLocaleTimeString("pt-BR", {
    hour: "2-digit",
    minute: "2-digit",
  });

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[85%] ${isUser ? "order-2" : "order-1"}`}>
        {/* Avatar */}
        <div className={`flex items-end gap-2 ${isUser ? "flex-row-reverse" : ""}`}>
          <div
            className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0 ${
              isUser
                ? "bg-primary-600 text-white"
                : "bg-gradient-to-br from-purple-500 to-indigo-600 text-white"
            }`}
          >
            {isUser ? "V" : "IA"}
          </div>

          <div
            className={`rounded-2xl px-4 py-3 ${
              isUser
                ? "bg-primary-600 text-white rounded-br-md"
                : "bg-gray-100 text-gray-800 rounded-bl-md"
            }`}
          >
            <div className="text-sm leading-relaxed space-y-1">
              {formatContent(content)}
              {isStreaming && (
                <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
              )}
            </div>
          </div>
        </div>

        <p
          className={`text-xs text-gray-400 mt-1 ${
            isUser ? "text-right mr-10" : "ml-10"
          }`}
        >
          {time}
        </p>
      </div>
    </div>
  );
}
