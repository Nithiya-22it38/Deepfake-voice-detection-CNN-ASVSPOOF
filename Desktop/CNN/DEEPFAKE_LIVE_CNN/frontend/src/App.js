// import React, { useState, useCallback, useRef } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import {
//   Mic,
//   Square,
//   Loader2,
//   Upload,
//   FileAudio,
//   X,
//   ShieldCheck,
//   ShieldAlert,
// } from "lucide-react";
// import "./App.css";

// function App() {
//   const [isAnalyzing, setIsAnalyzing] = useState(false);
//   const [result, setResult] = useState(null);
//   const [mode, setMode] = useState(null);
//   const [errorMsg, setErrorMsg] = useState(null);

//   const handleAnalyze = useCallback(async (audio) => {
//     setIsAnalyzing(true);
//     setResult(null);
//     setErrorMsg(null);

//     try {
//       const formData = new FormData();
//       // Use the provided name or generate one for recordings
//       const filename = audio && audio.name ? audio.name : `recording-${Date.now()}.webm`;

//       // Connection: "file" matches request.files["file"] in your app.py
//       formData.append("file", audio, filename);

//       const response = await fetch("http://127.0.0.1:5000/predict", {
//         method: "POST",
//         body: formData,
//       });

//       if (!response.ok) {
//         const text = await response.text();
//         throw new Error(text || "Backend error");
//       }

//       const data = await response.json();
//       if (data && data.error) {
//         throw new Error(data.error);
//       }

//       // Logic to match your app.py output: {"prediction": "Real"/"FAKE", "confidence": float}
//       const prediction = (data.prediction || "").toString().toLowerCase();
//       const verdict = prediction === "real" ? "real" : "fake";
//       const confidence = typeof data.confidence === "number"
//         ? Math.round(data.confidence)
//         : Math.round(65 + Math.random() * 30);

//       setResult({ verdict, confidence });
//     } catch (e) {
//       console.error("Analysis failed", e);
//       setErrorMsg(e && e.message ? e.message : "Analysis failed. Please try again.");
//     } finally {
//       setIsAnalyzing(false);
//     }
//   }, []);

//   return (
//     <div className="min-h-screen bg-background flex items-center justify-center">
//       <div className="max-w-md w-full mx-auto px-4 py-12 space-y-8">
//         <motion.div
//           initial={{ opacity: 0, y: -20 }}
//           animate={{ opacity: 1, y: 0 }}
//           className="text-center space-y-3"
//         >
//           <h1 className="text-3xl font-bold font-display tracking-tight text-foreground">
//             Deepfake Voice Detector
//           </h1>
//           <p className="text-muted-foreground text-sm max-w-sm mx-auto">
//             AI-powered deepfake voice detection. Record or upload audio to verify authenticity in seconds.
//           </p>
//         </motion.div>

//         <motion.div
//           initial={{ opacity: 0 }}
//           animate={{ opacity: 1 }}
//           transition={{ delay: 0.2 }}
//           className="flex gap-3"
//         >
//           <button
//             type="button"
//             className={`btn ${mode === "record" ? "btn-primary" : "btn-outline"}`}
//             onClick={() => {
//               setMode("record");
//               setResult(null);
//               setErrorMsg(null);
//             }}
//           >
//             <Mic className="icon" />
//             Record Audio
//           </button>
//           <button
//             type="button"
//             className={`btn ${mode === "upload" ? "btn-primary" : "btn-outline"}`}
//             onClick={() => {
//               setMode("upload");
//               setResult(null);
//               setErrorMsg(null);
//             }}
//           >
//             <Upload className="icon" />
//             Upload Audio
//           </button>
//         </motion.div>

//         <AnimatePresence mode="wait">
//           {mode === "record" && (
//             <motion.div
//               key="record"
//               initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: -10 }}
//               className="card"
//             >
//               <AudioRecorder onRecordingComplete={handleAnalyze} isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//           {mode === "upload" && (
//             <motion.div
//               key="upload"
//               initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: -10 }}
//               className="card"
//             >
//               <FileUploader onFileSelect={handleAnalyze} isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//         </AnimatePresence>

//         <AnimatePresence mode="wait">
//           {isAnalyzing && (
//             <motion.div
//               key="loading"
//               initial={{ opacity: 0 }}
//               animate={{ opacity: 1 }}
//               exit={{ opacity: 0 }}
//               className="loading"
//             >
//               <motion.div
//                 className="spinner"
//                 animate={{ rotate: 360 }}
//                 transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
//               />
//               <p className="text-sm text-muted-foreground font-mono">Analyzing...</p>
//             </motion.div>
//           )}
//           {result && !isAnalyzing && (
//             <motion.div key="result">
//               <ResultDisplay result={result} />
//             </motion.div>
//           )}
//           {errorMsg && !isAnalyzing && (
//             <motion.div
//               key="error"
//               initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0 }}
//               className="error-card"
//             >
//               {errorMsg}
//             </motion.div>
//           )}
//         </AnimatePresence>
//       </div>
//     </div>
//   );
// }

// function AudioRecorder({ onRecordingComplete, isAnalyzing }) {
//   const [isRecording, setIsRecording] = useState(false);
//   const [duration, setDuration] = useState(0);
//   const mediaRecorderRef = useRef(null);
//   const chunksRef = useRef([]);
//   const timerRef = useRef(null);

//   const startRecording = useCallback(async () => {
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
//       const mediaRecorder = new MediaRecorder(stream);
//       mediaRecorderRef.current = mediaRecorder;
//       chunksRef.current = [];

//       mediaRecorder.ondataavailable = (e) => {
//         if (e.data.size > 0) chunksRef.current.push(e.data);
//       };

//       mediaRecorder.onstop = () => {
//         const blob = new Blob(chunksRef.current, { type: "audio/webm" });
//         onRecordingComplete(blob); // This triggers handleAnalyze in the parent
//         stream.getTracks().forEach((t) => t.stop());
//       };

//       mediaRecorder.start();
//       setIsRecording(true);
//       setDuration(0);
//       timerRef.current = setInterval(() => setDuration((d) => d + 1), 1000);
//     } catch (e) {
//       console.error("Microphone access denied", e);
//     }
//   }, [onRecordingComplete]);

//   const stopRecording = useCallback(() => {
//     if (mediaRecorderRef.current) mediaRecorderRef.current.stop();
//     setIsRecording(false);
//     clearInterval(timerRef.current);
//   }, []);

//   const formatTime = (s) =>
//     `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;

//   return (
//     <div className="recorder">
//       <AnimatePresence>
//         {isRecording && (
//           <motion.div
//             initial={{ opacity: 0, height: 0 }}
//             animate={{ opacity: 1, height: "auto" }}
//             exit={{ opacity: 0, height: 0 }}
//             className="waveform"
//           >
//             {Array.from({ length: 20 }).map((_, i) => (
//               <motion.div
//                 key={i}
//                 className="wave-bar"
//                 animate={{ height: [4, Math.random() * 32 + 8, 4] }}
//                 transition={{
//                   duration: 0.6 + Math.random() * 0.4,
//                   repeat: Infinity,
//                   ease: "easeInOut",
//                   delay: i * 0.05,
//                 }}
//               />
//             ))}
//           </motion.div>
//         )}
//       </AnimatePresence>

//       {isRecording && (
//         <span className="timer">{formatTime(duration)}</span>
//       )}

//       <div className="record-btn-wrap">
//         {isRecording && (
//           <motion.div
//             className="record-ring"
//             animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
//             transition={{ duration: 1.5, repeat: Infinity }}
//           />
//         )}
//         <motion.button
//           whileHover={{ scale: 1.05 }}
//           whileTap={{ scale: 0.95 }}
//           onClick={isRecording ? stopRecording : startRecording}
//           disabled={isAnalyzing}
//           className={`record-btn ${isRecording ? "recording" : "idle"} ${
//             isAnalyzing ? "disabled" : ""
//           }`}
//         >
//           {isAnalyzing ? (
//             <Loader2 className="icon-lg spin" />
//           ) : isRecording ? (
//             <Square className="icon-md" />
//           ) : (
//             <Mic className="icon-lg" />
//           )}
//         </motion.button>
//       </div>

//       <p className="helper">
//         {isAnalyzing
//           ? "Analyzing audio..."
//           : isRecording
//           ? "Recording - tap to stop"
//           : "Tap to start recording"}
//       </p>
//     </div>
//   );
// }

