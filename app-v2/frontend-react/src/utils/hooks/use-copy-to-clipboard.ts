import { toast } from "#/components/ui/sonner";

export function useCopyToClipboard() {

  /** 
   * Copy text to clipboard.  
   * It uses Promise (never throws) and return `true` or `false` indicating success.  
   * @neverthrows
   */
  const copy = async ({
    text,
    showToast = true
  }: {
    text: string,
    showToast?: boolean;
  }) => {
    return navigator.clipboard.writeText(text)
      .then(() => true)
      .catch(() => false)
      .then((copied) => {
        if (showToast) {
          if (copied) toast.success('Copied to clipboard');
          else toast.error('Failed to copy to clipboard');
        }
        return copied;
      });
  };

  /**
   * Paste text from clipboard.  
   * It uses Promise (never throws) and return `string` if success or `null` if errored.
   * @neverthrows
   */
  const paste = async ({
    showToast = true
  }: {
    showToast?: boolean;
  }) => {
    return navigator.clipboard.readText()
      .then((text) => text)
      .catch(() => null)
      .then((text) => {
        if (showToast) {
          if (text) toast.success('Pasted from clipboard');
          else toast.error('Failed to paste from clipboard');
        }
        return text;
      });
  };

  return { copy, paste };
}