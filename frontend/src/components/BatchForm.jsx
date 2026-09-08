import { useState } from 'react';
import { ChevronDown, ChevronUp, Loader } from 'lucide-react';
import './BatchForm.css';

const sections = [
  {
    id: 'material', title: 'Raw Material Quality',
    fields: [
      { name: 'API_water_content', label: 'API Water Content (%)' },
      { name: 'API_impurities', label: 'API Impurities (%)' },
      { name: 'API_particle_size', label: 'API Particle Size (µm)' },
      { name: 'excipient_moisture', label: 'Excipient Moisture (%)' }
    ]
  },
  {
    id: 'process', title: 'Process Parameters',
    fields: [
      { name: 'compression_force', label: 'Compression Force (kN)' },
      { name: 'fill_depth', label: 'Fill Depth (mm)' },
      { name: 'turret_speed', label: 'Turret Speed (rpm)' },
      { name: 'ejection_force', label: 'Ejection Force (N)' }
    ]
  },
  {
    id: 'product', title: 'In-Process Measurements',
    fields: [
      { name: 'tablet_weight', label: 'Tablet Weight (mg)' },
      { name: 'tablet_thickness', label: 'Tablet Thickness (mm)' },
      { name: 'tablet_hardness', label: 'Tablet Hardness (kp)' },
      { name: 'tensile_strength', label: 'Tensile Strength (MPa)' },
      { name: 'coating_thickness', label: 'Coating Thickness (µm)' }
    ]
  },
  {
    id: 'batch', title: 'Batch Information',
    fields: [
      { name: 'product_code', label: 'Product Code (Numeric)' },
      { name: 'is_weekend', label: 'Weekend Shift (0 or 1)' },
      { name: 'waste_percentage', label: 'Waste Percentage (%)' }
    ]
  }
];

function BatchForm({ onSubmit, isLoading }) {
  const [openSection, setOpenSection] = useState('material');
  const [formData, setFormData] = useState({});

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: parseFloat(value) || 0 }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    const batch_id = `BATCH-${Math.floor(1000 + Math.random() * 9000)}`;
    onSubmit({ batch_id, ...formData });
  };

  return (
    <form className="batch-form" onSubmit={handleSubmit}>
      {sections.map((section) => (
        <div key={section.id} className="form-section glass-card">
          <div 
            className="section-header" 
            onClick={() => setOpenSection(openSection === section.id ? null : section.id)}
          >
            <h3>{section.title}</h3>
            {openSection === section.id ? <ChevronUp /> : <ChevronDown />}
          </div>
          
          {openSection === section.id && (
            <div className="section-content fade-in">
              {section.fields.map((field) => (
                <div key={field.name} className="form-group">
                  <label htmlFor={field.name}>{field.label}</label>
                  <input
                    type="number"
                    step="any"
                    id={field.name}
                    name={field.name}
                    className="input-field"
                    required
                    onChange={handleChange}
                    value={formData[field.name] || ''}
                  />
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
      
      <div className="form-actions">
        <button type="submit" className="btn btn-primary submit-btn" disabled={isLoading}>
          {isLoading ? <><Loader className="spinner" /> Analyzing...</> : 'Evaluate Batch Quality'}
        </button>
      </div>
    </form>
  );
}

export default BatchForm;