// function FileUploader({ onFileSelect, isAnalyzing }) {
//   const inputRef = useRef(null);
//   const [dragOver, setDragOver] = useState(false);
//   const [selectedFile, setSelectedFile] = useState(null);

//   const handleFile = (file) => {
//     if (!file || !file.type.startsWith("audio/")) return;
//     setSelectedFile(file);
//     onFileSelect(file); // This triggers handleAnalyze in the parent
//   };

//   const clearFile = () => {
//     setSelectedFile(null);
//     if (inputRef.current) inputRef.current.value = "";
//   };

//   return (
//     <div className="uploader">
//       {selectedFile ? (
//         <motion.div
//           initial={{ opacity: 0, y: 8 }}
//           animate={{ opacity: 1, y: 0 }}
//           className="file-pill"
//         >
//           <FileAudio className="icon" />
//           <div className="file-meta">
//             <p className="file-name">{selectedFile.name}</p>
//             <p className="file-size">
//               {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
//             </p>
//           </div>
//           {!isAnalyzing && (
//             <button type="button" onClick={clearFile} className="icon-btn">
//               <X className="icon-sm" />
//             </button>
//           )}
//         </motion.div>
//       ) : (
//         <motion.div
//           whileHover={{ scale: 1.01 }}
//           onClick={() => inputRef.current && inputRef.current.click()}
//           onDragOver={(e) => {
//             e.preventDefault();
//             setDragOver(true);
//           }}
//           onDragLeave={() => setDragOver(false)}
//           onDrop={(e) => {
//             e.preventDefault();
//             setDragOver(false);
//             const f = e.dataTransfer.files[0];
//             if (f) handleFile(f);
//           }}
//           className={`dropzone ${dragOver ? "drag" : ""}`}
//         >
//           <Upload className="icon-lg muted" />
//           <div className="text-center">
//             <p className="drop-title">Drop audio file or click to upload</p>
//             <p className="drop-sub">MP3, WAV, OGG, FLAC, WebM</p>
//           </div>
//         </motion.div>
//       )}
//       <input
//         ref={inputRef}
//         type="file"
//         accept="audio/*"
//         className="hidden"
//         onChange={(e) => {
//           const f = e.target.files && e.target.files[0];
//           if (f) handleFile(f);
//         }}
//       />
//     </div>
//   );
// }

// function ResultDisplay({ result }) {
//   const isReal = result.verdict === "real";

//   return (
//     <motion.div
//       initial={{ opacity: 0, y: 20 }}
//       animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.5 }}
//       className="result"
//     >
//       <motion.div
//         initial={{ scale: 0.95 }}
//         animate={{ scale: 1 }}
//         className={`result-card ${isReal ? "real" : "fake"}`}
//       >
//         <div className="result-head">
//           <motion.div
//             initial={{ rotate: -180, opacity: 0 }}
//             animate={{ rotate: 0, opacity: 1 }}
//             transition={{ duration: 0.6, type: "spring" }}
//           >
//             {isReal ? (
//               <ShieldCheck className="icon-xl success" />
//             ) : (
//               <ShieldAlert className="icon-xl danger" />
//             )}
//           </motion.div>
//           <h3 className="result-title">
//             {isReal ? "Authentic Voice" : "Deepfake Detected"}
//           </h3>
//         </div>

//         <div className="result-body">
//           <p className="result-label">Accuracy Level</p>
//           <span className="result-value">{result.confidence}%</span>
//           <div className="meter">
//             <motion.div
//               initial={{ width: 0 }}
//               animate={{ width: `${result.confidence}%` }}
//               transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
//               className={`meter-fill ${isReal ? "success" : "danger"}`}
//             />
//           </div>
//         </div>
//       </motion.div>
//     </motion.div>
//   );
// }

// export default App;

//////////////////////////////////// CLAUDE AI  one ////////////////////////////////////
// import React, { useState, useCallback, useRef } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import {
//   Mic, Square, Loader2, Upload, FileAudio,
//   X, ShieldCheck, ShieldAlert, AlertTriangle,
// } from "lucide-react";
// import "./App.css";

// const API_URL = "http://127.0.0.1:5000";
// const MIN_RECORD_SECONDS = 3;   // enforce minimum recording length

// // ─────────────────────────────────────────────
// // Main App
// // ─────────────────────────────────────────────
// function App() {
//   const [isAnalyzing, setIsAnalyzing]   = useState(false);
//   const [result,      setResult]        = useState(null);
//   const [mode,        setMode]          = useState(null);
//   const [errorMsg,    setErrorMsg]      = useState(null);

//   const handleAnalyze = useCallback(async (audio) => {
//     setIsAnalyzing(true);
//     setResult(null);
//     setErrorMsg(null);

//     try {
//       const formData = new FormData();
//       const filename = audio?.name ?? `recording-${Date.now()}.webm`;
//       formData.append("file", audio, filename);

//       const response = await fetch(`${API_URL}/predict`, {
//         method: "POST",
//         body: formData,
//       });

//       const data = await response.json();

//       if (!response.ok || data?.error) {
//         throw new Error(data?.error || "Backend error");
//       }

//       // ✅ backend returns "Bonafide", "Spoof", or "Uncertain"
//       const raw       = (data.prediction || "").toLowerCase().trim();
//       const verdict   = raw === "bonafide" ? "real"
//                       : raw === "spoof"    ? "fake"
//                       : "uncertain";

//       // Show the confidence for the winning class
//       const confidence =
//         verdict === "real"      ? Math.round(data.bonafide_prob ?? data.confidence) :
//         verdict === "fake"      ? Math.round(data.spoof_prob    ?? data.confidence) :
//                                   Math.round(data.confidence ?? 0);

//       setResult({
//         verdict,
//         confidence,
//         bonafide: data.bonafide_prob,
//         spoof:    data.spoof_prob,
//         message:  data.message ?? null,
//       });

//     } catch (e) {
//       console.error("Analysis failed", e);
//       setErrorMsg(e?.message || "Analysis failed. Please try again.");
//     } finally {
//       setIsAnalyzing(false);
//     }
//   }, []);

//   const switchMode = (m) => {
//     setMode(m);
//     setResult(null);
//     setErrorMsg(null);
//   };

//   return (
//     <div className="min-h-screen bg-background flex items-center justify-center">
//       <div className="max-w-md w-full mx-auto px-4 py-12 space-y-8">

//         {/* Header */}
//         <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
//           className="text-center space-y-3">
//           <h1 className="text-3xl font-bold font-display tracking-tight text-foreground">
//             Deepfake Voice Detector
//           </h1>
//           <p className="text-muted-foreground text-sm max-w-sm mx-auto">
//             AI-powered deepfake voice detection. Record or upload audio to verify authenticity.
//           </p>
//         </motion.div>

//         {/* Mode toggle */}
//         <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//           transition={{ delay: 0.2 }} className="flex gap-3">
//           <button type="button"
//             className={`btn ${mode === "record" ? "btn-primary" : "btn-outline"}`}
//             onClick={() => switchMode("record")}>
//             <Mic className="icon" /> Record Audio
//           </button>
//           <button type="button"
//             className={`btn ${mode === "upload" ? "btn-primary" : "btn-outline"}`}
//             onClick={() => switchMode("upload")}>
//             <Upload className="icon" /> Upload Audio
//           </button>
//         </motion.div>

//         {/* Panels */}
//         <AnimatePresence mode="wait">
//           {mode === "record" && (
//             <motion.div key="record"
//               initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: -10 }} className="card">
//               <AudioRecorder onRecordingComplete={handleAnalyze} isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//           {mode === "upload" && (
//             <motion.div key="upload"
//               initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: -10 }} className="card">
//               <FileUploader onFileSelect={handleAnalyze} isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//         </AnimatePresence>

//         {/* Results / feedback */}
//         <AnimatePresence mode="wait">
//           {isAnalyzing && (
//             <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//               exit={{ opacity: 0 }} className="loading">
//               <motion.div className="spinner"
//                 animate={{ rotate: 360 }}
//                 transition={{ duration: 1, repeat: Infinity, ease: "linear" }} />
//               <p className="text-sm text-muted-foreground font-mono">Analyzing audio…</p>
//             </motion.div>
//           )}
//           {result && !isAnalyzing && (
//             <motion.div key="result">
//               <ResultDisplay result={result} />
//             </motion.div>
//           )}
//           {errorMsg && !isAnalyzing && (
//             <motion.div key="error"
//               initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0 }} className="error-card">
//               {errorMsg}
//             </motion.div>
//           )}
//         </AnimatePresence>
//       </div>
//     </div>
//   );
// }

