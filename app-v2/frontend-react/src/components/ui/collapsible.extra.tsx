import { ChevronDownIcon } from "lucide-react";

export function CollapsibleIconChevron() {
  return (
    <ChevronDownIcon
      className="ml-auto transition-transform [[data-slot=collapsible][data-open]>*>*>&]:rotate-180"
    />
  );
}