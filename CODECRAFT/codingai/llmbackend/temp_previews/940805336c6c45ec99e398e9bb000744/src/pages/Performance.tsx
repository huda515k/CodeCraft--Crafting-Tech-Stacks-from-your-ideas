import React, { useState } from 'react';
import Card from '../components/Card';
import Input from '../components/Input';
import { mockPlayers, mockPerformance } from '../utils/data';

interface PlayerPerformanceWithDetails extends mockPerformance {
  playerName: string;
  playerRole: string;
}

const Performance: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');

  const combinedPerformance: PlayerPerformanceWithDetails[] = mockPerformance.map(perf => {
    const player = mockPlayers.find(p => p.id === perf.playerId);
    return {
      ...perf,
      playerName: player?.name || 'Unknown',
      playerRole: player?.role || 'Unknown',
    };
  });

  const filteredPerformance = combinedPerformance.filter(perf =>
    perf.playerName.toLowerCase().includes(searchTerm.toLowerCase()) ||
    perf.playerRole.toLowerCase().includes(searchTerm.toLowerCase()) ||
    perf.bestPerformance.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Player Performance</h2>

      <Card title="Individual Performance Metrics">
        <div className="mb-4">
          <Input
            id="performance-search"
            type="text"
            placeholder="Search by player name, role, or best performance..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Player Name
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Matches
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Runs
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Wickets
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Catches
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Avg
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  SR
                </th>
                <th scope="col" className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Best Perf.
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPerformance.length > 0 ? (
                filteredPerformance.map((perf) => (
                  <tr key={perf.playerId}>
                    <td className="px-4 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                      {perf.playerName}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.playerRole}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.matchesPlayed}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.runsScored}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.wicketsTaken}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.catches}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.average.toFixed(1)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.strikeRate.toFixed(1)}
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm text-gray-600">
                      {perf.bestPerformance}
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="px-6 py-4 text-center text-gray-500">
                    No performance data found for the search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
};

export default Performance;