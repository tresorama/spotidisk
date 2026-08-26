import { useState } from "react";

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

/** 
 * React Hook for controlling {@link DialogConfirmAction} visibility state when used th controlled way.  
 * @example
 * ```tsx
 * const dialogState = useDialogConfirmAction();
 * 
 * <DialogConfirmAction dialogState={dialogState} />
 * <Button onClick={() => dialogState.setIsOpen(true)}>
 *   Show Dialog
 * </Button>
 * ```
 * */
export function useDialogConfirmAction() {
  const [isOpen, setIsOpen] = useState(false);
  return {
    isOpen,
    setIsOpen,
  };
}

export function DialogConfirmAction({
  title = "Are you sure?",
  description = "This action cannot be undone and cannot be reversed.",
  buttonCancelText = "Abort",
  buttonConfirmText = "Confirm",
  triggerJsx,
  dialogState,
  onConfirm,
}: {
  title?: string,
  description?: string,
  buttonCancelText?: string,
  buttonConfirmText?: string,
  /** Pass this for using uncontrolled component. Use `dialogState` for controlled component */
  triggerJsx?: React.ReactElement,
  /** Pass this for using controlled component. Use `triggerJsx` for uncontrolled component */
  dialogState?: ReturnType<typeof useDialogConfirmAction>,
  onConfirm?: () => void;
}) {

  if (typeof triggerJsx === "undefined" && typeof dialogState === "undefined") {
    throw new Error("You must pass either `triggerJsx` or `dialogState`");
  }

  if (triggerJsx) {
    return (
      <AlertDialog>
        <AlertDialogTrigger render={triggerJsx} />
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>
              {title}
            </AlertDialogTitle>
            <AlertDialogDescription>
              {description}
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>
              {buttonCancelText}
            </AlertDialogCancel>
            <AlertDialogAction onClick={onConfirm}>
              {buttonConfirmText}
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    );
  }

  return (
    <AlertDialog
      open={dialogState?.isOpen}
      onOpenChange={dialogState?.setIsOpen}
    >
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {title}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {description}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <AlertDialogFooter>
          <AlertDialogCancel>
            {buttonCancelText}
          </AlertDialogCancel>
          <AlertDialogAction onClick={onConfirm}>
            {buttonConfirmText}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}