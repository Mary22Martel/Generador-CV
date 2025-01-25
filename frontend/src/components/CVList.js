import React, { useEffect, useState } from 'react';
import axios from 'axios';

function CVList() {
    const [cvs, setCvs] = useState([]);

    useEffect(() => {
        // Realizar la solicitud GET al backend
        axios.get('http://127.0.0.1:5000/get-cvs')
            .then(response => {
                setCvs(response.data); // Almacena la respuesta en el estado
            })
            .catch(error => {
                console.error('Error al cargar los CVs:', error);
            });
    }, []);

    return (
        <div>
            <h2>CVs Subidos</h2>
            <ul>
                {cvs.map(cv => (
                    <li key={cv.id}>{cv.filename}</li>
                ))}
            </ul>
        </div>
    );
}

export default CVList;
