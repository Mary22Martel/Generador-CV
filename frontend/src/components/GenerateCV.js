import React, { useState } from "react";
import axios from "axios";

function GenerateCV() {
  const [loading, setLoading] = useState(false); // Estado para controlar la carga
  const [error, setError] = useState(""); // Estado para manejar errores

  const handleGenerate = async () => {
    setLoading(true);
    setError("");

    try {
      // Llama al endpoint para generar el PDF del CV
      const response = await axios.get("http://127.0.0.1:5000/generate-cv", {
        responseType: "blob", // Importante para manejar archivos binarios como PDFs
      });

      // Crear un enlace de descarga para el archivo PDF generado
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "nuevo_formato_cv.pdf"); // Nombre del archivo descargado
      document.body.appendChild(link);
      link.click();
      link.remove();

      alert("PDF generado y descargado correctamente.");
    } catch (err) {
      // Manejo de errores en la solicitud
      const errorMessage = err.response?.data?.error || err.message || "Error desconocido";
      setError(`Error al generar el PDF: ${errorMessage}`);
    } finally {
      setLoading(false); // Desactiva el estado de carga
    }
  };

  return (
    <div>
      {/* Botón para generar el PDF */}
      <button onClick={handleGenerate} disabled={loading}>
        {loading ? "Generando..." : "Generar PDF del CV"}
      </button>
      {/* Muestra errores si ocurren */}
      {error && <p style={{ color: "red" }}>{error}</p>}
    </div>
  );
}

export default GenerateCV;
