import React from 'react';
import Card from '@components/Card';
import Table from '@components/Table';
import { teams, Team } from '@utils/data';

const Teams: React.FC = () => {
  const teamColumns = [
    { key: 'name', header: 'Team Name' },
    { key: 'city', header: 'City' },
    { key: 'coach', header: 'Coach' },
    { key: 'captain', header: 'Captain' },
    { key: 'homeGround', header: 'Home Ground' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-gray-900">Teams Management</h1>

      <Card>
        <Table data={teams} columns={teamColumns} />
      </Card>
    </div>
  );
};

export default Teams;