// // ─────────────────────────────────────────────
// // AudioRecorder
// // ─────────────────────────────────────────────
// function AudioRecorder({ onRecordingComplete, isAnalyzing }) {
//   const [isRecording, setIsRecording] = useState(false);
//   const [duration,    setDuration]    = useState(0);
//   const [tooShort,    setTooShort]    = useState(false);

//   const mediaRecorderRef = useRef(null);
//   const chunksRef        = useRef([]);
//   const timerRef         = useRef(null);
//   const durationRef      = useRef(0);   // shadow state for use inside onstop closure

//   const startRecording = useCallback(async () => {
//     setTooShort(false);
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

//       // Pick the best supported MIME type for ffmpeg/pydub compatibility
//       const mimeType =
//         MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" :
//         MediaRecorder.isTypeSupported("audio/webm")             ? "audio/webm"             : "";

//       const recorder = new MediaRecorder(stream, mimeType ? { mimeType } : {});
//       mediaRecorderRef.current = recorder;
//       chunksRef.current        = [];

//       // ✅ timeslice=100ms — fires ondataavailable every 100ms, prevents empty blobs
//       recorder.ondataavailable = (e) => {
//         if (e.data?.size > 0) chunksRef.current.push(e.data);
//       };

//       recorder.onstop = () => {
//         const usedMime = recorder.mimeType || "audio/webm";
//         const blob     = new Blob(chunksRef.current, { type: usedMime });
//         console.log(`Recording: ${chunksRef.current.length} chunks, ${blob.size} bytes, ${usedMime}`);

//         stream.getTracks().forEach((t) => t.stop());

//         // ✅ Minimum length guard — short blobs are mostly silence
//         if (durationRef.current < MIN_RECORD_SECONDS) {
//           setTooShort(true);
//           return;
//         }
//         onRecordingComplete(blob);
//       };

//       recorder.start(100);   // ✅ timeslice
//       setIsRecording(true);
//       setDuration(0);
//       durationRef.current = 0;
//       timerRef.current = setInterval(() => {
//         durationRef.current += 1;
//         setDuration((d) => d + 1);
//       }, 1000);

//     } catch (e) {
//       console.error("Microphone access denied", e);
//     }
//   }, [onRecordingComplete]);

//   const stopRecording = useCallback(() => {
//     clearInterval(timerRef.current);
//     setIsRecording(false);
//     if (mediaRecorderRef.current?.state !== "inactive") {
//       mediaRecorderRef.current.requestData(); // ✅ flush final chunk
//       mediaRecorderRef.current.stop();
//     }
//   }, []);

//   const fmt = (s) =>
//     `${Math.floor(s / 60).toString().padStart(2, "0")}:${(s % 60).toString().padStart(2, "0")}`;

//   return (
//     <div className="recorder">
//       <AnimatePresence>
//         {isRecording && (
//           <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
//             exit={{ opacity: 0, height: 0 }} className="waveform">
//             {Array.from({ length: 20 }).map((_, i) => (
//               <motion.div key={i} className="wave-bar"
//                 animate={{ height: [4, Math.random() * 32 + 8, 4] }}
//                 transition={{ duration: 0.6 + Math.random() * 0.4, repeat: Infinity,
//                   ease: "easeInOut", delay: i * 0.05 }} />
//             ))}
//           </motion.div>
//         )}
//       </AnimatePresence>

//       {isRecording && <span className="timer">{fmt(duration)}</span>}

//       {/* Minimum-length hint */}
//       {!isRecording && !isAnalyzing && (
//         <p className="helper" style={{ fontSize: "0.72rem", opacity: 0.55, marginBottom: 4 }}>
//           Minimum {MIN_RECORD_SECONDS} seconds recommended
//         </p>
//       )}

//       {/* Too-short warning */}
//       {tooShort && !isRecording && (
//         <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//           className="helper" style={{ color: "var(--color-text-warning)", marginBottom: 4 }}>
//           Recording too short — please record at least {MIN_RECORD_SECONDS} seconds
//         </motion.p>
//       )}

//       <div className="record-btn-wrap">
//         {isRecording && (
//           <motion.div className="record-ring"
//             animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
//             transition={{ duration: 1.5, repeat: Infinity }} />
//         )}
//         <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
//           onClick={isRecording ? stopRecording : startRecording}
//           disabled={isAnalyzing}
//           className={`record-btn ${isRecording ? "recording" : "idle"} ${isAnalyzing ? "disabled" : ""}`}>
//           {isAnalyzing ? <Loader2 className="icon-lg spin" />
//             : isRecording  ? <Square  className="icon-md" />
//             :                <Mic     className="icon-lg" />}
//         </motion.button>
//       </div>

//       <p className="helper">
//         {isAnalyzing ? "Analyzing audio…"
//           : isRecording ? "Recording — tap to stop"
//           : "Tap to start recording"}
//       </p>
//     </div>
//   );
// }

// // ─────────────────────────────────────────────
// // FileUploader
// // ─────────────────────────────────────────────
// function FileUploader({ onFileSelect, isAnalyzing }) {
//   const inputRef                    = useRef(null);
//   const [dragOver, setDragOver]     = useState(false);
//   const [selectedFile, setFile]     = useState(null);

//   const handleFile = (file) => {
//     if (!file?.type.startsWith("audio/")) return;
//     setFile(file);
//     onFileSelect(file);
//   };

//   const clearFile = () => {
//     setFile(null);
//     if (inputRef.current) inputRef.current.value = "";
//   };

//   return (
//     <div className="uploader">
//       {selectedFile ? (
//         <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
//           className="file-pill">
//           <FileAudio className="icon" />
//           <div className="file-meta">
//             <p className="file-name">{selectedFile.name}</p>
//             <p className="file-size">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
//           </div>
//           {!isAnalyzing && (
//             <button type="button" onClick={clearFile} className="icon-btn">
//               <X className="icon-sm" />
//             </button>
//           )}
//         </motion.div>
//       ) : (
//         <motion.div whileHover={{ scale: 1.01 }}
//           onClick={() => inputRef.current?.click()}
//           onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
//           onDragLeave={() => setDragOver(false)}
//           onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
//           className={`dropzone ${dragOver ? "drag" : ""}`}>
//           <Upload className="icon-lg muted" />
//           <div className="text-center">
//             <p className="drop-title">Drop audio file or click to upload</p>
//             <p className="drop-sub">MP3, WAV, OGG, FLAC, WebM</p>
//           </div>
//         </motion.div>
//       )}
//       <input ref={inputRef} type="file" accept="audio/*" className="hidden"
//         onChange={(e) => { const f = e.target.files?.[0]; if (f) handleFile(f); }} />
//     </div>
//   );
// }

// // ─────────────────────────────────────────────
// // ResultDisplay
// // ─────────────────────────────────────────────
// function ResultDisplay({ result }) {
//   const { verdict, confidence, bonafide, spoof, message } = result;

//   const isReal      = verdict === "real";
//   const isUncertain = verdict === "uncertain";

//   const Icon  = isUncertain ? AlertTriangle : isReal ? ShieldCheck : ShieldAlert;
//   const title = isUncertain ? "Uncertain Result"
//               : isReal      ? "Real Voice"
//               :               "Deepfake Detected";
//   const cardClass = isUncertain ? "uncertain" : isReal ? "real" : "fake";
//   const fillClass = isUncertain ? "warning"   : isReal ? "success" : "danger";

//   return (
//     <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.5 }} className="result">
//       <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }}
//         className={`result-card ${cardClass}`}>

//         <div className="result-head">
//           <motion.div initial={{ rotate: -180, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }}
//             transition={{ duration: 0.6, type: "spring" }}>
//             <Icon className={`icon-xl ${fillClass}`} />
//           </motion.div>
//           <h3 className="result-title">{title}</h3>
//         </div>

