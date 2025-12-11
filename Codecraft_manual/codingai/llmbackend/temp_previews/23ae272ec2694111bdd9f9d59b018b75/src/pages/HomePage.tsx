import React from 'react';
import { useFetch } from '../hooks/useFetch';

const HomePage = () => {
  const { data, error } = useFetch('https://jsonplaceholder.typicode.com/todos');

  if (error) return <div>Error: {error.message}</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Todo List</h1>
      <ul>
        {data.map(todo => (
          <li key={todo.id} className="p-2 border-b border-gray-200">
            {todo.title}
          </li>
        ))}
      </ul>
    </div>
  );
};

export default HomePage;