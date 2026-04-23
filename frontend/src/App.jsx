import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Upload, CheckCircle, XCircle, AlertCircle, 
  FileText, CreditCard, Wallet, Search, 
  ChevronRight, RefreshCw, Layers, Award,
  Sparkles, ShieldCheck, Fingerprint, Activity,
  Cpu, Zap, Eye, Database
} from 'lucide-react';

const API_BASE = 'http://localhost:8000';

const App = () => {
  const [files, setFiles] = useState({
    id_card: null,
    marksheet: null,
    income: null
  });
  const [previews, setPreviews] = useState({});
  const [status, setStatus] = useState({ is_processing: false, progress: 0, message: 'Idle', error: null });
  const [results, setResults] = useState(null);
  const [stage, setStage] = useState('upload'); // 'upload', 'processing', 'results'

  const handleFileChange = (type, file) => {
    if (file) {
      setFiles(prev => ({ ...prev, [type]: file }));
      const reader = new FileReader();
      reader.onloadend = () => {
        setPreviews(prev => ({ ...prev, [type]: reader.result }));
      };
      reader.readAsDataURL(file);
    }
  };

  const startVerification = async () => {
    if (!files.id_card || !files.marksheet || !files.income) {
      alert('Please upload all 3 documents.');
      return;
    }

    try {
      setStage('processing');
      setStatus({ is_processing: true, progress: 0, message: 'Initializing...', error: null });

      const formData = new FormData();
      formData.append('id_card', files.id_card);
      formData.append('marksheet', files.marksheet);
      formData.append('income', files.income);

      await fetch(`${API_BASE}/api/upload`, { method: 'POST', body: formData });
      await fetch(`${API_BASE}/api/process`, { method: 'POST' });
      pollStatus();
    } catch (err) {
      setStatus(prev => ({ ...prev, error: 'Failed to connect to server.' }));
    }
  };

  const pollStatus = async () => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status`);
        const data = await res.json();
        setStatus(data);

        if (!data.is_processing) {
          clearInterval(interval);
          if (!data.error) {
            fetchResults();
          }
        }
      } catch (err) {
        clearInterval(interval);
      }
    }, 1000);
  };

  const fetchResults = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/results`);
      const data = await res.json();
      setResults(data);
      setStage('results');
    } catch (err) {
      console.error('Failed to fetch results');
    }
  };

  return (
    <div className="container">
      <header style={{ textAlign: 'center', margin: '1rem 0 2rem' }}>
        <motion.div
           initial={{ opacity: 0, scale: 0.9 }}
           animate={{ opacity: 1, scale: 1 }}
           transition={{ duration: 0.5 }}
        >
          <div style={{ display: 'inline-flex', alignItems: 'center', gap: '10px', padding: '10px 20px', background: 'var(--surface)', borderRadius: '100px', marginBottom: '1.5rem', border: '1px solid var(--surface-border)', fontSize: '11px', fontWeight: '800', color: 'var(--primary)', letterSpacing: '3px' }}>
            <Sparkles size={16} /> PRECISION VERIFICATION ENGINE
          </div>
          <h1 style={{ fontSize: '3.5rem', marginBottom: '0.5rem', fontWeight: '800', letterSpacing: '-0.05em', color: 'var(--primary)' }}>
            Verification <span style={{ color: 'var(--accent-purple)' }}>Workspace</span>
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '1.1rem', maxWidth: '600px', margin: '0 auto' }}>
            Elevating scholarship processing through intelligent document intelligence.
          </p>
        </motion.div>
      </header>

      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: 0 }}>
        <AnimatePresence mode="wait">
          {stage === 'upload' && (
            <UploadStage 
              key="upload" 
              files={files} 
              previews={previews} 
              onFileChange={handleFileChange} 
              onStart={startVerification} 
            />
          )}

          {stage === 'processing' && (
            <ProcessingStage 
              key="processing" 
              status={status} 
            />
          )}

          {stage === 'results' && results && (
            <ResultsStage 
              key="results" 
              results={results} 
              previews={previews}
              onReset={() => {
                  setStage('upload');
                  setResults(null);
                  setFiles({ id_card: null, marksheet: null, income: null });
                  setPreviews({});
              }} 
            />
          )}
        </AnimatePresence>
      </div>
      
      <footer style={{ padding: '1.5rem 0', textAlign: 'center', color: 'var(--text-muted)', fontSize: '13px' }}>
        <p>© 2026 Advanced Scholarship Processing System • Premium Tier Experience</p>
      </footer>
    </div>
  );
};

