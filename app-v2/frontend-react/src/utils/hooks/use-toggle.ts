import { useState } from "react";

export function useToggle({
  initialValue = false
}: {
  initialValue?: boolean;
}) {
  const [value, setValue] = useState(initialValue);
  const toggleValue = () => setValue(prev => !prev);
  const setValueTrue = () => setValue(true);
  const setValueFalse = () => setValue(false);
  return {
    value,
    setValue,
    setValueTrue,
    setValueFalse,
    toggleValue,
  };
}