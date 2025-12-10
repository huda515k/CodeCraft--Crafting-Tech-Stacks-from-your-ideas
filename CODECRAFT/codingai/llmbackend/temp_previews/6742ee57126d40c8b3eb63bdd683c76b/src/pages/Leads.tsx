import React from 'react';
import { leads } from '../utils/mockData';

interface Lead {
  id: string;
  name: string;
  source: string;
  stage: 'New' | 'Contacted' | 'Qualified' | 'Lost';
}

const Leads: React.FC = () => {
  const getStageColor = (stage: Lead['stage']) => {
    switch (stage) {
      case 'New':
        return 'bg-blue-100 text-blue-800';
      case 'Contacted':
        return 'bg-purple-100 text-purple-800';
      case 'Qualified':
        return 'bg-green-100 text-green-800';
      case 'Lost':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Leads</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {leads.map((lead) => (
          <div key={lead.id} className="bg-white rounded-lg shadow-md p-6 transform transition-transform hover:scale-105 duration-200">
            <h3 className="text-xl font-semibold text-gray-900">{lead.name}</h3>
            <p className="mt-2 text-gray-600">Source: <span className="font-medium">{lead.source}</span></p>
            <div className="mt-4">
              <span className={`px-3 py-1 inline-flex text-sm leading-5 font-semibold rounded-full ${getStageColor(lead.stage)}`}>
                {lead.stage}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default Leads;