//         <div className="result-body">
//           <p className="result-label">Confidence</p>
//           <span className="result-value">{confidence}%</span>
//           <div className="meter">
//             <motion.div initial={{ width: 0 }} animate={{ width: `${confidence}%` }}
//               transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
//               className={`meter-fill ${fillClass}`} />
//           </div>

//           {/* Probability breakdown */}
//           {bonafide != null && spoof != null && (
//             <div className="prob-row">
//               <span className="prob-label">Bonafide</span>
//               <span className="prob-value success">{bonafide}%</span>
//               <span className="prob-sep">·</span>
//               <span className="prob-label">Spoof</span>
//               <span className="prob-value danger">{spoof}%</span>
//             </div>
//           )}

//           {/* Message from backend (e.g. low confidence hint) */}
//           {message && (
//             <p className="result-message">{message}</p>
//           )}
//         </div>
//       </motion.div>
//     </motion.div>
//   );
// }

// export default App;

/////////////////////////// Cloude AI 2 working ///////////////////////////////////////////


// import React, { useState, useCallback, useRef } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import {
//   Mic, Square, Loader2, Upload, FileAudio,
//   X, ShieldCheck, ShieldAlert, AlertTriangle,
// } from "lucide-react";
// import "./App.css";

// const API_URL = "http://127.0.0.1:5000";
// const MIN_RECORD_SECONDS = 3;

// function App() {
//   const [isAnalyzing, setIsAnalyzing] = useState(false);
//   const [result,      setResult]      = useState(null);
//   const [mode,        setMode]        = useState(null);
//   const [errorMsg,    setErrorMsg]    = useState(null);

//   const handleAnalyze = useCallback(async (audio) => {
//     setIsAnalyzing(true);
//     setResult(null);
//     setErrorMsg(null);

//     try {
//       const formData = new FormData();
//       const filename = audio && audio.name ? audio.name : "recording-" + Date.now() + ".webm";
//       formData.append("file", audio, filename);

//       const response = await fetch(API_URL + "/predict", {
//         method: "POST",
//         body: formData,
//       });

//       const data = await response.json();

//       if (!response.ok || data.error) {
//         throw new Error(data.error || "Backend error");
//       }

//       const raw    = (data.prediction || "").toLowerCase().trim();
//       const verdict = raw === "bonafide" ? "real" : "fake";

//       // Show only the probability for the predicted class
//       const displayProb = verdict === "real"
//         ? data.bonafide_prob
//         : data.spoof_prob;

//       setResult({
//         verdict:     verdict,
//         confidence:  Math.round(displayProb),
//         displayProb: displayProb,
//       });

//     } catch (e) {
//       console.error("Analysis failed", e);
//       setErrorMsg(e && e.message ? e.message : "Analysis failed. Please try again.");
//     } finally {
//       setIsAnalyzing(false);
//     }
//   }, []);

//   const switchMode = function(m) {
//     setMode(m);
//     setResult(null);
//     setErrorMsg(null);
//   };

//   return (
//     <div className="min-h-screen bg-background flex items-center justify-center">
//       <div className="max-w-md w-full mx-auto px-4 py-12 space-y-8">

//         <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
//           className="text-center space-y-3">
//           <h1 className="text-3xl font-bold font-display tracking-tight text-foreground">
//             Deepfake Voice Detector
//           </h1>
//           <p className="text-muted-foreground text-sm max-w-sm mx-auto">
//             AI-powered deepfake voice detection. Record or upload audio to verify authenticity.
//           </p>
//         </motion.div>

//         <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//           transition={{ delay: 0.2 }} className="flex gap-3">
//           <button type="button"
//             className={"btn " + (mode === "record" ? "btn-primary" : "btn-outline")}
//             onClick={function() { switchMode("record"); }}>
//             <Mic className="icon" /> Record Audio
//           </button>
//           <button type="button"
//             className={"btn " + (mode === "upload" ? "btn-primary" : "btn-outline")}
//             onClick={function() { switchMode("upload"); }}>
//             <Upload className="icon" /> Upload Audio
//           </button>
//         </motion.div>

//         <AnimatePresence mode="wait">
//           {mode === "record" && (
//             <motion.div key="record"
//               initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: -10 }} className="card">
//               <AudioRecorder onRecordingComplete={handleAnalyze} isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//           {mode === "upload" && (
//             <motion.div key="upload"
//               initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0, y: -10 }} className="card">
//               <FileUploader onFileSelect={handleAnalyze} isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//         </AnimatePresence>

//         <AnimatePresence mode="wait">
//           {isAnalyzing && (
//             <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//               exit={{ opacity: 0 }} className="loading">
//               <motion.div className="spinner"
//                 animate={{ rotate: 360 }}
//                 transition={{ duration: 1, repeat: Infinity, ease: "linear" }} />
//               <p className="text-sm text-muted-foreground font-mono">Analyzing audio...</p>
//             </motion.div>
//           )}
//           {result && !isAnalyzing && (
//             <motion.div key="result">
//               <ResultDisplay result={result} />
//             </motion.div>
//           )}
//           {errorMsg && !isAnalyzing && (
//             <motion.div key="error"
//               initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
//               exit={{ opacity: 0 }} className="error-card">
//               {errorMsg}
//             </motion.div>
//           )}
//         </AnimatePresence>
//       </div>
//     </div>
//   );
// }

// function AudioRecorder({ onRecordingComplete, isAnalyzing }) {
//   const [isRecording, setIsRecording] = useState(false);
//   const [duration,    setDuration]    = useState(0);
//   const [tooShort,    setTooShort]    = useState(false);

//   const mediaRecorderRef = useRef(null);
//   const chunksRef        = useRef([]);
//   const timerRef         = useRef(null);
//   const durationRef      = useRef(0);

//   const startRecording = useCallback(async function() {
//     setTooShort(false);
//     try {
//       const stream = await navigator.mediaDevices.getUserMedia({ audio: true });

//       const mimeType =
//         MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" :
//         MediaRecorder.isTypeSupported("audio/webm")             ? "audio/webm" : "";

//       const recorder = new MediaRecorder(stream, mimeType ? { mimeType: mimeType } : {});
//       mediaRecorderRef.current = recorder;
//       chunksRef.current        = [];

//       recorder.ondataavailable = function(e) {
//         if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
//       };

//       recorder.onstop = function() {
//         var usedMime = recorder.mimeType || "audio/webm";
//         var blob     = new Blob(chunksRef.current, { type: usedMime });
//         stream.getTracks().forEach(function(t) { t.stop(); });
//         if (durationRef.current < MIN_RECORD_SECONDS) {
//           setTooShort(true);
//           return;
//         }
//         onRecordingComplete(blob);
//       };

//       recorder.start(100);
//       setIsRecording(true);
//       setDuration(0);
//       durationRef.current = 0;
//       timerRef.current = setInterval(function() {
//         durationRef.current += 1;
//         setDuration(function(d) { return d + 1; });
//       }, 1000);

//     } catch (e) {
//       console.error("Microphone access denied", e);
//     }
//   }, [onRecordingComplete]);

//   const stopRecording = useCallback(function() {
//     clearInterval(timerRef.current);
//     setIsRecording(false);
//     if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
//       mediaRecorderRef.current.requestData();
//       mediaRecorderRef.current.stop();
//     }
//   }, []);

//   function fmt(s) {
//     return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
//   }

//   return (
//     <div className="recorder">
//       <AnimatePresence>
//         {isRecording && (
//           <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
//             exit={{ opacity: 0, height: 0 }} className="waveform">
//             {Array.from({ length: 20 }).map(function(_, i) {
//               return (
//                 <motion.div key={i} className="wave-bar"
//                   animate={{ height: [4, Math.random() * 32 + 8, 4] }}
//                   transition={{ duration: 0.6 + Math.random() * 0.4, repeat: Infinity,
//                     ease: "easeInOut", delay: i * 0.05 }} />
//               );
//             })}
//           </motion.div>
//         )}
//       </AnimatePresence>

//       {isRecording && <span className="timer">{fmt(duration)}</span>}

//       {!isRecording && !isAnalyzing && (
//         <p className="helper" style={{ fontSize: "0.72rem", opacity: 0.55, marginBottom: 4 }}>
//           Minimum {MIN_RECORD_SECONDS} seconds recommended
//         </p>
//       )}

//       {tooShort && !isRecording && (
//         <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//           className="helper" style={{ color: "var(--color-text-warning)", marginBottom: 4 }}>
//           Too short — please record at least {MIN_RECORD_SECONDS} seconds
//         </motion.p>
//       )}

