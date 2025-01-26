import React, { useState, useEffect } from "react";
import axios from "axios";
import "../styles/CriteriaList.css"; // Importar el archivo CSS

function CriteriaList({ refresh }) {
    const [criteria, setCriteria] = useState({});
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true); // Estado para el spinner
  
    useEffect(() => {
      setLoading(true); // Activar el spinner
      axios
        .get("http://127.0.0.1:5000/get-criteria")
        .then((response) => {
          setCriteria(response.data);
          setLoading(false); // Desactivar el spinner
        })
        .catch((err) => {
          setError("Error al cargar los criterios");
          setLoading(false);
        });
    }, [refresh]);
  
    const handleVote = (id, valid, category) => {
      axios
        .patch(`http://127.0.0.1:5000/vote-criteria/${id}`, { valid })
        .then(() => {
          setCriteria((prevCriteria) => {
            const updatedCategory = prevCriteria[category].map((crit) =>
              crit.id === id ? { ...crit, valid } : crit
            );
            return { ...prevCriteria, [category]: updatedCategory };
          });
        })
        .catch(() => setError("Error al votar por el criterio"));
    };
  
    if (loading) {
      return <p style={{ textAlign: "center" }}>Cargando criterios...</p>;
    }
  
    return (
      <div className="criteria-container">
        <h2>Criterios Extraídos</h2>
        {error && <p className="error-message">{error}</p>}
        {Object.keys(criteria).length === 0 ? (
          <p>No hay criterios disponibles.</p>
        ) : (
          Object.keys(criteria).map((category) => (
            <div key={category} className="category-section">
              <h3 className="category-title">{category}</h3>
              <ul className="criteria-list">
                {criteria[category].map((crit) => (
                  <li key={crit.id} className="criteria-item">
                    <p>{crit.description}</p>
                    <div className="vote-buttons">
                      <button
                        className={`vote-button ${crit.valid ? "valid" : ""}`}
                        onClick={() => handleVote(crit.id, true, category)}
                      >
                        Válido
                      </button>
                      <button
                        className={`vote-button ${!crit.valid ? "invalid" : ""}`}
                        onClick={() => handleVote(crit.id, false, category)}
                      >
                        No Válido
                      </button>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          ))
        )}
      </div>
    );
  }

  
  
  export default CriteriaList;
