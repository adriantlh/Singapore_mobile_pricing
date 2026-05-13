import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer 
} from 'recharts';
import { Smartphone, TrendingUp, AlertCircle, Info, RefreshCw } from 'lucide-react';

const API_BASE_URL = 'http://localhost:8000';

interface Product {
  id: string;
  name: string;
  brand_name: string;
  price: number;
  currency: string;
  scraped_at: string;
  source_name: string;
  attributes: any;
}

interface PriceHistory {
  price: number;
  currency: string;
  scraped_at: string;
}

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedProduct, setSelectedProduct] = useState<Product | null>(null);
  const [history, setHistory] = useState<PriceHistory[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/products`);
      setProducts(response.data);
      setError(null);
    } catch (err) {
      setError('Failed to fetch products. Is the API running?');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchHistory = async (variantId: string) => {
    try {
      setHistoryLoading(true);
      const response = await axios.get(`${API_BASE_URL}/api/products/${variantId}/history`);
      setHistory(response.data);
    } catch (err) {
      console.error('Failed to fetch price history', err);
    } finally {
      setHistoryLoading(false);
    }
  };

  const handleProductClick = (product: Product) => {
    setSelectedProduct(product);
    fetchHistory(product.id);
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-SG', {
      day: '2-digit',
      month: 'short',
      year: 'numeric'
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <div className="bg-indigo-600 p-2 rounded-lg">
              <Smartphone className="h-6 w-6 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">SG Mobile Price Tracker</h1>
          </div>
          <button 
            onClick={fetchProducts}
            className="flex items-center space-x-2 px-4 py-2 bg-indigo-50 text-indigo-700 rounded-md hover:bg-indigo-100 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Note about Data Quality */}
        <div className="mb-8 bg-blue-50 border-l-4 border-blue-400 p-4 rounded-r-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <Info className="h-5 w-5 text-blue-400" />
            </div>
            <div className="ml-3">
              <p className="text-sm text-blue-700">
                <span className="font-bold text-blue-800">Note:</span> RedWhite Mobile data may contain inconsistencies due to the site's layout. We are aggressively filtering non-product entries and standardizing names.
              </p>
            </div>
          </div>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-64">
            <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-center space-x-3">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        ) : (
          <div className="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Product</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Brand</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Condition</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Price</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Source</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Last Scraped</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product) => (
                  <tr 
                    key={product.id} 
                    className="hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => handleProductClick(product)}
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{product.name}</div>
                      {product.attributes?.storage && (
                        <div className="text-xs text-gray-500">{product.attributes.storage}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                        {product.brand_name}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 capitalize">
                      {product.attributes?.condition || 'new'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-bold text-gray-900">
                        ${product.price.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </div>
                      <div className="text-xs text-gray-400">{product.currency}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {product.source_name}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {formatDate(product.scraped_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </main>

      {/* Detail Modal */}
      {selectedProduct && (
        <div className="fixed inset-0 z-10 overflow-y-auto">
          <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div className="fixed inset-0 transition-opacity" aria-hidden="true">
              <div className="absolute inset-0 bg-gray-500 opacity-75" onClick={() => setSelectedProduct(null)}></div>
            </div>

            <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>

            <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
              <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                <div className="flex justify-between items-start mb-6">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-900">{selectedProduct.name}</h3>
                    <p className="text-sm text-gray-500">{selectedProduct.brand_name} • {selectedProduct.attributes?.condition || 'New'}</p>
                  </div>
                  <button 
                    onClick={() => setSelectedProduct(null)}
                    className="text-gray-400 hover:text-gray-500"
                  >
                    <span className="sr-only">Close</span>
                    <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="h-96 w-full">
                  {historyLoading ? (
                    <div className="flex justify-center items-center h-full">
                      <RefreshCw className="h-8 w-8 animate-spin text-indigo-600" />
                    </div>
                  ) : history.length > 0 ? (
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={history}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f0f0f0" />
                        <XAxis 
                          dataKey="scraped_at" 
                          tickFormatter={formatDate}
                          tick={{ fontSize: 12 }}
                        />
                        <YAxis 
                          tickFormatter={(value) => `$${value}`}
                          tick={{ fontSize: 12 }}
                        />
                        <Tooltip 
                          formatter={(value: any) => [`$${Number(value).toLocaleString()}`, 'Price']}
                          labelFormatter={(label: any) => formatDate(String(label))}
                        />
                        <Line 
                          type="monotone" 
                          dataKey="price" 
                          stroke="#4f46e5" 
                          strokeWidth={2}
                          dot={{ r: 4, fill: '#4f46e5' }}
                          activeDot={{ r: 6 }}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  ) : (
                    <div className="flex flex-col justify-center items-center h-full text-gray-400">
                      <TrendingUp className="h-12 w-12 mb-2" />
                      <p>No price history data available yet.</p>
                    </div>
                  )}
                </div>
              </div>
              <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                <button 
                  type="button" 
                  className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-indigo-600 text-base font-medium text-white hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:ml-3 sm:w-auto sm:text-sm"
                  onClick={() => setSelectedProduct(null)}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