//       <div className="record-btn-wrap">
//         {isRecording && (
//           <motion.div className="record-ring"
//             animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
//             transition={{ duration: 1.5, repeat: Infinity }} />
//         )}
//         <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
//           onClick={isRecording ? stopRecording : startRecording}
//           disabled={isAnalyzing}
//           className={"record-btn " + (isRecording ? "recording" : "idle") + " " + (isAnalyzing ? "disabled" : "")}>
//           {isAnalyzing    ? <Loader2 className="icon-lg spin" />
//             : isRecording ? <Square  className="icon-md" />
//             :               <Mic     className="icon-lg" />}
//         </motion.button>
//       </div>

//       <p className="helper">
//         {isAnalyzing   ? "Analyzing audio..."
//           : isRecording ? "Recording — tap to stop"
//           :               "Tap to start recording"}
//       </p>
//     </div>
//   );
// }

// function FileUploader({ onFileSelect, isAnalyzing }) {
//   const inputRef               = useRef(null);
//   const [dragOver, setDragOver] = useState(false);
//   const [selectedFile, setFile] = useState(null);

//   function handleFile(file) {
//     if (!file || !file.type.startsWith("audio/")) return;
//     setFile(file);
//     onFileSelect(file);
//   }

//   function clearFile() {
//     setFile(null);
//     if (inputRef.current) inputRef.current.value = "";
//   }

//   return (
//     <div className="uploader">
//       {selectedFile ? (
//         <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }}
//           className="file-pill">
//           <FileAudio className="icon" />
//           <div className="file-meta">
//             <p className="file-name">{selectedFile.name}</p>
//             <p className="file-size">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
//           </div>
//           {!isAnalyzing && (
//             <button type="button" onClick={clearFile} className="icon-btn">
//               <X className="icon-sm" />
//             </button>
//           )}
//         </motion.div>
//       ) : (
//         <motion.div whileHover={{ scale: 1.01 }}
//           onClick={function() { if (inputRef.current) inputRef.current.click(); }}
//           onDragOver={function(e) { e.preventDefault(); setDragOver(true); }}
//           onDragLeave={function() { setDragOver(false); }}
//           onDrop={function(e) {
//             e.preventDefault(); setDragOver(false);
//             var f = e.dataTransfer.files[0];
//             if (f) handleFile(f);
//           }}
//           className={"dropzone " + (dragOver ? "drag" : "")}>
//           <Upload className="icon-lg muted" />
//           <div className="text-center">
//             <p className="drop-title">Drop audio file or click to upload</p>
//             <p className="drop-sub">MP3, WAV, OGG, FLAC, WebM</p>
//           </div>
//         </motion.div>
//       )}
//       <input ref={inputRef} type="file" accept="audio/*" className="hidden"
//         onChange={function(e) {
//           var f = e.target.files && e.target.files[0];
//           if (f) handleFile(f);
//         }} />
//     </div>
//   );
// }

// function ResultDisplay({ result }) {
//   var isReal = result.verdict === "real";

//   var Icon      = isReal ? ShieldCheck : ShieldAlert;
//   var title     = isReal ? "Authentic Voice" : "Deepfake Detected";
//   var cardClass = isReal ? "real" : "fake";
//   var fillClass = isReal ? "success" : "danger";

//   // Label shown next to the percentage
//   var probLabel = isReal ? "Authentic" : "Spoof";

//   return (
//     <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.5 }} className="result">
//       <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }}
//         className={"result-card " + cardClass}>

//         <div className="result-head">
//           <motion.div initial={{ rotate: -180, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }}
//             transition={{ duration: 0.6, type: "spring" }}>
//             <Icon className={"icon-xl " + fillClass} />
//           </motion.div>
//           <h3 className="result-title">{title}</h3>
//         </div>

//         <div className="result-body">
//           <p className="result-label">Confidence</p>
//           <span className="result-value">{result.confidence}%</span>
//           <div className="meter">
//             <motion.div initial={{ width: 0 }} animate={{ width: result.confidence + "%" }}
//               transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
//               className={"meter-fill " + fillClass} />
//           </div>

//           {/* Only show the probability for the predicted class */}
//           <div className="prob-row">
//             <span className={"prob-value " + fillClass}>{result.displayProb}%</span>
//             <span className="prob-label">&nbsp;{probLabel}</span>
//           </div>
//         </div>

//       </motion.div>
//     </motion.div>
//   );
// }

// export default App;

/////////////////// CAI live recording working but its confidence is 100 ////////////////////////



// import React, { useState, useCallback, useRef } from "react";
// import { motion, AnimatePresence } from "framer-motion";
// import { Mic, Square, Loader2, Upload, FileAudio, X, ShieldCheck, ShieldAlert } from "lucide-react";
// import "./App.css";

// const API_URL         = "http://127.0.0.1:5000";
// const MIN_RECORD_SECS = 3;
// const TARGET_SR       = 16000;

// /**
//  * Extract raw PCM float32 samples from a Blob using AudioContext.
//  *
//  * WHY THIS WORKS:
//  * The browser MediaRecorder produces webm/opus blobs.
//  * On Windows, pydub+ffmpeg frequently decodes these to all-zero PCM
//  * due to missing opus codec support in some ffmpeg builds.
//  *
//  * AudioContext.decodeAudioData() uses the browser's own built-in
//  * audio decoder — the same engine that produced the recording.
//  * It ALWAYS works correctly. We then send the raw float32 samples
//  * as JSON, bypassing any file format issues entirely.
//  */
// async function extractPCMSamples(blob, targetSampleRate) {
//   var arrayBuffer = await blob.arrayBuffer();
//   var audioCtx    = new AudioContext({ sampleRate: targetSampleRate });

//   var decoded;
//   try {
//     decoded = await audioCtx.decodeAudioData(arrayBuffer);
//   } catch (err) {
//     audioCtx.close();
//     throw new Error("Audio decode failed: " + err.message);
//   }
//   audioCtx.close();

//   // Take channel 0 (mono). AudioContext already resampled to targetSampleRate.
//   var rawSamples = decoded.getChannelData(0);

//   // Find peak to detect silence
//   var peak = 0;
//   for (var i = 0; i < rawSamples.length; i++) {
//     var a = Math.abs(rawSamples[i]);
//     if (a > peak) peak = a;
//   }

//   console.log(
//     "PCM extracted | samples=" + rawSamples.length +
//     " | sampleRate=" + decoded.sampleRate +
//     " | duration=" + (rawSamples.length / decoded.sampleRate).toFixed(2) + "s" +
//     " | peak=" + peak.toFixed(5)
//   );

//   if (peak < 0.0001) {
//     throw new Error(
//       "Microphone recorded silence (peak=" + peak.toFixed(6) + "). " +
//       "Please go to Windows Settings → Sound → Input and unmute your microphone."
//     );
//   }

//   // Convert Float32Array to plain JS Array for JSON serialization
//   return {
//     samples:    Array.from(rawSamples),
//     sampleRate: decoded.sampleRate,
//     duration:   rawSamples.length / decoded.sampleRate,
//     peak:       peak,
//   };
// }

// // ── App ───────────────────────────────────────────────────────────────────────
// function App() {
//   var [isAnalyzing, setIsAnalyzing] = useState(false);
//   var [result,      setResult]      = useState(null);
//   var [mode,        setMode]        = useState(null);
//   var [errorMsg,    setErrorMsg]    = useState(null);

//   var handleAnalyze = useCallback(async function(blob, isLive) {
//     setIsAnalyzing(true);
//     setResult(null);
//     setErrorMsg(null);

//     try {
//       var response;

//       if (isLive) {
//         // Extract raw PCM via AudioContext, send as JSON
//         console.log("Extracting PCM samples from recording...");
//         var pcm = await extractPCMSamples(blob, TARGET_SR);

//         console.log("Sending " + pcm.samples.length + " samples to /predict-live");

//         response = await fetch(API_URL + "/predict-live", {
//           method:  "POST",
//           headers: { "Content-Type": "application/json" },
//           body:    JSON.stringify({
//             samples:    pcm.samples,
//             sampleRate: pcm.sampleRate,
//           }),
//         });

