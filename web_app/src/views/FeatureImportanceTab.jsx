import React from 'react';
import { FileSearch } from 'lucide-react';

export default function FeatureImportanceTab({ feature_importance }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="glass-panel p-6 lg:col-span-2">
        <h3 className="text-xl font-bold mb-8 text-slate-200 flex items-center gap-2"><FileSearch size={20} className="text-[#0ea5e9]" /> XGBoost Information Gain Rankings</h3>
        <div className="flex flex-col gap-6">
          {feature_importance.slice(0, 10).map((feat, idx) => {
            const maxImp = feature_importance[0].importance;
            const pct = (feat.importance / maxImp) * 100;
            return (
              <div key={idx} className="flex items-center gap-6">
                <div className="w-8 text-center text-slate-500 font-mono font-bold text-sm bg-slate-800/50 py-1 rounded">
                  {idx + 1}
                </div>
                <div className="w-56 text-sm font-bold text-slate-300 truncate font-mono">
                  {feat.feature}
                </div>
                <div className="flex-1 h-2.5 bg-[#030712] rounded-full overflow-hidden border border-slate-800">
                  <div 
                    className="h-full bg-gradient-to-r from-[#8b5cf6] to-[#0ea5e9] relative" 
                    style={{ width: `${pct}%` }}
                  >
                    <div className="absolute top-0 right-0 bottom-0 w-8 bg-white/20 blur-sm"></div>
                  </div>
                </div>
                <div className="w-20 text-right text-sm text-[#0ea5e9] font-mono font-bold">
                  {feat.importance.toFixed(4)}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="glass-panel p-6 border-slate-800 flex flex-col justify-between">
        <div>
          <h3 className="text-lg font-bold mb-4 text-slate-300">Feature Insights</h3>
          <p className="text-sm text-slate-400 leading-relaxed mb-4">
            The model heavily prioritizes temporal tracking features and baseline activity frequencies. The highest ranking features typically represent core structural behaviors.
          </p>
          <div className="bg-[#f59e0b]/10 border border-[#f59e0b]/30 rounded p-4 text-sm text-[#f59e0b]/90 leading-relaxed">
            <strong className="text-[#f59e0b] block mb-1">Analytical Note:</strong> 
            Engineered features with near-zero importance do not imply they are fundamentally useless. Rather, on CERT r4.2's specific noise profile, XGBoost extracted superior split signal from basic temporal/device logs over complex anthropological variants.
          </div>
        </div>
      </div>
    </div>
  );
}
