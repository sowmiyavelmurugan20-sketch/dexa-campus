import React, { useState, useRef } from 'react';
import { Mic, MicOff, X, Volume2, VolumeX, Sparkles, ArrowRight, Globe, AlertCircle } from 'lucide-react';
import { sendChatQuery } from '../api';

interface VoiceCopilotModalProps {
  onClose: () => void;
  onNavigateTab: (tabId: string) => void;
}

export const VoiceCopilotModal: React.FC<VoiceCopilotModalProps> = ({ onClose, onNavigateTab }) => {
  const [command, setCommand] = useState('Show students needing attendance follow-up');
  const [lang, setLang] = useState<'en-US' | 'ta-IN'>('en-US');
  const [isRecording, setIsRecording] = useState(false);
  const [loading, setLoading] = useState(false);
  const [speaking, setSpeaking] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const [aiResponse, setAiResponse] = useState<string>(
    'DEXA Telemetry indicates 186 students currently maintain attendance under the 75% cutoff threshold. Navigating to Attendance & Engagement to review the detention watchlist.'
  );

  const recognitionRef = useRef<any>(null);
  const synthRef = useRef<SpeechSynthesis | null>(typeof window !== 'undefined' ? window.speechSynthesis : null);

  const toggleRecording = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      setErrorMsg('Speech recognition is not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    if (isRecording) {
      if (recognitionRef.current) recognitionRef.current.stop();
      setIsRecording(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = lang;
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onstart = () => {
        setIsRecording(true);
        setErrorMsg(null);
      };

      recognition.onresult = (e: any) => {
        const text = Array.from(e.results)
          .map((r: any) => r[0].transcript)
          .join('');
        setCommand(text);
      };

      recognition.onerror = (e: any) => {
        console.error('Speech error:', e.error);
        setIsRecording(false);
        if (e.error === 'not-allowed') {
          setErrorMsg('Microphone access denied. Please allow microphone permissions in browser.');
        } else if (e.error !== 'no-speech') {
          setErrorMsg(`Voice transcription error: ${e.error}`);
        }
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      setIsRecording(false);
      setErrorMsg('Could not start microphone recording.');
    }
  };

  const handleProcessQuery = async (queryText?: string) => {
    const text = (queryText || command).trim();
    if (!text) return;

    if (synthRef.current) synthRef.current.cancel();
    setSpeaking(false);
    setLoading(true);
    setErrorMsg(null);

    try {
      const res = await sendChatQuery(text, 'vibe');
      setAiResponse(res.content);

      // Auto-trigger speech response if user spoke
      if ('speechSynthesis' in window) {
        handleSpeak(res.content);
      }
    } catch (err: any) {
      setErrorMsg('Failed to process voice query via Gemini.');
    } finally {
      setLoading(false);
    }
  };

  const handleSpeak = (textToSpeak?: string) => {
    if (!synthRef.current) return;

    if (speaking) {
      synthRef.current.cancel();
      setSpeaking(false);
      return;
    }

    synthRef.current.cancel();
    const cleanText = (textToSpeak || aiResponse)
      .replace(/[*_#`~\[\]]/g, '')
      .replace(/https?:\/\/\S+/g, '')
      .replace(/\n+/g, ' ')
      .trim();

    const utterance = new SpeechSynthesisUtterance(cleanText);
    const hasTamil = /[\u0B80-\u0BFF]/.test(cleanText);
    utterance.lang = hasTamil ? 'ta-IN' : 'en-US';

    utterance.onend = () => setSpeaking(false);
    utterance.onerror = () => setSpeaking(false);

    setSpeaking(true);
    synthRef.current.speak(utterance);
  };

  const handleExecuteIntent = () => {
    const q = command.toLowerCase();
    if (q.includes('risk') || q.includes('ஆபத்து') || q.includes('intervention')) {
      onNavigateTab('interventions');
    } else if (q.includes('attendance') || q.includes('வருகை') || q.includes('detention')) {
      onNavigateTab('attendance');
    } else if (q.includes('placement') || q.includes('வேலை') || q.includes('coding')) {
      onNavigateTab('placement');
    } else if (q.includes('student') || q.includes('மாணவர்') || q.includes('stu')) {
      onNavigateTab('students');
    } else {
      onNavigateTab('overview');
    }
    onClose();
  };

  return (
    <div className="drawer-backdrop" onClick={onClose} style={{ zIndex: 1100 }}>
      <div
        onClick={(e) => e.stopPropagation()}
        style={{
          backgroundColor: '#FFFFFF',
          borderRadius: '16px',
          padding: '1.75rem',
          width: '100%',
          maxWidth: '560px',
          margin: 'auto',
          boxShadow: '0 20px 50px rgba(15, 23, 42, 0.25)',
          border: '1px solid #E2E8F0'
        }}
      >
        {/* Header */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
            <div
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '10px',
                backgroundColor: '#1E40AF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                boxShadow: '0 4px 12px rgba(30,64,175,0.35)'
              }}
            >
              <Mic size={20} color="#FFFFFF" />
            </div>
            <div>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#0F172A', margin: 0 }}>
                Real Multilingual Voice Copilot
              </h3>
              <div style={{ fontSize: '0.74rem', color: '#64748B' }}>
                Speak in English or தமிழ் (Tamil) • Real Gemini AI Transcription & Audio
              </div>
            </div>
          </div>
          <button
            onClick={() => {
              if (synthRef.current) synthRef.current.cancel();
              onClose();
            }}
            style={{ background: 'none', border: 'none', color: '#64748B', cursor: 'pointer' }}
          >
            <X size={20} />
          </button>
        </div>

        {/* Language Selection & Voice Recording Bar */}
        <div
          style={{
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            borderRadius: '12px',
            padding: '1rem',
            marginBottom: '1rem',
            textAlign: 'center'
          }}
        >
          <div style={{ display: 'flex', justifyContent: 'center', gap: '8px', marginBottom: '1rem' }}>
            <button
              onClick={() => setLang('en-US')}
              style={{
                padding: '4px 12px',
                borderRadius: '999px',
                fontSize: '0.74rem',
                fontWeight: 700,
                border: lang === 'en-US' ? '1px solid #1E40AF' : '1px solid #CBD5E1',
                backgroundColor: lang === 'en-US' ? '#EFF6FF' : '#FFFFFF',
                color: lang === 'en-US' ? '#1E40AF' : '#475569',
                cursor: 'pointer'
              }}
            >
              English 🇺🇸
            </button>
            <button
              onClick={() => setLang('ta-IN')}
              style={{
                padding: '4px 12px',
                borderRadius: '999px',
                fontSize: '0.74rem',
                fontWeight: 700,
                border: lang === 'ta-IN' ? '1px solid #1E40AF' : '1px solid #CBD5E1',
                backgroundColor: lang === 'ta-IN' ? '#EFF6FF' : '#FFFFFF',
                color: lang === 'ta-IN' ? '#1E40AF' : '#475569',
                cursor: 'pointer'
              }}
            >
              தமிழ் (Tamil) 🇮🇳
            </button>
          </div>

          {/* Large Microphone Action Circle */}
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '0.5rem' }}>
            <button
              onClick={toggleRecording}
              style={{
                width: '64px',
                height: '64px',
                borderRadius: '50%',
                backgroundColor: isRecording ? '#DC2626' : '#1E40AF',
                color: '#FFFFFF',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                boxShadow: isRecording
                  ? '0 0 0 8px rgba(220, 38, 38, 0.25)'
                  : '0 4px 16px rgba(30, 64, 175, 0.35)',
                transition: 'all 0.2s ease'
              }}
            >
              {isRecording ? <MicOff size={28} className="animate-pulse" /> : <Mic size={28} />}
            </button>
            <div style={{ fontSize: '0.8rem', fontWeight: 700, color: isRecording ? '#DC2626' : '#334155' }}>
              {isRecording ? `Listening in ${lang === 'en-US' ? 'English' : 'Tamil'}... Tap to finish` : 'Tap to Speak Question'}
            </div>
          </div>
        </div>

        {/* Error notification if any */}
        {errorMsg && (
          <div
            style={{
              backgroundColor: '#FEF2F2',
              border: '1px solid #FECACA',
              color: '#DC2626',
              padding: '6px 10px',
              borderRadius: '8px',
              fontSize: '0.75rem',
              marginBottom: '0.85rem',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <AlertCircle size={14} />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Transcribed Speech / Command Review */}
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontSize: '0.74rem', fontWeight: 700, color: '#475569', marginBottom: '4px', textTransform: 'uppercase' }}>
            Transcribed User Question:
          </label>
          <div style={{ display: 'flex', gap: '6px' }}>
            <input
              type="text"
              value={command}
              onChange={(e) => setCommand(e.target.value)}
              placeholder="Your transcribed question will appear here..."
              style={{
                flex: 1,
                padding: '8px 12px',
                borderRadius: '8px',
                border: '1px solid #CBD5E1',
                fontSize: '0.85rem',
                color: '#0F172A',
                outline: 'none'
              }}
            />
            <button
              onClick={() => handleProcessQuery()}
              disabled={loading || !command.trim()}
              className="btn-primary"
              style={{ padding: '8px 14px', fontSize: '0.82rem', whiteSpace: 'nowrap' }}
            >
              {loading ? 'Analyzing...' : 'Ask Gemini'}
            </button>
          </div>
        </div>

        {/* Gemini Response Display Box */}
        <div
          style={{
            backgroundColor: '#F8FAFC',
            border: '1px solid #E2E8F0',
            borderRadius: '10px',
            padding: '1rem',
            marginBottom: '1.25rem',
            maxHeight: '160px',
            overflowY: 'auto'
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
            <span style={{ fontSize: '0.7rem', fontWeight: 700, color: '#1E40AF', textTransform: 'uppercase' }}>
              🤖 Gemini AI Response
            </span>
            <button
              onClick={() => handleSpeak()}
              style={{
                background: 'none',
                border: 'none',
                color: speaking ? '#1E40AF' : '#64748B',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '0.72rem',
                fontWeight: 700
              }}
            >
              {speaking ? <VolumeX size={14} /> : <Volume2 size={14} />}
              <span>{speaking ? 'Stop Audio' : 'Listen'}</span>
            </button>
          </div>
          <div style={{ fontSize: '0.82rem', color: '#0F172A', lineHeight: 1.5, whiteSpace: 'pre-wrap' }}>
            {aiResponse}
          </div>
        </div>

        {/* Footer Actions */}
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <button
            onClick={() => handleSpeak()}
            className="btn-secondary"
            style={{ flex: 1, padding: '0.65rem', justifyContent: 'center' }}
          >
            {speaking ? <VolumeX size={15} /> : <Volume2 size={15} />}
            <span>{speaking ? 'Stop Speaking' : 'Read Aloud'}</span>
          </button>

          <button
            onClick={handleExecuteIntent}
            className="btn-primary"
            style={{ flex: 1, padding: '0.65rem', justifyContent: 'center' }}
          >
            <span>Open Related Dashboard</span>
            <ArrowRight size={15} />
          </button>
        </div>
      </div>
    </div>
  );
};
