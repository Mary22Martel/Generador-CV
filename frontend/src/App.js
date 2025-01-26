import React, { useState, useEffect } from 'react';
import UploadCV from './components/UploadCV';
import CVList from './components/CVList';
import CriteriaList from './components/CriteriaList';
import ProcessCVs from './components/ProcessCVs';
import ResetButton from './ResetButton';
import GenerateCV from "./components/GenerateCV";
import './styles/App.css'; // Archivo CSS para agregar estilos globales

function App() {
  const [cvs, setCvs] = useState([]);
  const [refresh, setRefresh] = useState(false);

  // Función para actualizar la lista de CVs
  const fetchCVs = () => {
    fetch('http://127.0.0.1:5000/get-cvs')
      .then((response) => response.json())
      .then((data) => setCvs(data))
      .catch((error) => console.error('Error al cargar los CVs:', error));
  };

  // Cargar CVs al iniciar la app o cuando se necesite refrescar
  useEffect(() => {
    fetchCVs();
  }, [refresh]);

  // Manejo de actualizaciones desde los componentes hijos
  const handleUploadSuccess = () => {
    setRefresh((prev) => !prev); // Forzar recarga de CVs
  };

  const handleProcessComplete = () => {
    setRefresh((prev) => !prev); // Refrescar criterios también
  };

  return (
    <div className="app-container">
      <header className="app-header">
        <h1>Generador de CV</h1>
        <p>
          Sube archivos, procesa la información y organiza criterios relevantes
          para tu CV.
        </p>
      </header>
      <ResetButton onReset={handleUploadSuccess} />
      <main className="main-content">
        <section className="section">
          <p>Sube tus archivos en formato PDF o Word para comenzar.</p>
          <UploadCV onUploadSuccess={handleUploadSuccess} />
        </section>
        <section className="section">
          <p>Aquí puedes ver los CVs que ya has subido:</p>
          <CVList cvs={cvs} />
        </section>
        <section className="section">
          <p>Extrae automáticamente los criterios relevantes de tus CVs subidos.</p>
          <ProcessCVs onProcess={handleProcessComplete} />
        </section>
        <section className="section">
          <CriteriaList refresh={refresh} />
        </section>
        <section className="section">
          <p>Genera un nuevo formato de CV basado en los criterios válidos.</p>
          <GenerateCV />
        </section>
      </main>
    </div>
  );
}

export default App;
