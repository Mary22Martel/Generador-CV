import React, { useState } from 'react';
import axios from 'axios';

function ProcessCVs({ onProcess }) {
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const handleProcess = () => {
        setLoading(true);
        setError("");
        axios.post('http://127.0.0.1:5000/process-cvs')
            .then(response => {
                alert("CVs procesados correctamente.");
                onProcess(); // Actualiza los criterios extraídos
                setLoading(false);
            })
            .catch(err => {
                setError("Error al procesar los CVs.");
                setLoading(false);
            });
    };

    return (
        <div>
            <h2>Procesar CVs</h2>
            <button onClick={handleProcess} disabled={loading} style={{ margin: '10px' }}>
                {loading ? "Procesando..." : "Procesar CVs"}
            </button>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </div>
    );
}

export default ProcessCVs;
