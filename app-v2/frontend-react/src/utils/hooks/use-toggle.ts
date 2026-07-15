import { useState } from "react";

export function useToggle({
  initialValue = false
}: {
  initialValue?: boolean;
}) {
  const [isOn, setIsOn] = useState(initialValue);
  const toggleValue = () => setIsOn(prev => !prev);
  return {
    value: isOn,
    setValue: setIsOn,
    toggleValue,
  };
}