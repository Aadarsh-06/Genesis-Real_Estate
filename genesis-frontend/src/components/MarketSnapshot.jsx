import { useEffect, useState, useCallback } from "react";
import { Pie, Bar } from "react-chartjs-2";
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
} from "chart.js";

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

const BASE_URL = "http://127.0.0.1:8000";

export default function MarketSnapshot() {
  const [data, setData] = useState(null);
  const [filterOptions, setFilterOptions] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [insufficientData, setInsufficientData] = useState(false);

  // Filter states
  const [selectedBhk, setSelectedBhk] = useState([]);
  const [priceRange, setPriceRange] = useState([0, 1000]);
  const [areaRange, setAreaRange] = useState([0, 5000]);
  const [selectedLocalities, setSelectedLocalities] = useState([]);
  const [selectedCity, setSelectedCity] = useState("all");

  // Fetch filter options on mount
  useEffect(() => {
    fetch(`${BASE_URL}/market_filters`)
      .then((res) => res.json())
      .then((d) => {
        setFilterOptions(d);
        setPriceRange([d.price_range.min, d.price_range.max]);
        setAreaRange([d.area_range.min, d.area_range.max]);
      })
      .catch((e) => console.error("Failed to load filters:", e));
  }, []);

  // Fetch snapshot data with filters
  const fetchData = useCallback(() => {
    setLoading(true);
    setInsufficientData(false);
    
    const params = new URLSearchParams();
    if (selectedBhk.length > 0) params.append("bhk", selectedBhk.join(","));
    if (priceRange[0] > 0 || (filterOptions && priceRange[1] < filterOptions.price_range.max)) {
      if (priceRange[0] > 0) params.append("min_price", priceRange[0]);
      if (filterOptions && priceRange[1] < filterOptions.price_range.max) params.append("max_price", priceRange[1]);
    }
    if (areaRange[0] > 0 || (filterOptions && areaRange[1] < filterOptions.area_range.max)) {
      if (areaRange[0] > 0) params.append("min_area", areaRange[0]);
      if (filterOptions && areaRange[1] < filterOptions.area_range.max) params.append("max_area", areaRange[1]);
    }
    if (selectedLocalities.length > 0) params.append("localities", selectedLocalities.join(","));

    const url = `${BASE_URL}/market_snapshot${params.toString() ? "?" + params.toString() : ""}`;
    
    fetch(url)
      .then((res) => res.json())
      .then((d) => {
        if (d.error === "insufficient_data") {
          setInsufficientData(true);
          setData(null);
        } else {
          setData(d);
        }
        setLoading(false);
      })
      .catch((e) => {
        setError(e.message);
        setLoading(false);
      });
  }, [selectedBhk, priceRange, areaRange, selectedLocalities, filterOptions]);

  // Initial fetch and refetch on filter change
  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const resetFilters = () => {
    setSelectedBhk([]);
    if (filterOptions) {
      setPriceRange([filterOptions.price_range.min, filterOptions.price_range.max]);
      setAreaRange([filterOptions.area_range.min, filterOptions.area_range.max]);
    }
    setSelectedLocalities([]);
    setSelectedCity("all");
  };

  const toggleBhk = (bhk) => {
    setSelectedBhk((prev) =>
      prev.includes(bhk) ? prev.filter((b) => b !== bhk) : [...prev, bhk]
    );
  };

  const toggleLocality = (loc) => {
    setSelectedLocalities((prev) =>
      prev.includes(loc) ? prev.filter((l) => l !== loc) : [...prev, loc]
    );
  };

  const getLocalitiesForCity = () => {
    if (!filterOptions) return [];
    if (selectedCity === "all") {
      return [...(filterOptions.localities.Bangalore || []), ...(filterOptions.localities.Mumbai || [])].slice(0, 20);
    }
    return (filterOptions.localities[selectedCity] || []).slice(0, 20);
  };

  // Filter section component
  const FiltersSection = () => (
    <div className="bg-slate-900/80 rounded-2xl p-5 mb-6 border border-slate-800">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-semibold text-slate-200 flex items-center gap-2">
          <span>🎛️</span> Filters
          <span className="text-xs text-slate-500 font-normal ml-2">Charts update based on selected filters</span>
        </h3>
        <button
          onClick={resetFilters}
          className="text-xs px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition-colors border border-slate-700"
        >
          ↺ Reset Filters
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* BHK Filter */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">🏠 BHK Type</label>
          <div className="flex flex-wrap gap-2">
            {filterOptions?.bhk_options?.map((bhk) => (
              <button
                key={bhk}
                onClick={() => toggleBhk(bhk)}
                className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  selectedBhk.includes(bhk)
                    ? "bg-indigo-500 text-white"
                    : "bg-slate-800 text-slate-400 hover:bg-slate-700 border border-slate-700"
                }`}
              >
                {bhk} BHK
              </button>
            ))}
          </div>
          {selectedBhk.length === 0 && <p className="text-xs text-slate-600 mt-1">All selected</p>}
        </div>

        {/* Budget Range */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">💰 Budget (₹ Lakhs)</label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={priceRange[0]}
              onChange={(e) => setPriceRange([Number(e.target.value), priceRange[1]])}
              className="w-20 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-xs"
              placeholder="Min"
            />
            <span className="text-slate-600">-</span>
            <input
              type="number"
              value={priceRange[1]}
              onChange={(e) => setPriceRange([priceRange[0], Number(e.target.value)])}
              className="w-20 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-xs"
              placeholder="Max"
            />
          </div>
        </div>

        {/* Area Range */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">📐 Area (sqft)</label>
          <div className="flex items-center gap-2">
            <input
              type="number"
              value={areaRange[0]}
              onChange={(e) => setAreaRange([Number(e.target.value), areaRange[1]])}
              className="w-20 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-xs"
              placeholder="Min"
            />
            <span className="text-slate-600">-</span>
            <input
              type="number"
              value={areaRange[1]}
              onChange={(e) => setAreaRange([areaRange[0], Number(e.target.value)])}
              className="w-20 px-2 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-xs"
              placeholder="Max"
            />
          </div>
        </div>

        {/* City Selector for Localities */}
        <div>
          <label className="text-xs text-slate-400 mb-2 block">📍 City</label>
          <select
            value={selectedCity}
            onChange={(e) => {
              setSelectedCity(e.target.value);
              setSelectedLocalities([]);
            }}
            className="w-full px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-slate-200 text-xs"
          >
            <option value="all">All Cities</option>
            <option value="Bangalore">Bangalore</option>
            <option value="Mumbai">Mumbai</option>
          </select>
        </div>
      </div>

      {/* Locality Filter */}
      <div className="mt-4">
        <label className="text-xs text-slate-400 mb-2 block">🏘️ Localities {selectedLocalities.length > 0 && `(${selectedLocalities.length} selected)`}</label>
        <div className="flex flex-wrap gap-1.5 max-h-20 overflow-y-auto">
          {getLocalitiesForCity().map((loc) => (
            <button
              key={loc}
              onClick={() => toggleLocality(loc)}
              className={`px-2 py-1 rounded text-xs transition-all ${
                selectedLocalities.includes(loc)
                  ? "bg-emerald-500 text-white"
                  : "bg-slate-800 text-slate-500 hover:bg-slate-700 hover:text-slate-300"
              }`}
            >
              {loc}
            </button>
          ))}
        </div>
        {selectedLocalities.length === 0 && <p className="text-xs text-slate-600 mt-1">All localities</p>}
      </div>

      {/* Active Filters Summary */}
      {(selectedBhk.length > 0 || selectedLocalities.length > 0 || 
        (filterOptions && (priceRange[0] > filterOptions.price_range.min || priceRange[1] < filterOptions.price_range.max)) ||
        (filterOptions && (areaRange[0] > filterOptions.area_range.min || areaRange[1] < filterOptions.area_range.max))) && (
        <div className="mt-4 pt-3 border-t border-slate-800">
          <p className="text-xs text-emerald-400">
            ✓ Filters active — showing {data?.total_filtered || 0} properties
          </p>
        </div>
      )}
    </div>
  );

  if (error) return <div className="py-8 text-rose-400 text-center">Failed to load market snapshot.</div>;

  // Chart configurations
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        position: "bottom",
        labels: { color: "#94a3b8", font: { size: 11 } }
      }
    }
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: { legend: { display: false } },
    scales: {
      y: { 
        beginAtZero: true,
        ticks: { color: "#64748b" },
        grid: { color: "#1e293b" }
      },
      x: {
        ticks: { color: "#94a3b8" },
        grid: { display: false }
      }
    }
  };

  return (
    <section className="w-full max-w-6xl mx-auto py-6 px-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 via-emerald-400 to-amber-400 bg-clip-text text-transparent">
          📊 Market Snapshot
        </h2>
        {loading && <span className="text-xs text-slate-500 animate-pulse">Updating...</span>}
      </div>

      <FiltersSection />

      {insufficientData ? (
        <div className="bg-amber-900/20 border border-amber-700/50 rounded-2xl p-8 text-center">
          <span className="text-4xl mb-4 block">⚠️</span>
          <h3 className="text-lg font-semibold text-amber-400 mb-2">Not Enough Data</h3>
          <p className="text-slate-400 text-sm mb-4">The selected filters return too few properties for meaningful analysis.</p>
          <button
            onClick={resetFilters}
            className="px-4 py-2 rounded-xl bg-amber-600 hover:bg-amber-500 text-white text-sm font-medium transition-colors"
          >
            Reset Filters
          </button>
        </div>
      ) : loading && !data ? (
        <div className="py-12 text-center text-slate-400">
          <div className="h-8 w-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin mx-auto mb-3"></div>
          Loading market data...
        </div>
      ) : data ? (
        <>
          {/* Charts Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            {/* Bangalore Pie */}
            <div className="bg-slate-900/60 rounded-2xl p-5 border border-slate-800">
              <h3 className="text-sm font-semibold text-slate-300 mb-3 text-center">🏙️ Bangalore</h3>
              <div className="h-48">
                <Pie
                  data={{
                    labels: ["Buy", "Rent"],
                    datasets: [{
                      data: [data.buy_rent_distribution.Bangalore?.buy || 0, data.buy_rent_distribution.Bangalore?.rent || 0],
                      backgroundColor: ["#34d399", "#fbbf24"],
                      borderColor: ["#059669", "#b45309"],
                      borderWidth: 2,
                    }],
                  }}
                  options={chartOptions}
                />
              </div>
              <p className="text-xs text-slate-500 mt-3 text-center">
                {data.buy_rent_distribution.Bangalore?.total || 0} properties analyzed
              </p>
            </div>

            {/* Mumbai Pie */}
            <div className="bg-slate-900/60 rounded-2xl p-5 border border-slate-800">
              <h3 className="text-sm font-semibold text-slate-300 mb-3 text-center">🏙️ Mumbai</h3>
              <div className="h-48">
                <Pie
                  data={{
                    labels: ["Buy", "Rent"],
                    datasets: [{
                      data: [data.buy_rent_distribution.Mumbai?.buy || 0, data.buy_rent_distribution.Mumbai?.rent || 0],
                      backgroundColor: ["#34d399", "#fbbf24"],
                      borderColor: ["#059669", "#b45309"],
                      borderWidth: 2,
                    }],
                  }}
                  options={chartOptions}
                />
              </div>
              <p className="text-xs text-slate-500 mt-3 text-center">
                {data.buy_rent_distribution.Mumbai?.total || 0} properties analyzed
              </p>
            </div>

            {/* Median Price Bar */}
            <div className="bg-slate-900/60 rounded-2xl p-5 border border-slate-800">
              <h3 className="text-sm font-semibold text-slate-300 mb-3 text-center">💰 Median ₹/sqft</h3>
              <div className="h-48">
                <Bar
                  data={{
                    labels: ["Bangalore", "Mumbai"],
                    datasets: [{
                      label: "₹ per sqft",
                      data: [data.median_price_per_sqft.Bangalore || 0, data.median_price_per_sqft.Mumbai || 0],
                      backgroundColor: ["#6366f1", "#f59e42"],
                      borderRadius: 6,
                    }],
                  }}
                  options={barOptions}
                />
              </div>
              <p className="text-xs text-slate-500 mt-3 text-center">
                Median price per square foot
              </p>
            </div>
          </div>

          {/* Break-Even Chart */}
          <div className="bg-slate-900/60 rounded-2xl p-5 border border-slate-800">
            <h3 className="text-sm font-semibold text-slate-300 mb-3">📅 Average Break-Even Period (Years)</h3>
            <div className="h-48">
              <Bar
                data={{
                  labels: ["Bangalore", "Mumbai"],
                  datasets: [{
                    label: "Years",
                    data: [data.avg_break_even_year.Bangalore || 0, data.avg_break_even_year.Mumbai || 0],
                    backgroundColor: ["#10b981", "#fbbf24"],
                    borderRadius: 6,
                  }],
                }}
                options={barOptions}
              />
            </div>
            <p className="text-xs text-slate-500 mt-3 text-center">
              Lower is better — indicates how quickly buying becomes more favorable than renting.
            </p>
          </div>

          {/* Insight Summary */}
          <div className="mt-6 bg-indigo-900/20 border border-indigo-700/30 rounded-xl p-4">
            <p className="text-sm text-indigo-300">
              💡 <strong>Insight:</strong> Based on {data.total_filtered || 0} filtered properties, 
              {data.buy_rent_distribution.Bangalore?.buy > data.buy_rent_distribution.Mumbai?.buy
                ? " Bangalore shows a stronger preference for buying over renting compared to Mumbai."
                : " Mumbai shows more balanced buy vs rent decisions compared to Bangalore."}
            </p>
          </div>
        </>
      ) : null}
    </section>
  );
}
