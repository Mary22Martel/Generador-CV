import React, { useState } from 'react';
import axios from 'axios';

const UploadCV = ({ onUploadSuccess }) => {
  const [files, setFiles] = useState([]);
  const [message, setMessage] = useState('');

  const handleFileChange = (e) => {
    setFiles(e.target.files);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append('files', files[i]);
    }

    try {
      const response = await axios.post('http://127.0.0.1:5000/upload-cv', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      setMessage(response.data.message || 'Archivos subidos exitosamente');
      onUploadSuccess(); // Notifica a la app principal
    } catch (error) {
      console.error(error);
      setMessage('Error al subir los archivos');
    }
  };

  return (
    <div>
      <form onSubmit={handleSubmit} className="upload-form">
        <input type="file" onChange={handleFileChange} multiple />
        <button type="submit">Subir</button>
      </form>
      {message && <p>{message}</p>}
    </div>
  );
};

export default UploadCV;