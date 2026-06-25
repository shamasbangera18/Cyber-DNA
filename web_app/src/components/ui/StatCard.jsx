import React from 'react';

export default function StatCard({ icon: Icon, title, value, subtitle, iconColor, valueColor, borderClass = "" }) {
  return (
    <div className={`stat-card ${borderClass}`}>
      <Icon size={48} className={`stat-card-icon ${iconColor}`} />
      <span className={`text-xs font-bold uppercase tracking-widest mb-1 ${iconColor.replace('text-', 'text-')}`}>{title}</span>
      <span className={`text-3xl font-black ${valueColor}`}>{value}</span>
      <span className="text-xs text-slate-400 mt-2">{subtitle}</span>
    </div>
  );
}
