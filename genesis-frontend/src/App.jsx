import { useState } from "react";
import axios from "axios";

const API_URL = "http://127.0.0.1:8000/ask";

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [intent, setIntent] = useState(null);
  const [error, setError] = useState(null);

  const handleAsk = async (e) => {
    e.preventDefault();
    setError(null);
    const trimmed = query.trim();
    if (!trimmed) return;

    const userMsg = { role: "user", content: trimmed };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);

    try {
      const res = await axios.post(API_URL, { query: trimmed });
      const { answer, intent: backendIntent } = res.data;
      setIntent(backendIntent || null);
      const assistantMsg = {
        role: "assistant",
        content: answer || "No answer returned from the RAG system.",
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail || err.message || "Something went wrong calling the RAG API."
      );
      const errorMsg = {
        role: "assistant",
        content: "⚠️ Failed to fetch answer from backend.",
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Genesis RAG – Real Estate Explainer</h1>
          <p className="text-xs text-slate-400 mt-1">Ask anything about the financial logic behind your property analyses.</p>
        </div>
        {intent && (
          <div className="px-3 py-1 rounded-full text-xs bg-emerald-500/10 text-emerald-300 border border-emerald-500/40">
            Intent: <span className="font-medium">{intent}</span>
          </div>
        )}
      </header>

      <main className="flex-1 flex flex-col md:flex-row">
        <section className="flex-1 flex flex-col border-r border-slate-800">
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3">
            {messages.length === 0 && (
              <div className="h-full flex flex-col items-center justify-center text-center text-slate-500 text-sm">
                <p className="mb-2">Start by asking something like:</p>
                <p className="font-mono text-xs bg-slate-900 px-3 py-2 rounded">“Why is buying better than renting for 3 BHK in Surat?”</p>
              </div>
            )}

            {messages.map((m, idx) => (
              <div key={idx} className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}>
                <div className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed shadow-sm
                    ${m.role === "user" ? "bg-indigo-500 text-white" : "bg-slate-900 border border-slate-800"}`}>
                  {m.content}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex justify-start">
                <div className="max-w-[70%] rounded-2xl px-4 py-3 text-sm bg-slate-900 border border-slate-800 text-slate-400 flex items-center gap-2">
                  <span className="h-2 w-2 rounded-full bg-emerald-400 animate-pulse"></span>
                  Thinking with RAG + Gemini 2.5 Flash…
                </div>
              </div>
            )}
          </div>

          <form onSubmit={handleAsk} className="border-t border-slate-800 px-4 py-3 flex gap-3 bg-slate-950/80 backdrop-blur">
            <input type="text" className="flex-1 rounded-xl bg-slate-900 border border-slate-700 px-3 py-2 text-sm outline-none focus:border-indigo-400 focus:ring-1 focus:ring-indigo-500" placeholder="Ask about a property, ROI logic, wealth comparison, or tax impact…" value={query} onChange={(e) => setQuery(e.target.value)} />
            <button type="submit" disabled={loading} className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-500 hover:bg-indigo-400 disabled:bg-slate-700 text-white px-4 py-2 text-sm font-medium transition-colors">{loading ? "Asking…" : "Ask"}</button>
          </form>

          {error && <div className="px-4 py-2 text-xs text-rose-300 bg-rose-950/40 border-t border-rose-700/40">{error}</div>}
        </section>

        <aside className="w-full md:w-80 border-t md:border-t-0 md:border-l border-slate-800 bg-slate-950/60 px-4 py-4 space-y-4 text-xs text-slate-300">
          <div>
            <h2 className="text-sm font-semibold text-slate-100 mb-1">How this works</h2>
            <ol className="list-decimal list-inside space-y-1 text-slate-400">
              <li>Query is classified into an intent.</li>
              <li>We fetch candidate properties from Postgres.</li>
              <li>We refine with semantic search over your FAISS index.</li>
              <li>Gemini 2.5 Flash explains the financial logic using only your analysis text.</li>
            </ol>
          </div>

          <div className="border border-slate-800 rounded-lg p-3 bg-slate-950/60">
            <h3 className="text-xs font-semibold text-slate-100 mb-1">Safety & Rules</h3>
            <ul className="list-disc list-inside space-y-1 text-slate-400">
              <li>No made‑up numbers – only your data is used.</li>
              <li>No automatic BUY/RENT decisions by the model.</li>
              <li>Focus is on explaining “why”, not giving advice.</li>
            </ul>
          </div>

          <div className="border border-slate-800 rounded-lg p-3 bg-slate-950/60">
            <h3 className="text-xs font-semibold text-slate-100 mb-1">Example questions</h3>
            <ul className="list-disc list-inside space-y-1 text-slate-400">
              <li>“Why is renting better for this property?”</li>
              <li>“How do tax savings impact the final wealth?”</li>
              <li>“Explain EMI vs rent tradeoff for this case.”</li>
            </ul>
          </div>
        </aside>
      </main>
    </div>
  );
}

export default App;
