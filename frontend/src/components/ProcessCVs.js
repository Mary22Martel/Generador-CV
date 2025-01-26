import React, { useState } from "react";
import axios from "axios";

function ProcessCVs({ onProcess }) {
  const [loading, setLoading] = useState(false); // Estado para controlar si el proceso está en ejecución
  const [error, setError] = useState(""); // Estado para manejar errores

  const handleProcess = async () => {
    setLoading(true); // Activa el estado de carga
    setError(""); // Resetea errores previos

    try {
      // Llama al endpoint /extract-criteria-all para procesar y extraer criterios de todos los CVs
      const response = await axios.post("http://127.0.0.1:5000/extract-criteria-all");
      if (response.status === 200) {
        alert("Criterios extraídos correctamente."); // Muestra una alerta de éxito
        onProcess(); // Refresca la lista de criterios en el frontend
      }
    } catch (err) {
      // Maneja errores de la solicitud
      const errorMessage = err.response?.data?.error || err.message || "Error desconocido";
      setError(`Error al extraer criterios: ${errorMessage}`);
    } finally {
      setLoading(false); // Desactiva el estado de carga
    }
  };

  return (
    <div>
      {/* Botón para procesar CVs */}
      <button onClick={handleProcess} disabled={loading}>
        {loading ? "Procesando..." : "Procesar CVs"} {/* Cambia el texto según el estado de carga */}
      </button>
      {/* Muestra errores si ocurren */}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default ProcessCVs;
