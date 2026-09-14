export function ToastPresetHttpRequestError({
  title,
  httpRequestStatus,
  httpStatusCode,
  message
}: {
  title: string,
  httpRequestStatus: 'OK' | 'ERROR',
  httpStatusCode: number | '-',
  message: string,
}) {
  return (
    <>

      <ToastTitle>
        {title}
      </ToastTitle>

      <ToastContent>

        <TextBlock aria-label="HTTP Communication Status">
          <TextBlockLabel>
            HTTP STATUS
          </TextBlockLabel>
          <TextBlockValue>
            {httpRequestStatus}
          </TextBlockValue>
        </TextBlock>

        <TextBlock aria-label="HTTP Status Code">
          <TextBlockLabel>
            HTTP CODE
          </TextBlockLabel>
          <TextBlockValue>
            {httpStatusCode}
          </TextBlockValue>
        </TextBlock>

        <TextBlock aria-label="HTTP Message">
          <TextBlockLabel>
            HTTP MESSAGE
          </TextBlockLabel>
          <TextBlockValue>
            {message}
          </TextBlockValue>
        </TextBlock>

      </ToastContent>

    </>
  );
}

function ToastTitle(props: React.ComponentProps<"p">) {
  return (
    <p
      aria-label="Toast Title"
      className="font-semibold"
      {...props}
    />
  );
}

function ToastContent(props: React.ComponentProps<"div">) {
  return (
    <div
      aria-label="Toast Content"
      className="mt-2 flex flex-col gap-1"
      {...props}
    />
  );
}

function TextBlock(props: React.ComponentProps<"p">) {
  return (
    <p
      className="px-1 py-0.5 flex flex-wrap gap-1 bg-foreground/5 rounded"
      {...props}
    />
  );
}

function TextBlockLabel(props: React.ComponentProps<"span">) {
  return (
    <span
      className="font-semibold opacity-50"
      {...props}
    />
  );
}

function TextBlockValue(props: React.ComponentProps<"div">) {
  return (
    <div
      className="font-semibold whitespace-pre-wrap"
      {...props}
    />
  );
}