const UploadStage = ({ files, previews, onFileChange, onStart }) => {
  const uploadCards = [
    { type: 'id_card', label: 'Identity Proof', sub: 'Aadhaar / PAN Authentication', icon: <Fingerprint size={28} />, color: 'var(--primary)' },
    { type: 'marksheet', label: 'Academic Merits', sub: 'Grade Transcript Verification', icon: <Award size={28} />, color: 'var(--accent-purple)' },
    { type: 'income', label: 'Financial Status', sub: 'Economic Standing Certificate', icon: <Wallet size={28} />, color: 'var(--accent-peach)' }
  ];

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', flex: 1, justifyContent: 'center' }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        {uploadCards.map(card => (
          <motion.div 
            key={card.type} 
            whileHover={{ y: -5 }}
            className="glass-card" 
            style={{ padding: '2rem', textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center' }}
          >
            <div style={{ 
              width: '56px', height: '56px', borderRadius: '16px', background: `${card.color}15`, 
              display: 'flex', alignItems: 'center', justifyContent: 'center', marginBottom: '1rem', color: card.color 
            }}>
              {card.icon}
            </div>
            <h3 style={{ marginBottom: '0.25rem', fontSize: '1.2rem' }}>{card.label}</h3>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginBottom: '1.5rem' }}>{card.sub}</p>
            
            <label className={`custom-file-upload ${files[card.type] ? 'has-file' : ''}`} style={{ 
              width: '100%', padding: '1rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center'
            }}>
              <input 
                type="file" 
                accept="image/*" 
                onChange={(e) => onFileChange(card.type, e.target.files[0])}
                style={{ display: 'none' }}
              />
              {previews[card.type] ? (
                <div style={{ width: '100%' }}>
                    <img src={previews[card.type]} alt="Preview" style={{ width: '100%', height: '100px', objectFit: 'cover', borderRadius: '12px' }} />
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.4rem' }}>
                  <Upload size={18} style={{ color: 'var(--primary)', opacity: 0.6 }} />
                  <span style={{ fontSize: '0.8rem', fontWeight: '600' }}>Attach Document</span>
                </div>
              )}
            </label>
          </motion.div>
        ))}
      </div>

      <div style={{ textAlign: 'center' }}>
        <button 
          className="premium-button" 
          onClick={onStart}
          disabled={!files.id_card || !files.marksheet || !files.income}
          style={{ minWidth: '260px', display: 'inline-flex', alignItems: 'center', justifyContent: 'center', gap: '0.75rem' }}
        >
          Initialize Analysis Engine
          <ChevronRight size={18} />
        </button>
      </div>
    </motion.div>
  );
};

