import React, { useState, useEffect, useMemo } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { 
  Smartphone, TrendingUp, AlertCircle, RefreshCw, Search, Filter, 
  ArrowDownRight, ShieldCheck, Zap, Package,
  ShoppingBag, Flame, ExternalLink, ArrowRight, Info,
  Sun, Moon
} from 'lucide-react';
import './App.css';

const API_BASE_URL = window.location.hostname === 'localhost' ? 'http://localhost:8000' : '';

interface Variant {
  id: string;
  name: string;
  attributes: {
    storage?: string;
    condition?: string;
    color?: string;
    promo?: string;
    [key: string]: any;
  };
  price: number;
  currency: string;
  url: string;
  scraped_at: string;
  source_name: string;
}

interface TopDeal {
  variant_id: string;
  variant_name: string;
  family_name: string;
  brand_name: string;
  image_url?: string;
  old_price: number;
  new_price: number;
  drop_pct: number;
  url: string;
  source_name: string;
}

interface Family {
  id: string;
  name: string;
  brand_name: string;
  category: string;
  released_at: string | null;
  image_url?: string;
  variants: Variant[];
}

interface PriceHistory {
  price: number;
  currency: string;
  scraped_at: string;
}

const App: React.FC = () => {
  const [families, setFamilies] = useState<Family[]>([]);
  const [topDeals, setTopDeals] = useState<TopDeal[]>([]);
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
  
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    if (typeof window !== 'undefined') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }
    return 'dark';
  });

  useEffect(() => {
    fetchFamilies();
    fetchTopDeals();
  }, []);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  const toggleTheme = () => setTheme(prev => prev === 'light' ? 'dark' : 'light');

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

  const fetchTopDeals = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/alerts/top`);
      setTopDeals(response.data);
    } catch (err) {
      console.error('Failed to fetch top deals', err);
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

  const filteredFamilies = useMemo(() => {
    let result = families.filter(f => {
      const matchesSearch = f.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                           f.brand_name.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesBrand = activeBrand === 'All' || f.brand_name === activeBrand;
      const matchesCategory = activeCategory === 'All' || f.category.toLowerCase() === activeCategory.toLowerCase();
      return matchesSearch && matchesBrand && matchesCategory;
    });

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

  const ProductImage = ({ brand, image_url, className = "" }: { brand: string, image_url?: string, name?: string, className?: string }) => {
    const getPlaceholder = () => {
      const b = brand.toLowerCase();
      if (b.includes('apple')) return <div className="text-theme-secondary font-bold"></div>;
      if (b.includes('samsung')) return <div className="text-blue-500 font-black tracking-tighter text-[10px]">SAMSUNG</div>;
      if (b.includes('google')) return <div className="text-red-500 font-black text-xl">G</div>;
      return <Smartphone className="text-theme-secondary h-8 w-8 opacity-40" />;
    };

    return (
      <div className={`img-placeholder rounded-2xl overflow-hidden ${className}`}>
        {image_url ? (
          <img 
            src={image_url} 
            alt={brand} 
            className="w-full h-full object-contain p-2 hover:scale-110 transition-transform duration-500"
            onError={(e) => {
              (e.target as HTMLImageElement).style.display = 'none';
              (e.target as HTMLImageElement).parentElement!.innerHTML = '<div class="text-theme-secondary font-bold opacity-20 text-[8px]">NO IMG</div>';
            }}
          />
        ) : (
          getPlaceholder()
        )}
      </div>
    );
  };

  const TopDeals = () => {
    if (topDeals.length === 0) return null;
    return (
      <div className="mb-12 animate-fade-in">
        <div className="flex items-center space-x-2 mb-6">
          <div className="bg-red-500/20 p-1.5 rounded-lg">
            <Flame className="h-5 w-5 text-red-500" />
          </div>
          <h2 className="text-xl font-black text-theme-primary uppercase tracking-tight">Today's Biggest Drops</h2>
        </div>
        <div className="flex space-x-4 overflow-x-auto pb-4 custom-scrollbar-none">
          {topDeals.map((deal, idx) => (
            <a 
              key={idx}
              href={deal.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-none w-[280px] glass rounded-3xl p-5 card-hover group/deal border-theme-border"
            >
              <div className="flex justify-between items-start mb-4">
                <div className="deal-badge px-2 py-1 rounded-lg text-[10px] font-black text-white">-{Math.round(deal.drop_pct)}% OFF</div>
                <div className="text-[10px] font-bold text-theme-secondary uppercase">{deal.source_name}</div>
              </div>
              <div className="flex space-x-4">
                <ProductImage brand={deal.brand_name} image_url={deal.image_url} className="h-16 w-16 text-lg" />
                <div className="flex-1 min-w-0">
                  <div className="text-[10px] font-bold text-theme-secondary truncate mb-1">{deal.brand_name}</div>
                  <div className="text-sm font-black text-theme-primary truncate leading-tight mb-2 group-hover/deal:text-theme-accent transition-colors">{deal.variant_name}</div>
                  <div className="flex items-baseline space-x-2">
                    <div className="text-lg font-black text-theme-primary">${deal.new_price.toLocaleString()}</div>
                    <div className="text-xs text-theme-secondary line-through">${deal.old_price.toLocaleString()}</div>
                  </div>
                </div>
              </div>
            </a>
          ))}
        </div>
      </div>
    );
  };

  const VariantBox = ({ variants, type }: { variants?: Variant[], type: 'new' | 'used' }) => {
    const [localActiveIdx, setLocalActiveIdx] = useState(0);
    if (!variants || variants.length === 0) {
      return <div className="text-center py-4 text-[10px] text-theme-secondary font-bold italic uppercase tracking-widest bg-theme-base/30 rounded-xl border border-theme-border">{type === 'new' ? 'Out of Stock' : 'None Available'}</div>;
    }

    const sorted = [...variants].sort((a, b) => a.price - b.price);
    const active = sorted[localActiveIdx] || sorted[0];
    const savings = type === 'used' && selectedFamily?.variants.find(v => v.attributes.storage === active.attributes.storage && v.attributes.condition === 'new');

    return (
      <div 
        className={`p-4 rounded-2xl border transition-all relative group/box overflow-hidden ${
          selectedVariantId === active.id 
          ? (type === 'new' ? 'bg-theme-accent/10 border-theme-accent/50 shadow-xl' : 'bg-success/10 border-success/50 shadow-xl')
          : 'bg-theme-base/40 border-theme-border hover:border-theme-accent/30'
        }`}
        onClick={() => {
          setSelectedVariantId(active.id);
          fetchHistory(active.id);
        }}
      >
        <div className="flex flex-col space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex flex-col">
              <div className="flex items-baseline space-x-2">
                <div className="text-xl font-black text-theme-primary tracking-tighter">${active.price.toLocaleString()}</div>
                {savings && active.price < savings.price && (
                  <div className="text-[10px] bg-success/20 text-success px-1.5 py-0.5 rounded-full font-black flex items-center">
                    <ArrowDownRight className="h-3 w-3 mr-0.5" />
                    SAVE {Math.round((1 - active.price / savings.price) * 100)}%
                  </div>
                )}
              </div>
              <div className="text-[9px] font-bold text-theme-secondary uppercase tracking-widest mt-1">Best from {active.source_name}</div>
            </div>
            {active.attributes.promo && (
              <div className="bg-theme-accent/20 text-theme-accent p-1.5 rounded-lg group-hover/box:bg-theme-accent group-hover/box:text-white transition-all cursor-help" title={active.attributes.promo}>
                <Zap className="h-4 w-4" />
              </div>
            )}
          </div>

          <a 
            href={active.url} 
            target="_blank" 
            rel="noopener noreferrer"
            className={`cta-button flex items-center justify-center space-x-2 py-2.5 rounded-xl text-[11px] font-black uppercase tracking-widest text-white no-underline shadow-lg shadow-black/20`}
            onClick={(e) => e.stopPropagation()}
          >
            <ShoppingBag className="h-3.5 w-3.5" />
            <span>Buy at {active.source_name.split(' ')[0]}</span>
            <ExternalLink className="h-3 w-3 opacity-50" />
          </a>

          {Array.from(new Set(variants.map(v => v.source_name))).length > 1 && (
            <div className="pt-3 border-t border-theme-border space-y-2">
              <div className="text-[8px] text-theme-secondary font-black uppercase tracking-[0.2em] text-center">Market Comparison</div>
              <div className="grid grid-cols-1 gap-1.5">
                {Array.from(new Set(variants.map(v => v.source_name))).filter(s => s !== active.source_name).map(sourceName => {
                  const lowest = variants.filter(v => v.source_name === sourceName).sort((a,b) => a.price - b.price)[0];
                  return (
                    <a 
                      key={sourceName} 
                      href={lowest.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex justify-between items-center text-[10px] bg-theme-primary/[0.03] hover:bg-theme-primary/[0.08] px-2 py-1.5 rounded-lg transition-colors border border-transparent hover:border-theme-border"
                      onClick={(e) => e.stopPropagation()}
                    >
                      <span className="text-theme-secondary font-bold truncate max-w-[80px]">{sourceName}</span>
                      <span className="font-black text-theme-primary">${lowest.price.toLocaleString()}</span>
                    </a>
                  );
                })}
              </div>
            </div>
          )}

          {variants.length > 1 && (
            <div className="flex flex-wrap gap-1 justify-center mt-2 pt-2 border-t border-theme-border">
              {variants.map((v) => (
                <button
                  key={v.id}
                  title={`${v.attributes.color || 'Default'} - $${v.price}`}
                  className={`w-4 h-4 rounded-full border-2 transition-all transform hover:scale-125 ${
                    selectedVariantId === v.id ? 'border-theme-primary scale-110 shadow-lg' : 'border-transparent opacity-60'
                  }`}
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
      </div>
    );
  };

  return (
    <div className="min-h-screen pb-20">
      <header className="sticky top-0 z-50 glass border-b border-theme-border py-4 px-6 mb-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center space-x-3">
            <div className="bg-theme-accent p-2 rounded-xl shadow-lg">
              <TrendingUp className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-black text-theme-primary uppercase tracking-tighter leading-none">SG Mobile</h1>
              <p className="text-[10px] font-bold text-theme-secondary uppercase tracking-widest mt-1">Price Tracker</p>
            </div>
          </div>

          <div className="flex flex-1 max-w-xl relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 h-4 w-4 text-theme-secondary" />
            <input 
              type="text"
              placeholder="Search by model or brand..."
              className="w-full bg-theme-base/50 border border-theme-border rounded-2xl py-2.5 pl-11 pr-4 text-sm text-theme-primary focus:outline-none focus:border-theme-accent focus:ring-1 focus:ring-theme-accent transition-all"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <div className="flex items-center space-x-2">
            <div className="flex p-1 bg-theme-base/80 rounded-xl border border-theme-border shadow-sm">
              {['All', 'Phone', 'Watch', 'Tablet', 'Accessory'].map(cat => (
                <button
                  key={cat}
                  onClick={() => setActiveCategory(cat)}
                  className={`px-3 py-1.5 rounded-lg text-[10px] font-black uppercase tracking-tight transition-all ${
                    activeCategory.toLowerCase() === cat.toLowerCase() ? 'bg-theme-accent text-white shadow-lg' : 'text-theme-secondary hover:text-theme-primary'
                  }`}
                >
                  {cat}
                </button>
              ))}
            </div>
            
            <button 
              onClick={toggleTheme}
              className="flex items-center space-x-2 px-3 py-2 bg-theme-accent text-white rounded-xl shadow-lg hover:scale-105 transition-all"
              title="Toggle Light/Dark Mode"
            >
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
              <span className="text-[10px] font-black uppercase tracking-widest hidden lg:block">Theme</span>
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6">
        <TopDeals />

        <div className="flex items-center justify-between mb-8">
          <div className="flex items-center space-x-6 overflow-x-auto custom-scrollbar-none pb-2 md:pb-0">
            <div className="flex items-center space-x-2">
              <Filter className="h-4 w-4 text-theme-accent mr-2" />
              <div className="flex space-x-2">
                {brands.map(brand => (
                  <button
                    key={brand}
                    onClick={() => setActiveBrand(brand)}
                    className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest border transition-all ${
                      activeBrand === brand 
                      ? 'bg-theme-primary text-theme-base border-theme-primary shadow-xl' 
                      : 'bg-transparent text-theme-secondary border-theme-border hover:border-theme-accent/30'
                    }`}
                  >
                    {brand}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="flex items-center space-x-2 bg-theme-base/40 p-1 rounded-xl border border-theme-border flex-shrink-0">
            <select 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="bg-transparent text-theme-primary text-[10px] font-black uppercase px-2 py-1 outline-none cursor-pointer"
            >
              <option value="newest">Newest First</option>
              <option value="price_low">Cheapest First</option>
              <option value="price_high">Premium First</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="flex flex-col items-center justify-center py-20">
            <RefreshCw className="h-10 w-10 text-theme-accent animate-spin mb-4" />
            <p className="text-theme-secondary font-bold uppercase tracking-widest animate-pulse">Updating Market Data...</p>
          </div>
        ) : error ? (
          <div className="glass rounded-3xl p-12 text-center border-red-500/20">
            <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
            <h3 className="text-xl font-black text-theme-primary uppercase mb-2">Connection Error</h3>
            <p className="text-theme-secondary text-sm">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {filteredFamilies.map((family) => (
              <div 
                key={family.id}
                className="glass rounded-[2rem] p-6 card-hover cursor-pointer group flex flex-col h-full border border-theme-border"
                onClick={() => {
                  setSelectedFamily(family);
                  setSelectedVariantId(family.variants[0]?.id || null);
                  if (family.variants[0]?.id) fetchHistory(family.variants[0].id);
                }}
              >
                <div className="flex justify-between items-start mb-6">
                  <ProductImage brand={family.brand_name} image_url={family.image_url} className="h-14 w-14 text-sm" />
                  <div className="bg-theme-accent/10 text-theme-accent px-2 py-1 rounded-lg text-[9px] font-black uppercase tracking-tighter">
                    {family.category}
                  </div>
                </div>
                
                <div className="flex-1">
                  <div className="text-[10px] font-bold text-theme-secondary uppercase tracking-widest mb-1">{family.brand_name}</div>
                  <h3 className="text-lg font-black text-theme-primary mb-2 leading-tight group-hover:text-theme-accent transition-colors">
                    {family.name}
                  </h3>
                  <div className="flex items-center space-x-2 text-theme-secondary mb-4">
                    <TrendingUp className="h-3.5 w-3.5 text-success" />
                    <span className="text-xs font-bold">{getPriceRange(family)}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-theme-border flex items-center justify-between">
                  <div className="text-[9px] text-theme-secondary font-bold uppercase">{family.variants.length} Variants</div>
                  <div className="flex items-center space-x-1 text-theme-accent font-black text-[10px] uppercase group-hover:translate-x-1 transition-transform">
                    <span>Explore</span>
                    <ArrowRight className="h-3 w-3" />
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {selectedFamily && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-6 bg-slate-950/60 backdrop-blur-md animate-fade-in">
          <div className="glass w-full max-w-6xl max-h-[90vh] rounded-[2.5rem] overflow-hidden flex flex-col shadow-2xl">
            <div className="p-6 md:p-8 overflow-y-auto custom-scrollbar">
              <div className="flex justify-between items-start mb-8">
                <div className="flex items-center space-x-6">
                  <ProductImage brand={selectedFamily.brand_name} image_url={selectedFamily.image_url} className="h-20 w-20 text-2xl hidden md:flex" />
                  <div>
                    <div className="flex items-center space-x-2 text-xs font-bold text-theme-secondary uppercase tracking-[0.2em] mb-2">
                      <span>{selectedFamily.brand_name}</span>
                      <span className="h-1 w-1 rounded-full bg-theme-border" />
                      <span>{selectedFamily.category}</span>
                    </div>
                    <h2 className="text-3xl font-black text-theme-primary uppercase tracking-tight">{selectedFamily.name}</h2>
                  </div>
                </div>
                <button 
                  onClick={() => { setSelectedFamily(null); setSelectedVariantId(null); }}
                  className="p-3 bg-theme-base/5 hover:bg-theme-base/10 rounded-2xl text-theme-secondary hover:text-theme-primary transition-all border border-theme-border"
                >
                  <RefreshCw className="h-5 w-5 rotate-45" />
                </button>
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-12 gap-8">
                <div className="xl:col-span-7 space-y-8">
                  {groupVariantsByStorage(selectedFamily.variants).map(([storage, types]) => (
                    <div key={storage} className="animate-fade-in">
                      <div className="flex items-center space-x-3 mb-4">
                        <div className="bg-theme-base/5 px-3 py-1 rounded-full text-[10px] font-black text-theme-secondary uppercase tracking-widest border border-theme-border">
                          {storage}
                        </div>
                        <div className="flex-1 h-px bg-theme-border" />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2 text-[9px] font-black text-theme-secondary uppercase tracking-widest pl-1">
                            <Zap className="h-3 w-3 text-theme-accent" />
                            <span>Brand New</span>
                          </div>
                          <VariantBox variants={types.new} type="new" />
                        </div>
                        <div className="space-y-3">
                          <div className="flex items-center space-x-2 text-[9px] font-black text-theme-secondary uppercase tracking-widest pl-1">
                            <ShieldCheck className="h-3 w-3 text-success" />
                            <span>Verified Used</span>
                          </div>
                          <VariantBox variants={types.used} type="used" />
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="xl:col-span-5 space-y-6">
                  <div className="glass rounded-3xl p-6 border-theme-border">
                    <div className="flex items-center justify-between mb-6">
                      <div className="flex items-center space-x-2">
                        <TrendingUp className="h-4 w-4 text-theme-accent" />
                        <h3 className="text-xs font-black text-theme-primary uppercase tracking-widest">Market History</h3>
                      </div>
                      <div className="flex items-center space-x-1 text-[10px] font-bold text-theme-secondary bg-theme-base/5 px-2 py-1 rounded-lg">
                        <Info className="h-3 w-3" />
                        <span>Last 30 Days</span>
                      </div>
                    </div>
                    
                    <div className="h-[250px] w-full">
                      {historyLoading ? (
                        <div className="h-full flex flex-col items-center justify-center">
                          <RefreshCw className="h-6 w-6 text-theme-secondary animate-spin mb-2" />
                          <span className="text-[10px] text-theme-secondary font-bold uppercase">Loading...</span>
                        </div>
                      ) : history.length > 0 ? (
                        <ResponsiveContainer width="100%" height="100%">
                          <LineChart data={history}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff05" vertical={false} />
                            <XAxis 
                              dataKey="scraped_at" 
                              tickFormatter={formatDate}
                              tick={{fill: theme === 'dark' ? '#475569' : '#94a3b8', fontSize: 10, fontWeight: 700}}
                              axisLine={false}
                              tickLine={false}
                            />
                            <YAxis 
                              hide 
                              domain={['dataMin - 50', 'dataMax + 50']}
                            />
                            <Tooltip 
                              contentStyle={{ 
                                backgroundColor: theme === 'dark' ? '#0f172a' : '#fff', 
                                border: '1px solid var(--border-color)',
                                borderRadius: '12px',
                                fontSize: '12px',
                                fontWeight: 800,
                                color: 'var(--text-primary)'
                              }}
                              itemStyle={{ color: 'var(--accent)' }}
                              labelFormatter={(label: any) => formatDate(label as string)}
                            />
                            <Line 
                              type="monotone" 
                              dataKey="price" 
                              stroke="var(--accent)" 
                              strokeWidth={3} 
                              dot={{r: 4, fill: 'var(--accent)', strokeWidth: 2, stroke: 'var(--bg-primary)'}}
                              activeDot={{r: 6, strokeWidth: 0}}
                              animationDuration={1000}
                            />
                          </LineChart>
                        </ResponsiveContainer>
                      ) : (
                        <div className="h-full flex flex-col items-center justify-center bg-theme-base/20 rounded-2xl border border-dashed border-theme-border">
                          <TrendingUp className="h-8 w-8 text-theme-secondary opacity-30 mb-2" />
                          <span className="text-[10px] text-theme-secondary font-black uppercase">No Data Patterns Yet</span>
                        </div>
                      )}
                    </div>
                  </div>

                  <div className="bg-theme-accent rounded-3xl p-6 text-white shadow-xl shadow-theme-accent/20 relative overflow-hidden group">
                    <Package className="absolute -right-4 -bottom-4 h-32 w-32 text-white/10 -rotate-12 group-hover:rotate-0 transition-transform duration-500" />
                    <h4 className="text-sm font-black uppercase tracking-widest mb-2">Deal Prediction</h4>
                    <p className="text-xs text-white/80 font-medium leading-relaxed mb-4 relative z-10">
                      Based on current retail trends, prices for this model are stable. We recommend buying now if you find a deal under the market average.
                    </p>
                    <button className="bg-white text-theme-accent px-4 py-2 rounded-xl text-[10px] font-black uppercase tracking-tight hover:bg-white/90 transition-colors relative z-10">
                      Get Price Alerts
                    </button>
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
