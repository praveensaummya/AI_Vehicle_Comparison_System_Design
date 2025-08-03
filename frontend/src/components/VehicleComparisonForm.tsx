'use client';

import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { Car, Search, Sparkles, AlertCircle, Filter, X } from 'lucide-react';
import { ApiClient, validateVehicleAnalysisRequest } from '@/lib/api';
import { VehicleAnalysisRequest, VehicleAnalysisResponse, VEHICLE_SUGGESTIONS, ALL_VEHICLES } from '@/types/api';
import { cn } from '@/lib/utils';
import ProgressIndicator from '@/components/ui/ProgressIndicator';
import AdCard from '@/components/ui/AdCard';
import VehicleSelectionMenu from '@/components/ui/VehicleSelectionMenu';

export default function VehicleComparisonForm() {
  const [vehicle1, setVehicle1] = useState('');
  const [vehicle2, setVehicle2] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<VehicleAnalysisResponse | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [showVehicleSelection, setShowVehicleSelection] = useState(false);
  const [currentVehicleInput, setCurrentVehicleInput] = useState<1 | 2 | null>(null);
  
  const categories = Object.keys(VEHICLE_SUGGESTIONS);
  
  const handleVehicleSelect = (vehicle: string) => {
    if (currentVehicleInput === 1) {
      setVehicle1(vehicle);
    } else if (currentVehicleInput === 2) {
      setVehicle2(vehicle);
    }
    setShowVehicleSelection(false);
    setSelectedCategory(null);
    setCurrentVehicleInput(null);
  };
  
  const openVehicleSelection = (vehicleNumber: 1 | 2) => {
    setCurrentVehicleInput(vehicleNumber);
    setShowVehicleSelection(true);
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setData(null);
    
    const request: VehicleAnalysisRequest = { vehicle1, vehicle2 };
    const validationErrors = validateVehicleAnalysisRequest(request);
    if (validationErrors.length) {
      setError(validationErrors.join(', '));
      return;
    }
    
    setLoading(true);
    try {
      const response = await ApiClient.analyzeVehicles(request);
      setData(response);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-4">
      {/* Header Section */}
      <div className="text-center mb-8">
        <div className="flex items-center justify-center mb-4">
          <div className="bg-indigo-100 p-3 rounded-full">
            <Car className="w-8 h-8 text-indigo-600" />
          </div>
        </div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Vehicle Comparison</h1>
        <p className="text-gray-600 max-w-2xl mx-auto">
          Enter any two vehicle models to get AI-powered comparison reports and real-time market data from Sri Lankan dealerships.
        </p>
      </div>

      {/* Comparison Form */}
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid md:grid-cols-2 gap-6">
            {/* Vehicle 1 Input */}
            <div className="space-y-2">
              <label htmlFor="vehicle1" className="block text-sm font-semibold text-gray-700">
                First Vehicle
              </label>
              <div className="space-y-2">
                <div className="relative">
                  <input
                    type="text"
                    id="vehicle1"
                    value={vehicle1}
                    onChange={e => setVehicle1(e.target.value)}
                    placeholder="e.g., Toyota Aqua"
                    className="w-full px-4 py-3 pl-12 pr-20 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 text-gray-900"
                    list="vehicle-list"
                    disabled={loading}
                  />
                  <Car className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <button
                    type="button"
                    onClick={() => openVehicleSelection(1)}
                    disabled={loading}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 text-xs font-medium text-indigo-600 hover:text-indigo-700 border border-indigo-300 hover:border-indigo-400 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Browse
                  </button>
                </div>
              </div>
            </div>

            {/* Vehicle 2 Input */}
            <div className="space-y-2">
              <label htmlFor="vehicle2" className="block text-sm font-semibold text-gray-700">
                Second Vehicle
              </label>
              <div className="space-y-2">
                <div className="relative">
                  <input
                    type="text"
                    id="vehicle2"
                    value={vehicle2}
                    onChange={e => setVehicle2(e.target.value)}
                    placeholder="e.g., Honda Fit"
                    className="w-full px-4 py-3 pl-12 pr-20 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent transition-all duration-200 text-gray-900"
                    list="vehicle-list"
                    disabled={loading}
                  />
                  <Car className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <button
                    type="button"
                    onClick={() => openVehicleSelection(2)}
                    disabled={loading}
                    className="absolute right-2 top-1/2 transform -translate-y-1/2 px-3 py-1 text-xs font-medium text-indigo-600 hover:text-indigo-700 border border-indigo-300 hover:border-indigo-400 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Browse
                  </button>
                </div>
              </div>
            </div>
          </div>

          <datalist id="vehicle-list">
            {ALL_VEHICLES.map(vehicle => <option key={vehicle} value={vehicle} />)}
          </datalist>

          {/* Error Display */}
          {error && (
            <div className="flex items-center space-x-2 p-4 bg-red-50 border border-red-200 rounded-xl">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
              <p className="text-red-700 text-sm">{error}</p>
            </div>
          )}

          {/* Submit Button */}
          <div className="flex justify-center">
            <button
              type="submit"
              disabled={loading || !vehicle1.trim() || !vehicle2.trim()}
              className={cn(
                "inline-flex items-center px-8 py-4 rounded-xl font-semibold text-white transition-all duration-200 transform",
                loading || !vehicle1.trim() || !vehicle2.trim()
                  ? "bg-gray-400 cursor-not-allowed"
                  : "bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 hover:scale-105 shadow-lg hover:shadow-xl"
              )}
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3" />
                  AI Agents Working...
                </>
              ) : (
                <>
                  <Search className="w-5 h-5 mr-3" />
                  Start AI Analysis
                </>
              )}
            </button>
          </div>
        </form>
      </div>

{/* Vehicle Selection Menu */}
      {showVehicleSelection 
&& (
        <div className="mb-8">
          <VehicleSelectionMenu onSelect={handleVehicleSelect} currentInput={currentVehicleInput as 1 | 2} />
        </div>
      )}

      {/* Progress Indicator */}
      <ProgressIndicator isLoading={loading} className="mb-8" />

      {/* Results Section */}
      {data && (
        <div className="space-y-8">
          {/* Comparison Report */}
          <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
            <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-8 py-6">
              <div className="flex items-center space-x-3">
                <Sparkles className="w-6 h-6 text-white" />
                <h2 className="text-2xl font-bold text-white">AI Comparison Report</h2>
              </div>
              <p className="text-indigo-100 mt-2">
                Detailed analysis comparing {vehicle1} vs {vehicle2}
              </p>
            </div>
            <div className="p-8">
              <ReactMarkdown className="prose prose-lg max-w-none prose-indigo prose-headings:text-gray-900 prose-p:text-gray-700">
                {data.comparison_report}
              </ReactMarkdown>
            </div>
          </div>

          {/* Advertisements Section */}
          <div className="grid lg:grid-cols-2 gap-8">
            {[
              { title: `${vehicle1} Advertisements`, ads: data.vehicle1_ads, color: 'from-blue-500 to-cyan-500' },
              { title: `${vehicle2} Advertisements`, ads: data.vehicle2_ads, color: 'from-emerald-500 to-teal-500' }
            ].map(({ title, ads, color }) => (
              <div key={title} className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
                <div className={cn("bg-gradient-to-r px-6 py-4", color)}>
                  <h3 className="text-xl font-bold text-white">{title}</h3>
                  <p className="text-white/90 text-sm mt-1">
                    {ads.length} listing{ads.length !== 1 ? 's' : ''} found
                  </p>
                </div>
                <div className="p-6">
                  {ads.length > 0 ? (
                    <div className="space-y-4">
                      {ads.map(ad => (
                        <AdCard key={ad.link} ad={ad} />
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <div className="text-gray-400 mb-3">
                        <Search className="w-12 h-12 mx-auto" />
                      </div>
                      <p className="text-gray-500">No advertisements found for this vehicle.</p>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
  