const ProcessingStage = ({ status }) => {
  const [displayProgress, setDisplayProgress] = useState(0);
  const engagementMessages = [
    "Sculpting document structure for analysis...",
    "Extracting intelligence from visual indices...",
    "Orchestrating multi-layer verification protocols...",
    "Validating government authenticity markers...",
    "Finalizing high-fidelity data synthesis...",
    "Securing the decision-making perimeter...",
    "Readying the comprehensive insights report..."
  ];
  const [msgIdx, setMsgIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setMsgIdx(prev => (prev + 1) % engagementMessages.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    const target = status.progress;
    const interval = setInterval(() => {
        setDisplayProgress(prev => {
            if (prev < target) return Math.min(prev + 0.5, target);
            return prev;
        });
    }, 30);
    return () => clearInterval(interval);
  }, [status.progress]);

  return (
    <motion.div 
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="glass-card" 
      style={{ padding: '3rem', textAlign: 'center', maxWidth: '800px', margin: 'auto', width: '100%' }}
    >
      <div style={{ position: 'relative', width: '100px', height: '100px', margin: '0 auto 2rem' }}>
         <motion.div 
            animate={{ rotate: 360 }}
            transition={{ repeat: Infinity, duration: 4, ease: "linear" }}
            style={{ position: 'absolute', inset: 0, border: '2px dashed var(--primary)', borderRadius: '50%', opacity: 0.3 }}
         />
         <motion.div 
            animate={{ rotate: -360 }}
            transition={{ repeat: Infinity, duration: 2, ease: "linear" }}
            style={{ position: 'absolute', inset: '8px', border: '4px solid var(--accent-purple)', borderRadius: '50%', borderTopColor: 'transparent' }}
         />
         <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--primary)' }}>
            <Cpu size={36} />
         </div>
      </div>

      <h2 style={{ marginBottom: '0.75rem', fontSize: '1.75rem', fontWeight: '800' }}>{status.message}</h2>
      <motion.p 
        key={msgIdx}
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ color: 'var(--accent-purple)', marginBottom: '3rem', fontSize: '1.1rem', fontWeight: '500' }}
      >
        {engagementMessages[msgIdx]}
      </motion.p>

      <div style={{ width: '100%', height: '6px', background: 'var(--secondary)', borderRadius: '20px', overflow: 'hidden', marginBottom: '1rem', position: 'relative' }}>
        <motion.div 
          style={{ height: '100%', background: 'linear-gradient(90deg, var(--primary), var(--primary-light))', width: `${displayProgress}%` }}
        />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', color: 'var(--text-muted)', fontWeight: '800', letterSpacing: '1px' }}>
        <span>ENGINE OPERATIONAL</span>
        <span style={{ color: 'var(--primary)' }}>{Math.round(displayProgress)}% COMPLETE</span>
      </div>

      {status.error && (
        <motion.div 
          initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          style={{ marginTop: '2rem', padding: '1rem', background: '#fff5f5', border: '1px solid #feb2b2', color: 'var(--danger)', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '1rem' }}
        >
          <AlertCircle size={20} />
          <div style={{ textAlign: 'left' }}>
            <div style={{ fontWeight: 'bold', fontSize: '0.9rem' }}>Exception Detected</div>
            <div style={{ fontSize: '0.8rem' }}>{status.error}</div>
          </div>
        </motion.div>
      )}
    </motion.div>
  );
};

