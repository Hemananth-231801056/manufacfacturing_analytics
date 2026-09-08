import './Footer.css';

function Footer() {
  return (
    <footer className="footer">
      <div className="footer-content">
        <p className="footer-tagline">AI-Powered Decision Support for Pharmaceutical Manufacturing</p>
        <p className="footer-disclaimer">
          <strong>Disclaimer:</strong> This system is for decision support only. Final release decisions must be made by authorized QA/QC personnel.
        </p>
        <p className="footer-copyright">&copy; {new Date().getFullYear()} PharmaBatch AI. All rights reserved.</p>
      </div>
    </footer>
  );
}

export default Footer;
