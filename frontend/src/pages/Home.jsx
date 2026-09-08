import { Link } from 'react-router-dom';
import { Activity, ShieldCheck, Zap, FileText, ArrowRight } from 'lucide-react';
import './Home.css';

function Home() {
  return (
    <div className="home fade-in">
      <section className="hero">
        <div className="hero-content">
          <h1>AI-Powered Batch Quality Intelligence</h1>
          <p>
            Transform pharmaceutical manufacturing with multi-agent decision support. 
            Evaluate batch quality, prevent rework, and generate compliance-ready reports in real-time.
          </p>
          <Link to="/predict" className="btn btn-primary hero-btn">
            Evaluate a Batch <ArrowRight size={18} />
          </Link>
        </div>
      </section>

      <section className="features">
        <div className="feature-card glass-card">
          <Activity className="feature-icon" size={32} />
          <h3>Predictive Analytics</h3>
          <p>ML-powered quality prediction based on historical API and process data.</p>
        </div>
        <div className="feature-card glass-card">
          <Zap className="feature-icon" size={32} />
          <h3>Explainable AI</h3>
          <p>SHAP-based transparency provides exact reasoning for every quality decision.</p>
        </div>
        <div className="feature-card glass-card">
          <ShieldCheck className="feature-icon" size={32} />
          <h3>Intelligent Agents</h3>
          <p>A specialized 5-agent pipeline handling validation, prediction, decisions, and reporting.</p>
        </div>
        <div className="feature-card glass-card">
          <FileText className="feature-icon" size={32} />
          <h3>Professional Reports</h3>
          <p>Instantly generate PDF QA/QC reports for regulatory compliance and batch release.</p>
        </div>
      </section>

      <section className="stats glass-card">
        <div className="stat-item">
          <h4>1,005</h4>
          <p>Batches Analyzed</p>
        </div>
        <div className="stat-item">
          <h4>95%+</h4>
          <p>Accuracy</p>
        </div>
        <div className="stat-item">
          <h4>5</h4>
          <p>AI Agents</p>
        </div>
        <div className="stat-item">
          <h4>&lt;2s</h4>
          <p>Real-Time Predictions</p>
        </div>
      </section>
    </div>
  );
}

export default Home;
