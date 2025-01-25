import React from 'react';
import UploadCV from './components/UploadCV';
import CVList from './components/CVList';

function App() {
  return (
    <div>
      <h1>Generador de CV</h1>
      <UploadCV />
      <CVList />
    </div>
  );
}

export default App;
