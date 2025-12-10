import React, { useState } from 'react';
import Card from '../components/Card';
import Button from '../components/Button';
import Input from '../components/Input';
import Modal from '../components/Modal';
import { mockPlayers, dashboardStats, Player } from '../utils/data';
import useToggle from '../hooks/useToggle';

const Dashboard: React.FC = () => {
  const [isModalOpen, toggleModal] = useToggle(false);
  const [selectedPlayer, setSelectedPlayer] = useState<Player | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const filteredPlayers = mockPlayers.filter(player =>
    player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    player.role.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleViewDetails = (player: Player) => {
    setSelectedPlayer(player);
    toggleModal();
  };

  const handleCloseModal = () => {
    toggleModal();
    setSelectedPlayer(null);
  };

  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-900">Dashboard Overview</h2>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <p className="text-sm font-medium text-gray-500">Total Players</p>
          <p className="text-3xl font-bold text-gray-900 mt-1">{dashboardStats.totalPlayers}</p>
        </Card>
        <Card>
          <p className="text-sm font-medium text-gray-500">Active Players</p>
          <p className="text-3xl font-bold text-green-600 mt-1">{dashboardStats.activePlayers}</p>
        </Card>
        <Card>
          <p className="text-sm font-medium text-gray-500">Injured Players</p>
          <p className="text-3xl font-bold text-red-600 mt-1">{dashboardStats.injuredPlayers}</p>
        </Card>
        <Card>
          <p className="text-sm font-medium text-gray-500">Upcoming Matches</p>
          <p className="text-3xl font-bold text-blue-600 mt-1">{dashboardStats.upcomingMatches}</p>
        </Card>
      </div>

      {/* Recent Activity */}
      <Card title="Recent Activity">
        <p className="text-gray-700">{dashboardStats.recentActivity}</p>
        <Button variant="outline" size="sm" className="mt-4">View All Activities</Button>
      </Card>

      {/* Player List */}
      <Card title="Team Roster">
        <div className="mb-4">
          <Input
            id="player-search"
            type="text"
            placeholder="Search players by name or role..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Player
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Age
                </th>
                <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th scope="col" className="relative px-6 py-3">
                  <span className="sr-only">Actions</span>
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredPlayers.length > 0 ? (
                filteredPlayers.map((player) => (
                  <tr key={player.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div className="flex-shrink-0 h-10 w-10">
                          <img className="h-10 w-10 rounded-full" src={player.avatar} alt={player.name} />
                        </div>
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">{player.name}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{player.role}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{player.age}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        player.status === 'Active' ? 'bg-green-100 text-green-800' :
                        player.status === 'Injured' ? 'bg-red-100 text-red-800' :
                        'bg-yellow-100 text-yellow-800'
                      }`}>
                        {player.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <Button variant="outline" size="sm" onClick={() => handleViewDetails(player)}>
                        View
                      </Button>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={5} className="px-6 py-4 text-center text-gray-500">
                    No players found.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Player Details Modal */}
      <Modal isOpen={isModalOpen} onClose={handleCloseModal} title={selectedPlayer ? `${selectedPlayer.name} Details` : 'Player Details'}>
        {selectedPlayer && (
          <div className="space-y-4">
            <div className="flex items-center space-x-4">
              <img className="h-16 w-16 rounded-full" src={selectedPlayer.avatar} alt={selectedPlayer.name} />
              <div>
                <p className="text-lg font-semibold">{selectedPlayer.name}</p>
                <p className="text-sm text-gray-600">{selectedPlayer.role}</p>
              </div>
            </div>
            <p><strong>Age:</strong> {selectedPlayer.age}</p>
            <p><strong>Status:</strong> <span className={`font-semibold ${
              selectedPlayer.status === 'Active' ? 'text-green-600' :
              selectedPlayer.status === 'Injured' ? 'text-red-600' :
              'text-yellow-600'
            }`}>{selectedPlayer.status}</span></p>
            {/* Add more player details if available in data */}
          </div>
        )}
        <div className="mt-6 flex justify-end">
          <Button onClick={handleCloseModal} variant="secondary">Close</Button>
        </div>
      </Modal>
    </div>
  );
};

export default Dashboard;