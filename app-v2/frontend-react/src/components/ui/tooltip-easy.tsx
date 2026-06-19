import { Tooltip, TooltipContent, TooltipTrigger } from "./tooltip";

export function TooltipEasy({
  children,
  tooltipText,
  className,
}: {
  children: React.ReactNode,
  tooltipText: React.ReactNode,
  className?: React.ComponentProps<"div">["className"];
}) {
  return (
    <Tooltip>
      <TooltipTrigger className="text-left">
        {children}
      </TooltipTrigger>
      <TooltipContent className={className}>
        {tooltipText}
      </TooltipContent>
    </Tooltip>
  );
}