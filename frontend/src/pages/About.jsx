import { BookOpen, Database, Cpu, AlertTriangle } from 'lucide-react';
import './About.css';

function About() {
  return (
    <div className="about fade-in">
      <div className="about-header">
        <h1>About PharmaBatch AI</h1>
        <p>Understanding the architecture, methodology, and scope of our agentic AI system.</p>
      </div>

      <div className="about-grid">
        <section className="about-card glass-card">
          <h2><BookOpen className="icon" /> Manufacturing Context</h2>
          <p>
            In pharmaceutical API and solid dosage manufacturing, batch release is a critical process.
            Traditional QA/QC involves extensive manual review of process parameters and quality attributes.
            PharmaBatch AI provides decision support to flag risky batches before formal release, preventing costly reworks and ensuring compliance.
          </p>
        </section>

        <section className="about-card glass-card">
          <h2><Cpu className="icon" /> System Architecture</h2>
          <div className="agent-pipeline">
            <div className="agent-node">1. Validation Agent</div>
            <div className="agent-arrow">→</div>
            <div className="agent-node">2. Prediction Agent (XGBoost)</div>
            <div className="agent-arrow">→</div>
            <div className="agent-node">3. Explanation Agent (SHAP)</div>
            <div className="agent-arrow">→</div>
            <div className="agent-node">4. Decision Agent</div>
            <div className="agent-arrow">→</div>
            <div className="agent-node">5. Reporting Agent</div>
          </div>
        </section>

        <section className="about-card glass-card">
          <h2><Database className="icon" /> Methodology & Data</h2>
          <p>
            Our core machine learning model utilizes XGBoost, trained on pharmaceutical manufacturing data.
            It evaluates raw material properties, process parameters, and in-process measurements to predict the final batch outcome:
            <strong> Approved, Rework, or Rejected.</strong>
          </p>
          <p className="attribution">
            *Dataset attribution: Based on synthetic/anonymized pharmaceutical manufacturing datasets (e.g., Žagar & Mihelič).
          </p>
        </section>

        <section className="about-card glass-card warning">
          <h2><AlertTriangle className="icon" /> Limitations & Disclaimer</h2>
          <p>
            This system operates in a simulated environment and is designed for <strong>demonstration and decision support only</strong>.
            It does not replace GMP compliance procedures, authorized Qualified Persons (QPs), or standard operating procedures.
          </p>
        </section>
      </div>
    </div>
  );
}

export default About;
