import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { videoService } from '../services/api';

const VideoJoin = () => {
  const { appointmentId } = useParams();
  const nav = useNavigate();
  const [otp, setOtp] = useState('');
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState('');

  const pasteFromClipboard = async () => {
    try {
      const t = await navigator.clipboard.readText();
      setOtp(t.trim());
    } catch {
      setMsg('Clipboard not available');
    }
  };

  const join = async () => {
    if (!otp.trim()) {
      setMsg('Enter OTP to join');
      return;
    }
    setLoading(true);
    setMsg('');
    try {
      // Try starting via generic video start (returns meeting_link when OTP is valid)
      const r = await videoService.startVideoCall({ appointment_id: Number(appointmentId), otp: otp.trim() });
      const link = r?.data?.meeting_link;
      if (link) {
        window.open(link, '_blank', 'noopener,noreferrer');
        return;
      }
      // Fallback: if session already started, get join link
      const j = await videoService.getVideoLink(Number(appointmentId));
      const joinLink = j?.data?.video_link || j?.data?.meeting_link;
      if (joinLink) {
        window.open(joinLink, '_blank', 'noopener,noreferrer');
        return;
      }
      setMsg('Link not ready yet. Please wait for the doctor to start.');
    } catch {
      setMsg('Invalid OTP or call not ready yet.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="vj">
      <div className="top">
        <button className="back" onClick={() => nav('/dashboard')} aria-label="Back">← Back</button>
        <h2>Video Consultation</h2>
        <p className="sub">Enter the OTP shared by your doctor to join</p>
      </div>

      <div className="join-card">
        <div className="label">Enter OTP to Join</div>
        <input
          className="otp"
          placeholder="Enter OTP here"
          value={otp}
          onChange={(e) => setOtp(e.target.value)}
        />
        {msg ? <div className="msg">{msg}</div> : null}
        <button className="primary" disabled={loading} onClick={join}>{loading ? 'Joining…' : 'Join Call'}</button>
      </div>

      <style>{`
        .vj{min-height:100vh;background:#F9FAFB;padding-bottom:80px}
        .top{background:linear-gradient(135deg,#8E44AD,#9B59B6);color:#fff;padding:1.2rem 1.25rem 3rem;border-bottom-left-radius:24px;border-bottom-right-radius:24px}
        .back{background:transparent;border:none;color:#fff;margin-bottom:.4rem}
        .sub{opacity:.9;margin:.25rem 0 0 0}
        .join-card{background:#fff;border-radius:16px;box-shadow:0 6px 18px rgba(0,0,0,0.06);margin:-1.5rem 1rem 0 1rem;padding:1rem}
        .label{font-weight:800;margin-bottom:.5rem}
        .otp{width:100%;border:1px solid #E5E7EB;border-radius:14px;padding:1rem;font-size:1rem;letter-spacing:.15rem;margin-bottom:.5rem}
        .msg{color:#991B1B;background:#FEF2F2;border:1px solid #FEE2E2;border-radius:10px;padding:.5rem;margin-bottom:.5rem}
        .primary{width:100%;background:#8E44AD;color:#fff;border:none;border-radius:14px;padding:.9rem 1rem}
      `}</style>
    </div>
  );
};

export default VideoJoin;

