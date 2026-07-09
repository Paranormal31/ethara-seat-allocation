import React, { useState, useRef, useEffect } from 'react';
import { useApp } from '../context/AppContext';
import { Send, MessageSquare, Trash2 } from 'lucide-react';

export const ChatSidebar: React.FC = () => {
  const { aiMessages, sendAIQuery, clearChat, loading } = useApp();
  const [inputText, setInputText] = useState<string>('');
  const chatEndRef = useRef<HTMLDivElement>(null);

  const quickPills = [
    'Where is Amit seated?',
    'Who sits near Amit?',
    'Show available seats on floor 3',
    'Zone A utilization',
    'Who is in Project Talos?',
  ];

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [aiMessages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || loading) return;
    const query = inputText.trim();
    setInputText('');
    await sendAIQuery(query);
  };

  const handlePillClick = async (pillText: string) => {
    if (loading) return;
    await sendAIQuery(pillText);
  };

  return (
    <aside className="w-80 bg-white border-l border-slate-200 flex flex-col h-screen shrink-0 text-xs">
      {/* Header */}
      <div className="h-16 flex items-center justify-between px-4 border-b border-slate-200 shrink-0 bg-slate-50">
        <div className="flex items-center gap-2">
          <MessageSquare size={16} className="text-slate-500" />
          <span className="font-bold text-slate-800 tracking-tight">AI Workspace Assistant</span>
        </div>
        <button
          onClick={clearChat}
          className="p-1.5 hover:bg-slate-200 rounded text-slate-400 hover:text-slate-600 transition-colors"
          title="Clear Chat Logs"
        >
          <Trash2 size={14} />
        </button>
      </div>

      {/* Suggestion Tray Pills */}
      <div className="p-3 border-b border-slate-100 shrink-0 bg-slate-50 flex flex-col gap-1.5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider font-mono">
          Query suggestions
        </span>
        <div className="flex flex-wrap gap-1.5">
          {quickPills.map((pill, idx) => (
            <button
              key={idx}
              onClick={() => handlePillClick(pill)}
              disabled={loading}
              className="px-2.5 py-1.5 bg-white border border-slate-200 hover:border-blue-400 rounded text-[10px] text-slate-600 hover:text-blue-700 transition-all font-mono text-left block"
            >
              {pill}
            </button>
          ))}
        </div>
      </div>

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 font-mono bg-slate-50">
        {aiMessages.map((msg, idx) => {
          const isAssistant = msg.sender === 'assistant';
          return (
            <div
              key={idx}
              className={`flex flex-col space-y-1 max-w-[85%] ${
                isAssistant ? 'self-start mr-auto' : 'self-end ml-auto items-end'
              }`}
            >
              <div
                className={`p-3 rounded border text-left whitespace-pre-line ${
                  isAssistant
                    ? 'bg-white border-slate-200 text-slate-800'
                    : 'bg-blue-600 border-blue-700 text-white'
                }`}
              >
                {msg.text}
              </div>
              <span className="text-[9px] text-slate-400 px-1">
                {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </span>
            </div>
          );
        })}
        {loading && (
          <div className="self-start mr-auto max-w-[85%] p-3 rounded border bg-white border-slate-200 text-slate-400 font-mono animate-pulse">
            Processing query...
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Box */}
      <form onSubmit={handleSubmit} className="p-3 border-t border-slate-200 shrink-0 bg-white flex gap-2">
        <input
          type="text"
          value={inputText}
          onChange={e => setInputText(e.target.value)}
          placeholder="Ask a workspace question..."
          disabled={loading}
          className="flex-1 border border-slate-200 rounded px-3 py-2 bg-slate-50 focus:bg-white text-xs font-mono"
        />
        <button
          type="submit"
          disabled={loading || !inputText.trim()}
          className="p-2 bg-slate-900 border border-slate-950 hover:bg-slate-800 text-white rounded transition-colors disabled:opacity-50 flex items-center justify-center"
        >
          <Send size={14} />
        </button>
      </form>
    </aside>
  );
};