const ResultsStage = ({ results, previews, onReset }) => {
  const decision = results.decision || {};
  const analysis = decision.analysis || {};
  const extracted_data = analysis.extracted_data || {};
  const annotated_images = results.annotated_images || [];
  
  const [selectedImage, setSelectedImage] = useState(null);

  const statusColor = decision.status === 'APPROVED' ? 'var(--primary)' : 'var(--danger)';
  const statusIcon = decision.status === 'APPROVED' ? <ShieldCheck size={28} /> : <AlertCircle size={28} />;

  return (
    <motion.div 
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', flex: 1, minHeight: 0 }}
    >
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) 3fr', gap: '1.5rem', flex: 1, minHeight: 0 }}>
        {/* Statistics & Data Container */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', minHeight: 0 }}>
          <div className="glass-card" style={{ padding: '1.5rem', borderLeft: `6px solid ${statusColor}` }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem', color: statusColor, fontWeight: '800', fontSize: '0.75rem', letterSpacing: '1.5px' }}>
              {statusIcon} OVERALL STATUS
            </div>
            <h2 style={{ fontSize: '2.5rem', color: statusColor, fontWeight: '900', lineHeight: 1, marginBottom: '1rem' }}>{decision.status}</h2>
            <div style={{ background: 'rgba(0,0,0,0.03)', padding: '1rem', borderRadius: '12px' }}>
               <p style={{ color: 'var(--text-muted)', fontSize: '0.7rem', fontWeight: 'bold', marginBottom: '0.25rem' }}>ALLOCATED FUNDING</p>
               <h3 style={{ fontSize: '2rem', fontWeight: '800' }}>₹{(decision.scholarship_amount || 0).toLocaleString()}</h3>
            </div>
          </div>

          <div className="glass-card" style={{ padding: '1.5rem', flex: 1, overflowY: 'auto' }}>
             <h3 style={{ marginBottom: '1.25rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
               <Database size={18} style={{ color: 'var(--accent-purple)' }} /> Extracted Intelligence
             </h3>
             <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
               <DataRow label="Name" value={extracted_data.name} />
               <DataRow label="Guardian" value={extracted_data.guardian} />
               <DataRow label="DOB" value={extracted_data.dob} />
               <DataRow label="Merit Score" value={extracted_data.percentage?.includes('%') ? extracted_data.percentage : `${extracted_data.percentage}%`} />
               <DataRow label="Income" value={`₹${(extracted_data.income || 0).toLocaleString()}`} />
               <div style={{ height: '1px', background: 'var(--surface-border)', margin: '0.25rem 0' }} />
               <DataRow label="Consistency" value={analysis.data_consistency} color={analysis.data_consistency?.includes('100') ? 'var(--primary)' : 'var(--warning)'} />
               <DataRow label="Authenticity" value={analysis.authenticity_check} color={analysis.authenticity_check === 'PASSED' ? 'var(--primary)' : 'var(--danger)'} />
             </div>

             {decision.reasons?.length > 0 && (
                <div style={{ marginTop: '1.5rem' }}>
                  <p style={{ fontSize: '0.7rem', fontWeight: '800', color: 'var(--text-muted)', marginBottom: '0.75rem', letterSpacing: '1px' }}>SYSTEM NOTES</p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {decision.reasons.map((r, i) => (
                      <div key={i} style={{ fontSize: '0.8rem', color: 'var(--text-muted)', background: 'var(--background)', padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid var(--surface-border)' }}>
                        • {r}
                      </div>
                    ))}
                  </div>
                </div>
             )}
          </div>
          <motion.button 
            whileHover={{ scale: 1.01, backgroundColor: 'var(--primary)', color: 'white' }}
            whileTap={{ scale: 0.98 }}
            className="premium-button" 
            style={{ 
              width: '100%', 
              background: 'transparent', 
              color: 'var(--primary)', 
              border: '1px solid var(--primary)', 
              boxShadow: 'none',
              marginTop: '1rem',
              transition: 'all 0.2s ease'
            }}
            onClick={onReset}
          >
            Initiate New Analysis
          </motion.button>
        </div>

        {/* Visual Evidence - Divided in 2 parts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', minHeight: 0 }}>
          <div className="glass-card" style={{ padding: '1.5rem', display: 'flex', flexDirection: 'column', flex: 1, minHeight: 0 }}>
            <h3 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '1.1rem' }}>
              <Eye size={18} style={{ color: 'var(--accent-peach)' }} /> Source Document Validation
            </h3>
            
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', flex: 1, minHeight: 0 }}>
              {/* Part 1: Original Images */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minHeight: 0, background: 'rgba(84, 107, 65, 0.02)', padding: '1.25rem', borderRadius: '16px', border: '1px solid rgba(84, 107, 65, 0.05)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.75rem', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '900', color: 'var(--primary)', letterSpacing: '2px' }}>ORIGINAL SOURCE</span>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--primary)', opacity: 0.5 }}></div>
                </div>
                
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', overflowY: 'auto', paddingRight: '0.75rem', paddingBottom: '1rem' }}>
                  {['id_card', 'marksheet', 'income'].map(type => (
                    <motion.div 
                      key={type}
                      whileHover={{ y: -2 }}
                      className="document-preview-card"
                    >
                      <div className="card-image-wrapper" onClick={() => setSelectedImage(previews[type])}>
                        <div className="card-badge" style={{ background: 'white', color: 'var(--primary)' }}>ORIGINAL</div>
                        <img 
                          src={previews[type]} 
                          alt={type} 
                          style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
                        />
                        <div className="card-overlay">
                          <div style={{ background: 'white', padding: '10px', borderRadius: '50%', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', color: 'var(--primary)' }}>
                            <Search size={20} />
                          </div>
                        </div>
                      </div>
                      <div className="card-label">
                        {type.replace('_', ' ')}
                      </div>
                    </motion.div>
                  ))}
                </div>
              </div>

              {/* Part 2: Annotated Images */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', minHeight: 0, background: 'rgba(142, 122, 173, 0.02)', padding: '1.25rem', borderRadius: '16px', border: '1px solid rgba(142, 122, 173, 0.05)' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: '1px solid var(--surface-border)', paddingBottom: '0.75rem', marginBottom: '0.5rem' }}>
                  <span style={{ fontSize: '0.75rem', fontWeight: '900', color: 'var(--accent-purple)', letterSpacing: '2px' }}>AI DETECTION</span>
                  <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--accent-purple)', opacity: 0.5 }}></div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem', overflowY: 'auto', paddingRight: '0.75rem', paddingBottom: '1rem' }}>
                  {['id', 'marksheet', 'income'].map(type => {
                    const imgName = `uploaded_${type}.png`;
                    const hasAnnotated = annotated_images.includes(imgName);
                    const imgSrc = `${API_BASE}/api/images/${imgName}?t=${Date.now()}`;
                    
                    return (
                      <motion.div 
                        key={type}
                        whileHover={hasAnnotated ? { y: -2 } : {}}
                        className="document-preview-card"
                        style={{ opacity: hasAnnotated ? 1 : 0.7 }}
                      >
                        <div 
                          className="card-image-wrapper" 
                          style={{ cursor: hasAnnotated ? 'pointer' : 'default', background: hasAnnotated ? '#f8f9fa' : '#f1f2f6' }}
                          onClick={() => hasAnnotated && setSelectedImage(imgSrc)}
                        >
                          {hasAnnotated ? (
                            <>
                              <div className="card-badge" style={{ background: 'var(--accent-purple)', color: 'white' }}>AI LAYER</div>
                              <img 
                                src={imgSrc} 
                                alt={`Annotated ${type}`} 
                                style={{ width: '100%', height: '100%', objectFit: 'contain' }} 
                              />
                              <div className="card-overlay">
                                <div style={{ background: 'white', padding: '10px', borderRadius: '50%', boxShadow: '0 4px 12px rgba(0,0,0,0.1)', color: 'var(--accent-purple)' }}>
                                  <Zap size={20} />
                                </div>
                              </div>
                            </>
                          ) : (
                            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', color: 'var(--text-muted)', opacity: 0.5 }}>
                              <AlertCircle size={24} style={{ marginBottom: '0.5rem' }} />
                              <span style={{ fontSize: '0.7rem', fontWeight: '700' }}>PENDING DETECTION</span>
                            </div>
                          )}
                        </div>
                        <div className="card-label">
                          YOLO {type.replace('_', ' ')}
                        </div>
                      </motion.div>
                    );
                  })}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Fullscreen Image Viewer Modal */}
      <AnimatePresence>
        {selectedImage && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSelectedImage(null)}
            style={{ 
              position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.9)', zIndex: 1000, 
              display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem'
            }}
          >
            <motion.div 
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              style={{ maxWidth: '90%', maxHeight: '90%', position: 'relative' }}
              onClick={e => e.stopPropagation()}
            >
              <img src={selectedImage} alt="Fullscreen" style={{ maxWidth: '100%', maxHeight: '90vh', objectFit: 'contain', borderRadius: '8px' }} />
              <button 
                onClick={() => setSelectedImage(null)}
                style={{ position: 'absolute', top: '-40px', right: 0, background: 'white', border: 'none', borderRadius: '50%', width: '32px', height: '32px', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
              >
                <XCircle size={20} color="black" />
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};


const DataRow = ({ label, value, color }) => (
  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
    <span className="data-label">{label}</span>
    <span className="data-value" style={{ color: color || 'var(--text)' }}>{value || 'N/A'}</span>
  </div>
);

export default App;

