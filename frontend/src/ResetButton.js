import React from 'react';
import axios from 'axios';

function ResetButton() {
    const handleReset = () => {
        if (window.confirm("¿Estás seguro de que quieres limpiar todos los datos?")) {
            axios.post('http://127.0.0.1:5000/reset')
                .then(response => {
                    alert(response.data.message);
                    window.location.reload(); // Refresca la página para actualizar la UI
                })
                .catch(err => {
                    alert("Error al limpiar los datos");
                });
        }
    };

    return (
        <button onClick={handleReset} style={{ margin: '20px', backgroundColor: 'red', color: 'white' }}>
            Limpiar Todo
        </button>
    );
}

export default ResetButton;
