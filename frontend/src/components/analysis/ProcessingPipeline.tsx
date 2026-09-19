import { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Check, Loader2 } from 'lucide-react';

const STEPS = [
  'Image loaded',
  'Image preprocessed',
  'Leaf detected',
  'Leaf segmented',
  'Shape analyzed',
  'Color analyzed',
  'Texture analyzed',
  'Species analyzed',
  'Leaf health analyzed',
  'Growth stage analyzed',
  'Results generated',
];

export function ProcessingPipeline() {
  const [activeIdx, setActiveIdx] = useState(0);

  useEffect(() => {
    const id = setInterval(() => {
      setActiveIdx((i) => (i < STEPS.length - 1 ? i + 1 : i));
    }, 450);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="glass rounded-xl2 p-6 md:p-8">
      <p className="font-display text-lg mb-5">LeafLens Analysis</p>
      <div className="flex flex-col gap-3">
        {STEPS.map((step, idx) => {
          const done = idx < activeIdx;
          const current = idx === activeIdx;
          return (
            <motion.div
              key={step}
              initial={{ opacity: 0.3 }}
              animate={{ opacity: done || current ? 1 : 0.35 }}
              className="flex items-center gap-3 text-sm"
            >
              <span
                className="flex h-5 w-5 items-center justify-center rounded-full"
                style={{
                  backgroundColor: done ? 'var(--accent)' : 'transparent',
                  border: done ? 'none' : '1.5px solid var(--border)',
                }}
              >
                {done && <Check size={12} className="text-white" />}
                {current && <Loader2 size={12} className="animate-spin" style={{ color: 'var(--accent)' }} />}
              </span>
              <span className={done || current ? 'text-[var(--ink)]' : 'text-[var(--ink-soft)]'}>{step}</span>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}
