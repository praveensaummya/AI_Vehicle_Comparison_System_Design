'use client';

import React, { useState } from 'react';
import { VEHICLE_SUGGESTIONS } from '@/types/api';
import { cn } from '@/lib/utils';
import { Car, X, ChevronRight } from 'lucide-react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCar, faCarSide, faTruck, faGem, faMoneyBill, faRoad } from '@fortawesome/free-solid-svg-icons';
import '@/lib/fontawesome';

interface VehicleSelectionProps {
  onSelect: (vehicle: string) => void;
  currentInput: 1 | 2;
  onClose?: () => void;
}

const CATEGORY_ICONS = {
  'Popular Japanese Models': faCar,
  'Hybrid Vehicles': faCarSide,
  'Luxury Vehicles': faGem,
  'SUVs': faTruck,
  'Budget Cars': faMoneyBill,
  'Commercial Vehicles': faRoad
};

export default function VehicleSelectionMenu({ onSelect, currentInput, onClose }: VehicleSelectionProps) {
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  const categories = Object.keys(VEHICLE_SUGGESTIONS);

  const handleVehicleSelect = (vehicle: string) => {
    onSelect(vehicle);
    setSelectedCategory(null);
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg border border-gray-100 overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-indigo-600 to-purple-600 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="bg-white/20 p-2 rounded-lg">
              <Car className="w-5 h-5 text-white" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-white">
                Select Vehicle {currentInput}
              </h3>
              <p className="text-indigo-100 text-sm">
                Browse by category or search for any vehicle model
              </p>
            </div>
          </div>
          {onClose && (
            <button
              onClick={onClose}
              className="text-white/80 hover:text-white transition-colors p-1"
            >
              <X className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      <div className="p-6">
        {/* Category Selection - Horizontal Scrollable */}
        <div className="mb-6">
          <h4 className="text-sm font-semibold text-gray-700 mb-3">Vehicle Categories</h4>
          <div className="flex space-x-3 overflow-x-auto pb-2 scrollbar-thin scrollbar-thumb-gray-300">
            {categories.map(category => {
              const icon = CATEGORY_ICONS[category as keyof typeof CATEGORY_ICONS];
              const isSelected = selectedCategory === category;
              
              return (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(isSelected ? null : category)}
                  className={cn(
                    "flex-shrink-0 flex flex-col items-center p-4 rounded-xl border-2 transition-all duration-200 min-w-[120px]",
                    isSelected
                      ? "border-indigo-500 bg-indigo-50 shadow-md"
                      : "border-gray-200 hover:border-indigo-300 hover:bg-gray-50"
                  )}
                >
                  <div className={cn(
                    "w-10 h-10 rounded-full flex items-center justify-center mb-2",
                    isSelected ? "bg-indigo-100" : "bg-gray-100"
                  )}>
                    <FontAwesomeIcon 
                      icon={icon} 
                      className={cn(
                        "text-base",
                        isSelected ? "text-indigo-600" : "text-gray-600"
                      )} 
                    />
                  </div>
                  <span className={cn(
                    "text-xs font-semibold text-center leading-tight",
                    isSelected ? "text-indigo-800" : "text-gray-800"
                  )}>
                    {category}
                  </span>
                </button>
              );
            })}
          </div>
        </div>

        {/* Vehicle List - Horizontal Grid */}
        {selectedCategory && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h4 className="text-lg font-semibold text-gray-900">
                {selectedCategory}
              </h4>
              <span className="text-sm text-gray-500">
                {VEHICLE_SUGGESTIONS[selectedCategory].length} vehicles
              </span>
            </div>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {VEHICLE_SUGGESTIONS[selectedCategory].map(vehicle => (
                <button
                  key={vehicle}
                  onClick={() => handleVehicleSelect(vehicle)}
                  className="group flex items-center justify-between p-4 bg-gray-50 hover:bg-indigo-50 border border-gray-200 hover:border-indigo-300 rounded-xl transition-all duration-200 text-left"
                >
                  <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center group-hover:bg-indigo-100 transition-colors">
                      <Car className="w-4 h-4 text-gray-600 group-hover:text-indigo-600" />
                    </div>
                    <span className="text-sm font-semibold text-gray-900 group-hover:text-indigo-800">
                      {vehicle}
                    </span>
                  </div>
                  <ChevronRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-500 transition-colors" />
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Instructions */}
        {!selectedCategory && (
          <div className="text-center py-8">
            <div className="text-gray-400 mb-3">
              <Car className="w-12 h-12 mx-auto" />
            </div>
            <p className="text-gray-500 text-sm">
              Choose a category above to browse vehicles, or type directly in the input field
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