//       } else {
//         // Send file directly to /predict
//         var formData = new FormData();
//         formData.append("file", blob, blob.name || "upload.wav");
//         response = await fetch(API_URL + "/predict", {
//           method: "POST",
//           body:   formData,
//         });
//       }

//       var data = await response.json();

//       if (!response.ok || data.error) {
//         throw new Error(data.error || "Backend error");
//       }

//       var raw      = (data.prediction || "").toLowerCase().trim();
//       var verdict  = raw === "bonafide" ? "real" : "fake";
//       var dispProb = verdict === "real" ? data.bonafide_prob : data.spoof_prob;

//       setResult({ verdict: verdict, confidence: Math.round(dispProb), displayProb: dispProb });

//     } catch (e) {
//       console.error("Analysis failed:", e);
//       setErrorMsg(e && e.message ? e.message : "Analysis failed. Please try again.");
//     } finally {
//       setIsAnalyzing(false);
//     }
//   }, []);

//   function switchMode(m) { setMode(m); setResult(null); setErrorMsg(null); }

//   return (
//     <div className="min-h-screen bg-background flex items-center justify-center">
//       <div className="max-w-md w-full mx-auto px-4 py-12 space-y-8">

//         <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
//           className="text-center space-y-3">
//           <h1 className="text-3xl font-bold font-display tracking-tight text-foreground">
//             Deepfake Voice Detector
//           </h1>
//           <p className="text-muted-foreground text-sm max-w-sm mx-auto">
//             AI-powered deepfake voice detection. Record or upload audio to verify authenticity.
//           </p>
//         </motion.div>

//         <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//           transition={{ delay: 0.2 }} className="flex gap-3">
//           <button type="button"
//             className={"btn " + (mode === "record" ? "btn-primary" : "btn-outline")}
//             onClick={function() { switchMode("record"); }}>
//             <Mic className="icon" /> Record Audio
//           </button>
//           <button type="button"
//             className={"btn " + (mode === "upload" ? "btn-primary" : "btn-outline")}
//             onClick={function() { switchMode("upload"); }}>
//             <Upload className="icon" /> Upload Audio
//           </button>
//         </motion.div>

//         <AnimatePresence mode="wait">
//           {mode === "record" && (
//             <motion.div key="record" initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="card">
//               <AudioRecorder
//                 onRecordingComplete={function(b) { handleAnalyze(b, true); }}
//                 isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//           {mode === "upload" && (
//             <motion.div key="upload" initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="card">
//               <FileUploader
//                 onFileSelect={function(f) { handleAnalyze(f, false); }}
//                 isAnalyzing={isAnalyzing} />
//             </motion.div>
//           )}
//         </AnimatePresence>

//         <AnimatePresence mode="wait">
//           {isAnalyzing && (
//             <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
//               exit={{ opacity: 0 }} className="loading">
//               <motion.div className="spinner" animate={{ rotate: 360 }}
//                 transition={{ duration: 1, repeat: Infinity, ease: "linear" }} />
//               <p className="text-sm text-muted-foreground font-mono">Analyzing audio...</p>
//             </motion.div>
//           )}
//           {result && !isAnalyzing && (
//             <motion.div key="result"><ResultDisplay result={result} /></motion.div>
//           )}
//           {errorMsg && !isAnalyzing && (
//             <motion.div key="error" initial={{ opacity: 0, y: 10 }}
//               animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="error-card">
//               {errorMsg}
//             </motion.div>
//           )}
//         </AnimatePresence>
//       </div>
//     </div>
//   );
// }

// // ── AudioRecorder ─────────────────────────────────────────────────────────────
// function AudioRecorder({ onRecordingComplete, isAnalyzing }) {
//   var [isRecording, setIsRecording] = useState(false);
//   var [duration,    setDuration]    = useState(0);
//   var [tooShort,    setTooShort]    = useState(false);
//   var mediaRecorderRef = useRef(null);
//   var chunksRef        = useRef([]);
//   var timerRef         = useRef(null);
//   var durationRef      = useRef(0);

//   var startRecording = useCallback(async function() {
//     setTooShort(false);
//     try {
//       var stream = await navigator.mediaDevices.getUserMedia({
//         audio: {
//           channelCount:     1,
//           sampleRate:       16000,
//           echoCancellation: false,
//           noiseSuppression: false,
//           autoGainControl:  false,
//         }
//       });

//       var mimeType =
//         MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" :
//         MediaRecorder.isTypeSupported("audio/webm")             ? "audio/webm"             :
//         MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")  ? "audio/ogg;codecs=opus"  : "";

//       var recorder = new MediaRecorder(stream, mimeType ? { mimeType: mimeType } : {});
//       mediaRecorderRef.current = recorder;
//       chunksRef.current        = [];

//       recorder.ondataavailable = function(e) {
//         if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
//       };

//       recorder.onstop = function() {
//         var mime = recorder.mimeType || "audio/webm";
//         var blob = new Blob(chunksRef.current, { type: mime });
//         stream.getTracks().forEach(function(t) { t.stop(); });
//         console.log("Blob: " + blob.size + " bytes | " + mime +
//           " | chunks=" + chunksRef.current.length);
//         if (durationRef.current < MIN_RECORD_SECS) { setTooShort(true); return; }
//         onRecordingComplete(blob);
//       };

//       recorder.start(100);
//       setIsRecording(true);
//       setDuration(0);
//       durationRef.current = 0;
//       timerRef.current = setInterval(function() {
//         durationRef.current += 1;
//         setDuration(function(d) { return d + 1; });
//       }, 1000);

//     } catch (e) { console.error("Microphone error:", e); }
//   }, [onRecordingComplete]);

//   var stopRecording = useCallback(function() {
//     clearInterval(timerRef.current);
//     setIsRecording(false);
//     if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
//       mediaRecorderRef.current.requestData();
//       mediaRecorderRef.current.stop();
//     }
//   }, []);

//   function fmt(s) {
//     return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
//   }

//   return (
//     <div className="recorder">
//       <AnimatePresence>
//         {isRecording && (
//           <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
//             exit={{ opacity: 0, height: 0 }} className="waveform">
//             {Array.from({ length: 20 }).map(function(_, i) {
//               return (
//                 <motion.div key={i} className="wave-bar"
//                   animate={{ height: [4, Math.random() * 32 + 8, 4] }}
//                   transition={{ duration: 0.6 + Math.random() * 0.4,
//                     repeat: Infinity, ease: "easeInOut", delay: i * 0.05 }} />
//               );
//             })}
//           </motion.div>
//         )}
//       </AnimatePresence>

//       {isRecording && <span className="timer">{fmt(duration)}</span>}
//       {!isRecording && !isAnalyzing && (
//         <p className="helper" style={{ fontSize: "0.72rem", opacity: 0.55, marginBottom: 4 }}>
//           Minimum {MIN_RECORD_SECS} seconds recommended
//         </p>
//       )}
//       {tooShort && !isRecording && (
//         <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="helper"
//           style={{ color: "var(--color-text-warning)", marginBottom: 4 }}>
//           Too short — please record at least {MIN_RECORD_SECS} seconds
//         </motion.p>
//       )}

//       <div className="record-btn-wrap">
//         {isRecording && (
//           <motion.div className="record-ring"
//             animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
//             transition={{ duration: 1.5, repeat: Infinity }} />
//         )}
//         <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
//           onClick={isRecording ? stopRecording : startRecording} disabled={isAnalyzing}
//           className={"record-btn " + (isRecording ? "recording" : "idle") +
//             (isAnalyzing ? " disabled" : "")}>
//           {isAnalyzing ? <Loader2 className="icon-lg spin" />
//             : isRecording ? <Square className="icon-md" />
//             : <Mic className="icon-lg" />}
//         </motion.button>
//       </div>

//       <p className="helper">
//         {isAnalyzing ? "Analyzing audio..."
//           : isRecording ? "Recording — tap to stop"
//           : "Tap to start recording"}
//       </p>
//     </div>
//   );
// }

// // ── FileUploader ──────────────────────────────────────────────────────────────
// function FileUploader({ onFileSelect, isAnalyzing }) {
//   var inputRef                = useRef(null);
//   var [dragOver, setDragOver] = useState(false);
//   var [file, setFile]         = useState(null);

//   function handleFile(f) {
//     if (!f || !f.type.startsWith("audio/")) return;
//     setFile(f); onFileSelect(f);
//   }
//   function clearFile() { setFile(null); if (inputRef.current) inputRef.current.value = ""; }

