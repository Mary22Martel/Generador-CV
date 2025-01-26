import React from 'react';

const CVList = ({ cvs }) => {
  return (
    <div>
      <h2>CVs Subidos</h2>
      {cvs.length === 0 ? (
        <p>No hay CVs subidos aún.</p>
      ) : (
        <ul className="cv-list">
          {cvs.map((cv) => (
            <li key={cv.id}>{cv.filename}</li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default CVList;
