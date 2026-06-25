import React from 'react';
import { ShieldCheck, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function ResearchResultsTab({ final, key_findings }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <div className="flex flex-col gap-6">
        <div className="glass-panel p-8 border-[#10b981]/30 bg-[#10b981]/5 relative overflow-hidden">
          <ShieldCheck size={120} className="absolute -bottom-6 -right-6 text-[#10b981]/10" />
          <h3 className="text-2xl font-black text-glow-success mb-6 tracking-wide">PHASE 11 FROZEN</h3>
          <p className="text-slate-300 text-lg leading-relaxed relative z-10">
            Cyber DNA successfully improves insider-threat detection on CMU CERT r4.2 by combining baseline behaviors with USB, off-hours, and temporal drift signals. 
            <br/><br/>
            The final frozen model achieves an F1-score of <strong className="text-white border-b-2 border-[#10b981]">{(final.f1*100).toFixed(2)}%</strong> on unseen future data.
          </p>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-lg font-bold mb-4 text-slate-200">Key Analytical Findings</h3>
          <ul className="flex flex-col gap-4">
            {key_findings.map((finding, idx) => (
              <li key={idx} className="flex gap-3 text-sm text-slate-400 leading-relaxed">
                <ArrowRight size={16} className="text-[#0ea5e9] shrink-0 mt-0.5" />
                <span dangerouslySetInnerHTML={{ __html: finding.replace(/(\d+\.\d+%|\d+\.\d+)/g, '<strong class="text-slate-200 font-mono">$1</strong>') }} />
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="flex flex-col gap-6">
        <div className="terminal-box h-full min-h-[400px] flex flex-col">
          <div className="flex items-center gap-2 border-b border-slate-700/50 pb-3 mb-4">
            <div className="flex gap-1.5">
              <div className="w-3 h-3 rounded-full bg-[#ef4444]"></div>
              <div className="w-3 h-3 rounded-full bg-[#f59e0b]"></div>
              <div className="w-3 h-3 rounded-full bg-[#10b981]"></div>
            </div>
            <span className="ml-2 text-xs text-slate-500 font-bold uppercase tracking-widest">Phase 11 Execution Log</span>
          </div>
          
          <div className="flex-1 overflow-y-auto pr-2 flex flex-col gap-1">
            <div className="text-[#0ea5e9] font-bold">&gt; python cyber_dna_phase11_ablation.py</div>
            <div className="text-slate-300 font-bold">=== PHASE 11: ABLATION & TUNING PIPELINE ===</div>
            <div><span className="text-[#8b5cf6]">[*]</span> Loading Ground Truth from insiders.csv...</div>
            <div className="text-slate-500">    Loaded 1069 true malicious user-weeks.</div>
            <div><span className="text-[#8b5cf6]">[*]</span> Loading CERT r4.2 Data...</div>
            <div className="text-slate-500">  -&gt; Loading logon.csv</div>
            <div className="text-slate-500">  -&gt; Loading email.csv</div>
            <div className="text-slate-500">  -&gt; Loading device.csv</div>
            <br />
            <div className="text-slate-400 border-l-2 border-slate-700 pl-2">--- Evaluating Config: A. Baseline Verified ---</div>
            <div>    [Tuning] Best threshold on Train CV: <span className="text-slate-300">0.500</span></div>
            <div className="text-slate-500">    Test: Precision 0.6364 | Recall 0.3415 | F1 0.4444 | AUPRC 0.4059</div>
            <br />
            <div className="text-slate-300 border-l-2 border-[#0ea5e9] pl-2 font-bold">--- Evaluating Config: E. Full Phase 11 ---</div>
            <div>    [Tuning] Best threshold on Train CV: <span className="text-[#0ea5e9]">0.300</span></div>
            <div className="text-[#10b981]">    Test: Precision 0.5067 | Recall 0.4634 | F1 0.4841 | AUPRC 0.4490</div>
            <div>    <span className="text-[#10b981]">TP: 38</span> | <span className="text-[#ef4444]">FP: 37</span> | FN: 44</div>
            <br />
            <div className="text-[#10b981] font-bold mt-4 flex items-center gap-2">
              <CheckCircle2 size={14} /> PHASE 11 VALIDATION COMPLETE
            </div>
          </div>
        </div>
      </div>

    </div>
  );
}
