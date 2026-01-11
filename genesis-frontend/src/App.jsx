import { useState } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import MarketSnapshot from "./components/MarketSnapshot";
import About from "./components/About";

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

  const PropertyCard = ({ property, index }) => {
    const isBuy = property.decision?.toLowerCase().includes("buy");
    const bedrooms = property.bedrooms?.toString().replace(".0", "") || "N/A";
    return (
      <div
        className="glass-card rounded-2xl p-5 hover:scale-[1.02] transition-all duration-300 animate-slide-up"
        style={{ animationDelay: `${index * 100}ms` }}
      >
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center bg-cyan-500/10 text-cyan-400">
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m3 9 9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" /><polyline points="9 22 9 12 15 12 15 22" /></svg>
            </div>
            <div>
              <h3 className="font-semibold text-white">{bedrooms} BHK Apartment</h3>
              <p className="text-sm text-slate-400">{property.location ? (property.location + ", " + property.city) : property.city}</p>
            </div>
          </div>
          <span className={"px-4 py-1.5 rounded-full text-xs font-semibold " + (isBuy ? "bg-[#00d4ff]/20 text-[#00d4ff] border border-[#00d4ff]/30" : "bg-amber-500/20 text-amber-400 border border-amber-500/30")}>
            {isBuy ? "Buy" : "Rent"}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-3 mb-4">
          <div className="rounded-xl p-3 border border-[#00d4ff]/10" style={{ background: 'rgba(0,212,255,0.05)' }}>
            <p className="text-xs text-slate-500 mb-1">Price</p>
            <p className="text-sm font-bold text-[#00d4ff]">{"₹" + (property.price_lakhs?.toFixed(1) || "N/A") + " L"}</p>
          </div>
          <div className="rounded-xl p-3 border border-slate-700/30" style={{ background: 'rgba(15,23,42,0.6)' }}>
            <p className="text-xs text-slate-500 mb-1">Monthly Rent</p>
            <p className="text-sm font-bold text-slate-200">{"₹" + (property.monthly_rent || "N/A")}</p>
          </div>
          <div className="rounded-xl p-3 border border-slate-700/30" style={{ background: 'rgba(15,23,42,0.6)' }}>
            <p className="text-xs text-slate-500 mb-1">Area</p>
            <p className="text-sm font-bold text-slate-200">{(property.area_sqft?.toFixed(0) || "N/A") + " sqft"}</p>
          </div>
          <div className="rounded-xl p-3 border border-slate-700/30" style={{ background: 'rgba(15,23,42,0.6)' }}>
            <p className="text-xs text-slate-500 mb-1">Wealth Diff</p>
            <p className={"text-sm font-bold " + (property.wealth_difference?.startsWith("-") ? "text-red-400" : "text-emerald-400")}>{"₹" + (property.wealth_difference || "N/A")}</p>
          </div>
        </div>
        <div className={"text-xs px-4 py-2.5 rounded-xl font-medium " + (isBuy ? "bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/20" : "bg-amber-500/10 text-amber-300 border border-amber-500/20")}>
          {isBuy ? "Buying is financially better for this property" : "Renting is more cost-effective here"}
        </div>
        {property.source_row !== undefined && (
          <div className="mt-4 grid grid-cols-2 gap-3">
            <button onClick={() => fetchExplanation(property.source_row)} className="py-2.5 px-4 rounded-xl border border-[#00d4ff]/30 text-[#00d4ff] hover:bg-[#00d4ff]/10 text-sm font-medium transition-all flex items-center justify-center gap-2 hover:scale-105">
              <span>Why?</span>
            </button>
            <button onClick={() => fetchFlipExplanation(property.source_row)} className="py-2.5 px-4 rounded-xl bg-amber-700/20 hover:bg-amber-600/30 border border-amber-600/30 hover:border-amber-500/50 text-amber-300 hover:text-amber-200 text-sm font-medium transition-all flex items-center justify-center gap-2 hover:scale-105">
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
      <div className="fixed inset-0 bg-black/80 backdrop-blur-sm flex items-center justify-center z-50 p-4 animate-fade-in" onClick={closeExplanationModal}>
        <div className="glass-card rounded-3xl max-w-2xl w-full max-h-[80vh] overflow-hidden shadow-2xl animate-slide-up" onClick={(e) => e.stopPropagation()}>
          <div className={"flex items-center justify-between px-6 py-5 border-b " + (isFlipType ? "border-amber-500/30 bg-amber-900/20" : "border-[#00d4ff]/30 bg-[#00d4ff]/10")}>
            <h2 className="text-lg font-bold text-white">{title}</h2>
            <button onClick={closeExplanationModal} className="text-slate-400 hover:text-white text-2xl transition-colors">✕</button>
          </div>
          <div className="px-6 py-5 overflow-y-auto max-h-[60vh]">
            {explanationModal.loading && (
              <div className="flex flex-col items-center justify-center py-12">
                <div className="h-10 w-10 rounded-full border-3 border-[#00d4ff] border-t-transparent animate-spin mb-4"></div>
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
          <div className="px-6 py-4 border-t border-slate-700/50 bg-slate-900/50">
            <button onClick={closeExplanationModal} className="w-full py-3 rounded-xl bg-[#00d4ff]/20 hover:bg-[#00d4ff]/30 text-[#00d4ff] text-sm font-semibold transition-all border border-[#00d4ff]/30">Close</button>
          </div>
        </div>
      </div>
    );
  };

  const PropertyCardsGrid = ({ properties }) => (
    <div className="grid grid-cols-1 gap-4 mt-4">
      {properties.map((prop, idx) => <PropertyCard key={idx} property={prop} index={idx} />)}
    </div>
  );

  const FilterChips = ({ filters }) => (
    <div className="mt-4 space-y-4 animate-slide-up">
      <div>
        <p className="text-xs text-slate-400 mb-2">Select City</p>
        <div className="flex flex-wrap gap-2">
          {filters.cities?.map((city) => (
            <button key={city.value} onClick={() => handleFilterClick("city", city.value, city.label)} className={"feature-chip " + (selectedFilters.city?.value === city.value ? "active" : "")}>{city.label}</button>
          ))}
        </div>
      </div>
      <div>
        <p className="text-xs text-slate-400 mb-2">Property Type</p>
        <div className="flex flex-wrap gap-2">
          {filters.property_types?.map((type) => (
            <button key={type.value} onClick={() => handleFilterClick("type", type.value, type.label)} className={"feature-chip " + (selectedFilters.type?.value === type.value ? "active" : "")}>{type.label}</button>
          ))}
        </div>
      </div>
      <div>
        <p className="text-xs text-slate-400 mb-2">Looking to</p>
        <div className="flex flex-wrap gap-2">
          {filters.intent?.map((item) => (
            <button key={item.value} onClick={() => handleFilterClick("intent", item.value, item.label)} className={"feature-chip " + (selectedFilters.intent?.value === item.value ? "active" : "")}>{item.label}</button>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen flex flex-col text-slate-100">
      <ExplanationModal />

      {/* Navigation */}
      <nav className="sticky top-0 z-50 backdrop-blur-xl border-b border-[#00d4ff]/10" style={{ background: 'rgba(10, 22, 40, 0.9)' }}>
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <img src="/logo.png" alt="EstateEngine Logo" className="h-12 w-auto object-contain rounded-lg animate-logo-reveal" />
              <div>
                <h1 className="text-xl font-bold text-[#0a1628] hidden">EstateEngine</h1>
              </div>
            </div>

            {/* Tab Buttons */}
            <div className="flex items-center gap-1 p-1.5 rounded-2xl border border-[#00d4ff]/20" style={{ background: 'rgba(0,212,255,0.05)' }}>
              <button onClick={() => setActiveTab("ai")} className={"px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 " + (activeTab === "ai" ? "bg-[#00d4ff] text-[#0a1628] shadow-lg" : "text-slate-400 hover:text-[#00d4ff] hover:bg-[#00d4ff]/10")}>
                AI Advisor
              </button>
              <button onClick={() => setActiveTab("market")} className={"px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 " + (activeTab === "market" ? "bg-[#00d4ff] text-[#0a1628] shadow-lg" : "text-slate-400 hover:text-[#00d4ff] hover:bg-[#00d4ff]/10")}>
                Market Insights
              </button>
              <button onClick={() => setActiveTab("about")} className={"px-6 py-2.5 rounded-xl text-sm font-semibold transition-all duration-300 flex items-center gap-2 " + (activeTab === "about" ? "bg-[#00d4ff] text-[#0a1628] shadow-lg" : "text-slate-400 hover:text-[#00d4ff] hover:bg-[#00d4ff]/10")}>
                About
              </button>
            </div>

            {/* Intent Badge */}
            <div className="w-40 flex justify-end">
              {intent && activeTab === "ai" && (
                <div className="px-4 py-2 rounded-full text-xs bg-[#00d4ff]/20 text-[#00d4ff] border border-[#00d4ff]/30 font-medium animate-fade-in">
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
      ) : activeTab === "about" ? (
        <div className="flex-1 overflow-auto">
          <About />
        </div>
      ) : (
        <main className="flex-1 flex flex-col md:flex-row">
          <section className="flex-1 flex flex-col">
            <div className="flex-1 overflow-y-auto px-6 py-6 space-y-4">
              {messages.length === 0 && (
                <div className="h-full flex flex-col items-center justify-center text-center py-20 animate-fade-in">
                  <div className="w-24 h-24 rounded-3xl flex items-center justify-center mb-6 border border-[#00d4ff]/20 shadow-2xl animate-float" style={{ background: 'linear-gradient(135deg, rgba(0,212,255,0.1) 0%, rgba(0,168,204,0.05) 100%)' }}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#00d4ff" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M3 21h18" /><path d="M5 21V7l8-4 8 4v14" /><path d="M9 10a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v11" /></svg>
                  </div>
                  <h2 className="text-3xl font-bold text-white mb-3">AI-Powered Real Estate</h2>
                  <h3 className="text-2xl font-bold text-[#00d4ff] mb-4">Investment Advisor</h3>
                  <p className="text-slate-400 max-w-lg mb-8">Leverage advanced AI to analyze market data, predict trends, and discover the perfect investment opportunities tailored to your goals.</p>

                  {/* Feature Chips */}
                  <div className="flex flex-wrap justify-center gap-4 mb-8">
                    <div className="feature-chip">
                      Smart Property Search
                    </div>
                    <div className="feature-chip">
                      Market Analysis
                    </div>
                  </div>

                  <div className="glass-card px-6 py-4 rounded-2xl">
                    <p className="text-xs text-slate-500 mb-2">Try asking:</p>
                    <p className="font-mono text-sm text-[#00d4ff]">"Show me 3BHK properties in Mumbai"</p>
                  </div>
                </div>
              )}

              {messages.map((m, idx) => (
                <div key={idx} className={"flex animate-slide-up " + (m.role === "user" ? "justify-end" : "justify-start")}>
                  <div className={"max-w-[90%] rounded-2xl px-6 py-5 " + (m.role === "user" ? "text-white" : "glass-card")} style={m.role === "user" ? { background: 'linear-gradient(135deg, #00d4ff 0%, #00a8cc 100%)' } : {}}>
                    {m.role === "user" ? (
                      <p className="text-sm font-medium">{m.content}</p>
                    ) : (
                      <div>
                        <div className="markdown-content text-sm">
                          <ReactMarkdown>{m.content}</ReactMarkdown>
                        </div>
                        {m.properties && m.properties.length > 0 && (
                          <div className="mt-6 pt-4 border-t border-[#00d4ff]/20">
                            <p className="text-sm text-slate-400 mb-4 font-medium">{m.properties.length} properties found:</p>
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
                <div className="flex justify-start animate-fade-in">
                  <div className="glass-card rounded-2xl px-5 py-4 border-[#00d4ff]/30 text-slate-300 flex items-center gap-3">
                    <span className="h-3 w-3 rounded-full bg-[#00d4ff] animate-pulse"></span>
                    Analyzing with AI...
                  </div>
                </div>
              )}
            </div>

            {/* Input Form */}
            <form onSubmit={handleAsk} className="border-t border-[#00d4ff]/10 px-6 py-4 flex gap-4 backdrop-blur-xl" style={{ background: 'rgba(10, 22, 40, 0.9)' }}>
              <input
                type="text"
                className="flex-1 rounded-2xl px-5 py-3 text-sm outline-none transition-all placeholder:text-slate-500 border border-[#00d4ff]/20 focus:border-[#00d4ff] focus:ring-2 focus:ring-[#00d4ff]/20"
                style={{ background: 'rgba(0,212,255,0.05)' }}
                placeholder="Ask about properties, ROI, or investment decisions..."
                value={query}
                onChange={(e) => setQuery(e.target.value)}
              />
              <button
                type="submit"
                disabled={loading}
                className="btn-cyan disabled:opacity-50 disabled:transform-none"
              >
                {loading ? "..." : "Ask →"}
              </button>
            </form>

            {error && <div className="px-6 py-3 text-sm text-red-400 bg-red-500/10 border-t border-red-500/30">{error}</div>}
          </section>


        </main>
      )}
    </div>
  );
}

export default App;