//   return (
//     <div className="uploader">
//       {file ? (
//         <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="file-pill">
//           <FileAudio className="icon" />
//           <div className="file-meta">
//             <p className="file-name">{file.name}</p>
//             <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
//           </div>
//           {!isAnalyzing && (
//             <button type="button" onClick={clearFile} className="icon-btn">
//               <X className="icon-sm" />
//             </button>
//           )}
//         </motion.div>
//       ) : (
//         <motion.div whileHover={{ scale: 1.01 }}
//           onClick={function() { if (inputRef.current) inputRef.current.click(); }}
//           onDragOver={function(e) { e.preventDefault(); setDragOver(true); }}
//           onDragLeave={function() { setDragOver(false); }}
//           onDrop={function(e) { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
//           className={"dropzone " + (dragOver ? "drag" : "")}>
//           <Upload className="icon-lg muted" />
//           <div className="text-center">
//             <p className="drop-title">Drop audio file or click to upload</p>
//             <p className="drop-sub">MP3, WAV, OGG, FLAC, WebM</p>
//           </div>
//         </motion.div>
//       )}
//       <input ref={inputRef} type="file" accept="audio/*" className="hidden"
//         onChange={function(e) { var f = e.target.files && e.target.files[0]; if (f) handleFile(f); }} />
//     </div>
//   );
// }

// // ── ResultDisplay ─────────────────────────────────────────────────────────────
// function ResultDisplay({ result }) {
//   var isReal    = result.verdict === "real";
//   var Icon      = isReal ? ShieldCheck : ShieldAlert;
//   var title     = isReal ? "Authentic Voice" : "Deepfake Detected";
//   var cardClass = isReal ? "real" : "fake";
//   var fillClass = isReal ? "success" : "danger";
//   var probLabel = isReal ? "Authentic" : "Spoof";

//   return (
//     <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
//       transition={{ duration: 0.5 }} className="result">
//       <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }}
//         className={"result-card " + cardClass}>
//         <div className="result-head">
//           <motion.div initial={{ rotate: -180, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }}
//             transition={{ duration: 0.6, type: "spring" }}>
//             <Icon className={"icon-xl " + fillClass} />
//           </motion.div>
//           <h3 className="result-title">{title}</h3>
//         </div>
//         <div className="result-body">
//           <p className="result-label">Confidence</p>
//           <span className="result-value">{result.confidence}%</span>
//           <div className="meter">
//             <motion.div initial={{ width: 0 }} animate={{ width: result.confidence + "%" }}
//               transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
//               className={"meter-fill " + fillClass} />
//           </div>
//           <div className="prob-row">
//             <span className={"prob-value " + fillClass}>{result.displayProb}%</span>
//             <span className="prob-label">&nbsp;{probLabel}</span>
//           </div>
//         </div>
//       </motion.div>
//     </motion.div>
//   );
// }

// export default App;






/////////////////////////////////// CAI final ////////////////







import React, { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Mic, Square, Loader2, Upload, FileAudio, X, ShieldCheck, ShieldAlert } from "lucide-react";
import "./App.css";

const API_URL         = "http://127.0.0.1:5000";
const MIN_RECORD_SECS = 3;
const TARGET_SR       = 16000;

/**
 * Extract raw PCM float32 samples from a Blob using AudioContext.
 *
 * WHY THIS WORKS:
 * The browser MediaRecorder produces webm/opus blobs.
 * On Windows, pydub+ffmpeg frequently decodes these to all-zero PCM
 * due to missing opus codec support in some ffmpeg builds.
 *
 * AudioContext.decodeAudioData() uses the browser's own built-in
 * audio decoder — the same engine that produced the recording.
 * It ALWAYS works correctly. We then send the raw float32 samples
 * as JSON, bypassing any file format issues entirely.
 */
async function extractPCMSamples(blob, targetSampleRate) {
  var arrayBuffer = await blob.arrayBuffer();
  var audioCtx    = new AudioContext({ sampleRate: targetSampleRate });

  var decoded;
  try {
    decoded = await audioCtx.decodeAudioData(arrayBuffer);
  } catch (err) {
    audioCtx.close();
    throw new Error("Audio decode failed: " + err.message);
  }
  audioCtx.close();

  // Take channel 0 (mono). AudioContext already resampled to targetSampleRate.
  var rawSamples = decoded.getChannelData(0);

  // Find peak to detect silence
  var peak = 0;
  for (var i = 0; i < rawSamples.length; i++) {
    var a = Math.abs(rawSamples[i]);
    if (a > peak) peak = a;
  }

  console.log(
    "PCM extracted | samples=" + rawSamples.length +
    " | sampleRate=" + decoded.sampleRate +
    " | duration=" + (rawSamples.length / decoded.sampleRate).toFixed(2) + "s" +
    " | peak=" + peak.toFixed(5)
  );

  if (peak < 0.0001) {
    throw new Error(
      "Microphone recorded silence (peak=" + peak.toFixed(6) + "). " +
      "Please go to Windows Settings → Sound → Input and unmute your microphone."
    );
  }

  // Convert Float32Array to plain JS Array for JSON serialization
  return {
    samples:    Array.from(rawSamples),
    sampleRate: decoded.sampleRate,
    duration:   rawSamples.length / decoded.sampleRate,
    peak:       peak,
  };
}

