export interface Player {
  id: string;
  name: string;
  role: 'Batsman' | 'Bowler' | 'All-rounder' | 'Wicketkeeper';
  age: number;
  status: 'Active' | 'Injured' | 'Bench';
  avatar: string;
}

export interface PlayerPerformance {
  playerId: string;
  matchesPlayed: number;
  runsScored: number;
  wicketsTaken: number;
  catches: number;
  stumpings: number;
  average: number;
  strikeRate: number;
  bestPerformance: string;
}

export const mockPlayers: Player[] = [
  { id: 'P001', name: 'Virat Singh', role: 'Batsman', age: 34, status: 'Active', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=VS' },
  { id: 'P002', name: 'Rohit Sharma', role: 'Batsman', age: 36, status: 'Active', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=RS' },
  { id: 'P003', name: 'Jasprit Bumrah', role: 'Bowler', age: 29, status: 'Active', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=JB' },
  { id: 'P004', name: 'Hardik Pandya', role: 'All-rounder', age: 30, status: 'Injured', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=HP' },
  { id: 'P005', name: 'KL Rahul', role: 'Wicketkeeper', age: 31, status: 'Active', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=KL' },
  { id: 'P006', name: 'Ravindra Jadeja', role: 'All-rounder', age: 35, status: 'Active', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=RJ' },
  { id: 'P007', name: 'Mohammed Shami', role: 'Bowler', age: 33, status: 'Bench', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=MS' },
  { id: 'P008', name: 'Shubman Gill', role: 'Batsman', age: 24, status: 'Active', avatar: 'https://api.dicebear.com/7.x/initials/svg?seed=SG' },
];

export const mockPerformance: PlayerPerformance[] = [
  { playerId: 'P001', matchesPlayed: 250, runsScored: 12500, wicketsTaken: 50, catches: 150, stumpings: 0, average: 55.2, strikeRate: 92.1, bestPerformance: '183 vs PAK' },
  { playerId: 'P002', matchesPlayed: 260, runsScored: 10000, wicketsTaken: 10, catches: 100, stumpings: 0, average: 48.5, strikeRate: 89.0, bestPerformance: '264 vs SL' },
  { playerId: 'P003', matchesPlayed: 150, runsScored: 150, wicketsTaken: 250, catches: 20, stumpings: 0, average: 10.0, strikeRate: 70.0, bestPerformance: '6/7 vs ENG' },
  { playerId: 'P004', matchesPlayed: 180, runsScored: 4500, wicketsTaken: 120, catches: 70, stumpings: 0, average: 35.0, strikeRate: 110.0, bestPerformance: '93 & 4/31 vs AUS' },
  { playerId: 'P005', matchesPlayed: 160, runsScored: 6000, wicketsTaken: 0, catches: 180, stumpings: 30, average: 40.0, strikeRate: 85.0, bestPerformance: '112 & 3 catches vs NZ' },
  { playerId: 'P006', matchesPlayed: 220, runsScored: 3000, wicketsTaken: 180, catches: 85, stumpings: 0, average: 30.0, strikeRate: 80.0, bestPerformance: '5/36 & 68 vs SA' },
  { playerId: 'P007', matchesPlayed: 120, runsScored: 80, wicketsTaken: 200, catches: 15, stumpings: 0, average: 8.0, strikeRate: 65.0, bestPerformance: '5/28 vs WI' },
  { playerId: 'P008', matchesPlayed: 80, runsScored: 3500, wicketsTaken: 0, catches: 40, stumpings: 0, average: 45.0, strikeRate: 95.0, bestPerformance: '208 vs NZ' },
];

export const dashboardStats = {
  totalPlayers: mockPlayers.length,
  activePlayers: mockPlayers.filter(p => p.status === 'Active').length,
  injuredPlayers: mockPlayers.filter(p => p.status === 'Injured').length,
  upcomingMatches: 3,
  recentActivity: 'Team practice session scheduled for tomorrow.',
};