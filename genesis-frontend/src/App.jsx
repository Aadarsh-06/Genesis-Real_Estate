import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import MarketSnapshot from "./components/MarketSnapshot";

const API_URL = "http://127.0.0.1:8000/ask";
const EXPLAIN_URL = "http://127.0.0.1:8000/explain";
const FLIP_URL = "http://127.0.0.1:8000/flip";

function App() {
  const [query, setQuery] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [intent, setIntent] = useState(null);
  const [error, setError] = useState(null);
  const [lastQuery, setLastQuery] = useState("");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedFilters, setSelectedFilters] = useState({ city: null, type: null, intent: null });
  const [explanationModal, setExplanationModal] = useState({ open: false, loading: false, data: null, error: null, type: "why" });
  const [activeTab, setActiveTab] = useState("ai");

  const fetchExplanation = async (sourceRow) => {
    setExplanationModal({ open: true, loading: true, data: null, error: null, type: "why" });
    try {
      const res = await axios.post(EXPLAIN_URL, { source_row: sourceRow });
      if (res.data.success) {
        setExplanationModal({ open: true, loading: false, data: res.data, error: null, type: "why" });
      } else {
        setExplanationModal({ open: true, loading: false, data: null, error: res.data.error || "Failed to load explanation", type: "why" });
      }
    } catch (err) {
      setExplanationModal({ open: true, loading: false, data: null, error: err.message || "Network error", type: "why" });
    }
  };

  const fetchFlipExplanation = async (sourceRow) => {
    setExplanationModal({ open: true, loading: true, data: null, error: null, type: "flip" });
    try {
      const res = await axios.post(FLIP_URL, { source_row: sourceRow });
      if (res.data.success) {
        setExplanationModal({ open: true, loading: false, data: res.data, error: null, type: "flip" });
      } else {
        setExplanationModal({ open: true, loading: false, data: null, error: res.data.error || "Failed to load flip analysis", type: "flip" });
      }
    } catch (err) {
      setExplanationModal({ open: true, loading: false, data: null, error: err.message || "Network error", type: "flip" });
    }
  };

  const closeExplanationModal = () => {
    setExplanationModal({ open: false, loading: false, data: null, error: null, type: "why" });
  };

  const executeFilterSearch = async (filters) => {
    const parts = [];
    if (filters.intent?.value) parts.push(filters.intent.value);
    if (filters.type?.value) parts.push(filters.type.value);
    if (filters.city?.value) parts.push("properties in " + filters.city.value);
    const builtQuery = parts.join(" ");
    if (!builtQuery) return;
    setLoading(true);
    try {
      const res = await axios.post(API_URL, { query: builtQuery, page: 1 });
      const { answer, intent: backendIntent, total_results, page: resPage, has_more, show_filters, filters: resFilters, properties } = res.data;
      setIntent(backendIntent || null);
      setLastQuery(builtQuery);
      setCurrentPage(1);
      const assistantMsg = {
        role: "assistant",
        content: answer,
        pagination: total_results !== undefined ? { total_results, page: resPage, has_more } : null,
        show_filters,
        filters: resFilters,
        properties
      };
      setMessages((prev) => {
        const filtered = prev.filter(m => !m.show_filters);
        return [...filtered, assistantMsg];
      });
      setSelectedFilters({ city: null, type: null, intent: null });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterClick = (filterType, value, label) => {
    const newFilters = { ...selectedFilters, [filterType]: { value, label } };
    setSelectedFilters(newFilters);
    if (newFilters.city && newFilters.type && newFilters.intent) {
      executeFilterSearch(newFilters);
    }
  };

  const handleAsk = async (e, page = 1) => {
    e?.preventDefault();
    setError(null);
    setSelectedFilters({ city: null, type: null, intent: null });
    const trimmed = query.trim().toLowerCase();
    let queryToSend = query.trim();
    let pageToSend = page;
    const showMorePhrases = ["more", "show more", "more results", "more properties", "show me more", "next", "next page", "continue", "see more", "load more", "additional", "other options", "what else", "any more", "another", "other properties"];
    const isShowMore = showMorePhrases.some(phrase => trimmed === phrase || trimmed.includes(phrase)) || trimmed.startsWith("page ");
    if (isShowMore && lastQuery) {
      if (trimmed.startsWith("page ")) {
        const pageNum = parseInt(trimmed.replace("page ", ""));
        if (!isNaN(pageNum)) pageToSend = pageNum;
      } else {
        pageToSend = currentPage + 1;
      }
      queryToSend = lastQuery;
    } else if (!isShowMore) {
      setLastQuery(queryToSend);
      pageToSend = 1;
    }
    if (!queryToSend) return;
    const userMsg = { role: "user", content: query.trim() || ("Page " + pageToSend) };
    setMessages((prev) => [...prev, userMsg]);
    setQuery("");
    setLoading(true);
    try {
      const res = await axios.post(API_URL, { query: queryToSend, page: pageToSend });
      const { answer, intent: backendIntent, total_results, page: resPage, has_more, show_filters, filters, properties } = res.data;
      setIntent(backendIntent || null);
      setCurrentPage(resPage || 1);
      const assistantMsg = {
        role: "assistant",
        content: answer || "No answer returned from the RAG system.",
        pagination: total_results !== undefined ? { total_results, page: resPage, has_more } : null,
        show_filters,
        filters,
        properties
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err) {
      setError(err.response?.data?.detail || err.message || "Something went wrong calling the RAG API.");
      setMessages((prev) => [...prev, { role: "assistant", content: "Failed to fetch answer from backend." }]);
    } finally {
      setLoading(false);
    }
  };

  const PropertyCard = ({ property }) => {
    const isBuy = property.decision?.toLowerCase().includes("buy");
    const bedrooms = property.bedrooms?.toString().replace(".0", "") || "N/A";
    return (
      <div className="bg-slate-800/60 border border-slate-700/50 rounded-2xl p-5 hover:border-indigo-500/50 hover:shadow-xl hover:shadow-indigo-500/5 transition-all duration-300">
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-indigo-500/20 to-emerald-500/20 flex items-center justify-center">
              <span className="text-2xl"></span>
            </div>
            <div>
              <h3 className="font-semibold text-slate-100">{bedrooms} BHK Apartment</h3>
              <p className="text-sm text-slate-400">{property.location ? (property.location + ", " + property.city) : property.city}</p>
            </div>
          </div>
          <span className={"px-4 py-1.5 rounded-full text-xs font-semibold " + (isBuy ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30")}>
            {isBuy ? "Buy" : "Rent"}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-700/30">
            <p className="text-xs text-slate-500 mb-1">Price</p>
            <p className="text-sm font-bold text-indigo-400">{"Rs " + (property.price_lakhs?.toFixed(1) || "N/A") + " Lakhs"}</p>
          </div>
          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-700/30">
            <p className="text-xs text-slate-500 mb-1">Monthly Rent</p>
            <p className="text-sm font-bold text-slate-200">{"Rs " + (property.monthly_rent || "N/A")}</p>
          </div>
          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-700/30">
            <p className="text-xs text-slate-500 mb-1">Area</p>
            <p className="text-sm font-bold text-slate-200">{(property.area_sqft?.toFixed(0) || "N/A") + " sqft"}</p>
          </div>
          <div className="bg-slate-900/60 rounded-xl p-3 border border-slate-700/30">
            <p className="text-xs text-slate-500 mb-1">Wealth Diff</p>
            <p className={"text-sm font-bold " + (property.wealth_difference?.startsWith("-") ? "text-red-400" : "text-emerald-400")}>{"Rs " + (property.wealth_difference || "N/A")}</p>
          </div>
        </div>
        <div className={"text-xs px-4 py-2.5 rounded-xl font-medium " + (isBuy ? "bg-emerald-500/10 text-emerald-300 border border-emerald-500/20" : "bg-amber-500/10 text-amber-300 border border-amber-500/20")}>
          {isBuy ? "Buying is financially better for this property" : "Renting is more cost-effective here"}
        </div>
        {property.source_row !== undefined && (
          <div className="mt-4 grid grid-cols-2 gap-3">
            <button onClick={() => fetchExplanation(property.source_row)} className="py-2.5 px-4 rounded-xl bg-slate-700/50 hover:bg-indigo-500/20 border border-slate-600/50 hover:border-indigo-500/50 text-slate-300 hover:text-white text-sm font-medium transition-all flex items-center justify-center gap-2">
              <span>Why?</span>
            </button>
            <button onClick={() => fetchFlipExplanation(property.source_row)} className="py-2.5 px-4 rounded-xl bg-amber-700/20 hover:bg-amber-600/30 border border-amber-600/30 hover:border-amber-500/50 text-amber-300 hover:text-amber-200 text-sm font-medium transition-all flex items-center justify-center gap-2">
              <span>What would flip?</span>
            </button>
          </div>
        )}
      </div>
    );
  };

  const ExplanationModal = () => {
    if (!explanationModal.open) return null;
    const isFlipType = explanationModal.type === "flip";
    const title = isFlipType ? "What Would Flip This Decision?" : "Why This Decision?";
    return (
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={closeExplanationModal}>
        <div className="bg-slate-900 border border-slate-700 rounded-3xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl" onClick={(e) => e.stopPropagation()}>
          <div className={"flex items-center justify-between px-6 py-5 border-b border-slate-700 " + (isFlipType ? "bg-amber-900/20" : "bg-indigo-900/20")}>
            <h2 className="text-lg font-bold text-slate-100">{title}</h2>
            <button onClick={closeExplanationModal} className="text-slate-400 hover:text-white text-2xl">x</button>
          </div>
          <div className="px-6 py-5 overflow-y-auto max-h-[60vh]">
            {explanationModal.loading && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="h-10 w-10 rounded-full border-3 border-emerald-400 border-t-transparent animate-spin mb-4"></div>
                <p className="text-slate-400">Generating explanation...</p>
              </div>
            )}
            {explanationModal.error && <div className="text-red-400 bg-red-500/10 border border-red-500/30 rounded-xl px-4 py-3">{explanationModal.error}</div>}
            {explanationModal.data && (
              <div className="markdown-content">
                <ReactMarkdown>{explanationModal.data.explanation}</ReactMarkdown>
              </div>
            )}
          </div>
          <div className="px-6 py-4 border-t border-slate-700 bg-slate-800/30">
            <button onClick={closeExplanationModal} className="w-full py-3 rounded-xl bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold transition-colors">Close</button>
          </div>
        </div>
      </div>
    );
  };

  const PropertyCardsGrid = ({ properties }) => (
    <div className="grid grid-cols-1 gap-4 mt-4">
      {properties.map((prop, idx) => <PropertyCard key={idx} property={prop} />)}
    </div>
  );

  const FilterChips = ({ filters }) => (
    <div className="mt-4 space-y-4">
      <div>
        <p className="text-xs text-slate-400 mb-2">Select City</p>
        <div className="flex flex-wrap gap-2">
          {filters.cities?.map((city) => (
            <button key={city.value} onClick={() => handleFilterClick("city", city.value, city.label)} className={"px-4 py-2 rounded-xl text-sm font-medium transition-all " + (selectedFilters.city?.value === city.value ? "bg-indigo-500 text-white shadow-lg" : "bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700")}>{city.label}</button>
          ))}
        </div>
      </div>
      <div>
        <p className="text-xs text-slate-400 mb-2">Property Type</p>
        <div className="flex flex-wrap gap-2">
          {filters.property_types?.map((type) => (
            <button key={type.value} onClick={() => handleFilterClick("type", type.value, type.label)} className={"px-4 py-2 rounded-xl text-sm font-medium transition-all " + (selectedFilters.type?.value === type.value ? "bg-emerald-500 text-white shadow-lg" : "bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700")}>{type.label}</button>
          ))}
        </div>
      </div>
      <div>
        <p className="text-xs text-slate-400 mb-2">Looking to</p>
        <div className="flex flex-wrap gap-2">
          {filters.intent?.map((item) => (
            <button key={item.value} onClick={() => handleFilterClick("intent", item.value, item.label)} className={"px-4 py-2 rounded-xl text-sm font-medium transition-all " + (selectedFilters.intent?.value === item.value ? "bg-amber-500 text-white shadow-lg" : "bg-slate-800 text-slate-300 hover:bg-slate-700 border border-slate-700")}>{item.label}</button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-slate-100">
      <ExplanationModal />
      
      <nav className="sticky top-0 z-50 bg-slate-900/90 backdrop-blur-xl border-b border-slate-800/50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 via-emerald-500 to-amber-400 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <span className="text-xl"></span>
              </div>
              <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 via-emerald-400 to-amber-400 bg-clip-text text-transparent">Genesis</h1>
            </div>
            
            <div className="flex items-center gap-1 bg-slate-800/60 rounded-2xl p-1.5 border border-slate-700/50">
              <button onClick={() => setActiveTab("ai")} className={"px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 " + (activeTab === "ai" ? "bg-gradient-to-r from-indigo-500 to-emerald-500 text-white shadow-lg shadow-indigo-500/25" : "text-slate-400 hover:text-white hover:bg-slate-700/50")}>
                AI Analyser
              </button>
              <button onClick={() => setActiveTab("market")} className={"px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 " + (activeTab === "market" ? "bg-gradient-to-r from-amber-500 to-orange-500 text-white shadow-lg shadow-amber-500/25" : "text-slate-400 hover:text-white hover:bg-slate-700/50")}>
                Market Snapshots
              </button>
            </div>

            <div className="w-40 flex justify-end">
              {intent && activeTab === "ai" && (
                <div className="px-4 py-2 rounded-full text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 font-medium">
                  {intent}
                </div>
              )}
            </div>
          </div>
        </div>
      </nav>

      {activeTab === "market" ? (
        <div className="flex-1 overflow-auto">
          <MarketSnapshot />
        </div>
      ) : (
        <main className="flex-1 flex flex-col md:flex-row">
          <section className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center py-20">
                  <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-indigo-500/20 via-emerald-500/20 to-amber-500/20 flex items-center justify-center mb-6 border border-slate-700/50 shadow-2xl">
                    <span className="text-5xl"></span>
                  </div>
                  <h2 className="text-2xl font-bold text-slate-100 mb-3">Real Estate AI Assistant</h2>
                  <p className="text-slate-400 max-w-md mb-6">Ask anything about buy vs rent decisions, property investments, or financial analysis.</p>
                  <div className="bg-slate-800/60 px-6 py-4 rounded-2xl border border-slate-700/50">
                    <p className="text-xs text-slate-500 mb-2">Try asking:</p>
                    <p className="font-mono text-sm text-indigo-400">"Show me 3BHK properties in Mumbai"</p>
                  </div>
                </div>
              )}

              {messages.map((m, idx) => (
                <div key={idx} className={"flex " + (m.role === "user" ? "justify-end" : "justify-start")}>
                  <div className={"max-w-[90%] rounded-2xl px-6 py-5 " + (m.role === "user" ? "bg-gradient-to-br from-indigo-500 to-emerald-500 text-white" : "bg-slate-800/80 border border-slate-700/50")}>
                    {m.role === "user" ? (
                      <p className="text-sm">{m.content}</p>
                    ) : (
                      <div>
                        <div className="markdown-content text-sm">
                          <ReactMarkdown>{m.content}</ReactMarkdown>
                        </div>
                        {m.properties && m.properties.length > 0 && (
                          <div className="mt-6 pt-4 border-t border-slate-700">
                            <p className="text-sm text-slate-400 mb-4 font-medium">📊 {m.properties.length} properties found:</p>
                            <PropertyCardsGrid properties={m.properties} />
                          </div>
                        )}
                        {m.show_filters && m.filters && idx === messages.length - 1 && <FilterChips filters={m.filters} />}
                      </div>
                    )}
                  </div>
                </div>
              ))}

              {loading && (
                <div className="flex justify-start">
                  <div className="rounded-2xl px-5 py-4 bg-slate-800/80 border border-indigo-500/30 text-slate-300 flex items-center gap-3">
                    <span className="h-3 w-3 rounded-full bg-gradient-to-br from-emerald-400 to-indigo-400 animate-pulse"></span>
                    Thinking with RAG + Gemini...
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleAsk} className="border-t border-slate-800 px-6 py-4 flex gap-4 bg-slate-900/80 backdrop-blur-xl">
              <input type="text" className="flex-1 rounded-2xl bg-slate-800/80 border border-slate-700 px-5 py-3 text-sm outline-none focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20 transition-all placeholder:text-slate-500" placeholder="Ask about properties, ROI, or investment decisions..." value={query} onChange={(e) => setQuery(e.target.value)} />
              <button type="submit" disabled={loading} className="px-6 py-3 rounded-2xl bg-gradient-to-r from-indigo-500 to-emerald-500 hover:from-indigo-400 hover:to-emerald-400 disabled:opacity-50 text-white text-sm font-semibold shadow-lg shadow-indigo-500/20 transition-all">{loading ? "..." : "Ask"}</button>
            </form>

            {error && <div className="px-6 py-3 text-sm text-red-400 bg-red-500/10 border-t border-red-500/30">{error}</div>}
          </section>

          <aside className="hidden md:block w-72 border-l border-slate-800 bg-slate-900/50 px-5 py-6 space-y-5">
            <div>
              <h2 className="text-sm font-semibold text-slate-100 mb-2">How it works</h2>
              <ol className="list-decimal list-inside space-y-1 text-xs text-slate-400">
                <li>Query is classified</li>
                <li>Properties are fetched</li>
                <li>Semantic search refines</li>
                <li>Gemini explains logic</li>
              </ol>
            </div>
            <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/50">
              <h3 className="text-xs font-semibold text-slate-100 mb-2">Example questions</h3>
              <ul className="space-y-2 text-xs text-slate-400">
                <li>"3BHK in Bangalore"</li>
                <li>"Why is renting better?"</li>
                <li>"Compare Mumbai vs Surat"</li>
              </ul>
            </div>
          </aside>
        </main>
      )}
    </div>
  );
}

export default App;
