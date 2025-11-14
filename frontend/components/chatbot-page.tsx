"use client";

import { useState, useRef, useEffect } from "react";
import { Send } from "lucide-react";
import { Button } from "@/components/ui/button";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function ChatbotPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your AI Supply Chain Assistant. I can help you analyze your data, optimize operations, and answer questions about your supply chain. What would you like to know?",
      timestamp: new Date(),
    },
  ]);

  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // -----------------------------
  // Send message to Flask backend
  // -----------------------------
  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);

    const userText = input;
    setInput("");
    setLoading(true);

    let reply = "Something went wrong.";

    try {
      const res = await fetch("http://localhost:5000/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question: userText }),
      });

      if (!res.ok) {
        throw new Error(`HTTP error: ${res.status}`);
      }

      const data = await res.json();

      // ---- FIX: Use correct field returned by Flask backend ----
      reply = data?.insights?.[0]?.text || "No insights received.";
    } catch (err) {
      console.error("FETCH ERROR:", err);
      reply = "Server error. Please try again.";
    }

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: "assistant",
      content: reply,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMessage]);
    setLoading(false);
  };

  return (
    <>
      <style>{`
        .leaves-bg {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          opacity: 0.75;
          pointer-events: none;
          z-index: 0;
          background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 400"></svg>');
          background-repeat: repeat;
          background-size: 700px;
        }

        @keyframes fadeInUp {
          from { opacity: 0; transform: translateY(20px); }
          to   { opacity: 1; transform: translateY(0); }
        }

        .message-animate {
          animation: fadeInUp 0.4s ease-out forwards;
        }
      `}</style>

      <div className="flex flex-col h-full bg-background dark:bg-slate-900 relative overflow-hidden">
        <div className="leaves-bg" />

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-4 md:px-8 py-8 relative z-10">
          <div className="max-w-3xl mx-auto space-y-6">
            {messages.map((message, idx) => (
              <div
                key={message.id}
                className={`flex justify-center ${
                  idx > 0 ? "message-animate" : ""
                }`}
                style={{ animationDelay: idx > 0 ? `${idx * 0.1}s` : "0s" }}
              >
                <div
                  className={`w-full max-w-2xl px-8 py-5 rounded-3xl backdrop-blur-md border-2 transition-all duration-300 ${
                    message.role === "user"
                      ? "bg-linear-to-r from-primary via-accent to-primary text-white border-accent/70 shadow-2xl shadow-primary/40"
                      : "bg-linear-to-br from-white/20 to-white/10 text-white border-white/30 shadow-2xl shadow-black/30"
                  }`}
                >
                  <p className="text-base leading-relaxed font-medium">
                    {message.content}
                  </p>
                  <p className="text-xs mt-3 font-semibold text-white/60">
                    {message.timestamp.toLocaleTimeString([], {
                      hour: "2-digit",
                      minute: "2-digit",
                    })}
                  </p>
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-center message-animate">
                <div className="w-full max-w-2xl bg-linear-to-br from-white/20 to-white/10 px-8 py-5 rounded-3xl border-2 border-white/30 shadow-2xl shadow-black/30">
                  <div className="flex gap-3 justify-center">
                    <div className="w-3 h-3 bg-accent rounded-full animate-bounce" />
                    <div className="w-3 h-3 bg-accent rounded-full animate-bounce delay-100" />
                    <div className="w-3 h-3 bg-accent rounded-full animate-bounce delay-200" />
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-border/50 px-4 md:px-8 py-8 bg-background dark:bg-slate-900 relative z-10">
          <div className="max-w-3xl mx-auto">
            <div className="flex gap-3 mb-3">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendMessage()}
                placeholder="Ask me about your supply chain..."
                className="flex-1 px-5 py-3 rounded-full bg-white/10 backdrop-blur-sm text-white border-2 border-border/50 focus:ring-2 focus:ring-accent transition-all duration-300"
                disabled={loading}
              />

              <Button
                size="lg"
                onClick={handleSendMessage}
                disabled={loading || !input.trim()}
                className="bg-linear-to-r from-primary to-accent rounded-full px-8 hover:scale-105 transition-all"
              >
                <Send className="w-4 h-4" />
              </Button>
            </div>

            <p className="text-xs text-muted-foreground text-center">
              💡 Ask about demand forecasting, optimal stock levels, warehouse
              efficiency, or transportation delays
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
