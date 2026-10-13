import React, { useState, useEffect, useRef } from 'react';
import {
  Sparkles,
  Send,
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  RotateCcw,
  Trash2,
  X,
  AlertCircle,
  HelpCircle,
  Cpu,
  BookOpen,
  Smile
} from 'lucide-react';
import { sendChatQuery, fetchChatStatus, ChatMessage } from '../api';

interface AskZoroWidgetProps {
  userRole?: string;
  userId?: string;
}

export const AskZoroWidget: React.FC<AskZoroWidgetProps> = ({ userRole = 'HOD / Admin', userId = 'admin' }) => {
  const [open, setOpen] = useState(false);
  const [mode, setMode] = useState<'vibe' | 'study'>('vibe');
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: 'assistant',
      content:
        '👋 **Hello! I am Zoro**, your DEXA AI Copilot powered by Google Gemini.\n\nAsk me anything about departmental analytics, student success scores, attendance risk patterns, or switch to Study Copilot for algorithms and placement interview guidance!'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [lastFailedMessage, setLastFailedMessage] = useState<string | null>(null);

  // Gemini Service Telemetry
  const [aiStatus, setAiStatus] = useState<{
    configured: boolean;
    sdk: string;
    preferred_model: string;
    status_message: string;
  } | null>(null);

  // Voice Input (Speech Recognition) State
  const [isRecording, setIsRecording] = useState(false);
  const [speechLang, setSpeechLang] = useState<'en-US' | 'ta-IN'>('en-US');
  const recognitionRef = useRef<any>(null);

  // Voice Output (Speech Synthesis) State
  const [speakingIdx, setSpeakingIdx] = useState<number | null>(null);
  const synthRef = useRef<SpeechSynthesis | null>(typeof window !== 'undefined' ? window.speechSynthesis : null);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Check Gemini API status
    fetchChatStatus()
      .then((st) => setAiStatus(st))
      .catch(() => setAiStatus(null));
  }, []);

  useEffect(() => {
    if (open) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, open]);

  // Clean markdown for text-to-speech
  const stripMarkdown = (text: string) => {
    return text
      .replace(/[*_#`~\[\]]/g, '')
      .replace(/https?:\/\/\S+/g, '')
      .replace(/\n+/g, ' ')
      .trim();
  };

  // Text-To-Speech Output
  const handleSpeak = (text: string, idx: number) => {
    if (!synthRef.current) return;

    if (speakingIdx === idx) {
      synthRef.current.cancel();
      setSpeakingIdx(null);
      return;
    }

    synthRef.current.cancel();
    const cleanText = stripMarkdown(text);
    const utterance = new SpeechSynthesisUtterance(cleanText);

    // Auto-detect language
    const hasTamil = /[\u0B80-\u0BFF]/.test(text);
    utterance.lang = hasTamil ? 'ta-IN' : 'en-US';
    utterance.rate = 1.0;

    utterance.onend = () => setSpeakingIdx(null);
    utterance.onerror = () => setSpeakingIdx(null);

    setSpeakingIdx(idx);
    synthRef.current.speak(utterance);
  };

  // Voice-To-Text Input
  const toggleSpeechRecognition = () => {
    const SpeechRecognition =
      (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;

    if (!SpeechRecognition) {
      alert('Speech Recognition is not supported in this browser. Please use Google Chrome or Microsoft Edge.');
      return;
    }

    if (isRecording) {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      setIsRecording(false);
      return;
    }

    try {
      const recognition = new SpeechRecognition();
      recognition.lang = speechLang;
      recognition.continuous = false;
      recognition.interimResults = true;

      recognition.onstart = () => {
        setIsRecording(true);
        setErrorMsg(null);
      };

      recognition.onresult = (event: any) => {
        const transcript = Array.from(event.results)
          .map((res: any) => res[0].transcript)
          .join('');
        setInput(transcript);
      };

      recognition.onerror = (event: any) => {
        console.error('Speech recognition error:', event.error);
        setIsRecording(false);
        if (event.error === 'not-allowed') {
          setErrorMsg('Microphone access denied. Please allow microphone permissions in your browser bar.');
        } else if (event.error !== 'no-speech') {
          setErrorMsg(`Voice transcription error: ${event.error}`);
        }
      };

      recognition.onend = () => {
        setIsRecording(false);
      };

      recognitionRef.current = recognition;
      recognition.start();
    } catch (err: any) {
      console.error('Failed to start speech recognition:', err);
      setIsRecording(false);
      setErrorMsg('Failed to initialize microphone.');
    }
  };

  // Send message to Gemini API
  const handleSend = async (overrideText?: string) => {
    const queryText = (overrideText || input).trim();
    if (!queryText) return;

    setErrorMsg(null);
    setLastFailedMessage(null);

    // Stop speaking if active
    if (synthRef.current) {
      synthRef.current.cancel();
      setSpeakingIdx(null);
    }

    const updatedMessages: ChatMessage[] = [...messages, { role: 'user', content: queryText }];
    setMessages(updatedMessages);
    setInput('');
    setLoading(true);

    try {
      // Send real multi-turn conversation context to Gemini API
      const res = await sendChatQuery(queryText, mode, messages, userRole, userId);

      setMessages([...updatedMessages, { role: 'assistant', content: res.content }]);

      // If missing key is detected, update status
      if (!res.configured) {
        setAiStatus((prev) => (prev ? { ...prev, configured: false } : null));
      }
    } catch (err: any) {
      console.error('Chat error:', err);
      setErrorMsg('Network or service exception connecting to DEXA Gemini server.');
      setLastFailedMessage(queryText);
      setMessages([
        ...updatedMessages,
        {
          role: 'assistant',
          content: '⚠️ **Request Failed**: Unable to communicate with the Gemini AI service. Check your connection or click **Retry** below.'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearHistory = () => {
    if (synthRef.current) synthRef.current.cancel();
    setSpeakingIdx(null);
    setMessages([
      {
        role: 'assistant',
        content: 'Conversation history cleared. How can I assist your student analytics review today?'
      }
    ]);
    setErrorMsg(null);
    setLastFailedMessage(null);
  };

  const samplePrompts =
    mode === 'study'
      ? [
          "Explain Dijkstra's Algorithm and its time complexity",
          "What is the difference between TCP and UDP?",
          "How can a student improve their coding score from 40 to 80?",
          "Explain Overfitting vs Underfitting in Machine Learning"
        ]
      : [
          "What are the main academic risk patterns in our 500 students?",
          "Which students need immediate attendance follow-up?",
          "Explain how DEXA's Student Success Score is calculated",
          "Why was student STU0005 flagged as high risk?"
        ];

  return (
    <div className="zoro-dock" style={{ zIndex: 1000 }}>
      {open ? (
        <div
          style={{
            width: '420px',
            height: '580px',
            maxWidth: 'calc(100vw - 32px)',
            maxHeight: 'calc(100vh - 40px)',
            backgroundColor: '#FFFFFF',
            border: '1px solid #CBD5E1',
            borderRadius: '16px',
            boxShadow: '0 16px 40px rgba(11, 19, 43, 0.22)',
            display: 'flex',
            flexDirection: 'column',
            overflow: 'hidden'
          }}
        >
          {/* HEADER */}
          <div
            style={{
              padding: '0.85rem 1.15rem',
              backgroundColor: '#0B132B',
              color: '#FFFFFF',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              borderBottom: '1px solid #1E293B'
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.65rem' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '8px',
                  backgroundColor: '#1E40AF',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(30,64,175,0.4)'
                }}
              >
                <Sparkles size={18} color="#FFFFFF" />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                  <span style={{ fontSize: '0.92rem', fontWeight: 800, color: '#FFFFFF' }}>Zoro Copilot</span>
                  <span
                    style={{
                      fontSize: '0.62rem',
                      padding: '1px 6px',
                      borderRadius: '4px',
                      backgroundColor: aiStatus?.configured ? '#059669' : '#D97706',
                      color: '#FFFFFF',
                      fontWeight: 700
                    }}
                  >
                    {aiStatus?.configured ? 'Gemini 2.5' : 'Key Setup'}
                  </span>
                </div>
                <div style={{ fontSize: '0.68rem', color: '#94A3B8' }}>
                  Real-Time Gemini AI • Department Telemetry
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <button
                onClick={handleClearHistory}
                title="Clear Conversation"
                style={{ background: 'transparent', border: 'none', color: '#94A3B8', cursor: 'pointer', padding: '4px' }}
              >
                <Trash2 size={16} />
              </button>
              <button
                onClick={() => {
                  if (synthRef.current) synthRef.current.cancel();
                  setOpen(false);
                }}
                style={{ background: 'transparent', border: 'none', color: '#94A3B8', cursor: 'pointer', padding: '4px' }}
              >
                <X size={18} />
              </button>
            </div>
          </div>

          {/* MODE & TELEMETRY STRIP */}
          <div
            style={{
              padding: '6px 10px',
              backgroundColor: '#F8FAFC',
              borderBottom: '1px solid #E2E8F0',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between'
            }}
          >
            <div style={{ display: 'flex', gap: '4px', flex: 1 }}>
              <button
                onClick={() => setMode('vibe')}
                style={{
                  flex: 1,
                  padding: '5px 8px',
                  borderRadius: '6px',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: mode === 'vibe' ? '#1E40AF' : '#E2E8F0',
                  color: mode === 'vibe' ? '#FFFFFF' : '#475569',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}
              >
                <Smile size={13} />
                <span>Vibe & Analytics</span>
              </button>
              <button
                onClick={() => setMode('study')}
                style={{
                  flex: 1,
                  padding: '5px 8px',
                  borderRadius: '6px',
                  fontSize: '0.74rem',
                  fontWeight: 700,
                  border: 'none',
                  cursor: 'pointer',
                  backgroundColor: mode === 'study' ? '#1E40AF' : '#E2E8F0',
                  color: mode === 'study' ? '#FFFFFF' : '#475569',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '4px'
                }}
              >
                <BookOpen size={13} />
                <span>Study & CS Prep</span>
              </button>
            </div>

            {/* Language toggle for Voice Recognition */}
            <button
              onClick={() => setSpeechLang(speechLang === 'en-US' ? 'ta-IN' : 'en-US')}
              title={`Voice Input Language: ${speechLang === 'en-US' ? 'English' : 'Tamil'}`}
              style={{
                marginLeft: '8px',
                padding: '4px 6px',
                borderRadius: '6px',
                fontSize: '0.68rem',
                fontWeight: 700,
                border: '1px solid #CBD5E1',
                backgroundColor: '#FFFFFF',
                color: '#334155',
                cursor: 'pointer'
              }}
            >
              {speechLang === 'en-US' ? 'EN 🇺🇸' : 'தமிழ் 🇮🇳'}
            </button>
          </div>

          {/* MESSAGES CONTAINER */}
          <div
            style={{
              flex: '1 1 0%',
              padding: '1rem',
              overflowY: 'auto',
              display: 'flex',
              flexDirection: 'column',
              gap: '0.75rem',
              backgroundColor: '#F8FAFC'
            }}
          >
            {messages.map((m, idx) => (
              <div
                key={idx}
                style={{
                  alignSelf: m.role === 'user' ? 'flex-end' : 'flex-start',
                  maxWidth: '88%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '4px'
                }}
              >
                <div
                  style={{
                    backgroundColor: m.role === 'user' ? '#1E40AF' : '#FFFFFF',
                    color: m.role === 'user' ? '#FFFFFF' : '#0F172A',
                    padding: '9px 13px',
                    borderRadius: m.role === 'user' ? '12px 12px 2px 12px' : '12px 12px 12px 2px',
                    fontSize: '0.82rem',
                    lineHeight: 1.5,
                    border: m.role === 'user' ? 'none' : '1px solid #E2E8F0',
                    boxShadow: '0 2px 6px rgba(15, 23, 42, 0.05)',
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word'
                  }}
                >
                  {m.content}
                </div>

                {/* Assistant Controls: Listen / TTS Button */}
                {m.role === 'assistant' && (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', paddingLeft: '4px' }}>
                    <button
                      onClick={() => handleSpeak(m.content, idx)}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: speakingIdx === idx ? '#1E40AF' : '#64748B',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '3px',
                        fontSize: '0.7rem',
                        fontWeight: 600,
                        padding: '2px 4px'
                      }}
                      title={speakingIdx === idx ? 'Stop Speaking' : 'Listen with Audio'}
                    >
                      {speakingIdx === idx ? <VolumeX size={13} /> : <Volume2 size={13} />}
                      <span>{speakingIdx === idx ? 'Stop' : 'Listen'}</span>
                    </button>
                  </div>
                )}
              </div>
            ))}

            {/* Loading Indicator */}
            {loading && (
              <div
                style={{
                  alignSelf: 'flex-start',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  backgroundColor: '#FFFFFF',
                  padding: '8px 12px',
                  borderRadius: '10px',
                  border: '1px solid #E2E8F0',
                  fontSize: '0.78rem',
                  color: '#475569'
                }}
              >
                <Cpu size={14} className="animate-spin text-blue-600" />
                <span>Gemini is generating verified response...</span>
              </div>
            )}

            {/* Error & Retry Banner */}
            {errorMsg && (
              <div
                style={{
                  backgroundColor: '#FEF2F2',
                  border: '1px solid #FECACA',
                  borderRadius: '8px',
                  padding: '8px 10px',
                  fontSize: '0.75rem',
                  color: '#DC2626',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                  <AlertCircle size={14} />
                  <span>{errorMsg}</span>
                </div>
                {lastFailedMessage && (
                  <button
                    onClick={() => handleSend(lastFailedMessage)}
                    style={{
                      background: '#DC2626',
                      color: '#FFFFFF',
                      border: 'none',
                      borderRadius: '4px',
                      padding: '2px 6px',
                      fontSize: '0.68rem',
                      fontWeight: 700,
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      gap: '2px'
                    }}
                  >
                    <RotateCcw size={11} />
                    <span>Retry</span>
                  </button>
                )}
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* SUGGESTED PROMPT CHIPS */}
          <div
            style={{
              padding: '6px 8px',
              backgroundColor: '#FFFFFF',
              borderTop: '1px solid #E2E8F0',
              display: 'flex',
              gap: '4px',
              overflowX: 'auto',
              whiteSpace: 'nowrap'
            }}
          >
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(p)}
                disabled={loading}
                style={{
                  background: '#F1F5F9',
                  border: '1px solid #CBD5E1',
                  borderRadius: '999px',
                  padding: '3px 10px',
                  fontSize: '0.7rem',
                  color: '#334155',
                  cursor: 'pointer',
                  flexShrink: 0
                }}
              >
                {p}
              </button>
            ))}
          </div>

          {/* INPUT BAR WITH VOICE INPUT BUTTON */}
          <div
            style={{
              padding: '10px',
              backgroundColor: '#FFFFFF',
              borderTop: '1px solid #E2E8F0',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            {/* Microphone Button (Speech to Text) */}
            <button
              onClick={toggleSpeechRecognition}
              title={isRecording ? 'Stop Recording' : `Speak in ${speechLang === 'en-US' ? 'English' : 'Tamil'}`}
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                border: isRecording ? '1px solid #DC2626' : '1px solid #CBD5E1',
                backgroundColor: isRecording ? '#FEF2F2' : '#F8FAFC',
                color: isRecording ? '#DC2626' : '#475569',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: 'pointer',
                flexShrink: 0
              }}
            >
              {isRecording ? <MicOff size={16} className="animate-pulse" /> : <Mic size={16} />}
            </button>

            {/* Text Input */}
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && !loading && handleSend()}
              placeholder={
                isRecording
                  ? `Listening in ${speechLang === 'en-US' ? 'English' : 'Tamil'}...`
                  : 'Ask Gemini about student success, risks, or CS topics...'
              }
              style={{
                flex: 1,
                padding: '7px 11px',
                borderRadius: '8px',
                border: isRecording ? '1px solid #DC2626' : '1px solid #CBD5E1',
                fontSize: '0.82rem',
                color: '#0F172A',
                outline: 'none',
                backgroundColor: isRecording ? '#FFF5F5' : '#FFFFFF'
              }}
              disabled={loading}
            />

            {/* Send Button */}
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              style={{
                width: '36px',
                height: '36px',
                borderRadius: '8px',
                backgroundColor: loading || !input.trim() ? '#94A3B8' : '#1E40AF',
                color: '#FFFFFF',
                border: 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
                flexShrink: 0,
                boxShadow: '0 2px 6px rgba(30,64,175,0.25)'
              }}
            >
              <Send size={15} />
            </button>
          </div>
        </div>
      ) : (
        <button
          onClick={() => setOpen(true)}
          style={{
            background: 'linear-gradient(135deg, #0B132B 0%, #1E40AF 100%)',
            color: '#FFFFFF',
            padding: '11px 20px',
            borderRadius: '9999px',
            boxShadow: '0 8px 24px rgba(11, 19, 43, 0.35)',
            fontWeight: 700,
            fontSize: '0.88rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '0.55rem',
            cursor: 'pointer',
            border: '1px solid rgba(255,255,255,0.15)',
            transition: 'transform 0.15s ease'
          }}
        >
          <Sparkles size={17} color="#60A5FA" />
          <span>Ask Zoro AI</span>
          <span
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: aiStatus?.configured ? '#10B981' : '#F59E0B'
            }}
          />
        </button>
      )}
    </div>
  );
};
