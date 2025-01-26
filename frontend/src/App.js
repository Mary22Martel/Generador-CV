import React, { useState } from 'react';
import UploadCV from './components/UploadCV';
import CVList from './components/CVList';
import CriteriaList from './components/CriteriaList';
import ProcessCVs from './components/ProcessCVs';
import ResetButton from './ResetButton';


function App() {
  const [refresh, setRefresh] = useState(false);

  // Función para manejar el refresco cuando los criterios cambien
  const refreshCriteria = () => {
    setRefresh(prev => !prev);
  };

   // Función para manejar el proceso completo de los CVs
   const handleProcessComplete = () => {
    refreshCriteria(); // Refrescar los criterios después de procesar
  };

  
  return (
    <div>
      <h1>Generador de CV</h1>
      <ResetButton />
      <UploadCV />
      <CVList />
      <ProcessCVs onProcess={handleProcessComplete} />
      <CriteriaList refresh={refreshCriteria} />
    </div>
  );
}

export default App;

