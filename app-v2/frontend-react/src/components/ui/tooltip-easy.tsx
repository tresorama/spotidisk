import { Tooltip, TooltipContent, TooltipTrigger } from "./tooltip";

export function TooltipEasy({
  children,
  tooltipText,
}: {
  children: React.ReactNode,
  tooltipText: string,
}) {
  return (
    <Tooltip>
      <TooltipTrigger>
        {children}
      </TooltipTrigger>
      <TooltipContent>
        {tooltipText}
      </TooltipContent>
    </Tooltip>
  );
}