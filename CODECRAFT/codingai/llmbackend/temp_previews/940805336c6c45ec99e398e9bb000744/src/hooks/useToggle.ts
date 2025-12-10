import { useState, useCallback } from 'react';

type UseToggleReturn = [boolean, () => void, (value: boolean) => void];

const useToggle = (initialState: boolean = false): UseToggleReturn => {
  const [state, setState] = useState<boolean>(initialState);

  const toggle = useCallback(() => setState((prevState) => !prevState), []);

  const setToggle = useCallback((value: boolean) => setState(value), []);

  return [state, toggle, setToggle];
};

export default useToggle;