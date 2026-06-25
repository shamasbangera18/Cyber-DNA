import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { Activity, Hexagon, Terminal } from 'lucide-react';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass-panel !p-3 !bg-black/80 !border-slate-700">
        <p className="font-bold text-slate-200 mb-2">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }} className="text-sm font-semibold">
            {entry.name}: {entry.value}%
          </p>
        ))}
      </div>
    );
  }
  return null;
};

export default function AblationTab({ ablation_results, baseline, final, chartData }) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        
        {/* Chart Section */}
        <div className="glass-panel xl:col-span-2 p-6 flex flex-col">
          <div className="flex justify-between items-start mb-6">
            <div>
              <h3 className="text-lg font-bold text-slate-200 mb-1 flex items-center gap-2"><Activity size={18} className="text-[#8b5cf6]" /> XGBOOST FEATURE ABLATION STUDY</h3>
              <p className="text-sm text-slate-400 max-w-2xl">
                Adding chronological behavioral descriptors improves detection on unseen test data.
              </p>
            </div>
            <div className="px-3 py-1 bg-[#10b981]/10 border border-[#10b981]/30 text-[#10b981] text-xs font-bold rounded">
              +{(final.f1*100 - baseline.f1*100).toFixed(2)}% F1 Increase
            </div>
          </div>
          
          <div className="h-[350px] w-full mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 20, right: 0, left: -20, bottom: 20 }}>
                <defs>
                  <linearGradient id="colorF1" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0ea5e9" stopOpacity={1}/>
                    <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.3}/>
                  </linearGradient>
                  <linearGradient id="colorPrec" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={1}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.3}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
                <XAxis dataKey="name" stroke="#64748b" tick={{fill: '#94a3b8', fontSize: 12, fontWeight: 500}} angle={-10} textAnchor="end" tickMargin={10} />
                <YAxis stroke="#64748b" tick={{fill: '#94a3b8', fontSize: 12}} domain={[0, 100]} tickFormatter={(val) => `${val}%`} />
                <RechartsTooltip content={<CustomTooltip />} cursor={{fill: 'rgba(255,255,255,0.02)'}} />
                <Legend wrapperStyle={{ paddingTop: '20px', fontSize: '14px', fontWeight: 'bold' }} />
                <Bar dataKey="Precision" fill="url(#colorPrec)" radius={[4, 4, 0, 0]} maxBarSize={60} />
                <Bar dataKey="F1" fill="url(#colorF1)" radius={[4, 4, 0, 0]} maxBarSize={60} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Interpretation Section */}
        <div className="glass-panel p-6 flex flex-col gap-4">
          <h3 className="text-lg font-bold text-slate-200 mb-2 flex items-center gap-2"><Hexagon size={18} className="text-[#0ea5e9]" /> BLOCK ANALYSIS</h3>
          
          <div className="p-4 rounded bg-[#030712]/50 border border-slate-800 border-l-4 border-l-[#8b5cf6]">
            <h4 className="text-sm font-bold text-slate-300 mb-1">USB & Off-Hours Blocks</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Provided modest precision-related filtering, catching clear behavioral anomalies outside standard hours, but lacked recall power on their own.
            </p>
          </div>

          <div className="p-4 rounded bg-[#030712]/50 border border-slate-800 border-l-4 border-l-[#ef4444]">
            <h4 className="text-sm font-bold text-slate-300 mb-1">Workstation Block</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              Chronological workstation-diversity actually degraded isolation performance, capturing high amounts of benign multi-machine usage noise within the CERT dataset.
            </p>
          </div>

          <div className="p-4 rounded bg-[#0ea5e9]/5 border border-[#0ea5e9]/20 border-l-4 border-l-[#0ea5e9]">
            <h4 className="text-sm font-bold text-[#0ea5e9] mb-1">Full Temporal Combination</h4>
            <p className="text-xs text-slate-300 leading-relaxed">
              The combination of all blocks with the proper threshold yielded the strongest overall F1 performance, significantly boosting recall of previously missed threats.
            </p>
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="glass-panel p-6 overflow-hidden mt-2">
        <h3 className="text-lg font-bold text-slate-200 mb-6 flex items-center gap-2"><Terminal size={18} /> SWEEP METRICS</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-sm text-slate-300">
            <thead className="text-xs uppercase tracking-wider text-slate-500 border-b border-slate-800">
              <tr>
                <th className="pb-3 px-4">Model Config</th>
                <th className="pb-3 px-4">Threshold</th>
                <th className="pb-3 px-4">Precision</th>
                <th className="pb-3 px-4">Recall</th>
                <th className="pb-3 px-4 text-[#0ea5e9]">F1-Score</th>
                <th className="pb-3 px-4">AUPRC</th>
                <th className="pb-3 px-4 text-right">TP / FP</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/50">
              {ablation_results.map((row, idx) => {
                const isFinal = row.configuration === final.name;
                return (
                  <tr key={idx} className={`transition-colors hover:bg-slate-800/30 ${isFinal ? 'bg-[#0ea5e9]/5' : ''}`}>
                    <td className={`py-4 px-4 font-mono text-xs ${isFinal ? 'text-[#0ea5e9] font-bold' : 'text-slate-400'}`}>
                      {row.configuration}
                    </td>
                    <td className="py-4 px-4 font-mono text-slate-400">{row.threshold_selected.toFixed(2)}</td>
                    <td className="py-4 px-4">{(row.precision * 100).toFixed(2)}%</td>
                    <td className="py-4 px-4">{(row.recall * 100).toFixed(2)}%</td>
                    <td className={`py-4 px-4 font-bold ${isFinal ? 'text-glow-primary text-[15px]' : 'text-slate-200'}`}>
                      {(row.f1 * 100).toFixed(2)}%
                    </td>
                    <td className="py-4 px-4 font-mono text-slate-400">{row.auprc.toFixed(4)}</td>
                    <td className="py-4 px-4 text-right">
                      <span className="text-[#10b981]">{row.tp}</span> <span className="text-slate-600">/</span> <span className="text-[#ef4444]">{row.fp}</span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
