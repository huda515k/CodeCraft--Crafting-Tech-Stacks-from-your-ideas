export interface Player {
  id: string;
  name: string;
  team: string;
  role: string;
  age: number;
  battingStyle: string;
  bowlingStyle: string;
}

export interface Team {
  id: string;
  name: string;
  city: string;
  coach: string;
  captain: string;
  homeGround: string;
}

export const players: Player[] = [
  {
    id: 'p1',
    name: 'Virat Kohli',
    team: 'Royal Challengers Bangalore',
    role: 'Batsman',
    age: 35,
    battingStyle: 'Right-hand Bat',
    bowlingStyle: 'Right-arm Medium',
  },
  {
    id: 'p2',
    name: 'Rohit Sharma',
    team: 'Mumbai Indians',
    role: 'Batsman',
    age: 36,
    battingStyle: 'Right-hand Bat',
    bowlingStyle: 'Right-arm Offbreak',
  },
  {
    id: 'p3',
    name: 'Jasprit Bumrah',
    team: 'Mumbai Indians',
    role: 'Bowler',
    age: 30,
    battingStyle: 'Right-hand Bat',
    bowlingStyle: 'Right-arm Fast',
  },
  {
    id: 'p4',
    name: 'Ravindra Jadeja',
    team: 'Chennai Super Kings',
    role: 'All-rounder',
    age: 35,
    battingStyle: 'Left-hand Bat',
    bowlingStyle: 'Left-arm Orthodox',
  },
  {
    id: 'p5',
    name: 'MS Dhoni',
    team: 'Chennai Super Kings',
    role: 'Wicketkeeper-Batsman',
    age: 42,
    battingStyle: 'Right-hand Bat',
    bowlingStyle: 'Right-arm Medium',
  },
];

export const teams: Team[] = [
  {
    id: 't1',
    name: 'Mumbai Indians',
    city: 'Mumbai',
    coach: 'Mark Boucher',
    captain: 'Hardik Pandya',
    homeGround: 'Wankhede Stadium',
  },
  {
    id: 't2',
    name: 'Chennai Super Kings',
    city: 'Chennai',
    coach: 'Stephen Fleming',
    captain: 'Ruturaj Gaikwad',
    homeGround: 'M. A. Chidambaram Stadium',
  },
  {
    id: 't3',
    name: 'Royal Challengers Bangalore',
    city: 'Bengaluru',
    coach: 'Andy Flower',
    captain: 'Faf du Plessis',
    homeGround: 'M. Chinnaswamy Stadium',
  },
  {
    id: 't4',
    name: 'Kolkata Knight Riders',
    city: 'Kolkata',
    coach: 'Chandrakant Pandit',
    captain: 'Shreyas Iyer',
    homeGround: 'Eden Gardens',
  },
  {
    id: 't5',
    name: 'Delhi Capitals',
    city: 'Delhi',
    coach: 'Ricky Ponting',
    captain: 'Rishabh Pant',
    homeGround: 'Arun Jaitley Stadium',
  },
];