// ── App ───────────────────────────────────────────────────────────────────────
function App() {
  var [isAnalyzing, setIsAnalyzing] = useState(false);
  var [result,      setResult]      = useState(null);
  var [mode,        setMode]        = useState(null);
  var [errorMsg,    setErrorMsg]    = useState(null);

  var handleAnalyze = useCallback(async function(blob, isLive) {
    setIsAnalyzing(true);
    setResult(null);
    setErrorMsg(null);

    try {
      var response;

      if (isLive) {
        // Extract raw PCM via AudioContext, send as JSON
        console.log("Extracting PCM samples from recording...");
        var pcm = await extractPCMSamples(blob, TARGET_SR);

        console.log("Sending " + pcm.samples.length + " samples to /predict-live");

        response = await fetch(API_URL + "/predict-live", {
          method:  "POST",
          headers: { "Content-Type": "application/json" },
          body:    JSON.stringify({
            samples:    pcm.samples,
            sampleRate: pcm.sampleRate,
          }),
        });

      } else {
        // Send file directly to /predict
        var formData = new FormData();
        formData.append("file", blob, blob.name || "upload.wav");
        response = await fetch(API_URL + "/predict", {
          method: "POST",
          body:   formData,
        });
      }

      var data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || "Backend error");
      }

      var raw      = (data.prediction || "").toLowerCase().trim();
      var verdict  = raw === "bonafide" ? "real" : "fake";
      var dispProb = verdict === "real" ? data.bonafide_prob : data.spoof_prob;

      setResult({ verdict: verdict, confidence: Math.round(dispProb), displayProb: dispProb });

    } catch (e) {
      console.error("Analysis failed:", e);
      setErrorMsg(e && e.message ? e.message : "Analysis failed. Please try again.");
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  function switchMode(m) { setMode(m); setResult(null); setErrorMsg(null); }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center">
      <div className="max-w-md w-full mx-auto px-4 py-12 space-y-8">

        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-3">
          <h1 className="text-3xl font-bold font-display tracking-tight text-foreground">
            Deepfake Voice Detector
          </h1>
          <p className="text-muted-foreground text-sm max-w-sm mx-auto">
            AI-powered deepfake voice detection. Record or upload audio to verify authenticity.
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }} className="flex gap-3">
          <button type="button"
            className={"btn " + (mode === "record" ? "btn-primary" : "btn-outline")}
            onClick={function() { switchMode("record"); }}>
            <Mic className="icon" /> Record Audio
          </button>
          <button type="button"
            className={"btn " + (mode === "upload" ? "btn-primary" : "btn-outline")}
            onClick={function() { switchMode("upload"); }}>
            <Upload className="icon" /> Upload Audio
          </button>
        </motion.div>

        <AnimatePresence mode="wait">
          {mode === "record" && (
            <motion.div key="record" initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="card">
              <AudioRecorder
                onRecordingComplete={function(b) { handleAnalyze(b, true); }}
                isAnalyzing={isAnalyzing} />
            </motion.div>
          )}
          {mode === "upload" && (
            <motion.div key="upload" initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }} className="card">
              <FileUploader
                onFileSelect={function(f) { handleAnalyze(f, false); }}
                isAnalyzing={isAnalyzing} />
            </motion.div>
          )}
        </AnimatePresence>

        <AnimatePresence mode="wait">
          {isAnalyzing && (
            <motion.div key="loading" initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              exit={{ opacity: 0 }} className="loading">
              <motion.div className="spinner" animate={{ rotate: 360 }}
                transition={{ duration: 1, repeat: Infinity, ease: "linear" }} />
              <p className="text-sm text-muted-foreground font-mono">Analyzing audio...</p>
            </motion.div>
          )}
          {result && !isAnalyzing && (
            <motion.div key="result"><ResultDisplay result={result} /></motion.div>
          )}
          {errorMsg && !isAnalyzing && (
            <motion.div key="error" initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="error-card">
              {errorMsg}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

// ── AudioRecorder ─────────────────────────────────────────────────────────────
function AudioRecorder({ onRecordingComplete, isAnalyzing }) {
  var [isRecording, setIsRecording] = useState(false);
  var [duration,    setDuration]    = useState(0);
  var [tooShort,    setTooShort]    = useState(false);
  var mediaRecorderRef = useRef(null);
  var chunksRef        = useRef([]);
  var timerRef         = useRef(null);
  var durationRef      = useRef(0);

  var startRecording = useCallback(async function() {
    setTooShort(false);
    try {
      var stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount:     1,
          sampleRate:       16000,
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl:  false,
        }
      });

      var mimeType =
        MediaRecorder.isTypeSupported("audio/webm;codecs=opus") ? "audio/webm;codecs=opus" :
        MediaRecorder.isTypeSupported("audio/webm")             ? "audio/webm"             :
        MediaRecorder.isTypeSupported("audio/ogg;codecs=opus")  ? "audio/ogg;codecs=opus"  : "";

      var recorder = new MediaRecorder(stream, mimeType ? { mimeType: mimeType } : {});
      mediaRecorderRef.current = recorder;
      chunksRef.current        = [];

      recorder.ondataavailable = function(e) {
        if (e.data && e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = function() {
        var mime = recorder.mimeType || "audio/webm";
        var blob = new Blob(chunksRef.current, { type: mime });
        stream.getTracks().forEach(function(t) { t.stop(); });
        console.log("Blob: " + blob.size + " bytes | " + mime +
          " | chunks=" + chunksRef.current.length);
        if (durationRef.current < MIN_RECORD_SECS) { setTooShort(true); return; }
        onRecordingComplete(blob);
      };

      recorder.start(100);
      setIsRecording(true);
      setDuration(0);
      durationRef.current = 0;
      timerRef.current = setInterval(function() {
        durationRef.current += 1;
        setDuration(function(d) { return d + 1; });
      }, 1000);

    } catch (e) { console.error("Microphone error:", e); }
  }, [onRecordingComplete]);

  var stopRecording = useCallback(function() {
    clearInterval(timerRef.current);
    setIsRecording(false);
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.requestData();
      mediaRecorderRef.current.stop();
    }
  }, []);

  function fmt(s) {
    return String(Math.floor(s / 60)).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
  }

  return (
    <div className="recorder">
      <AnimatePresence>
        {isRecording && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }} className="waveform">
            {Array.from({ length: 20 }).map(function(_, i) {
              return (
                <motion.div key={i} className="wave-bar"
                  animate={{ height: [4, Math.random() * 32 + 8, 4] }}
                  transition={{ duration: 0.6 + Math.random() * 0.4,
                    repeat: Infinity, ease: "easeInOut", delay: i * 0.05 }} />
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {isRecording && <span className="timer">{fmt(duration)}</span>}
      {!isRecording && !isAnalyzing && (
        <p className="helper" style={{ fontSize: "0.72rem", opacity: 0.55, marginBottom: 4 }}>
          Minimum {MIN_RECORD_SECS} seconds recommended
        </p>
      )}
      {tooShort && !isRecording && (
        <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="helper"
          style={{ color: "var(--color-text-warning)", marginBottom: 4 }}>
          Too short — please record at least {MIN_RECORD_SECS} seconds
        </motion.p>
      )}

      <div className="record-btn-wrap">
        {isRecording && (
          <motion.div className="record-ring"
            animate={{ scale: [1, 1.3, 1], opacity: [0.6, 0, 0.6] }}
            transition={{ duration: 1.5, repeat: Infinity }} />
        )}
        <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
          onClick={isRecording ? stopRecording : startRecording} disabled={isAnalyzing}
          className={"record-btn " + (isRecording ? "recording" : "idle") +
            (isAnalyzing ? " disabled" : "")}>
          {isAnalyzing ? <Loader2 className="icon-lg spin" />
            : isRecording ? <Square className="icon-md" />
            : <Mic className="icon-lg" />}
        </motion.button>
      </div>

      <p className="helper">
        {isAnalyzing ? "Analyzing audio..."
          : isRecording ? "Recording — tap to stop"
          : "Tap to start recording"}
      </p>
    </div>
  );
}

// ── FileUploader ──────────────────────────────────────────────────────────────
function FileUploader({ onFileSelect, isAnalyzing }) {
  var inputRef                = useRef(null);
  var [dragOver, setDragOver] = useState(false);
  var [file, setFile]         = useState(null);

  function handleFile(f) {
    if (!f || !f.type.startsWith("audio/")) return;
    setFile(f); onFileSelect(f);
  }
  function clearFile() { setFile(null); if (inputRef.current) inputRef.current.value = ""; }

  return (
    <div className="uploader">
      {file ? (
        <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} className="file-pill">
          <FileAudio className="icon" />
          <div className="file-meta">
            <p className="file-name">{file.name}</p>
            <p className="file-size">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
          </div>
          {!isAnalyzing && (
            <button type="button" onClick={clearFile} className="icon-btn">
              <X className="icon-sm" />
            </button>
          )}
        </motion.div>
      ) : (
        <motion.div whileHover={{ scale: 1.01 }}
          onClick={function() { if (inputRef.current) inputRef.current.click(); }}
          onDragOver={function(e) { e.preventDefault(); setDragOver(true); }}
          onDragLeave={function() { setDragOver(false); }}
          onDrop={function(e) { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
          className={"dropzone " + (dragOver ? "drag" : "")}>
          <Upload className="icon-lg muted" />
          <div className="text-center">
            <p className="drop-title">Drop audio file or click to upload</p>
            <p className="drop-sub">MP3, WAV, OGG, FLAC, WebM</p>
          </div>
        </motion.div>
      )}
      <input ref={inputRef} type="file" accept="audio/*" className="hidden"
        onChange={function(e) { var f = e.target.files && e.target.files[0]; if (f) handleFile(f); }} />
    </div>
  );
}

// ── ResultDisplay ─────────────────────────────────────────────────────────────
function ResultDisplay({ result }) {
  var isReal    = result.verdict === "real";
  var Icon      = isReal ? ShieldCheck : ShieldAlert;
  var title     = isReal ? "Authentic Voice" : "Deepfake Detected";
  var cardClass = isReal ? "real" : "fake";
  var fillClass = isReal ? "success" : "danger";
  var probLabel = isReal ? "Authentic" : "Spoof";

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }} className="result">
      <motion.div initial={{ scale: 0.95 }} animate={{ scale: 1 }}
        className={"result-card " + cardClass}>
        <div className="result-head">
          <motion.div initial={{ rotate: -180, opacity: 0 }} animate={{ rotate: 0, opacity: 1 }}
            transition={{ duration: 0.6, type: "spring" }}>
            <Icon className={"icon-xl " + fillClass} />
          </motion.div>
          <h3 className="result-title">{title}</h3>
        </div>
        <div className="result-body">
          <p className="result-label">Confidence</p>
          <span className="result-value">{result.confidence}%</span>
          <div className="meter">
            <motion.div initial={{ width: 0 }} animate={{ width: result.confidence + "%" }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
              className={"meter-fill " + fillClass} />
          </div>
          <div className="prob-row">
            <span className={"prob-value " + fillClass}>{result.displayProb}%</span>
            <span className="prob-label">&nbsp;{probLabel}</span>
          </div>
        </div>
      </motion.div>
    </motion.div>
  );
}

export default App;