import React, { useState } from 'react';
import axios from 'axios';

const UploadCV = () => {
  const [file, setFile] = useState(null);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload-cv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage(response.data.message || 'Archivo subido exitosamente');
    } catch (error) {
      console.error(error);
      setMessage('Error al subir el archivo');
    }
  };

  return (
    <div>
      <h2>Subir CV</h2>
      <form onSubmit={handleSubmit}>
        <input type="file" onChange={handleFileChange} />
        <button type="submit">Subir</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default UploadCV;
