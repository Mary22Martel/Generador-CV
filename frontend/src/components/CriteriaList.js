import React, { useState, useEffect } from 'react';
import axios from 'axios';

function CriteriaList({ refresh }) {
    const [criteria, setCriteria] = useState([]);
    const [error, setError] = useState("");

    // Cargar criterios cada vez que se monte el componente o cambie `refresh`
    useEffect(() => {
        axios.get('http://127.0.0.1:5000/get-criteria')
            .then(response => setCriteria(response.data))
            .catch(err => setError("Error al cargar los criterios"));
    }, [refresh]);

    // Manejar votos para los criterios
    const handleVote = (id, valid) => {
        axios.patch(`http://127.0.0.1:5000/vote-criteria/${id}`, { valid })
            .then(response => {
                // Actualiza el estado con el criterio actualizado
                setCriteria(prevCriteria =>
                    prevCriteria.map(crit =>
                        crit.id === id ? { ...crit, valid: valid } : crit
                    )
                );
            })
            .catch(err => setError("Error al votar por el criterio"));
    };

    return (
        <div>
            <h2>Criterios Extraídos</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <ul>
                {criteria.map(crit => (
                    <li key={crit.id}>
                        {crit.description} - {crit.valid ? "Válido" : "No Válido"}
                        <button onClick={() => handleVote(crit.id, true)} style={{ marginLeft: '10px' }}>Válido</button>
                        <button onClick={() => handleVote(crit.id, false)} style={{ marginLeft: '5px' }}>No Válido</button>
                    </li>
                ))}
            </ul>
        </div>
    );
}

export default CriteriaList;
