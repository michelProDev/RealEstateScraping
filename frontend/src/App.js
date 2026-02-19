import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = `http://${window.location.hostname}:5000/api`;

export default function App() {
  const [targets, setTargets] = useState([]);
  const [regiones, setRegiones] = useState([]);
  const [selectedRegiones, setSelectedRegiones] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);
  const [xlsxFile, setXlsxFile] = useState(null);
  const [htmlFile, setHtmlFile] = useState(null);

  useEffect(() => {
    axios.get(`${API_URL}/targets`)
      .then(res => {
        setTargets(res.data.targets || []);
        setRegiones(res.data.regiones || []);
        setSelectedRegiones(res.data.regiones || []);
      })
      .catch(err => {
        setError('Error cargando los datos de inmobiliarias');
        console.error(err);
      });
  }, []);

  const toggleRegion = (region) => {
    setSelectedRegiones(prev =>
      prev.includes(region)
        ? prev.filter(r => r !== region)
        : [...prev, region]
    );
  };

  const handleScrape = async (target) => {
    if (selectedRegiones.length === 0) {
      setError('Selecciona al menos una región');
      return;
    }

    setLoading(true);
    setMessage(null);
    setError(null);
    setXlsxFile(null);
    setHtmlFile(null);

    try {
      const res = await axios.post(`${API_URL}/scrape`, {
        nombre: target.nombre,
        web: target.web,
        regiones: selectedRegiones,
      });

      setMessage(res.data.message);
      setXlsxFile(res.data.xlsx_filename);
      setHtmlFile(res.data.html_filename);
    } catch (err) {
      const msg = err.response?.data?.error || 'Error durante el scraping';
      setError(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadXlsx = () => {
    if (xlsxFile) {
      window.open(`${API_URL}/download/${xlsxFile}`, '_blank');
    }
  };

  const handleDownloadHtml = () => {
    if (htmlFile) {
      window.open(`${API_URL}/download/${htmlFile}`, '_blank');
    }
  };

  return (
    <div style={styles.container}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.title}>🏠 HouseHunt</h1>
          <p style={styles.subtitle}>Scraper de inmobiliarias españolas</p>
        </div>
      </header>

      <main style={styles.main}>
        {/* Region Filter */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>📍 Regiones</h2>
          <div style={styles.regionContainer}>
            {regiones.map(region => (
              <button
                key={region}
                onClick={() => toggleRegion(region)}
                style={{
                  ...styles.regionChip,
                  ...(selectedRegiones.includes(region) ? styles.regionChipActive : {}),
                }}
              >
                {selectedRegiones.includes(region) ? '✓ ' : ''}{region}
              </button>
            ))}
          </div>
        </section>

        {/* Status Messages */}
        {loading && (
          <div style={styles.loadingBar}>
            <div style={styles.spinner}></div>
            <span>Scrapeando propiedades... Esto puede tardar unos minutos.</span>
          </div>
        )}

        {message && (
          <div style={styles.successMsg}>
            <span>✅ {message}</span>
            <div style={{display: 'flex', gap: '10px', flexWrap: 'wrap'}}>
              {xlsxFile && (
                <button onClick={handleDownloadXlsx} style={styles.downloadBtn}>
                  📥 Descargar Excel
                </button>
              )}
              {htmlFile && (
                <button onClick={handleDownloadHtml} style={styles.downloadBtnHtml}>
                  🌐 Descargar HTML
                </button>
              )}
            </div>
          </div>
        )}

        {error && (
          <div style={styles.errorMsg}>
            ❌ {error}
          </div>
        )}

        {/* Targets Grid */}
        <section style={styles.section}>
          <h2 style={styles.sectionTitle}>🏢 Inmobiliarias disponibles</h2>
          <p style={styles.hint}>Haz clic en una inmobiliaria para iniciar el scraping</p>
          <div style={styles.grid}>
            {targets.map((target, idx) => (
              <div
                key={idx}
                style={styles.card}
                onClick={() => !loading && handleScrape(target)}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-4px)';
                  e.currentTarget.style.boxShadow = '0 12px 24px rgba(0,0,0,0.15)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0,0,0,0.08)';
                }}
              >
                <div style={styles.cardIcon}>
                  {target.nombre.charAt(0).toUpperCase()}
                </div>
                <h3 style={styles.cardTitle}>{target.nombre}</h3>
                <a
                  href={target.web}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={styles.cardLink}
                  onClick={(e) => e.stopPropagation()}
                >
                  {target.web}
                </a>
                <button
                  style={{
                    ...styles.scrapeBtn,
                    ...(loading ? styles.scrapeBtnDisabled : {}),
                  }}
                  disabled={loading}
                >
                  {loading ? '⏳ Procesando...' : '🔍 Scrapear'}
                </button>
              </div>
            ))}
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer style={styles.footer}>
        <p>HouseHunt — Herramienta de scraping inmobiliario</p>
      </footer>

      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; }
      `}</style>
    </div>
  );
}

const styles = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    flexDirection: 'column',
    background: '#f0f2f5',
  },
  header: {
    background: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
    color: '#fff',
    padding: '40px 20px',
    textAlign: 'center',
  },
  headerContent: {
    maxWidth: '800px',
    margin: '0 auto',
  },
  title: {
    fontSize: '2.5rem',
    fontWeight: '700',
    marginBottom: '8px',
    letterSpacing: '-0.5px',
  },
  subtitle: {
    fontSize: '1.1rem',
    opacity: 0.8,
    fontWeight: '300',
  },
  main: {
    flex: 1,
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '30px 20px',
    width: '100%',
  },
  section: {
    marginBottom: '30px',
  },
  sectionTitle: {
    fontSize: '1.4rem',
    color: '#1a1a2e',
    marginBottom: '12px',
    fontWeight: '600',
  },
  hint: {
    color: '#666',
    fontSize: '0.9rem',
    marginBottom: '16px',
  },
  regionContainer: {
    display: 'flex',
    gap: '10px',
    flexWrap: 'wrap',
  },
  regionChip: {
    padding: '8px 20px',
    borderRadius: '25px',
    border: '2px solid #0f3460',
    background: '#fff',
    color: '#0f3460',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '500',
    transition: 'all 0.2s ease',
  },
  regionChipActive: {
    background: '#0f3460',
    color: '#fff',
  },
  loadingBar: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '16px 24px',
    background: '#fff3cd',
    borderRadius: '10px',
    marginBottom: '20px',
    border: '1px solid #ffc107',
    color: '#856404',
    fontWeight: '500',
  },
  spinner: {
    width: '24px',
    height: '24px',
    border: '3px solid #ffc107',
    borderTop: '3px solid #856404',
    borderRadius: '50%',
    animation: 'spin 1s linear infinite',
  },
  successMsg: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    flexWrap: 'wrap',
    gap: '12px',
    padding: '16px 24px',
    background: '#d4edda',
    borderRadius: '10px',
    marginBottom: '20px',
    border: '1px solid #28a745',
    color: '#155724',
    fontWeight: '500',
  },
  downloadBtn: {
    padding: '10px 24px',
    background: '#28a745',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '600',
    transition: 'background 0.2s',
  },
  downloadBtnHtml: {
    padding: '10px 24px',
    background: '#0f3460',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.95rem',
    fontWeight: '600',
    transition: 'background 0.2s',
  },
  errorMsg: {
    padding: '16px 24px',
    background: '#f8d7da',
    borderRadius: '10px',
    marginBottom: '20px',
    border: '1px solid #dc3545',
    color: '#721c24',
    fontWeight: '500',
  },
  grid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))',
    gap: '20px',
  },
  card: {
    background: '#fff',
    borderRadius: '14px',
    padding: '24px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.08)',
    cursor: 'pointer',
    transition: 'all 0.3s ease',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    textAlign: 'center',
    border: '1px solid #e8e8e8',
  },
  cardIcon: {
    width: '56px',
    height: '56px',
    borderRadius: '50%',
    background: 'linear-gradient(135deg, #0f3460, #1a1a2e)',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '1.5rem',
    fontWeight: '700',
    marginBottom: '14px',
  },
  cardTitle: {
    fontSize: '1.15rem',
    fontWeight: '600',
    color: '#1a1a2e',
    marginBottom: '6px',
  },
  cardLink: {
    color: '#0f3460',
    fontSize: '0.8rem',
    textDecoration: 'none',
    marginBottom: '16px',
    wordBreak: 'break-all',
    opacity: 0.7,
  },
  scrapeBtn: {
    padding: '10px 28px',
    background: 'linear-gradient(135deg, #0f3460, #1a1a2e)',
    color: '#fff',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '0.9rem',
    fontWeight: '600',
    transition: 'opacity 0.2s',
    marginTop: 'auto',
  },
  scrapeBtnDisabled: {
    opacity: 0.5,
    cursor: 'not-allowed',
  },
  footer: {
    textAlign: 'center',
    padding: '20px',
    color: '#888',
    fontSize: '0.85rem',
    borderTop: '1px solid #e0e0e0',
    background: '#fff',
  },
};
