import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
  Smartphone, TrendingUp, AlertCircle, RefreshCw, Search, Filter, 
  ChevronRight, ArrowDownRight, ShieldCheck, Zap, Package
} from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

interface Variant {
  id: string;
  name: string;
  attributes: {
    storage?: string;
    condition?: string;
    color?: string;
    [key: string]: any;
  };
  price: number;
  currency: string;
  url: string;
  scraped_at: string;
  source_name: string;
}

interface Family {
  id: string;
  name: string;
  brand_name: string;
  category: string;
  released_at: string | null;
  variants: Variant[];
}

interface PriceHistory {
  price: number;
  currency: string;
  scraped_at: string;
}

const App: React.FC = () => {
  const [families, setFamilies] = useState<Family[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFamily, setSelectedFamily] = useState<Family | null>(null);
  const [selectedVariantId, setSelectedVariantId] = useState<string | null>(null);
  const [history, setHistory] = useState<PriceHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeBrand, setActiveBrand] = useState('All');
  const [activeCategory, setActiveCategory] = useState('All');
  const [sortBy, setSortBy] = useState<'newest' | 'price_low' | 'price_high'>('newest');

  useEffect(() => {
    fetchFamilies();
  }, []);

  const fetchFamilies = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/families`);
      setFamilies(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to reach the API server.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (variantId: string) => {
    try {
      setHistoryLoading(true);
      setSelectedVariantId(variantId);
      const response = await axios.get(`${API_BASE_URL}/api/products/${variantId}/history`);
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch price history', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const brands = useMemo(() => {
    const b = new Set<string>();
    families.forEach(f => b.add(f.brand_name));
    return ['All', ...Array.from(b).sort()];
  }, [families]);

  const categories = useMemo(() => {
    const c = new Set<string>();
    families.forEach(f => c.add(f.category));
    return ['All', ...Array.from(c).sort()];
  }, [families]);

  const filteredFamilies = useMemo(() => {
    let result = families.filter(f => {
      const matchesSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           f.brand_name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesBrand = activeBrand === 'All' || f.brand_name === activeBrand;
      const matchesCategory = activeCategory === 'All' || f.category === activeCategory;
      return matchesSearch && matchesBrand && matchesCategory;
    });

    // Apply Sorting
    return result.sort((a, b) => {
      if (sortBy === 'newest') {
        const dateA = a.released_at ? new Date(a.released_at).getTime() : 0;
        const dateB = b.released_at ? new Date(b.released_at).getTime() : 0;
        return dateB - dateA;
      }
      const minA = Math.min(...a.variants.map(v => v.price));
      const minB = Math.min(...b.variants.map(v => v.price));
      return sortBy === 'price_low' ? minA - minB : minB - minA;
    });
  }, [families, searchQuery, activeBrand, activeCategory, sortBy]);

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-SG', {
      day: '2-digit',
      month: 'short'
    });
  };

  const getPriceRange = (family: Family) => {
    const prices = family.variants.map(v => v.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    if (min === max) return `$${min.toLocaleString()}`;
    return `$${min.toLocaleString()} - $${max.toLocaleString()}`;
  };

  const groupVariantsByStorage = (variants: Variant[]) => {
    const grouped: Record<string, { new?: Variant[], used?: Variant[] }> = {};
    variants.forEach(v => {
      const storage = v.attributes.storage || 'Standard';
      if (!grouped[storage]) grouped[storage] = {};
      const condition = v.attributes.condition || 'new';
      if (condition === 'new') {
        if (!grouped[storage].new) grouped[storage].new = [];
        grouped[storage].new.push(v);
      } else {
        if (!grouped[storage].used) grouped[storage].used = [];
        grouped[storage].used.push(v);
      }
    });
    return Object.entries(grouped).sort((a, b) => {
      const parse = (s: string) => {
        const n = parseInt(s);
        if (s.includes('TB')) return n * 1024;
        return isNaN(n) ? 0 : n;
      };
      return parse(a[0]) - parse(b[0]);
    });
  };

  const VariantBox = ({ variants, type }: { variants?: Variant[], type: 'new' | 'used' }) => {
    const [localActiveIdx, setLocalActiveIdx] = useState(0);
    if (!variants || variants.length === 0) {
      return <div className="text-center py-2 text-[10px] text-slate-700 font-bold italic uppercase">{type === 'new' ? 'OOS' : 'None'}</div>;
    }

    const sorted = [...variants].sort((a, b) => a.price - b.price);
    const active = sorted[localActiveIdx] || sorted[0];
    const savings = type === 'used' && selectedFamily?.variants.find(v => v.attributes.storage === active.attributes.storage && v.attributes.condition === 'new');

    return (
      <div 
        className={`p-3 rounded-xl border transition-all relative group/box ${
          selectedVariantId === active.id 
          ? (type === 'new' ? 'bg-indigo-600/20 border-indigo-500 shadow-[0_0_15px_rgba(99,102,241,0.1)]' : 'bg-emerald-600/20 border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.1)]')
          : 'bg-slate-900/50 border-white/5 hover:border-white/10'
        }`}
        onClick={() => {
          setSelectedVariantId(active.id);
          fetchHistory(active.id);
        }}
      >
        <div className="flex flex-col space-y-2">
          {/* Main Price Clickthrough */}
          <a 
            href={active.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className="block hover:no-underline group/link"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <div className="text-sm font-black text-white group-hover/link:text-indigo-400 transition-colors">${active.price.toLocaleString()}</div>
                {savings && active.price < savings.price && (
                  <div className="text-[10px] text-emerald-400 font-bold flex items-center">
                    <ArrowDownRight className="h-3 w-3" />
                    {Math.round((1 - active.price / savings.price) * 100)}%
                  </div>
                )}
              </div>
              <div className="text-[7px] font-black bg-white/10 px-1.5 py-0.5 rounded text-slate-300 uppercase tracking-tighter group-hover/link:bg-indigo-500/20 group-hover/link:text-indigo-300 transition-all">
                {active.source_name}
              </div>
            </div>
          </a>

          {/* Other Sources Comparison */}
          {Array.from(new Set(variants.map(v => v.source_name))).length > 1 && (
            <div className="pt-1 border-t border-white/5 space-y-1">
              <div className="text-[7px] text-slate-500 font-bold uppercase tracking-widest text-center">Compare Sources</div>
              {Array.from(new Set(variants.map(v => v.source_name))).filter(s => s !== active.source_name).map(sourceName => {
                const lowest = variants.filter(v => v.source_name === sourceName).sort((a,b) => a.price - b.price)[0];
                return (
                  <a 
                    key={sourceName} 
                    href={lowest.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex justify-between items-center text-[9px] hover:bg-white/5 px-1 rounded transition-colors"
                    onClick={(e) => e.stopPropagation()}
                  >
                    <span className="text-slate-400 truncate max-w-[60px]">{sourceName}</span>
                    <span className="font-bold text-slate-200">${lowest.price.toLocaleString()}</span>
                  </a>
                );
              })}
            </div>
          )}
        </div>
        
        {variants.length > 1 && (
          <div className="flex flex-wrap gap-1 justify-center mt-2 pt-2 border-t border-white/5">
            {variants.map((v) => (
              <button
                key={v.id}
                title={`${v.source_name}: ${v.attributes.color || 'Default'}`}
                className={`w-2.5 h-2.5 rounded-full border border-white/20 transition-transform ${active.id === v.id ? 'scale-125 ring-1 ring-white/50' : 'opacity-40 hover:opacity-100'}`}
                style={{ 
                  backgroundColor: v.attributes.color?.toLowerCase().includes('blue') ? '#3b82f6' : 
                                   v.attributes.color?.toLowerCase().includes('green') ? '#10b981' : 
                                   v.attributes.color?.toLowerCase().includes('red') ? '#ef4444' :
                                   v.attributes.color?.toLowerCase().includes('gold') ? '#f59e0b' :
                                   v.attributes.color?.toLowerCase().includes('titanium') ? '#94a3b8' :
                                   v.attributes.color?.toLowerCase().includes('purple') ? '#8b5cf6' :
                                   v.attributes.color?.toLowerCase().includes('orange') ? '#f97316' :
                                   v.attributes.color?.toLowerCase().includes('pink') ? '#ec4899' :
                                   v.attributes.color?.toLowerCase().includes('silver') ? '#e2e8f0' :
                                   v.attributes.color?.toLowerCase().includes('black') ? '#000' :
                                   v.attributes.color?.toLowerCase().includes('white') ? '#fff' : '#6366f1'
                }}
                onClick={(e) => {
                  e.stopPropagation();
                  const newIdx = sorted.findIndex(sv => sv.id === v.id);
                  setLocalActiveIdx(newIdx);
                  setSelectedVariantId(v.id);
                  fetchHistory(v.id);
                }}
              />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen pb-20">
      <nav className="glass sticky top-0 z-50 border-b border-white/5 py-4 mb-8">
        <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 p-2 rounded-xl shadow-lg shadow-indigo-500/20">
              <Smartphone className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black tracking-tight text-white">SG MOBILE</h1>
              <p className="text-[10px] uppercase tracking-widest text-indigo-400 font-bold">Price Tracker</p>
            </div>
          </div>

          <div className="flex items-center space-x-4 flex-1 max-w-xl md:ml-12">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input 
                type="text"
                placeholder="Search models, brands..."
                className="w-full bg-slate-900/50 border border-white/10 rounded-full py-2 pl-10 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 transition-all"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <button 
              onClick={fetchFamilies}
              className="p-2 bg-slate-800 rounded-full hover:bg-slate-700 transition-colors"
            >
              <RefreshCw className={`h-5 w-5 ${loading ? 'animate-spin text-indigo-400' : 'text-slate-300'}`} />
            </button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 mb-8">
          <div className="flex items-center space-x-2 overflow-x-auto pb-2 md:pb-0 scrollbar-hide">
            <Filter className="h-4 w-4 text-slate-500 mr-2 flex-shrink-0" />
            {brands.map(brand => (
              <button
                key={brand}
                onClick={() => setActiveBrand(brand)}
                className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap transition-all ${
                  activeBrand === brand 
                  ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' 
                  : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                }`}
              >
                {brand}
              </button>
            ))}
          </div>

          <div className="flex items-center space-x-4">
            <select 
              value={activeCategory}
              onChange={(e) => setActiveCategory(e.target.value)}
              className="bg-slate-800 text-slate-300 text-xs font-bold px-4 py-2 rounded-xl border border-white/5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              <option value="All">All Categories</option>
              {categories.filter(c => c !== 'All').map(c => (
                <option key={c} value={c}>{c.toUpperCase()}</option>
              ))}
            </select>

            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-slate-800 text-slate-300 text-xs font-bold px-4 py-2 rounded-xl border border-white/5 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              <option value="newest">Newest First</option>
              <option value="price_low">Price: Low to High</option>
              <option value="price_high">Price: High to Low</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {[1,2,3,4,5,6,7,8].map(i => (
              <div key={i} className="h-64 bg-slate-800/50 rounded-3xl animate-pulse"></div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-500/10 border border-red-500/20 text-red-400 px-6 py-8 rounded-3xl text-center">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <h3 className="text-lg font-bold">Connection Error</h3>
            <p className="text-sm opacity-80">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredFamilies.map((family) => (
              <div 
                key={family.id}
                onClick={() => {
                  setSelectedFamily(family);
                  if (family.variants.length > 0) {
                    const first = family.variants[0];
                    setSelectedVariantId(first.id);
                    fetchHistory(first.id);
                  }
                }}
                className="glass card-glow rounded-3xl p-6 cursor-pointer group transition-all"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="flex flex-col space-y-1">
                    <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400 bg-indigo-400/10 px-2 py-1 rounded-md w-fit">
                      {family.brand_name}
                    </span>
                    <span className="text-[9px] font-bold text-slate-500 uppercase tracking-tighter">
                      {family.category} {family.released_at ? `• ${new Date(family.released_at).getFullYear()}` : ''}
                    </span>
                  </div>
                  {family.variants.some(v => v.attributes.condition === 'used') && (
                    <span className="text-[10px] font-black uppercase tracking-widest text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md">
                      Used Stock
                    </span>
                  )}
                </div>
                
                <h3 className="text-xl font-bold text-white mb-1 group-hover:text-indigo-400 transition-colors">
                  {family.name}
                </h3>
                
                <div className="mt-8 flex items-baseline space-x-1">
                  <span className="text-xs text-slate-500 font-bold">FROM</span>
                  <span className="text-2xl font-black text-white">
                    {getPriceRange(family)}
                  </span>
                </div>
                
                <div className="mt-6 flex items-center justify-between">
                  <div className="flex -space-x-2">
                    {Array.from(new Set(family.variants.map(v => v.attributes.storage))).filter(Boolean).sort().map((s, i) => (
                      <div key={i} className="h-6 w-auto px-2 rounded-md border border-white/5 bg-slate-800 flex items-center justify-center text-[8px] font-bold text-slate-400">
                        {s}
                      </div>
                    ))}
                  </div>
                  <ChevronRight className="h-5 w-5 text-slate-600 group-hover:text-white transition-all transform group-hover:translate-x-1" />
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {selectedFamily && (
        <div className="fixed inset-0 z-[60] flex items-center justify-center p-4">
          <div 
            className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm"
            onClick={() => setSelectedFamily(null)}
          ></div>
          
          <div className="relative glass w-full max-w-6xl max-h-[90vh] rounded-[2rem] overflow-hidden flex flex-col shadow-2xl">
            <div className="p-8 pb-4 flex justify-between items-start border-b border-white/5">
              <div>
                <div className="flex items-center space-x-3 mb-2">
                  <span className="text-[10px] font-black uppercase tracking-widest text-indigo-400 bg-indigo-400/10 px-2 py-1 rounded-md">
                    {selectedFamily.brand_name}
                  </span>
                  <div className="flex items-center text-slate-500 text-[10px] font-bold">
                    <Zap className="h-3 w-3 mr-1" />
                    {selectedFamily.variants.length} Variants Tracked
                  </div>
                </div>
                <h2 className="text-3xl font-black text-white">{selectedFamily.name}</h2>
              </div>
              <button 
                onClick={() => setSelectedFamily(null)}
                className="p-2 bg-slate-800 rounded-full text-slate-400 hover:text-white transition-colors"
              >
                <RefreshCw className="h-6 w-6 transform rotate-45" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto custom-scrollbar p-8 pt-4">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
                <div className="lg:col-span-7">
                  <h4 className="text-xs font-black uppercase tracking-widest text-slate-500 mb-6 flex items-center">
                    <Package className="h-4 w-4 mr-2" />
                    Market Comparison
                  </h4>
                  
                  <div className="space-y-4">
                    <div className="grid grid-cols-12 gap-4 px-4 text-[10px] font-black uppercase tracking-widest text-slate-600">
                      <div className="col-span-3">SPEC</div>
                      <div className="col-span-4 text-center">NEW CONDITION</div>
                      <div className="col-span-5 text-center">USED / REFURBISHED</div>
                    </div>

                    {groupVariantsByStorage(selectedFamily.variants).map(([storage, types]) => (
                      <div key={storage} className="grid grid-cols-12 gap-4 bg-white/5 rounded-2xl p-4 border border-white/5 items-center">
                        <div className="col-span-3 font-bold text-indigo-400">{storage}</div>
                        
                        <div className="col-span-4">
                          <VariantBox variants={types.new} type="new" />
                        </div>

                        <div className="col-span-5">
                          <VariantBox variants={types.used} type="used" />
                        </div>
                      </div>
                    ))}
                  </div>

                  <div className="mt-8 bg-slate-900/50 rounded-2xl p-6 border border-white/5">
                    <div className="flex items-center space-x-2 mb-4 text-emerald-400">
                      <ShieldCheck className="h-5 w-5" />
                      <span className="text-xs font-bold uppercase tracking-tight">Trust & Verification</span>
                    </div>
                    <p className="text-xs text-slate-400 leading-relaxed">
                      Prices are updated automatically via retailers. Used device pricing reflects Grade A/B conditions unless specified. Always verify the source URL before purchase.
                    </p>
                  </div>
                </div>

                <div className="lg:col-span-5">
                  <h4 className="text-xs font-black uppercase tracking-widest text-slate-500 mb-6 flex items-center">
                    <TrendingUp className="h-4 w-4 mr-2" />
                    Price Trend
                  </h4>

                  <div className="bg-slate-900/50 rounded-[2rem] p-6 border border-white/5 h-[400px]">
                    {historyLoading ? (
                      <div className="flex flex-col justify-center items-center h-full">
                        <RefreshCw className="h-8 w-8 animate-spin text-indigo-500 mb-4" />
                        <span className="text-[10px] font-bold text-slate-600 uppercase tracking-widest">Analyzing History...</span>
                      </div>
                    ) : history.length > 1 ? (
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={history}>
                          <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#ffffff05" />
                          <XAxis 
                            dataKey="scraped_at" 
                            tickFormatter={formatDate}
                            tick={{ fontSize: 9, fill: '#64748b' }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <YAxis 
                            tickFormatter={(value) => `$${value}`}
                            tick={{ fontSize: 9, fill: '#64748b' }}
                            axisLine={false}
                            tickLine={false}
                          />
                          <Tooltip 
                            contentStyle={{ 
                              backgroundColor: '#1e293b', 
                              border: 'none', 
                              borderRadius: '12px',
                              fontSize: '10px',
                              color: '#fff'
                            }}
                            itemStyle={{ color: '#818cf8', fontWeight: 'bold' }}
                            formatter={(value: any) => [`$${Number(value).toLocaleString()}`, 'Price']}
                            labelFormatter={(label: any) => `Scraped: ${new Date(label).toLocaleString()}`}
                          />
                          <Line 
                            type="monotone" 
                            dataKey="price" 
                            stroke="#6366f1" 
                            strokeWidth={3}
                            dot={{ r: 0 }}
                            activeDot={{ r: 6, fill: '#6366f1', stroke: '#fff', strokeWidth: 2 }}
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    ) : (
                      <div className="flex flex-col justify-center items-center h-full text-center">
                        <div className="bg-slate-800 p-4 rounded-full mb-4">
                          <TrendingUp className="h-8 w-8 text-slate-600" />
                        </div>
                        <p className="text-xs text-slate-500 font-bold uppercase tracking-widest">Insufficient Price Data</p>
                        <p className="text-[10px] text-slate-600 mt-2 max-w-[200px]">We need at least two data points to generate a trend chart.</p>
                      </div>
                    )}
                  </div>

                  <div className="mt-6 flex justify-between items-center text-[10px] font-bold">
                    <div className="flex items-center text-slate-500">
                      <RefreshCw className="h-3 w-3 mr-1" />
                      AUTO-REFRESH ACTIVE
                    </div>
                    <div className="text-indigo-400">
                      LIVE MARKET DATA
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
