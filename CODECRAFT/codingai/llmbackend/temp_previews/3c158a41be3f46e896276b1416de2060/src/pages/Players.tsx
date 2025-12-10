import React, { useState } from 'react';
import Card from '@components/Card';
import Table from '@components/Table';
import Button from '@components/Button';
import Modal from '@components/Modal';
import Input from '@components/Input';
import { players as initialPlayers, Player } from '@utils/data';
import useModal from '@hooks/useModal';

const Players: React.FC = () => {
  const [players, setPlayers] = useState<Player[]>(initialPlayers);
  const { isOpen, openModal, closeModal } = useModal();
  const [editingPlayer, setEditingPlayer] = useState<Player | null>(null);
  const [formData, setFormData] = useState<Omit<Player, 'id'>>({
    name: '',
    team: '',
    role: '',
    age: 0,
    battingStyle: '',
    bowlingStyle: '',
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleAddEditPlayer = () => {
    if (editingPlayer) {
      // Edit player
      setPlayers(players.map((p) => (p.id === editingPlayer.id ? { ...p, ...formData, age: Number(formData.age) } : p)));
    } else {
      // Add new player
      const newPlayer: Player = {
        id: (players.length + 1).toString(), // Simple ID generation
        ...formData,
        age: Number(formData.age),
      };
      setPlayers([...players, newPlayer]);
    }
    setEditingPlayer(null);
    closeModal();
    setFormData({ name: '', team: '', role: '', age: 0, battingStyle: '', bowlingStyle: '' });
  };

  const openAddModal = () => {
    setEditingPlayer(null);
    setFormData({ name: '', team: '', role: '', age: 0, battingStyle: '', bowlingStyle: '' });
    openModal();
  };

  const openEditModal = (player: Player) => {
    setEditingPlayer(player);
    setFormData({ ...player, age: player.age }); // Ensure age is number for form
    openModal();
  };

  const deletePlayer = (id: string | number) => {
    if (window.confirm("Are you sure you want to delete this player?")) {
      setPlayers(players.filter((p) => p.id !== id));
    }
  };

  const playerColumns = [
    { key: 'name', header: 'Name' },
    { key: 'team', header: 'Team' },
    { key: 'role', header: 'Role' },
    { key: 'age', header: 'Age' },
    { key: 'battingStyle', header: 'Batting Style' },
    { key: 'bowlingStyle', header: 'Bowling Style' },
    {
      key: 'actions',
      header: 'Actions',
      render: (player: Player) => (
        <div className="flex space-x-2">
          <Button variant="secondary" size="sm" onClick={() => openEditModal(player)}>
            Edit
          </Button>
          <Button variant="danger" size="sm" onClick={() => deletePlayer(player.id)}>
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Players Management</h1>
        <Button onClick={openAddModal} variant="primary">
          Add New Player
        </Button>
      </div>

      <Card>
        <Table data={players} columns={playerColumns} />
      </Card>

      <Modal
        isOpen={isOpen}
        onClose={closeModal}
        title={editingPlayer ? 'Edit Player' : 'Add New Player'}
        footer={
          <div className="flex space-x-2">
            <Button variant="secondary" onClick={closeModal}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleAddEditPlayer}>
              {editingPlayer ? 'Save Changes' : 'Add Player'}
            </Button>
          </div>
        }
      >
        <form className="space-y-4">
          <Input label="Player Name" name="name" value={formData.name} onChange={handleInputChange} placeholder="E.g., Virat Kohli" />
          <Input label="Team" name="team" value={formData.team} onChange={handleInputChange} placeholder="E.g., Royal Challengers Bangalore" />
          <Input label="Role" name="role" value={formData.role} onChange={handleInputChange} placeholder="E.g., Batsman" />
          <Input label="Age" name="age" type="number" value={formData.age} onChange={handleInputChange} placeholder="E.g., 34" />
          <Input label="Batting Style" name="battingStyle" value={formData.battingStyle} onChange={handleInputChange} placeholder="E.g., Right-hand Bat" />
          <Input label="Bowling Style" name="bowlingStyle" value={formData.bowlingStyle} onChange={handleInputChange} placeholder="E.g., Right-arm Medium" />
        </form>
      </Modal>
    </div>
  );
};

export default Players;