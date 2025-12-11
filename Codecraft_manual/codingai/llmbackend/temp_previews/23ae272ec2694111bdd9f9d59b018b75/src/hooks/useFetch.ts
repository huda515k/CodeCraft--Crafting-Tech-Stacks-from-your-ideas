import { useState, useEffect } from 'react';

interface FetchResult<T> {
  data?: T;
  error?: Error | null;
}

const useFetch = <T>(url: string): FetchResult<T> => {
  const [data, setData] = useState<T>();
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    fetch(url)
      .then(response => response.json())
      .then(data => setData(data))
      .catch(error => setError(error));
  }, [url]);

  return { data, error };
};

export default useFetch;