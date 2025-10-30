import React, { useState } from 'react';
import axios from 'axios';

interface ExportButtonsProps {
  days: number;
}

const ExportButtons: React.FC<ExportButtonsProps> = ({ days }) => {
  const [loadingPDF, setLoadingPDF] = useState(false);
  const [loadingCSV, setLoadingCSV] = useState(false);

  const downloadPDF = async () => {
    try {
      setLoadingPDF(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.get(
        `http://localhost:8000/api/export/pdf?days=${days}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: 'blob',
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dashboard_report_${new Date().toISOString().split('T')[0]}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('PDF export error:', error);
      alert('Failed to export PDF');
    } finally {
      setLoadingPDF(false);
    }
  };

  const downloadCSV = async () => {
    try {
      setLoadingCSV(true);
      const token = localStorage.getItem('token');
      
      const response = await axios.get(
        `http://localhost:8000/api/export/csv?days=${days}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
          responseType: 'blob',
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `dashboard_data_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('CSV export error:', error);
      alert('Failed to export CSV');
    } finally {
      setLoadingCSV(false);
    }
  };

  return (
    <div className="flex items-center space-x-3">
      <button
        onClick={downloadPDF}
        disabled={loadingPDF}
        className="flex items-center space-x-2 bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
      >
        <span>📄</span>
        <span>{loadingPDF ? 'Exporting...' : 'Export PDF'}</span>
      </button>
      <button
        onClick={downloadCSV}
        disabled={loadingCSV}
        className="flex items-center space-x-2 bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
      >
        <span>📊</span>
        <span>{loadingCSV ? 'Exporting...' : 'Export CSV'}</span>
      </button>
    </div>
  );
};

export default ExportButtons;